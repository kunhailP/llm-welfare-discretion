"""Seed baseline for the thinking runs: per-item verdict agreement between two runs of the same model on the same
items (seed 0 vs seed 1, or thinking on vs off), and the paired hi-lo cue contrasts in the second run.
Flip rate at cue = none between seeds is the sampling-noise floor against which cue flips are read.
Usage: python src/eval/score_seed_agreement.py results/rules_think/qwen3-14b.jsonl results/rules_think/qwen3-14b_s1.jsonl
"""
import json, pathlib, sys
from collections import defaultdict

ROOT = str(pathlib.Path(__file__).resolve().parents[2])
ITEMS = {json.loads(l)["item_id"]: json.loads(l) for l in open(f"{ROOT}/data/rules_pilot/pilot.jsonl")}


def load(p):
    return {r["item_id"]: r for r in map(json.loads, open(p))}


def main(a, b):
    A, B = load(a), load(b)
    common = sorted(set(A) & set(B))
    out = dict(n_a=len(A), n_b=len(B), n_common=len(common),
               states_b={s: sum(r["verdict"] == s for r in B.values()) for s in ("YES", "NO", "TRUNCATED", "INVALID")})
    agree = defaultdict(list); acc_b = defaultdict(list); flips_none = defaultdict(list)
    for i in common:
        it = ITEMS[i]; va, vb = A[i]["verdict"], B[i]["verdict"]
        if va in ("YES", "NO") and vb in ("YES", "NO"):
            agree[it["task"]].append(va == vb)
            if it["cue"] == "none":
                flips_none[it["task"]].append(va != vb)
        if vb in ("YES", "NO"):
            acc_b[it["task"]].append(vb == it["gold"])
    out["agreement_by_task"] = {t: round(sum(x) / len(x), 4) for t, x in agree.items()}
    out["flip_rate_at_cue_none_by_task"] = {t: [round(sum(x) / len(x), 4), len(x)] for t, x in flips_none.items()}
    out["accuracy_b_by_task"] = {t: round(sum(x) / len(x), 4) for t, x in acc_b.items()}
    # errors that differ between runs, by base: how many bases have any disagreement
    dis = defaultdict(set)
    for i in common:
        if A[i]["verdict"] != B[i]["verdict"]:
            dis[ITEMS[i]["task"]].add(ITEMS[i]["base"])
    out["bases_with_any_disagreement"] = {t: len(v) for t, v in dis.items()}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
