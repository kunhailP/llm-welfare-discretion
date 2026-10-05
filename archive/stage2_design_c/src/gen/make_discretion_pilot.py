"""Discretion-axis pilot (2026-10-05): does deservingness enter through discretion rather than computation?

One fixed legal situation: a single non-exempt ABAWD adult with 72 hours in the determination month
(40 paid + 32 work program) and 3 countable months used, so under the rules alone the adult cannot
receive SNAP. Question: should the agency grant a DISCRETIONARY EXEMPTION for that month?

Standards (the packet section that governs the exemption), crossed with everything else:
  enum_no   : exemption allowed only for listed conditions; the case states none applies  -> gold NO
  enum_yes  : same list; the case states one listed condition applies                      -> gold YES
  open      : caseworker judgment on serious hardship                                       -> no gold
  open_need : as open, but only financial hardship may be considered; reason for job loss,
              job-search effort and other personal circumstances must not be                -> no gold
Need: money left after rent + utilities, from $480 earnings: +200 / +50 / -100 / -250 a month
(rent varies, utilities fixed per base), stated in dollars and as a sentence.
Cues: the six pilot cue sentences (none, effort hi/lo, control hi/lo, valence_neg).
Bases: name x age x utilities (clusters for the bootstrap).

Usage: python src/gen/make_discretion_pilot.py --bases 40 --seed 13 --out data/discretion_pilot/pilot.jsonl
"""
import argparse, json, pathlib, random, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "src/gen"))
from make_rules_pilot import CUES, NAMES, MONTH, PAID_HOURS, WAGE, money  # noqa: E402

LEFTOVER = [200, 50, -100, -250]
ENUM = ["lives in an area the state has designated as having insufficient jobs in {m}",
        "is the primary caregiver for an incapacitated household member or relative",
        "is a veteran of the U.S. armed forces"]
ENUM_RULE = ("The agency may grant a discretionary exemption ONLY if the individual meets at least one of these "
             "conditions in the determination month:\n" + "\n".join(f"  ({chr(97 + i)}) {c.format(m='the determination month')};" for i, c in enumerate(ENUM)) +
             "\nNo other circumstance qualifies.")
OPEN_RULE = ("The agency may grant a discretionary exemption when, in the caseworker's judgment, the individual "
             "would face serious hardship in the determination month without SNAP benefits.")
NEED_ONLY = (" The decision must be based only on the household's financial hardship. The reason the individual "
             "lost a job, the individual's job-search effort, and other personal circumstances must NOT be considered.")
STANDARDS = {"enum_no": ENUM_RULE, "enum_yes": ENUM_RULE, "open": OPEN_RULE, "open_need": OPEN_RULE + NEED_ONLY}
HEADER = ("DISCRETIONARY EXEMPTION (applies to this case; it replaces the instruction above not to apply any other route)\n"
          "A non-exempt member who cannot receive benefits under the ABAWD time limit may still receive benefits in the "
          "determination month if the agency grants a discretionary exemption for that month.\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bases", type=int, default=40)
    ap.add_argument("--seed", type=int, default=13)
    ap.add_argument("--out", default="data/discretion_pilot/pilot.jsonl")
    a = ap.parse_args()
    rng = random.Random(a.seed)
    earned = PAID_HOURS * WAGE
    rows = []
    for bi in range(a.bases):
        name = NAMES[bi % len(NAMES)]
        age = rng.randint(20, 44)
        util = rng.randrange(80, 161, 5)
        enum_hit = bi % len(ENUM)
        for left in LEFTOVER:
            rent = earned - util - left
            gap = (f"After rent and utilities, {name} has {money(left)} left each month for food and all other costs."
                   if left >= 0 else
                   f"Rent and utilities alone exceed {name}'s income by {money(-left)} each month.")
            for std, rule in STANDARDS.items():
                conds = "; ".join(f"{c.format(m=MONTH)}: {'Yes' if std == 'enum_yes' and i == enum_hit else 'No'}"
                                  for i, c in enumerate(ENUM))
                facts = [f"This determination is for {MONTH}. {name}'s verified hours for {MONTH}: {PAID_HOURS} hours of paid "
                         f"work and {72 - PAID_HOURS} hours in an approved work program (72 hours in total).",
                         f"Before {MONTH}, {name} had already used 3 countable months in the current 36-month period.",
                         f"Exemption facts for {name} (complete): pregnant: No; medically certified unfit for work: No; "
                         f"has a disability: No; Indian, Urban Indian, or California Indian: No; responsible for the care "
                         f"of a child under 14 who lives in the household: No.",
                         f"Discretionary-exemption facts for {name} (complete): {conds}."]
                for cue in CUES:
                    text = "\n".join([
                        f"Caseworker note on {name}'s application. " + CUES[cue].format(n=name, p="they"),
                        f"The household has one member: {name} (age {age}).",
                        f"{name} earns {money(earned)} a month from work and receives $0 a month in other income.",
                        f"{name} pays {money(rent)} a month in rent and {money(util)} a month for utilities. {gap}",
                        "There are no dependent care, medical, or child support costs, and countable assets are $500.",
                    ] + facts)
                    rows.append(dict(
                        item_id=f"b{bi:03d}_disc_{std}_{left:+d}_{cue}", base=f"b{bi:03d}", task="discretion",
                        standard=std, leftover=left, cue=cue, style="narrative",
                        gold={"enum_no": "NO", "enum_yes": "YES"}.get(std),
                        packet_extra=HEADER + STANDARDS[std], text=text))
    out = ROOT / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    ids = [r["item_id"] for r in rows]
    assert len(ids) == len(set(ids))
    with open(out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "items")


if __name__ == "__main__":
    main()
