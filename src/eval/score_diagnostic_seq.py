"""Score oracle-ladder items from sequence-level candidate-label scores.

Decision rule (same for every query): argmax over the full candidate label strings, then map the
chosen label to its meaning (SHORTFALL / SUFFICIENT / UNKNOWN). UNKNOWN stays its own state and
counts as wrong for accuracy; missing scores stay NaN ("MISSING"). The normalized candidate score
is a relative score within the candidate set, not a calibrated belief, and excludes EOS.

Reports per query:
  - accuracy by condition x gold (UNKNOWN = wrong), UNKNOWN and MISSING rates
  - shortfall-rate difference between contexts at each level (true difference = 0 by design),
    base-clustered bootstrap CI
  - SUFFICIENT-item accuracy contrasts (as before) and the relative-score curve by gap
  - monotonicity violations: within base x context x level, adjacent funds levels where the verdict
    goes SUFFICIENT -> SHORTFALL as funds increase (counted per comparison and per base)
Usage: python src/eval/score_diagnostic_seq.py --results results/diagnostic_seq/qwen3-8b.jsonl [--results more.jsonl]
"""
import argparse
import json
import os

import numpy as np
import pandas as pd

ROOT = os.environ.get("WN_ROOT", "/workspace/welfare-need-naacl")
DATA = f"{ROOT}/data/diagnostic/oracle_ladder.jsonl"
MEANING = {
    "q1_direct": {"SHORTFALL": "SHORTFALL", "SUFFICIENT": "SUFFICIENT", "UNKNOWN": "UNKNOWN"},
    "q1_direct_rev": {"SHORTFALL": "SHORTFALL", "SUFFICIENT": "SUFFICIENT", "UNKNOWN": "UNKNOWN"},
    "q2_definition": {"SHORTFALL": "SHORTFALL", "SUFFICIENT": "SUFFICIENT", "UNKNOWN": "UNKNOWN"},
    "q1_yesno": {"YES": "SUFFICIENT", "NO": "SHORTFALL", "UNKNOWN": "UNKNOWN"},
    "q1_yesno_rev": {"YES": "SUFFICIENT", "NO": "SHORTFALL", "UNKNOWN": "UNKNOWN"},
    "q1_ab": {"A": "SHORTFALL", "B": "SUFFICIENT", "C": "UNKNOWN"},
    "q1_ab_rev": {"A": "SUFFICIENT", "B": "SHORTFALL", "C": "UNKNOWN"},
}


def decide(q, scores):
    """Return (verdict, relative score of SUFFICIENT). verdict in SHORTFALL/SUFFICIENT/UNKNOWN/MISSING."""
    if not scores or any(v is None for v in scores.values()):
        return "MISSING", np.nan
    labs = list(scores)
    x = np.array([scores[k] for k in labs])
    p = np.exp(x - x.max()); p /= p.sum()
    m = MEANING[q]
    suff = next(k for k, v in m.items() if v == "SUFFICIENT")
    return m[labs[int(p.argmax())]], float(p[labs.index(suff)])


def boot(df, stat, n=2000, seed=0):
    rng = np.random.default_rng(seed)
    g = {k: v for k, v in df.groupby("base_id")}
    keys = list(g)
    vals = [stat(pd.concat([g[k] for k in rng.choice(keys, len(keys))])) for _ in range(n)]
    return [round(float(stat(df)), 3)] + [round(float(v), 3) for v in np.nanpercentile(vals, [2.5, 97.5])]


def monotonicity(d):
    """Adjacent funds levels within base x cond: SUFFICIENT at lower funds, SHORTFALL at higher funds."""
    viol, comps, bases = 0, 0, set()
    for (b, c), s in d.groupby(["base_id", "cond"]):
        v = s.sort_values("funds").verdict.tolist()
        for lo, hi in zip(v, v[1:]):
            if lo in ("SHORTFALL", "SUFFICIENT") and hi in ("SHORTFALL", "SUFFICIENT"):
                comps += 1
                if lo == "SUFFICIENT" and hi == "SHORTFALL":
                    viol += 1
                    bases.add(b)
    return dict(violations=viol, comparisons=comps, bases_with_violation=len(bases))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", action="append", required=True)
    a = ap.parse_args()
    prof = pd.read_json(DATA, lines=True)
    res = pd.concat([pd.read_json(r, lines=True) for r in a.results])
    res = res[res["query"].isin(MEANING)]
    out_v = [decide(q, s) for q, s in zip(res["query"], res["label_logprob"])]
    res["verdict"], res["rel_suff"] = zip(*out_v)
    df = res.merge(prof, on="profile_id")
    df["cond"] = df.context + "/" + df.level
    df["ok"] = df.verdict == df.gold_shortfall
    df["is_short"] = (df.verdict == "SHORTFALL").astype(float)
    out = {"model": sorted(res["model"].unique().tolist())}
    for q, d in df.groupby("query"):
        acc = d.pivot_table(index="cond", columns="gold_shortfall", values="ok", aggfunc="mean")
        rate_diff = {}
        for lv in ("L0", "L2", "L4"):
            s = d[d.level == lv]
            for ctx in ("unemployed", "employed"):
                rate_diff[f"{lv}:{ctx}_minus_none"] = boot(
                    s[s.context.isin([ctx, "none"])],
                    lambda t, c=ctx: t[t.context == c].is_short.mean() - t[t.context == "none"].is_short.mean())
        curve = d.pivot_table(index="gap_frac", columns="cond", values="rel_suff", aggfunc="mean")
        out[q] = dict(
            n=len(d),
            unknown_rate=round(float((d.verdict == "UNKNOWN").mean()), 4),
            missing_rate=round(float((d.verdict == "MISSING").mean()), 4),
            accuracy={c: {k: round(float(v), 3) for k, v in r.items()} for c, r in acc.iterrows()},
            shortfall_rate_diff_true_zero=rate_diff,
            monotonicity=monotonicity(d),
            relative_score_curve={c: {f"{g:+.2f}": round(float(v), 3) for g, v in curve[c].items()} for c in curve.columns},
        )
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
