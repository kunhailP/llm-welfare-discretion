"""Score Design C v2 (src/gen/make_design_c_v2.py). Polarity-normalised outcomes per item:
P(grant), P(deny), P(request), where for "pos" questions YES = grant and for "neg" questions YES = deny.
First-token rows: three-way softmax over YES/NO/REQUEST log-probs, averaged over answer orders.
Thinking rows: one-hot verdict; INVALID/TRUNCATED dropped and counted.
Reports (per task/cond, pooled or per polarity):
  - accuracy vs gold (enum standards, hours task), outcome rates;
  - polarity gap: P(grant | pos) - P(grant | neg) on the same case (0 if the question wording does not matter);
  - noise floor: |P(grant) change| for meaning-preserving edits (name, order) at cue = none;
  - cue effects on P(grant), P(deny), P(request): cue - none, hi - lo; cluster bootstrap over bases;
  - discretion open standards: need slope (per $100 less left over) and dollar equivalent of each cue.
Usage: python src/eval/score_design_c_v2.py results/design_c_v2/firsttoken/qwen3-14b.jsonl [...]"""
import json, math, random, sys
from collections import Counter, defaultdict

ROOT = "/workspace/welfare-need-naacl"
ITEMS = {json.loads(l)["item_id"]: json.loads(l) for l in open(f"{ROOT}/data/design_c_v2/items.jsonl")}
CONTRASTS = [("control_high", "control_low"), ("effort_high", "effort_low"), ("control_high", "none"),
             ("control_low", "none"), ("effort_high", "none"), ("effort_low", "none"), ("valence_neg", "none")]


def outcomes(path):
    per, states = defaultdict(list), Counter()
    for l in open(path):
        r = json.loads(l)
        if "verdict" in r:
            states[r["verdict"]] += 1
            if r["verdict"] not in ("YES", "NO", "REQUEST"):
                continue
            p = {k: float(r["verdict"] == k) for k in ("YES", "NO", "REQUEST")}
        else:
            lps = {"YES": r["lp_yes"], "NO": r["lp_no"], "REQUEST": r.get("lp_request")}
            lps = {k: (v if v is not None else -50.0) for k, v in lps.items()}
            if r["lp_yes"] is None and r["lp_no"] is None and r.get("lp_request") is None:
                states["MISSING"] += 1
                continue
            z = max(lps.values())
            e = {k: math.exp(v - z) for k, v in lps.items()}
            p = {k: v / sum(e.values()) for k, v in e.items()}
        it = ITEMS[r["item_id"]]
        g, d = ("YES", "NO") if it["polarity"] == "pos" else ("NO", "YES")
        per[r["item_id"]].append({"grant": p[g], "deny": p[d], "request": p["REQUEST"]})
    return {k: {o: sum(x[o] for x in v) / len(v) for o in ("grant", "deny", "request")} for k, v in per.items()}, states


def boot(by_base, stat, B=2000, seed=0):
    rng, bases = random.Random(seed), sorted(by_base)
    if not bases:
        return None
    est = stat([x for b in bases for x in by_base[b]])
    bs = sorted(stat([x for b in (rng.choice(bases) for _ in bases) for x in by_base[b]]) for _ in range(B))
    return [round(est, 3), round(bs[int(.025 * B)], 3), round(bs[int(.975 * B)], 3)]


mean = lambda xs: sum(xs) / len(xs)


def slope(pairs):
    xs, ys = [-x / 100 for x, _ in pairs], [y for _, y in pairs]
    mx, my = mean(xs), mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx else 0.0


def gold_outcome(it):
    if it["gold"] is None:
        return None
    if it["gold"] == "REQUEST":
        return "request"
    return "grant" if (it["gold"] == "YES") == (it["polarity"] == "pos") else "deny"


def score(path):
    P, states = outcomes(path)
    out = {"n_items": len(P), "states": dict(states)}
    cells = sorted({(ITEMS[k]["task"], ITEMS[k]["cond"]) for k in P})
    for task, cond in cells:
        ks = [k for k in P if ITEMS[k]["task"] == task and ITEMS[k]["cond"] == cond]
        o = {}
        orig_none = [k for k in ks if ITEMS[k]["cue"] == "none" and ITEMS[k]["edit"] == "orig"]
        o["rates_none"] = {pol: {x: round(mean([P[k][x] for k in orig_none if ITEMS[k]["polarity"] == pol]), 3)
                                 for x in ("grant", "deny", "request")} for pol in ("pos", "neg")}
        if gold_outcome(ITEMS[ks[0]]):
            g = gold_outcome(ITEMS[ks[0]])
            o["accuracy"] = {pol: round(mean([max(P[k], key=P[k].get) == g for k in ks if ITEMS[k]["polarity"] == pol]), 3)
                             for pol in ("pos", "neg")}
        # case key without polarity / edit
        key = lambda k: k.rsplit("_", 2)[0]
        pol_gap, noise = defaultdict(list), defaultdict(list)
        by_case = defaultdict(dict)
        for k in ks:
            by_case[key(k)][(ITEMS[k]["edit"], ITEMS[k]["polarity"])] = P[k]
        for ck, c in by_case.items():
            b = ITEMS[next(k for k in ks if key(k) == ck)]["base"]
            if ("orig", "pos") in c and ("orig", "neg") in c:
                pol_gap[b].append(c[("orig", "pos")]["grant"] - c[("orig", "neg")]["grant"])
            for ed in ("name", "order"):
                for pol in ("pos", "neg"):
                    if (ed, pol) in c and ("orig", pol) in c:
                        noise[b].append(abs(c[(ed, pol)]["grant"] - c[("orig", pol)]["grant"]))
        o["polarity_gap_grant"] = boot(pol_gap, mean)
        o["noise_floor_abs_dgrant"] = boot(noise, mean)
        grp = defaultdict(dict)
        for k in ks:
            it = ITEMS[k]
            if it["edit"] == "orig":
                grp[(it["base"], it["leftover"], it["polarity"])][it["cue"]] = P[k]
        sl = None
        if task == "discretion" and cond.startswith("open"):
            nb = defaultdict(list)
            for (b, left, _), c in grp.items():
                for v in c.values():
                    nb[b].append((left, v["grant"]))
            sl = boot(nb, slope)
            o["need_slope_grant_per_100_less"] = sl
        con = {}
        for hi, lo in CONTRASTS:
            for x in ("grant", "deny", "request"):
                d = defaultdict(list)
                for (b, _, _), c in grp.items():
                    if hi in c and lo in c:
                        d[b].append(c[hi][x] - c[lo][x])
                e = boot(d, mean)
                if e:
                    entry = {"d": e}
                    if x == "grant" and sl and sl[1] > 0:
                        entry["usd_equiv"] = round(e[0] / sl[0] * 100)
                    con[f"{hi}-{lo}|{x}"] = entry
        o["contrasts"] = con
        out[f"{task}|{cond}"] = o
    return out


if __name__ == "__main__":
    print(json.dumps({p: score(p) for p in sys.argv[1:]}, indent=1))
