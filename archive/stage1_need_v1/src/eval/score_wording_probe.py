"""Score the v2 wording probe: accuracy on gold-SUFFICIENT items by question x filler x context x gap
(verdict = argmax(YES, NO) per order, then both orders averaged), plus SHORTFALL accuracy.
Usage: python src/eval/score_wording_probe.py results/v2/wording_probe/qwen3-8b.jsonl [...]"""
import json, sys
from collections import defaultdict

for path in sys.argv[1:]:
    acc = defaultdict(list)
    for l in open(path):
        r = json.loads(l)
        if r["lp_yes"] is None or r["lp_no"] is None:
            continue
        says_yes = r["lp_yes"] > r["lp_no"]
        ok = says_yes == (r["gold"] == "SUFFICIENT")
        acc[(r["question"], r["filler"], r["context"], r["gold"], round(r["gap_frac"], 2))].append(ok)
    print("==", path)
    for q in ("v1_person", "v2_passive"):
        for fl in ("filler", "nofiller"):
            for ctx in ("none", "unemp_status"):
                cells = {k[4]: sum(v) / len(v) for k, v in acc.items() if k[:3] == (q, fl, ctx)}
                print(f"  {q:10s} {fl:8s} {ctx:12s} " + " ".join(f"{g:+.2f}:{cells[g]:.2f}" for g in sorted(cells)))
