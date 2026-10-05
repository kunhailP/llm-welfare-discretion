"""Audit aggregation (2026-10-05 review).

1) Effort pairs (pilot core, unemployed context, high vs low job search, same base and resource state):
   - complete pairs = both members have a binary verdict (SHORTFALL/SUFFICIENT)
   - true binary flips vs. state changes involving UNKNOWN / MISSING / TRUNCATED / INVALID
   - shortfall-rate difference (low - high) on complete pairs, base-clustered bootstrap
   - worst-case bounds over all pairs, letting every non-binary member take either value
     (bounds, not confidence intervals)
   Works for sequence-level results (--pilot-seq) and greedy generations (--pilot-gen).
2) Generation vs. sequence-score agreement on the oracle ladder (--diag-gen with --diag-seq):
   share of items whose parsed generated answer equals the argmax candidate verdict.

Usage:
  python src/eval/score_audit.py --pilot-seq results/pilot_seq/qwen3-8b.jsonl \
      --pilot-gen results/pilot/qwen3-8b.jsonl \
      --diag-seq results/diagnostic_seq/qwen3-8b.jsonl --diag-seq results/diagnostic_seq/qwen3-8b__audit.jsonl \
      --diag-gen results/diagnostic_gen/qwen3-8b.jsonl
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.environ.get("WN_ROOT", "/workspace/welfare-need-naacl")
sys.path.insert(0, f"{ROOT}/src/eval")
from score import parse  # noqa: E402
from score_diagnostic_seq import MEANING, decide  # noqa: E402

BIN = ("SHORTFALL", "SUFFICIENT")


def effort_pairs(df):
    out = {}
    core = df[df.control == "core"]
    for q, d in core.groupby("query"):
        w = d.pivot_table(index=["base_id", "resource_state"], columns="activity", values="verdict", aggfunc="first")
        w = w.dropna(subset=["high", "low"])
        complete = w[w.high.isin(BIN) & w.low.isin(BIN)]
        flips = complete[complete.high != complete.low]
        nonbin = w[~(w.high.isin(BIN) & w.low.isin(BIN))]
        status_changes = nonbin[nonbin.high != nonbin.low]

        def diff(t):
            return float((t.low == "SHORTFALL").mean() - (t.high == "SHORTFALL").mean())

        cp = complete.reset_index()
        g = {k: v for k, v in cp.groupby("base_id")}
        rng = np.random.default_rng(0)
        keys = list(g)
        boots = [diff(pd.concat([g[k] for k in rng.choice(keys, len(keys))])) for _ in range(2000)] if keys else [np.nan]
        n = len(w)
        lo_sh = (w.low == "SHORTFALL").sum()
        hi_sh = (w.high == "SHORTFALL").sum()
        lo_unk = (~w.low.isin(BIN)).sum()
        hi_unk = (~w.high.isin(BIN)).sum()
        lower = ((lo_sh) - (hi_sh + hi_unk)) / n
        upper = ((lo_sh + lo_unk) - hi_sh) / n
        out[q] = dict(
            pairs=n, complete_pairs=len(complete), binary_flips=len(flips),
            flip_patterns=(flips.high + ">" + flips.low).value_counts().to_dict(),
            nonbinary_status_changes=len(status_changes),
            nonbinary_patterns=(status_changes.high + ">" + status_changes.low).value_counts().to_dict(),
            low_minus_high_shortfall_rate_complete=[round(diff(complete), 4)] + [round(float(v), 4) for v in np.nanpercentile(boots, [2.5, 97.5])],
            worst_case_bounds_all_pairs=[round(float(lower), 4), round(float(upper), 4)],
            missing_rate_by_activity={a: round(float((~d[d.activity == a].verdict.isin(BIN)).mean()), 4) for a in ("high", "low")},
        )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot-seq")
    ap.add_argument("--pilot-gen")
    ap.add_argument("--diag-seq", action="append", default=[])
    ap.add_argument("--diag-gen")
    a = ap.parse_args()
    prof = pd.read_json(f"{ROOT}/data/pilot/profiles.jsonl", lines=True)
    out = {}
    if a.pilot_seq and os.path.exists(a.pilot_seq):
        r = pd.read_json(a.pilot_seq, lines=True)
        r["verdict"] = [decide(q, s)[0] for q, s in zip(r["query"], r["label_logprob"])]
        out["effort_pairs_seq"] = effort_pairs(r.merge(prof, on="profile_id"))
    if a.pilot_gen and os.path.exists(a.pilot_gen):
        r = pd.read_json(a.pilot_gen, lines=True, dtype={"raw": str})
        r = r[r["query"].isin(MEANING)]
        r["verdict"] = [v if v in BIN + ("UNKNOWN",) else str(v)
                        for v in (parse(q, x, f) for q, x, f in zip(r["query"], r["raw"], r["finish_reason"]))]
        out["effort_pairs_gen"] = effort_pairs(r.merge(prof, on="profile_id"))
    if a.diag_seq and a.diag_gen and os.path.exists(a.diag_gen):
        s = pd.concat([pd.read_json(p, lines=True) for p in a.diag_seq if os.path.exists(p)])
        s["seq"] = [decide(q, x)[0] for q, x in zip(s["query"], s["label_logprob"])]
        g = pd.read_json(a.diag_gen, lines=True, dtype={"raw": str})
        g["gen"] = [parse(q, x, f) for q, x, f in zip(g["query"], g["raw"], g["finish_reason"])]
        m = g.merge(s[["profile_id", "query", "seq"]], on=["profile_id", "query"])
        out["gen_vs_seq"] = {q: dict(n=len(t), agree=round(float((t.gen == t.seq).mean()), 4),
                                     gen_nonbinary=round(float((~t.gen.isin(BIN)).mean()), 4),
                                     disagreements=(t[t.gen != t.seq].seq + "->" + t[t.gen != t.seq].gen.astype(str)).value_counts().head(5).to_dict())
                             for q, t in m.groupby("query")}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
