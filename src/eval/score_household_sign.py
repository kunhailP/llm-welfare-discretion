"""Household-level re-analysis of the Qwen3-32B-AWQ thinking-off ABAWD controllability asymmetry (2026-10-12).
The paper's 17/3 count treats household-cells (household x exemption cell x seed) as independent trials; the
same household appears in up to four cells and two seeds. Here the unit is the household: for each household, the net
direction of controllability flips (blameless YES & fired NO = +1 'toward the deservingness prediction'; blameless NO &
fired YES = -1) summed over the four non-trap 72-hour cells and both seeds. An exact two-sided sign test is run over the
households with a nonzero net, overall and per seed.
Usage: python src/eval/score_household_sign.py -> results/common_scale/household_sign.json + .md
"""
import json, pathlib, sys
from collections import defaultdict
from math import comb

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src/run"))
from run_rules_think import subsample  # noqa: E402

MODEL = "qwen3-32b-awq"
RUNS = {"s0": "results/rules_think/qwen3-32b-awq_off.jsonl", "s1": "results/rules_think/qwen3-32b-awq_off_s1.jsonl"}
CELLS = [("nonexempt", 72), ("pregnant", 72), ("child_under_14", 72), ("medical", 72)]


def sign_test(pos, neg):
    n = pos + neg
    if n == 0:
        return None
    k = min(pos, neg)
    p = sum(comb(n, i) for i in range(0, k + 1)) * 2 / 2 ** n
    return min(1.0, p)


def main():
    rows = [json.loads(l) for l in open(ROOT / "data/rules_pilot/pilot.jsonl")]
    sub = {r["item_id"]: r for r, _ in subsample(rows)}
    verdict = {s: {r["item_id"]: r["verdict"] for r in map(json.loads, open(ROOT / p))} for s, p in RUNS.items()}
    net = defaultdict(lambda: defaultdict(int))   # seed -> household -> net
    cells_count = defaultdict(lambda: defaultdict(int))  # seed -> (+1/-1) -> count of household-cells
    for iid, r in sub.items():
        if r["task"] != "abawd" or (r["status"], r["hours"]) not in CELLS or r["cue"] != "control_high":
            continue
        lo = iid.replace("_control_high_", "_control_low_")
        for s in RUNS:
            h, l = verdict[s].get(iid), verdict[s].get(lo)
            if h not in ("YES", "NO") or l not in ("YES", "NO"):
                continue
            d = (h == "YES") - (l == "YES")
            if d:
                net[s][r["base"]] += d
                cells_count[s][d] += 1
    out = {}
    for name, seeds in (("both_seeds", list(RUNS)), ("s0", ["s0"]), ("s1", ["s1"])):
        tot = defaultdict(int)
        for s in seeds:
            for b, v in net[s].items():
                tot[b] += v
        pos = sum(v > 0 for v in tot.values()); neg = sum(v < 0 for v in tot.values()); zero = sum(v == 0 for v in tot.values())
        hc_pos = sum(cells_count[s][1] for s in seeds); hc_neg = sum(cells_count[s][-1] for s in seeds)
        out[name] = dict(household_cells_toward=hc_pos, household_cells_against=hc_neg,
                         households_net_toward=pos, households_net_against=neg, households_net_zero=zero,
                         households_any_flip=len(tot), sign_test_two_sided_p=sign_test(pos, neg),
                         household_cell_binomial_p_for_comparison=sign_test(hc_pos, hc_neg),
                         net_by_household={b: tot[b] for b in sorted(tot)})
    outdir = ROOT / "results/common_scale"; outdir.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(outdir / "household_sign.json", "w"), indent=1)
    md = ["# Household-level sign test, Qwen3-32B-AWQ thinking off, ABAWD non-trap 72-hour cells, controllability (blameless - fired)",
          "", "| seeds | household-cells toward / against | households net toward / against / zero | sign test p (households) | binomial p (household-cells, for comparison) |",
          "| --- | --- | --- | --- | --- |"]
    for name, v in out.items():
        md.append(f"| {name} | {v['household_cells_toward']} / {v['household_cells_against']} | "
                  f"{v['households_net_toward']} / {v['households_net_against']} / {v['households_net_zero']} | "
                  f"{v['sign_test_two_sided_p']:.4f} | {v['household_cell_binomial_p_for_comparison']:.4f} |")
    (outdir / "household_sign.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
