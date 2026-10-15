"""Computation-burden experiment (pre-registered 2026-10-12, docs/paper1/computed_burden.md).
From a pilot file, take the income rows (gross, elig) of the thinking subsample (same selection and groups as
src/run/run_rules_think.py) and write two files with identical item ids: the original case text, and the case text
plus a block of correct intermediate quantities (no YES/NO, no pass/fail flag).
Usage: python src/gen/make_computed_variant.py --data data/rules_pilot/pilot.jsonl --out-dir data/rules_pilot --tag sub
"""
import argparse, json, os, pathlib, sys
from fractions import Fraction
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src/run"))
from run_rules_think import subsample  # noqa: E402


def money(v):
    x = Fraction(str(v))            # facts are stored as strings, some as exact fractions ("927/2")
    return f"${int(x):,}" if x.denominator == 1 else f"${float(x):,.2f}"


def block(r, plain=False):
    """plain=True: preserve the quantities and remove 'verified' and 'under the rules in the packet'.
    This controls the authority prefix, not the information or salience of the quantities."""
    f, n = r["facts"], int(r["facts"]["size"])
    lead = "Computed from the figures above: " if plain else "Computed from the figures above under the rules in the packet (verified): "
    lines = [lead + f"household of {n}; "
             f"gross monthly income {money(f['gross'])}; gross income limit for a household of {n} {money(f['gross_limit'])}."]
    if r["task"] == "elig":
        lines.append(f"Deductions: earned-income {money(f['earned_ded'])}; standard {money(f['std_ded'])}; dependent care "
                     f"{money(f['dependent_care'])}; medical {money(f['medical_ded'])}; child support {money(f['child_support_ded'])}; "
                     f"adjusted income {money(f['adjusted'])}; shelter costs {money(f['shelter_costs'])}; excess shelter deduction "
                     f"{money(f['shelter_ded'])}; net monthly income {money(f['net'])}; net income limit for a household of {n} "
                     f"{money(f['net_limit'])}; countable assets $500; asset limit {money(f['asset_limit'])}.")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out-dir", default="data/rules_pilot")
    ap.add_argument("--tag", required=True, help="output names: <tag>_income.jsonl and <tag>_income_computed.jsonl")
    ap.add_argument("--plain", action="store_true", help="computed block without the 'verified' / packet wording (writes <tag>_income_computed_plain.jsonl only)")
    a = ap.parse_args()
    if a.plain:
        rows = [json.loads(l) for l in open(a.data)]
        jobs = [r for r, _ in subsample(rows) if r["task"] in ("gross", "elig")]
        with open(f"{a.out_dir}/{a.tag}_income_computed_plain.jsonl", "w") as fp:
            for r in jobs:
                rc = dict(r); rc["text"] = r["text"] + "\n" + block(r, plain=True); rc["variant"] = "computed_plain"
                fp.write(json.dumps(rc) + "\n")
        print(len(jobs), "items (plain computed block)"); return
    rows = [json.loads(l) for l in open(a.data)]
    jobs = [r for r, _ in subsample(rows) if r["task"] in ("gross", "elig")]
    os.makedirs(a.out_dir, exist_ok=True)
    with open(f"{a.out_dir}/{a.tag}_income.jsonl", "w") as fo, open(f"{a.out_dir}/{a.tag}_income_computed.jsonl", "w") as fc:
        for r in jobs:
            fo.write(json.dumps(r) + "\n")
            rc = dict(r); rc["text"] = r["text"] + "\n" + block(r); rc["variant"] = "computed"
            fc.write(json.dumps(rc) + "\n")
    print(len(jobs), "items per file;", sum(r["task"] == "gross" for r in jobs), "gross,", sum(r["task"] == "elig" for r in jobs), "elig")


if __name__ == "__main__":
    main()
