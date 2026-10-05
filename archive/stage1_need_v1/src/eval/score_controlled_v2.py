"""Score controlled_v2 items (sequence-level candidate scores and/or greedy generations).

Per query, with verdict = argmax candidate mapped to meaning (UNKNOWN wrong, MISSING kept):
  accuracy by context x gold; accuracy at exact equality (funds == bills, gold SUFFICIENT)
  shortfall-rate difference vs. `none` for every person context (true difference 0 by design),
    and budget_loss - budget_none; base-clustered bootstrap (2000)
  effort minimal pair: search_low - search_high
  the same key contrasts split by fact surface (format x order)
  monotonicity: within base x context, adjacent funds levels SUFFICIENT -> SHORTFALL as funds rise
Generated answers (--gen) are parsed by exact whole-word match of the candidate labels.
Usage:
  python src/eval/score_controlled_v2.py --data data/controlled_v2/dev.jsonl --seq results/v2/dev_seq/qwen3-8b.jsonl [--gen results/v2/dev_gen/qwen3-8b.jsonl]
"""
import argparse
import json
import os
import re
import sys

import numpy as np
import pandas as pd

ROOT = os.environ.get("WN_ROOT", "/workspace/welfare-need-naacl")
sys.path.insert(0, f"{ROOT}/src/eval")
from score_diagnostic_seq import MEANING, decide  # noqa: E402

PERSON = ["employed", "unemp_status", "unemp_cause", "unemp_nopay", "search_high", "search_low", "lexical_closure"]


def parse_gen(q, raw, finish):
    if finish == "length":
        return "TRUNCATED"
    t = str(raw).strip().upper()
    hits = [k for k in MEANING[q] if re.search(rf"\b{k}\b", t)]
    return MEANING[q][hits[0]] if len(hits) == 1 else "INVALID"


def rate_diff(d, a, b, n=2000, seed=0):
    """Shortfall-rate difference a - b with a base-clustered bootstrap. Every base has the same number of
    items per context (one per funds level), so the pooled difference equals the mean of per-base differences."""
    m = d[d.context.isin([a, b])].pivot_table(index="base_id", columns="context", values="is_short", aggfunc="mean")
    if a not in m or b not in m:
        return [float("nan")] * 3
    diff = (m[a] - m[b]).dropna().to_numpy()
    rng = np.random.default_rng(seed)
    bs = diff[rng.integers(0, len(diff), (n, len(diff)))].mean(axis=1)
    return [round(float(diff.mean()), 3)] + [round(float(v), 3) for v in np.percentile(bs, [2.5, 97.5])]


def monotonicity(d):
    viol = comps = 0
    bases = set()
    for (b, c), s in d.groupby(["base_id", "context"]):
        v = s.sort_values("funds").verdict.tolist()
        for lo, hi in zip(v, v[1:]):
            if {lo, hi} <= {"SHORTFALL", "SUFFICIENT"}:
                comps += 1
                if lo == "SUFFICIENT" and hi == "SHORTFALL":
                    viol += 1
                    bases.add(b)
    return dict(violations=viol, comparisons=comps, bases_with_violation=len(bases))


def summarize(df):
    out = {}
    for q, d in df.groupby("query"):
        d = d.assign(ok=d.verdict == d.gold, is_short=(d.verdict == "SHORTFALL").astype(float))
        acc = d.pivot_table(index="context", columns="gold", values="ok", aggfunc="mean")
        eq = d[d.gap_frac == 0].groupby("context").ok.mean()
        diffs = {f"{c}_minus_none": rate_diff(d, c, "none") for c in PERSON}
        diffs["budget_loss_minus_budget_none"] = rate_diff(d, "budget_loss", "budget_none")
        diffs["search_low_minus_search_high"] = rate_diff(d, "search_low", "search_high")
        by_surface = {}
        for (fmt, order), s in d.groupby(["format", "order"]):
            by_surface[f"{fmt}/{order}"] = {
                "unemp_nopay_minus_none": rate_diff(s, "unemp_nopay", "none"),
                "search_low_minus_search_high": rate_diff(s, "search_low", "search_high")}
        out[q] = dict(
            n=len(d), state_rates=d.verdict.value_counts(normalize=True).round(4).to_dict(),
            accuracy={c: {k: round(float(v), 3) for k, v in r.items()} for c, r in acc.iterrows()},
            accuracy_at_equality={c: round(float(v), 3) for c, v in eq.items()},
            shortfall_rate_diff_true_zero=diffs, by_fact_surface=by_surface, monotonicity=monotonicity(d))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--seq", action="append", default=[])
    ap.add_argument("--gen")
    a = ap.parse_args()
    items = pd.read_json(a.data, lines=True)
    out = {}
    if a.seq:
        r = pd.concat([pd.read_json(p, lines=True) for p in a.seq])
        r = r[r["query"].isin(MEANING)]
        r["verdict"] = [decide(q, s)[0] for q, s in zip(r["query"], r["label_logprob"])]
        out["model"] = sorted(r.model.unique().tolist())
        out["seq"] = summarize(r.merge(items, on="profile_id"))
    if a.gen:
        g = pd.read_json(a.gen, lines=True, dtype={"raw": str})
        g = g[g["query"].isin(MEANING)]
        g["verdict"] = [parse_gen(q, x, f) for q, x, f in zip(g["query"], g["raw"], g["finish_reason"])]
        out["gen"] = summarize(g.merge(items, on="profile_id"))
        if a.seq:
            m = g[["profile_id", "query", "verdict"]].merge(r[["profile_id", "query", "verdict"]], on=["profile_id", "query"], suffixes=("_gen", "_seq"))
            out["gen_vs_seq_agreement"] = m.groupby("query").apply(lambda t: round(float((t.verdict_gen == t.verdict_seq).mean()), 4)).to_dict()
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
