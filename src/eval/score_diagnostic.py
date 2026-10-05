"""Score the oracle-ladder diagnostic from first-token log-probabilities.

Label probability: top-20 first tokens are mapped to a label when the stripped, upper-cased token
is a non-empty prefix of exactly one label; tokens matching several labels count as 'ambiguous'
(their mass is reported, not assigned). q1_yesno is the clean readout (YES/NO/UNKNOWN are single,
distinct tokens); SHORTFALL/SUFFICIENT share the prefix "S" in some tokenizers.

Outputs, per query: P(SUFFICIENT) by context x level x gap, accuracy of the argmax label on each
side of the threshold, and the interpolated 50% threshold (gap fraction where P(SUFFICIENT)=0.5).
Usage: python src/eval/score_diagnostic.py --results results/diagnostic/qwen3-8b.jsonl
"""
import argparse
import json
import math

import numpy as np
import pandas as pd

DATA = "/workspace/welfare-need-naacl/data/diagnostic/oracle_ladder.jsonl"
LABELS = {"q1_yesno": {"YES": "SUFFICIENT", "NO": "SHORTFALL", "UNKNOWN": "UNKNOWN"}}
for q in ("q1_direct", "q1_direct_rev"):
    LABELS[q] = {"SHORTFALL": "SHORTFALL", "SUFFICIENT": "SUFFICIENT", "UNKNOWN": "UNKNOWN"}


def label_probs(q, top):
    mass = {"SHORTFALL": 0.0, "SUFFICIENT": 0.0, "UNKNOWN": 0.0, "ambiguous": 0.0}
    for tok, lp in top:
        t = (tok or "").strip().upper()
        if not t:
            continue
        hits = {v for k, v in LABELS[q].items() if k.startswith(t)}
        if len(hits) == 1:
            mass[hits.pop()] += math.exp(lp)
        elif len(hits) > 1:
            mass["ambiguous"] += math.exp(lp)
    covered = mass["SHORTFALL"] + mass["SUFFICIENT"] + mass["UNKNOWN"]
    p_suff = mass["SUFFICIENT"] / covered if covered > 0 else np.nan
    return p_suff, covered, mass["ambiguous"]


def threshold(curve):
    """Linear interpolation of the gap fraction where P(SUFFICIENT) crosses 0.5 (nan if never)."""
    g, p = curve.index.values, curve.values
    for i in range(len(g) - 1):
        if (p[i] - 0.5) * (p[i + 1] - 0.5) <= 0 and p[i] != p[i + 1]:
            return float(g[i] + (0.5 - p[i]) * (g[i + 1] - g[i]) / (p[i + 1] - p[i]))
    return float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    a = ap.parse_args()
    prof = pd.read_json(DATA, lines=True)
    res = pd.read_json(a.results, lines=True, dtype={"raw": str})
    vals = [label_probs(q, t) for q, t in zip(res["query"], res["top_logprobs"])]
    res["p_suff"], res["covered"], res["ambig"] = zip(*vals)
    df = res.merge(prof, on="profile_id")
    df["cond"] = df.context + "/" + df.level
    out = {"model": res["model"].iloc[0]}
    for q, d in df.groupby("query"):
        curve = d.pivot_table(index="gap_frac", columns="cond", values="p_suff", aggfunc="mean")
        d = d.assign(pred=np.where(d.p_suff > 0.5, "SUFFICIENT", "SHORTFALL"))
        acc = d.assign(ok=d.pred == d.gold_shortfall).pivot_table(index="cond", columns="gold_shortfall", values="ok", aggfunc="mean")
        out[q] = dict(
            label_mass_covered=round(float(d.covered.mean()), 3),
            ambiguous_mass=round(float(d.ambig.mean()), 3),
            threshold_gap_frac={c: round(threshold(curve[c]), 3) for c in curve.columns},
            accuracy={c: {k: round(float(v), 3) for k, v in r.items()} for c, r in acc.iterrows()},
            p_sufficient_curve={c: {f"{g:+.2f}": round(float(v), 3) for g, v in curve[c].items()} for c in curve.columns},
        )
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
