"""Score the Design C psychometric set (src/gen/make_design_c_psych.py).
P(grant) per item: pos question -> YES, neg question -> NO. First-token rows: two-way softmax of YES/NO,
averaged over answer orders; thinking rows: one-hot verdict (INVALID/TRUNCATED dropped, counted).
Per (leniency, prohibit, cue): logistic fit P(grant) = sigmoid(a + b * shortfall/100), shortfall = -leftover,
pooled over polarity (polarity gap reported separately). PSE = -a/b * 100 = the monthly shortfall ($) at which
P(grant) = 0.5. Cue effect = PSE(cue) - PSE(base): negative = the cue makes the model grant at a SMALLER
shortfall (more lenient). Cluster bootstrap over bases. PSE outside [-400, 800] is reported as out of range.
Usage: python src/eval/score_design_c_psych.py results/design_c_psych/firsttoken/qwen3-14b.jsonl [...]"""
import json, math, random, sys
from collections import Counter, defaultdict

import numpy as np

ROOT = "/workspace/welfare-need-naacl"
ITEMS = {json.loads(l)["item_id"]: json.loads(l) for l in open(f"{ROOT}/data/design_c_psych/items.jsonl")}
CUES = ["base", "effort_high", "effort_low", "control_high", "control_low", "valence_neg"]


def grant_probs(path):
    per, states = defaultdict(list), Counter()
    for l in open(path):
        r = json.loads(l)
        it = ITEMS[r["item_id"]]
        if "verdict" in r:
            states[r["verdict"]] += 1
            if r["verdict"] not in ("YES", "NO"):
                continue
            py = float(r["verdict"] == "YES")
        else:
            if r["lp_yes"] is None and r["lp_no"] is None:
                states["MISSING"] += 1
                continue
            a, b = (r["lp_yes"] if r["lp_yes"] is not None else -50), (r["lp_no"] if r["lp_no"] is not None else -50)
            py = 1 / (1 + math.exp(b - a))
        per[r["item_id"]].append(py if it["polarity"] == "pos" else 1 - py)
    return {k: sum(v) / len(v) for k, v in per.items()}, states


def fit(xs, ys, iters=50):
    """Logistic regression (fractional y allowed), ridge 1e-3 for separable data. Returns a, b."""
    X = np.c_[np.ones(len(xs)), np.asarray(xs, float)]
    y = np.asarray(ys, float)
    w = np.zeros(2)
    for _ in range(iters):
        p = 1 / (1 + np.exp(-np.clip(X @ w, -30, 30)))
        g = X.T @ (y - p) - 1e-3 * w
        H = -(X.T * (p * (1 - p))) @ X - 1e-3 * np.eye(2)
        w = w - np.linalg.solve(H, g)
    return w


def pse(pairs):
    xs = [-left / 100 for left, _ in pairs]
    ys = [p for _, p in pairs]
    if max(ys) - min(ys) < 0.05:
        return None
    a, b = fit(xs, ys)
    if b <= 1e-6:
        return None
    v = -a / b * 100
    return v if -400 <= v <= 800 else None


def boot_pse_diff(data_cue, data_base, B=1000, seed=0):
    bases = sorted(set(data_cue) & set(data_base))
    rng = random.Random(seed)
    def est(bs):
        pc = pse([x for b in bs for x in data_cue[b]])
        pb = pse([x for b in bs for x in data_base[b]])
        return None if pc is None or pb is None else pc - pb
    e = est(bases)
    if e is None:
        return None
    sims = [est([rng.choice(bases) for _ in bases]) for _ in range(B)]
    sims = sorted(s for s in sims if s is not None)
    if len(sims) < 0.9 * B:
        return [round(e), None, None, f"{len(sims)}/{B} resamples fit"]
    return [round(e), round(sims[int(.025 * len(sims))]), round(sims[int(.975 * len(sims))])]


def score(path):
    P, states = grant_probs(path)
    out = {"n_items": len(P), "states": dict(states)}
    cells = defaultdict(lambda: defaultdict(list))
    pol = defaultdict(dict)
    for k, p in P.items():
        it = ITEMS[k]
        cells[(it["leniency"], it["prohibit"], it["cue"])][it["base"]].append((it["leftover"], p))
        pol[(it["leniency"], it["prohibit"], it["cue"], it["base"], it["leftover"])][it["polarity"]] = p
    for len_k in ("serious", "basic", "food"):
        for pro in ("no", "yes"):
            if (len_k, pro, "base") not in cells:
                continue
            o = {}
            for cue in CUES:
                d = cells.get((len_k, pro, cue))
                if not d:
                    continue
                allp = [x for v in d.values() for x in v]
                curve = {left: round(np.mean([p for l_, p in allp if l_ == left]), 3) for left in sorted({l_ for l_, _ in allp}, reverse=True)}
                v = pse(allp)
                o[cue] = {"p_grant_by_leftover": curve, "pse_usd": None if v is None else round(v)}
                if cue != "base":
                    o[cue]["pse_shift_vs_base"] = boot_pse_diff(d, cells[(len_k, pro, "base")])
            gaps = [c["pos"] - c["neg"] for (l_, p_, *_), c in pol.items() if l_ == len_k and p_ == pro and len(c) == 2]
            o["polarity_gap_mean"] = round(float(np.mean(gaps)), 3) if gaps else None
            out[f"{len_k}|prohibit={pro}"] = o
    return out


if __name__ == "__main__":
    print(json.dumps({p: score(p) for p in sys.argv[1:]}, indent=1))
