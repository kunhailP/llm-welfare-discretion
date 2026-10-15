"""Score the computation-burden experiment (docs/paper1/computed_burden.md): balanced accuracy per task, wrongful-denial
rate at the baseline sentence, and the paired cue contrasts (control hi-lo, effort hi-lo, need-none) with pair flips
toward YES / toward NO and a base-clustered bootstrap CI. Works for first-token results (lp_yes/lp_no, two orders:
P(YES) = mean softmax over orders, verdict YES if > 0.5) and generated results (verdict field; INVALID drops the pair).
Usage: python src/eval/score_computed.py --data data/rules_pilot/sub_income_computed.jsonl --results results/computed/<run>.jsonl
"""
import argparse, json, math, random
from collections import defaultdict

CONTRASTS = [("control_high", "control_low"), ("effort_high", "effort_low"), ("valence_neg", "none"),
             ("control_high", "none"), ("control_low", "none"), ("effort_high", "none"), ("effort_low", "none")]


def pyes_direct(rows):
    by = defaultdict(dict)
    for r in rows:
        if r["lp_yes"] is None or r["lp_no"] is None:
            continue
        m = max(r["lp_yes"], r["lp_no"])
        by[r["item_id"]][r["order"]] = math.exp(r["lp_yes"] - m) / (math.exp(r["lp_yes"] - m) + math.exp(r["lp_no"] - m))
    return {i: sum(v.values()) / 2 for i, v in by.items() if len(v) == 2}


def pyes_generated(rows):
    return {r["item_id"]: (1.0 if r["verdict"] == "YES" else 0.0) for r in rows if r["verdict"] in ("YES", "NO")}


def boot(d, B=2000, seed=0):
    bases = sorted(d); xs = [x for b in bases for x in d[b]]
    if not xs:
        return None
    rng = random.Random(seed); ms = []
    for _ in range(B):
        s = [x for b in (rng.choice(bases) for _ in bases) for x in d[b]]
        ms.append(sum(s) / len(s))
    ms.sort()
    return dict(mean=round(sum(xs) / len(xs), 3), lo=round(ms[int(.025 * B)], 3), hi=round(ms[int(.975 * B)], 3), n=len(xs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--out")
    ap.add_argument("--scale", choices=["verdict", "probability"], default="verdict",
                    help="2026-10-12: the common scale across readouts is the 0/1 verdict (P(YES) > 0.5); "
                         "the probability scale exists only for first-token results and is reported separately")
    a = ap.parse_args()
    items = {json.loads(l)["item_id"]: json.loads(l) for l in open(a.data)}
    rows = [json.loads(l) for l in open(a.results)]
    kind = "direct" if "lp_yes" in rows[0] else "generated"
    p = pyes_direct(rows) if kind == "direct" else pyes_generated(rows)
    p = {i: v for i, v in p.items() if i in items}
    if a.scale == "verdict":
        p = {i: (1.0 if v > 0.5 else 0.0) for i, v in p.items()}
    elif kind != "direct":
        raise SystemExit("probability scale is only defined for first-token results")
    out = dict(kind=kind, scale=a.scale, n_items=len(items), n_scored=len(p), missing_or_invalid=len(items) - len(p), tasks={})
    for task in ("gross", "elig"):
        ids = [i for i in items if items[i]["task"] == task]
        if not ids:
            continue
        def bal(sub):
            tp = [p[i] > 0.5 for i in sub if i in p and items[i]["gold"] == "YES"]
            tn = [p[i] <= 0.5 for i in sub if i in p and items[i]["gold"] == "NO"]
            return round((sum(tp) / len(tp) + sum(tn) / len(tn)) / 2, 3) if tp and tn else None
        none = [i for i in ids if items[i]["cue"] == "none"]
        wd = [p[i] <= 0.5 for i in none if i in p and items[i]["gold"] == "YES"]
        t = dict(balanced_accuracy_all=bal(ids), balanced_accuracy_none=bal(none),
                 wrongful_denial_rate_none=round(sum(wd) / len(wd), 3) if wd else None, contrasts={})
        groups = defaultdict(dict)
        for i in ids:
            groups[i.replace("_" + items[i]["cue"] + "_", "_CUE_")][items[i]["cue"]] = i
        for hi, lo in CONTRASTS:
            d = defaultdict(list); up = down = 0
            for g, c in groups.items():
                if hi in c and lo in c and c[hi] in p and c[lo] in p:
                    d[items[c[hi]]["base"]].append(p[c[hi]] - p[c[lo]])
                    up += (p[c[hi]] > 0.5) and (p[c[lo]] <= 0.5)
                    down += (p[c[hi]] <= 0.5) and (p[c[lo]] > 0.5)
            b = boot(d)
            if b:
                t["contrasts"][f"{hi}-{lo}"] = dict(dPyes=b, flips_toward_yes=up, flips_toward_no=down, pairs=b["n"])
        out["tasks"][task] = t
    s = json.dumps(out, indent=1)
    if a.out:
        open(a.out, "w").write(s)
    print(s)


if __name__ == "__main__":
    main()
