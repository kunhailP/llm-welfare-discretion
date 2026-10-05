"""Score the oracle ladder from sequence-level label log-probabilities.

P(SUFFICIENT) = softmax over the full candidate label strings (YES maps to SUFFICIENT for q1_yesno).
Reports, per query: mean P(SUFFICIENT) by condition x gap, accuracy (argmax) on sufficient/shortfall
items, and base-clustered bootstrap CIs for the key contrast: accuracy on SUFFICIENT items in
`unemployed` minus `none` context, at each level.
Usage: python src/eval/score_diagnostic_seq.py --results results/diagnostic_seq/qwen3-8b.jsonl
"""
import argparse
import json

import numpy as np
import pandas as pd

DATA = "/workspace/welfare-need-naacl/data/diagnostic/oracle_ladder.jsonl"
SUFF = {"q1_yesno": "YES", "q1_yesno_rev": "YES", "q1_ab": "B", "q1_ab_rev": "A"}


def p_suff(q, d):
    if any(v is None for v in d.values()):
        return np.nan
    labs = list(d)
    x = np.array([d[k] for k in labs])
    p = np.exp(x - x.max()); p /= p.sum()
    return float(p[labs.index(SUFF.get(q, "SUFFICIENT"))])


def boot_diff(df, a, b, n=2000, seed=0):
    rng = np.random.default_rng(seed)
    bases = df.base_id.unique()
    g = {k: v for k, v in df.groupby("base_id")}
    f = lambda s: s[s.context == a].ok.mean() - s[s.context == b].ok.mean()
    vals = [f(pd.concat([g[k] for k in rng.choice(bases, len(bases))])) for _ in range(n)]
    return [round(f(df), 3)] + [round(float(v), 3) for v in np.percentile(vals, [2.5, 97.5])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    a = ap.parse_args()
    prof = pd.read_json(DATA, lines=True)
    res = pd.read_json(a.results, lines=True)
    res["p"] = [p_suff(q, d) for q, d in zip(res["query"], res["label_logprob"])]
    df = res.merge(prof, on="profile_id")
    df["cond"] = df.context + "/" + df.level
    df["ok"] = np.where(df.p > 0.5, "SUFFICIENT", "SHORTFALL") == df.gold_shortfall
    out = {"model": res["model"].iloc[0], "nan_rate": round(float(df.p.isna().mean()), 4)}
    for q, d in df.groupby("query"):
        curve = d.pivot_table(index="gap_frac", columns="cond", values="p", aggfunc="mean")
        acc = d.pivot_table(index="cond", columns="gold_shortfall", values="ok", aggfunc="mean")
        suff = d[d.gold_shortfall == "SUFFICIENT"]
        contrast = {}
        for lv in ("L0", "L2", "L4"):
            s = suff[suff.level == lv]
            contrast[lv] = {"unemployed_minus_none": boot_diff(s, "unemployed", "none"),
                            "employed_minus_none": boot_diff(s, "employed", "none")}
        out[q] = dict(accuracy={c: {k: round(float(v), 3) for k, v in r.items()} for c, r in acc.iterrows()},
                      sufficient_acc_contrast=contrast,
                      p_sufficient_curve={c: {f"{g:+.2f}": round(float(v), 3) for g, v in curve[c].items()} for c in curve.columns})
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
