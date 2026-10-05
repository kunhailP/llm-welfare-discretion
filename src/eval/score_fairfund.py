"""FairFund need-only probe: does causal framing move need severity (q4) when the material
situation text is shared across framings? Compare with deservingness (q5).

Estimate: mean(q4 | framing) - mean(q4 | structural), cluster bootstrap over scenario_id.
Usage: python src/eval/score_fairfund.py --results results/fairfund/qwen3-8b.jsonl
"""
import argparse
import json
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "/workspace/welfare-need-naacl/src/eval")
from score import parse  # noqa: E402

DATA = "/workspace/welfare-need-naacl/data/external/fairfund_need_probe.jsonl"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--n-boot", type=int, default=2000)
    a = ap.parse_args()
    prof = pd.read_json(DATA, lines=True)
    res = pd.read_json(a.results, lines=True, dtype={"raw": str})
    res["v"] = [parse(q, r, f) for q, r, f in zip(res["query"], res["raw"], res["finish_reason"])]
    df = res.merge(prof, on="profile_id")
    out = {"model": res["model"].iloc[0]}
    rng = np.random.default_rng(0)
    for q in ("q4_need_severity", "q5_deservingness"):
        d = df[(df["query"] == q)].copy()
        valid = d.v.map(lambda x: isinstance(x, int))
        d = d[valid].assign(v=lambda s: s.v.astype(float))
        means = d.groupby("framing").v.mean()
        scen = d.scenario_id.unique()
        groups = {s: g for s, g in d.groupby("scenario_id")}
        boots = []
        for _ in range(a.n_boot):
            b = pd.concat([groups[s] for s in rng.choice(scen, len(scen))]).groupby("framing").v.mean()
            boots.append(b - b["structural"])
        boots = pd.DataFrame(boots)
        out[q] = dict(valid_rate=round(float(valid.mean()), 3),
                      mean_by_framing=means.round(3).to_dict(),
                      diff_vs_structural={f: [round(means[f] - means["structural"], 3),
                                              round(float(np.percentile(boots[f], 2.5)), 3),
                                              round(float(np.percentile(boots[f], 97.5)), 3)]
                                          for f in means.index if f != "structural"})
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
