"""Cross-check src/rules/snap.py against PolicyEngine-US on random households (FY2026, January 2026).

Run with the separate env:  /workspace/venv_pe/bin/python src/rules/crosscheck_pe.py --n 500
Utilities are 0 and no TANF/SSI receipt so PolicyEngine's state utility allowance and categorical
eligibility do not enter; we compare the federal chain step by step.
"""
import argparse, json, random, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from rules.snap import Household, Member, compute

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=500)
ap.add_argument("--state", default="TX")
ap.add_argument("--out", default="results/rules/crosscheck_pe.json")
a = ap.parse_args()
rng = random.Random(7)
MONTH, YEAR = "2026-01", "2026"

cases = []
for i in range(a.n):
    size = rng.choice([1, 1, 2, 2, 3, 4, 5, 6])
    ages = [rng.choice([25, 34, 45, 58]) if j < 2 else rng.choice([3, 9, 15]) for j in range(size)]
    if rng.random() < 0.25:
        ages[0] = rng.choice([62, 70, 81])
    disabled = rng.random() < 0.1
    earned = rng.choice([0, 0] + list(range(400, 4400, 40)))
    unearned = rng.choice([0, 0, 0] + list(range(200, 1600, 20)))
    rent = rng.choice(range(300, 2200, 10))
    cases.append(dict(ages=ages, disabled=disabled, earned=earned, unearned=unearned, rent=rent))

people, spm, hh, tax, fam, mar = {}, {}, {}, {}, {}, {}
for i, c in enumerate(cases):
    ids = []
    for j, age in enumerate(c["ages"]):
        pid = f"p{i}_{j}"
        ids.append(pid)
        people[pid] = {
            "age": {YEAR: age},
            "is_disabled": {YEAR: bool(c["disabled"] and j == 0)},
            "employment_income": {YEAR: 12 * c["earned"] if j == 0 else 0},
            "pension_income": {YEAR: 12 * c["unearned"] if j == 0 else 0},
            "rent": {YEAR: 12 * c["rent"] if j == 0 else 0},
            # household-composition checks only: switch off member exclusions (ABAWD, students,
            # immigration) so the SNAP unit equals the listed household, as in our rule packet
            "meets_snap_work_requirements_person": {MONTH: True},
            "is_snap_immigration_status_eligible": {MONTH: True},
            "is_snap_ineligible_student": {YEAR: False},
            # switch off PolicyEngine imputations that our packet does not model:
            # automatic SSI/TANF benefits, imputed medical costs (e.g. Medicare Part B premium),
            # and the benefit-receipt definition of disability (our packet: "has a disability")
            "ssi": {YEAR: 0},
            "snap_allowable_medical_expenses": {MONTH: 0},
            "is_usda_disabled": {YEAR: bool(c["disabled"] and j == 0)},
        }
    spm[f"s{i}"] = {"members": ids, "tanf": {YEAR: 0}}
    hh[f"h{i}"] = {"members": ids, "state_code": {YEAR: a.state}}
    tax[f"t{i}"] = {"members": ids}
    fam[f"f{i}"] = {"members": ids}
    mar[f"m{i}"] = {"members": ids[:1]}
    for j, pid in enumerate(ids[1:], 1):
        mar[f"m{i}_{j}"] = {"members": [pid]}

from policyengine_us import Simulation
sim = Simulation(situation=dict(people=people, spm_units=spm, households=hh, tax_units=tax,
                                families=fam, marital_units=mar))
VARS = ["snap_gross_income", "snap_earned_income_deduction", "snap_standard_deduction",
        "snap_net_income_pre_shelter", "snap_excess_shelter_expense_deduction", "snap_net_income",
        "meets_snap_gross_income_test", "meets_snap_net_income_test", "snap_max_allotment",
        "snap_expected_contribution", "snap_normal_allotment", "snap_utility_allowance"]
pe = {v: sim.calculate(v, MONTH).tolist() for v in VARS}

ours_map = {"snap_gross_income": "gross", "snap_earned_income_deduction": "earned_ded",
            "snap_standard_deduction": "std_ded", "snap_net_income_pre_shelter": "adjusted",
            "snap_excess_shelter_expense_deduction": "shelter_ded", "snap_net_income": "net",
            "meets_snap_gross_income_test": "gross_pass", "meets_snap_net_income_test": "net_pass",
            "snap_max_allotment": "max_allot", "snap_expected_contribution": "contribution"}
mism = {k: [] for k in ours_map}
alloc_mism = []
for i, c in enumerate(cases):
    members = [Member(age, disabled=(c["disabled"] and j == 0)) for j, age in enumerate(c["ages"])]
    r = compute(Household(members, earned=c["earned"], unearned=c["unearned"], shelter=c["rent"]))
    for pv, ok in ours_map.items():
        x, y = pe[pv][i], r[ok]
        if isinstance(y, bool) or isinstance(x, bool):
            bad = bool(x) != bool(y)
        else:
            bad = abs(float(x) - float(y)) > 0.51
        if bad:
            mism[pv].append(dict(i=i, case=c, pe=x, ours=float(y) if not isinstance(y, bool) else y))
    # normal allotment comparable only when both say eligible under the federal tests
    if r["gross_pass"] and r["net_pass"] and abs(pe["snap_normal_allotment"][i] - r["benefit"]) > 0.51:
        alloc_mism.append(dict(i=i, case=c, pe=pe["snap_normal_allotment"][i], ours=r["benefit"]))

summary = {k: len(v) for k, v in mism.items()}
summary["snap_normal_allotment(eligible)"] = len(alloc_mism)
summary["pe_utility_allowance_nonzero"] = sum(1 for x in pe["snap_utility_allowance"] if x)
print(json.dumps(summary, indent=1))
pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
json.dump(dict(n=a.n, state=a.state, month=MONTH, summary=summary,
               examples={k: v[:5] for k, v in mism.items()}, alloc_examples=alloc_mism[:5]),
          open(a.out, "w"), indent=1, default=str)
