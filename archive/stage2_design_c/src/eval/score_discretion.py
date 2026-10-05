"""Score the discretion-axis pilot (src/gen/make_discretion_pilot.py).
Input rows: first-token runs (lp_yes/lp_no per order; P(YES) = mean over orders of the two-way softmax)
or thinking runs (verdict YES/NO; P(YES) in {0, 1}; INVALID/TRUNCATED dropped and counted).
Per standard:
  - P(YES) by leftover (cue = none) and the need slope: change in P(YES) per $100 less left over (OLS on all cues);
  - cue effects vs none and hi-lo, pooled over leftover levels, cluster bootstrap over bases;
  - "dollar equivalent" of a cue: effect / slope * $100 (only when the slope CI excludes 0);
  - enum standards: accuracy against gold.
Usage: python src/eval/score_discretion.py results/discretion_pilot/qwen3-14b.jsonl [...]"""
import json, math, random, sys
from collections import Counter, defaultdict

ROOT = "/workspace/welfare-need-naacl"
ITEMS = {json.loads(l)["item_id"]: json.loads(l) for l in open(f"{ROOT}/data/discretion_pilot/pilot.jsonl")}
CONTRASTS = [("control_high", "control_low"), ("effort_high", "effort_low"), ("control_high", "none"),
             ("control_low", "none"), ("effort_high", "none"), ("effort_low", "none"), ("valence_neg", "none")]


def p_yes(path):
    per, states = defaultdict(list), Counter()
    for l in open(path):
        r = json.loads(l)
        if "verdict" in r:
            states[r["verdict"]] += 1
            if r["verdict"] in ("YES", "NO"):
                per[r["item_id"]].append(1.0 if r["verdict"] == "YES" else 0.0)
        elif r["lp_yes"] is not None and r["lp_no"] is not None:
            per[r["item_id"]].append(1 / (1 + math.exp(r["lp_no"] - r["lp_yes"])))
    return {k: sum(v) / len(v) for k, v in per.items()}, states


def slope(pairs):
    xs, ys = [-x / 100 for x, _ in pairs], [y for _, y in pairs]   # per $100 LESS left over
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx else 0.0


def boot(by_base, stat, B=2000, seed=0):
    rng, bases = random.Random(seed), sorted(by_base)
    est = stat([x for b in bases for x in by_base[b]])
    bs = sorted(stat([x for b in (rng.choice(bases) for _ in bases) for x in by_base[b]]) for _ in range(B))
    return [round(est, 3), round(bs[int(.025 * B)], 3), round(bs[int(.975 * B)], 3)]


def score(path):
    py, states = p_yes(path)
    out = {"n_items": len(py), "states": dict(states)}
    for std in ("enum_no", "enum_yes", "open", "open_need"):
        its = {k: ITEMS[k] for k in py if ITEMS[k]["standard"] == std}
        o = {}
        o["p_yes_by_leftover_none"] = {str(left): round(sum(py[k] for k, r in its.items() if r["cue"] == "none" and r["leftover"] == left)
                                                        / max(1, sum(1 for r in its.values() if r["cue"] == "none" and r["leftover"] == left)), 3)
                                      for left in (200, 50, -100, -250)}
        if its and ITEMS[next(iter(its))]["gold"]:
            o["accuracy"] = round(sum((py[k] > .5) == (r["gold"] == "YES") for k, r in its.items()) / len(its), 3)
        nb = defaultdict(list)
        for k, r in its.items():
            nb[r["base"]].append((r["leftover"], py[k]))
        sl = boot(nb, slope) if nb else None
        o["need_slope_per_100_less"] = sl
        grp = defaultdict(dict)
        for k, r in its.items():
            grp[(r["base"], r["leftover"])][r["cue"]] = py[k]
        con = {}
        for hi, lo in CONTRASTS:
            d = defaultdict(list)
            for (b, _), c in grp.items():
                if hi in c and lo in c:
                    d[b].append(c[hi] - c[lo])
            if d:
                e = boot(d, lambda xs: sum(xs) / len(xs))
                usd = round(e[0] / sl[0] * 100) if sl and sl[1] > 0 else None
                con[f"{hi}-{lo}"] = {"dPyes": e, "usd_equiv": usd}
        o["contrasts"] = con
        out[std] = o
    return out


if __name__ == "__main__":
    print(json.dumps({p: score(p) for p in sys.argv[1:]}, indent=1))
