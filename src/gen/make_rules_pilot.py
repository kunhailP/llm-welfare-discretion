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
    "effort_high":  "Since losing a full-time job last summer, {n} has applied for about eight jobs every week.",
    "effort_low":   "Since losing a full-time job last summer, {n} has applied for one job in the past two months.",
    "control_high": "{n} lost a full-time job last summer when the warehouse where {p} worked closed down.",
    "control_low":  "{n} lost a full-time job last summer after being fired for repeatedly missing shifts.",
    "valence_neg":  "{n}'s car broke down last summer and it still has not been repaired.",
}
MARGINS = [-0.15, -0.04, 0.04, 0.15]
PAID_HOURS, WAGE, MONTH = 40, 12, "March 2026"   # ABAWD: fixed paid work; only program hours vary   # (value - limit) / limit for the decisive quantity


def money(x):
    x = Fraction(x)
    return f"${int(x):,}" if x.denominator == 1 else f"${float(x):,.2f}"


def load_structures(rng, k):
    cols = ["FSUSIZE", "FSEARN", "FSUNEARN", "RENT", "UTIL", "FSDEPDED", "FSMEDEXP", "FSCSEXP", "HWGT"]   # HWGT: sidecar only
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
             f"Monthly dependent care costs (paid so an adult member can work): {lines['dep']}; out-of-pocket medical costs of elderly or disabled members: {lines['med']}",
             f"Legally owed child support paid outside the household: {lines['cs']}",
             f"Countable assets: {lines['assets']}",
             f"Caseworker note: {cue_s}"] + [f"Caseworker note: {e}" for e in extra]
    else:
        t = [f"Caseworker note on {name}'s application. {cue_s}",
             (f"The household has {len(h.members)} members: " if len(h.members) > 1 else "The household has one member: ") + "; ".join(people) + ".",
             f"Together the members earn {lines['earned']} a month from work and receive {lines['unearned']} a month in other income.",
             f"They pay {lines['rent']} a month in rent and {lines['util']} a month for utilities.",
             f"They pay {lines['dep']} a month for dependent care so that an adult member can work, and out-of-pocket medical costs for elderly or disabled members are {lines['med']} a month.",
             f"They pay {lines['cs']} a month in legally owed child support to someone outside the household, and have {lines['assets']} in countable assets."] + extra
    return "\n".join(t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bases", type=int, default=40)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--out", default="data/rules_pilot/pilot.jsonl")
    ap.add_argument("--abawd-cues", default="none,effort_high,effort_low,control_high,control_low",
                    help="cues generated for the ABAWD task; 'all' adds the hardship control valence_neg (2026-10-08, blind-review round 4)")
    a = ap.parse_args()
    rng = random.Random(a.seed)
    bases = load_structures(rng, a.bases)
    # Sidecar for the consequence analysis (2026-10-08): source household weight per base. Items are unchanged.
    side = ROOT / a.out
    side = side.with_name(side.stem + "_bases_hwgt.json")
    side.parent.mkdir(parents=True, exist_ok=True)
    json.dump({f"b{bi:03d}": dict(hwgt=float(b["HWGT"]), size=int(b["FSUSIZE"])) for bi, b in enumerate(bases)},
              open(side, "w"), indent=1)
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
        # --- ABAWD task (revised 2026-10-05 per review_092727e):
        # * the determination month is named and every hours fact refers to it;
        # * paid work (40 h, $480) and earned income are FIXED; only approved work-program hours vary
        #   (32 vs 48 -> 72 vs 88 total), so the hours contrast carries no income change;
        # * every exemption condition is stated Yes/No (the packet says the list is complete).
        for status in ("nonexempt", "pregnant", "child_under_14", "child_15_trap", "medical"):
            for hours in (72, 88):
                prog = hours - PAID_HOURS
                focal = Member(min(max(mem[0].age, 20), 44), work_hours_month=hours,   # same age in every status; plausible for pregnancy
                               countable_months_used=3,
                               pregnant=status == "pregnant", medically_unfit=status == "medical",
                               cares_for_child_under_14=status in ("child_under_14", "child_15_trap"))
                others = [Member(9)] if status == "child_under_14" else [Member(15)] if status == "child_15_trap" else []
                h = Household([focal] + others, earned=PAID_HOURS * WAGE, unearned=0, shelter=int(base["RENT"]),
                              utilities=int(base["UTIL"] or 0), assets=500)
                g = abawd(focal, h)
                yn = lambda b: "Yes" if b else "No"
                facts = [f"This determination is for {MONTH}. {name}'s verified hours for {MONTH}: {PAID_HOURS} hours "
                         f"of paid work and {prog} hours in an approved work program ({hours} hours in total).",
                         f"Before {MONTH}, {name} had already used 3 countable months in the current 36-month period.",
                         f"Exemption facts for {name} (complete): pregnant: {yn(status == 'pregnant')}; "
                         f"medically certified unfit for work: {yn(status == 'medical')}; has a disability: No; "
                         f"Indian, Urban Indian, or California Indian: No; responsible for the care of a child "
                         f"who lives in the household: {yn(status in ('child_under_14', 'child_15_trap'))}."]
                abawd_cues = list(CUES) if a.abawd_cues == "all" else a.abawd_cues.split(",")
                for cue in abawd_cues:
                    for style in ("structured", "narrative"):
                        rows.append(dict(
                            item_id=f"b{bi:03d}_abawd_{status}_{hours}_{cue}_{style[0]}", base=f"b{bi:03d}",
                            task="abawd", status=status, exempt=g["exemption"] is not None, hours=hours,
                            paid_hours=PAID_HOURS, program_hours=prog, earned=h.earned, cue=cue, style=style,
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
