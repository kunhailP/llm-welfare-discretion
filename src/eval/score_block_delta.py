"""Before/after change of each paired cue contrast when the computation block is supplied (docs/paper1/computed_burden.md).
For every model, row set and readout present with and without the block, and for each task and contrast, the per-pair change
delta = (verdict_hi - verdict_lo)_block - (verdict_hi - verdict_lo)_original on the pairs scored in both files, with its
household-clustered 95% bootstrap interval (same resampling as score_computed.boot). Separates "the removal criterion is met"
(observed flips) from "the decrease is estimated precisely" (interval). Usage: python src/eval/score_block_delta.py [--dir results/computed]
"""
import argparse, json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src/eval"))
import score_computed as sc  # noqa: E402

PAIRS = [("sub_income", "sub_income_computed", "original -> + block"), ("sub_income", "sub_income_computed_plain", "original -> + plain block"),
         ("sub12_income", "sub12_income_computed", "s12 v1 -> + block"), ("sub12v2_income", "sub12v2_income_computed", "s12 v2 -> + block")]
MODELS = ["qwen3-8b", "ministral3-8b", "qwen3-14b", "qwen3-32b-awq"]
CONTRASTS = [("control_high", "control_low", "control"), ("effort_high", "effort_low", "effort")]


def verdicts(data, results):
    items = {json.loads(l)["item_id"]: json.loads(l) for l in open(data)}
    rows = [json.loads(l) for l in open(results)]
    p = sc.pyes_direct(rows) if "lp_yes" in rows[0] else sc.pyes_generated(rows)
    return items, {i: (1.0 if v > 0.5 else 0.0) for i, v in p.items() if i in items}


def delta(items0, v0, items1, v1, task, hi, lo):
    groups = {}
    for i in items0:
        if items0[i]["task"] == task:
            groups.setdefault(i.replace("_" + items0[i]["cue"] + "_", "_CUE_"), {})[items0[i]["cue"]] = i
    d, before, after, n = {}, [], [], 0
    for g, c in groups.items():
        if hi in c and lo in c and all(k in v0 and k in v1 for k in (c[hi], c[lo])):
            b = v0[c[hi]] - v0[c[lo]]; a = v1[c[hi]] - v1[c[lo]]
            d.setdefault(items0[c[hi]]["base"], []).append(a - b); before.append(b); after.append(a); n += 1
    if not n:
        return None
    bt = sc.boot(d)
    return dict(n=n, before=sum(before) / n, after=sum(after) / n, mean=bt["mean"], lo=bt["lo"], hi=bt["hi"])


def rows(d=ROOT / "results/computed"):
    out = []
    for m in MODELS:
        for f0, f1, label in PAIRS:
            for r1 in sorted(d.glob(f"{m}_{f1}_*.jsonl")):
                readout = r1.name[len(f"{m}_{f1}_"):-len(".jsonl")]
                if not re.fullmatch(r"direct|free_s\d", readout):
                    continue
                r0 = d / f"{m}_{f0}_{readout}.jsonl"
                if not r0.exists():
                    continue
                items0, v0 = verdicts(ROOT / f"data/rules_pilot/{f0}.jsonl", r0)
                items1, v1 = verdicts(ROOT / f"data/rules_pilot/{f1}.jsonl", r1)
                for task in ("gross", "elig"):
                    for hi, lo, name in CONTRASTS:
                        x = delta(items0, v0, items1, v1, task, hi, lo)
                        if x:
                            out.append(dict(model=m, change=label, readout=readout.replace("_", " "), task=task, contrast=name, **x))
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dir", default="results/computed"); a = ap.parse_args()
    print("| model | change | readout | task | contrast | pairs | before | after | change [95% CI] |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in rows(ROOT / a.dir):
        print(f"| {r['model']} | {r['change']} | {r['readout']} | {r['task']} | {r['contrast']} | {r['n']} | {r['before']:+.3f} | {r['after']:+.3f} | {r['mean']:+.3f} [{r['lo']:+.3f},{r['hi']:+.3f}] |")


if __name__ == "__main__":
    main()
