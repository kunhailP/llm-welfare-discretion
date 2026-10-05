"""Discretion pilot, first-token runs: effects in log-odds space (lp_yes - lp_no, mean of both orders).
Use when P(YES) is saturated (e.g. Qwen3-14B gives P(YES) ~ 0 on every open-standard item, but the
log-odds still move with need). Need slope = change in log-odds per $100 LESS left over; cue effects in
log-odds; dollar equivalent = cue effect / slope * $100. Cluster bootstrap over bases.
Usage: python src/eval/score_discretion_logit.py results/discretion_pilot/qwen3-14b.jsonl [...]"""
import json, sys
from collections import defaultdict

sys.path.insert(0, "/workspace/welfare-need-naacl/src/eval")
from score_discretion import ITEMS, CONTRASTS, boot, slope  # noqa: E402


def score(path):
    lo = defaultdict(list)
    for l in open(path):
        r = json.loads(l)
        if r["lp_yes"] is not None and r["lp_no"] is not None:
            lo[r["item_id"]].append(r["lp_yes"] - r["lp_no"])
    L = {k: sum(v) / len(v) for k, v in lo.items()}
    out = {}
    for std in ("enum_no", "enum_yes", "open", "open_need"):
        its = {k: ITEMS[k] for k in L if ITEMS[k]["standard"] == std}
        nb = defaultdict(list)
        for k, r in its.items():
            nb[r["base"]].append((r["leftover"], L[k]))
        sl = boot(nb, slope)
        grp = defaultdict(dict)
        for k, r in its.items():
            grp[(r["base"], r["leftover"])][r["cue"]] = L[k]
        con = {}
        for hi, lo_ in CONTRASTS:
            d = defaultdict(list)
            for (b, _), c in grp.items():
                if hi in c and lo_ in c:
                    d[b].append(c[hi] - c[lo_])
            e = boot(d, lambda xs: sum(xs) / len(xs))
            con[f"{hi}-{lo_}"] = {"dlogit": e, "usd_equiv": round(e[0] / sl[0] * 100) if sl[1] > 0 else None}
        mean_none = sum(L[k] for k, r in its.items() if r["cue"] == "none") / max(1, sum(r["cue"] == "none" for r in its.values()))
        out[std] = {"mean_logit_none": round(mean_none, 2), "need_slope_logit_per_100_less": sl, "contrasts": con}
    return out


if __name__ == "__main__":
    print(json.dumps({p: score(p) for p in sys.argv[1:]}, indent=1))
