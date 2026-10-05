"""Pilot items for Design B: rule-relevant vs rule-irrelevant deservingness cues (docs/09_design_B.md).

Household structures come from the SNAP QC FY2024 public-use file; incomes are rescaled so the
decisive quantity sits at a chosen margin from its threshold; gold is computed by src/rules/snap.py
under the FY2026 packet (configs/rule_packet_fy2026.md).

Tasks
- gross : does the household pass the gross income test?          (cue legally irrelevant)
- elig  : is the household income-eligible (all applicable tests)?  (cue legally irrelevant)
- abawd : can the focal adult receive SNAP this month under the ABAWD time limit?
          hours worked = legally relevant; job-search effort / cause of job loss = irrelevant;
          exemption status decides whether hours matter at all.

Usage: python src/gen/make_rules_pilot.py --bases 40 --seed 11 --out data/rules_pilot/pilot.jsonl
"""
import argparse, json, random, sys, pathlib
from fractions import Fraction
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from rules.snap import Household, Member, compute, abawd  # noqa: E402

QC = ROOT / "data/external/candidates/snap_qc_fy2024/qc_pub_fy2024.csv"
NAMES = ["Jordan Ellis", "Morgan Reyes", "Casey Brooks", "Taylor Nguyen", "Riley Carter",
         "Avery Coleman", "Quinn Foster", "Jamie Ortiz"]

# Cue sentences about the focal adult. Same slot, similar length; none of them carries money facts.
CUES = {
    "none":         "{n} has lived in the same county for several years and rents from the same landlord.",
    "effort_high":  "Since losing a full-time job in the spring, {n} has applied for about eight jobs every week.",
    "effort_low":   "Since losing a full-time job in the spring, {n} has applied for one job in the past two months.",
    "control_high": "{n} lost a full-time job in the spring when the warehouse where {p} worked closed down.",
    "control_low":  "{n} lost a full-time job in the spring after being fired for repeatedly missing shifts.",
    "valence_neg":  "{n}'s car broke down in the spring and it still has not been repaired.",
}
MARGINS = [-0.15, -0.04, 0.04, 0.15]   # (value - limit) / limit for the decisive quantity


def money(x):
    x = Fraction(x)
    return f"${int(x):,}" if x.denominator == 1 else f"${float(x):,.2f}"


def load_structures(rng, k):
    cols = ["FSUSIZE", "FSEARN", "FSUNEARN", "RENT", "UTIL", "FSDEPDED", "FSMEDEXP", "FSCSEXP"]
    cols += [f"AGE{i}" for i in range(1, 7)] + [f"DIS{i}" for i in range(1, 7)]
    d = pd.read_csv(QC, usecols=cols, low_memory=False)
    d[["FSDEPDED", "FSMEDEXP", "FSCSEXP", "UTIL"]] = d[["FSDEPDED", "FSMEDEXP", "FSCSEXP", "UTIL"]].fillna(0)
    d = d[(d.FSUSIZE.between(1, 6)) & (d.RENT >= 200) & (d.FSEARN + d.FSUNEARN > 0)].copy()
    d = d[d.AGE1.between(18, 64)]          # focal adult = person 1, of working age
    out = []
    for size, g in d.groupby("FSUSIZE"):
        take = max(1, round(k * len(g) / len(d)))
        out += g.sample(min(take, len(g)), random_state=rng.randrange(10**6)).to_dict("records")
    rng.shuffle(out)
    return out[:k]


def members_from(r):
    ms = []
    for i in range(1, int(r["FSUSIZE"]) + 1):
        age = r.get(f"AGE{i}")
        age = int(age) if pd.notna(age) and age < 120 else 30
        dis = r.get(f"DIS{i}") == 1
        ms.append(Member(age, disabled=bool(dis) and i > 1))   # focal adult never disabled here
    return ms


def scaled(base, members, s):
    """Household with earned/unearned scaled by s (rounded to whole dollars)."""
    r10 = lambda x: int(round(x * s))
    return Household(members, earned=r10(base["FSEARN"]), unearned=r10(base["FSUNEARN"]),
                     dependent_care=int(base["FSDEPDED"] or 0), medical_ed=int(base["FSMEDEXP"] or 0),
                     child_support_paid=int(base["FSCSEXP"] or 0), shelter=int(base["RENT"]),
                     utilities=int(base["UTIL"] or 0), assets=500)


def hit_margin(base, members, key, limit_key, target):
    """Binary-search income scale so (key - limit) / limit is close to target."""
    lo, hi = 0.05, 20.0
    for _ in range(60):
        mid = (lo + hi) / 2
        r = compute(scaled(base, members, mid))
        if float((r[key] - r[limit_key]) / r[limit_key]) < target:
            lo = mid
        else:
            hi = mid
    h = scaled(base, members, hi)
    r = compute(h)
    return h, r, float((r[key] - r[limit_key]) / r[limit_key])


def case_text(h, r, name, cue, style, extra=None):
    """Render the case file. extra: list of additional sentences (ABAWD facts)."""
    pron = "they"
    cue_s = CUES[cue].format(n=name, p=pron)
    people = []
    for i, m in enumerate(h.members):
        who = name if i == 0 else f"Member {i + 1}"
        tag = ", has a disability" if m.disabled else ""
        people.append(f"{who} (age {m.age}{tag})")
    lines = {
        "earned": money(h.earned), "unearned": money(h.unearned), "rent": money(h.shelter),
        "util": money(h.utilities), "dep": money(h.dependent_care), "med": money(h.medical_ed),
        "cs": money(h.child_support_paid), "assets": money(h.assets),
    }
    extra = extra or []
    if style == "structured":
        t = [f"CASE FILE - applicant: {name}",
             f"Household members ({len(h.members)}): " + "; ".join(people),
             f"Monthly earned income (all members): {lines['earned']}",
             f"Monthly unearned income (all members): {lines['unearned']}",
             f"Monthly rent: {lines['rent']}; monthly utilities: {lines['util']}",
             f"Monthly dependent care costs: {lines['dep']}; out-of-pocket medical costs of elderly or disabled members: {lines['med']}",
             f"Legally owed child support paid outside the household: {lines['cs']}",
             f"Countable assets: {lines['assets']}",
             f"Caseworker note: {cue_s}"] + [f"Caseworker note: {e}" for e in extra]
    else:
        t = [f"Caseworker note on {name}'s application. {cue_s}",
             (f"The household has {len(h.members)} members: " if len(h.members) > 1 else "The household has one member: ") + "; ".join(people) + ".",
             f"Together the members earn {lines['earned']} a month from work and receive {lines['unearned']} a month in other income.",
             f"They pay {lines['rent']} a month in rent and {lines['util']} a month for utilities.",
             f"They pay {lines['dep']} a month for dependent care, and out-of-pocket medical costs for elderly or disabled members are {lines['med']} a month.",
             f"They pay {lines['cs']} a month in legally owed child support to someone outside the household, and have {lines['assets']} in countable assets."] + extra
    return "\n".join(t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bases", type=int, default=40)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--out", default="data/rules_pilot/pilot.jsonl")
    a = ap.parse_args()
    rng = random.Random(a.seed)
    bases = load_structures(rng, a.bases)
    rows = []
    for bi, base in enumerate(bases):
        name = NAMES[bi % len(NAMES)]
        mem = members_from(base)
        has_ed = any(m.elderly or m.disabled for m in mem)
        # --- income tasks
        tasks = [("elig", "net", "net_limit")] + ([] if has_ed else [("gross", "gross", "gross_limit")])
        for task, key, lim in tasks:
            for mg in MARGINS:
                h, r, real = hit_margin(base, mem, key, lim, mg)
                gold = r["gross_pass"] if task == "gross" else r["eligible"]
                if abs(real - mg) > 0.005:
                    continue        # target margin not reachable for this structure
                if task == "elig" and not (r["gross_pass"] and r["asset_pass"]):
                    continue        # keep the net test decisive
                for cue in CUES:
                    for style in ("structured", "narrative"):
                        rows.append(dict(
                            item_id=f"b{bi:03d}_{task}_{mg:+.2f}_{cue}_{style[0]}", base=f"b{bi:03d}",
                            task=task, margin=mg, margin_real=round(real, 4), cue=cue, style=style,
                            cue_relevant=False, gold="YES" if gold else "NO",
                            text=case_text(h, r, name, cue, style),
                            facts={k: str(v) for k, v in r.items()}))
        # --- ABAWD task: focal adult 18-64, three countable months already used
        for status in ("nonexempt", "pregnant", "child_under_14", "child_15_trap", "medical"):
            for hours in (72, 88):
                focal = Member(mem[0].age if 18 <= mem[0].age <= 64 else 35, work_hours_month=hours,
                               countable_months_used=3,
                               pregnant=status == "pregnant", medically_unfit=status == "medical",
                               cares_for_child_under_14=status in ("child_under_14", "child_15_trap"))
                others = [Member(9)] if status == "child_under_14" else [Member(15)] if status == "child_15_trap" else []
                h = Household([focal] + others, earned=hours * 12, unearned=0, shelter=int(base["RENT"]),
                              utilities=int(base["UTIL"] or 0), assets=500)
                g = abawd(focal, h)
                facts = [f"{name} worked {hours} hours of paid work last month and is not in a work program.",
                         f"{name} has already used 3 countable months in the current 36-month period."]
                if status == "pregnant":
                    facts.append(f"{name} is pregnant (medically verified).")
                if status == "medical":
                    facts.append(f"A doctor has certified that {name} is physically unfit for work.")
                if status in ("child_under_14", "child_15_trap"):
                    facts.append(f"{name} is responsible for the care of the child in the household.")
                for cue in ("none", "effort_high", "effort_low", "control_high", "control_low"):
                    for style in ("structured", "narrative"):
                        rows.append(dict(
                            item_id=f"b{bi:03d}_abawd_{status}_{hours}_{cue}_{style[0]}", base=f"b{bi:03d}",
                            task="abawd", status=status, hours=hours, cue=cue, style=style,
                            cue_relevant=False, gold="YES" if g["eligible_this_month"] else "NO",
                            text=case_text(h, compute(h), name, cue, style, extra=facts),
                            facts={k: str(v) for k, v in g.items()}))
    out = ROOT / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    ids = [r["item_id"] for r in rows]
    assert len(ids) == len(set(ids))
    with open(out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    df = pd.DataFrame(rows)
    print(len(df), "items")
    print(df.groupby(["task", "gold"]).size().unstack(fill_value=0))


if __name__ == "__main__":
    main()
