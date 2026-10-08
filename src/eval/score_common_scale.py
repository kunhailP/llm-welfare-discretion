"""Both readouts on one scale (after the blind reviews, 2026-10-08): paired hi-lo cue contrasts as VERDICT differences
(YES=1/NO=0), base-clustered bootstrap CIs, for the direct readout (first-token verdict, both orders) and every generated
run (thinking on seeds, thinking off, greedy), on the same item set (the thinking subsample, narrative). For zero-flip
cells it also reports what a zero can exclude: the rule-of-three item-level upper bound (3/n) and a cluster-level bound
(1 - 0.05^(1/n_bases)): the largest per-base flip probability consistent with no flipped base at 95%.
ABAWD is reported with and without the child-15 trap cell.
Usage: python src/eval/score_common_scale.py  -> results/common_scale/contrasts.json + .md
"""
import json, pathlib, random
from collections import defaultdict
import numpy as np, pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[2]
import sys; sys.path.insert(0, str(ROOT / "src/run"))
from run_rules_think import subsample  # noqa: E402

PAIRS = {"control": ("control_high", "control_low"), "effort": ("effort_high", "effort_low")}
MODELS = ["qwen3-8b", "ministral3-8b", "qwen3-14b", "qwen3-32b-awq"]
RUNS = [("direct", "results/rules_pilot/{m}.jsonl"), ("think_s0", "results/rules_think/{m}.jsonl"),
        ("think_s1", "results/rules_think/{m}_s1.jsonl"), ("think_greedy", "results/rules_think/{m}_greedy.jsonl"),
        ("off_s0", "results/rules_think/{m}_off.jsonl"), ("off_s1", "results/rules_think/{m}_off_s1.jsonl")]


def items():
    rows = [json.loads(l) for l in open(ROOT / "data/rules_pilot/pilot.jsonl")]
    sub = {r["item_id"] for r, _ in subsample(rows)}
    d = pd.DataFrame([{k: v for k, v in r.items() if k not in ("text", "facts")} for r in rows])
    d = d[d.item_id.isin(sub)].copy()
    d["cell"] = np.where(d.task == "abawd", d.status.astype(str) + "|" + d.hours.astype(str), d.margin.astype(str))
    return d


def direct_verdicts(m):
    r = pd.read_json(ROOT / f"results/rules_pilot/{m}.jsonl", lines=True)
    r["p"] = np.where(r.lp_yes.isna() | r.lp_no.isna(), np.nan, 1 / (1 + np.exp(r.lp_no - r.lp_yes)))
    p = r.groupby("item_id").p.mean()
    return p.map(lambda x: None if pd.isna(x) else ("YES" if x > 0.5 else "NO")).to_dict()


def gen_verdicts(path):
    return {r["item_id"]: (r["verdict"] if r["verdict"] in ("YES", "NO") else None) for r in map(json.loads, open(path))}


def boot(df, n=2000, seed=0):
    bases = df.base.unique(); g = {b: df[df.base == b].d.values for b in bases}
    rng = np.random.default_rng(seed)
    vals = [np.concatenate([g[b] for b in rng.choice(bases, len(bases))]).mean() for _ in range(n)]
    return [round(float(df.d.mean()), 4), *np.round(np.percentile(vals, [2.5, 97.5]), 4).tolist()]


def contrasts(d, verdict):
    d = d.copy(); d["v"] = d.item_id.map(verdict)
    out = {}
    for task in ("gross", "elig", "abawd"):
        subsets = {"all": d[d.task == task]}
        if task == "abawd":
            subsets["no_trap"] = d[(d.task == task) & (d.status != "child_15_trap")]
        for sub, t in subsets.items():
            for name, (hi, lo) in PAIRS.items():
                h = t[t.cue == hi].set_index(["base", "cell"]).v; l = t[t.cue == lo].set_index(["base", "cell"]).v
                j = pd.concat([h, l], axis=1, keys=["h", "l"]).dropna().reset_index()
                if j.empty:
                    continue
                j["d"] = (j.h == "YES").astype(float) - (j.l == "YES").astype(float)
                flips = int((j.h != j.l).sum()); nb = int(j.base.nunique())
                out[f"{task}|{sub}|{name}"] = dict(n_pairs=int(len(j)), n_bases=nb, flips=flips, dP_verdict=boot(j),
                                                   upper_item_rule3=round(3 / len(j), 4) if flips == 0 else None,
                                                   upper_cluster95=round(1 - 0.05 ** (1 / nb), 4) if flips == 0 else None)
    return out


def main():
    d = items()
    res = {}
    for m in MODELS:
        res[m] = {}
        for tag, pat in RUNS:
            p = ROOT / pat.format(m=m)
            if p.exists():
                res[m][tag] = contrasts(d, direct_verdicts(m) if tag == "direct" else gen_verdicts(p))
    out = ROOT / "results/common_scale"; out.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(out / "contrasts.json", "w"), indent=1)
    rows = ["| model | readout | task | control hi-lo (verdict) [CI] | flips/pairs | effort hi-lo (verdict) [CI] | flips/pairs | zero bound (item / cluster) |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for m in MODELS:
        for tag in res[m]:
            for task in ("gross", "elig", "abawd|all", "abawd|no_trap"):
                key = task if "|" in task else f"{task}|all"
                c, e = res[m][tag].get(f"{key}|control"), res[m][tag].get(f"{key}|effort")
                if not c:
                    continue
                f = lambda x: f"{x['dP_verdict'][0]:+.3f} [{x['dP_verdict'][1]:+.3f}, {x['dP_verdict'][2]:+.3f}]"
                zb = f"{c['upper_item_rule3']} / {c['upper_cluster95']}" if c["flips"] == 0 else "-"
                rows.append(f"| {m} | {tag} | {task} | {f(c)} | {c['flips']}/{c['n_pairs']} | {f(e)} | {e['flips']}/{e['n_pairs']} | {zb} |")
    (out / "contrasts.md").write_text("\n".join(rows) + "\n")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
