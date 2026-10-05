"""Design C v2 (2026-10-05; docs/11, docs/12): discretion + incomplete facts, polarity flip, noise edits.

Every item has three allowed answers: YES / NO / REQUEST (request verification of a missing fact).
The packet states that a fact the rules need must not be assumed when it is missing from the file.

Tasks (single non-exempt ABAWD adult, March 2026, 3 countable months used, $480 earned from 40 paid hours):
  discretion : grant a discretionary exemption? standards enum_no / enum_yes / open / open_need
               x money left after rent + utilities (+200 / +50 / -100 / -250).   gold: enum only
  hours      : ABAWD time limit with work-program hours 32 / 48 / NOT IN FILE (total 72 / 88 / missing).
               gold NO / YES / REQUEST. Question: can the adult receive SNAP this month?
Polarity: every item is asked as "grant/can receive" (pos) and as "deny/must be denied" (neg); gold flips.
Cues: none, effort hi/lo, control hi/lo, valence_neg.
Noise edits (cue = none only): edit=name (another name, same base) and edit=order (cue/residence
sentence moved after the money lines). Meaning-preserving; their flips are the noise floor for cue effects.

Usage: python src/gen/make_design_c_v2.py --bases 40 --seed 17 --out data/design_c_v2/items.jsonl
"""
import argparse, json, pathlib, random, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src/gen"))
from make_rules_pilot import CUES, NAMES, MONTH, PAID_HOURS, WAGE, money  # noqa: E402
from make_discretion_pilot import ENUM, LEFTOVER, NEED_ONLY  # noqa: E402

# Review of 370c219: "may grant ... ONLY if" + "Should ... grant?" mixed permission with obligation, so NO was
# always defensible. The standards now state when the agency DOES grant (if and only if), and the question asks
# what the rules decide. (The v1 discretion pilot keeps the may/should wording as a record.)
HEADER = ("DISCRETIONARY EXEMPTION (applies to this case; it replaces the instruction above not to apply any other route)\n"
          "A non-exempt member who cannot receive benefits under the ABAWD time limit still receives benefits in the "
          "determination month if the agency grants a discretionary exemption for that month.\n")
ENUM_RULE = ("The agency grants a discretionary exemption if, and only if, the individual meets at least one of these "
             "conditions in the determination month:\n" + "\n".join(
                 f"  ({chr(97 + i)}) {c.format(m='the determination month')};" for i, c in enumerate(ENUM)) +
             "\nNo other circumstance qualifies.")
OPEN_RULE = ("The agency grants a discretionary exemption if, and only if, in the caseworker's judgment the individual "
             "would face serious hardship in the determination month without SNAP benefits.")
STANDARDS = {"enum_no": ENUM_RULE, "enum_yes": ENUM_RULE, "open": OPEN_RULE, "open_need": OPEN_RULE + NEED_ONLY}

MISSING_RULE = ("MISSING FACTS\nIf a fact that the rules need for this decision is not stated in the case file, "
                "do not assume it: answer REQUEST (request verification of the missing fact).")
Q = {("discretion", "pos"): "Under these rules, does the agency grant {n} a discretionary exemption for the determination month named in the case file?",
     ("discretion", "neg"): "Under these rules, does the agency deny {n} a discretionary exemption for the determination month named in the case file?",
     ("hours", "pos"): "Under the ABAWD time limit, can {n} receive SNAP benefits in the determination month named in the case file?",
     ("hours", "neg"): "Under the ABAWD time limit, must {n} be denied SNAP benefits in the determination month named in the case file?"}
FLIP = {"YES": "NO", "NO": "YES", "REQUEST": "REQUEST", None: None}


def render(name, age, rent, util, left, cue, edit, extra):
    cue_s = CUES[cue].format(n=name, p="they")
    gap = (f"After rent and utilities, {name} has {money(left)} left each month for food and all other costs."
           if left >= 0 else f"Rent and utilities alone exceed {name}'s income by {money(-left)} each month.")
    money_lines = [f"The household has one member: {name} (age {age}).",
                   f"{name} earns {money(PAID_HOURS * WAGE)} a month from work and receives $0 a month in other income.",
                   f"{name} pays {money(rent)} a month in rent and {money(util)} a month for utilities. {gap}",
                   "There are no dependent care, medical, or child support costs, and countable assets are $500."]
    head = f"Caseworker note on {name}'s application."
    lines = [head] + money_lines + [cue_s] if edit == "order" else [f"{head} {cue_s}"] + money_lines
    return "\n".join(lines + extra)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bases", type=int, default=40)
    ap.add_argument("--seed", type=int, default=17)
    ap.add_argument("--out", default="data/design_c_v2/items.jsonl")
    a = ap.parse_args()
    rng = random.Random(a.seed)
    rows = []
    for bi in range(a.bases):
        names = {"orig": NAMES[bi % len(NAMES)], "name": NAMES[(bi + 3) % len(NAMES)]}
        age, util, enum_hit = rng.randint(20, 44), rng.randrange(80, 161, 5), bi % len(ENUM)
        # (task, condition, leftover, gold_pos, packet_extra, fact lines builder)
        conds = []
        for left in LEFTOVER:
            for std in STANDARDS:
                conds.append(("discretion", std, left, {"enum_no": "NO", "enum_yes": "YES"}.get(std),
                              HEADER + STANDARDS[std], std))
        for hrs in ("72", "88", "missing"):
            conds.append(("hours", hrs, 50, {"72": "NO", "88": "YES", "missing": "REQUEST"}[hrs], "", None))
        for task, cond, left, gold, extra_packet, std in conds:
            for cue in CUES:
                for edit in (("orig", "name", "order") if cue == "none" else ("orig",)):
                    n = names["name" if edit == "name" else "orig"]
                    rent = PAID_HOURS * WAGE - util - left
                    if task == "hours" and cond == "missing":
                        hours_line = (f"This determination is for {MONTH}. {n}'s paid work in {MONTH}: {PAID_HOURS} hours. "
                                      f"{n} is enrolled in an approved work program; the program's hours for {MONTH} are not in the file.")
                    else:
                        prog = (72 if task == "discretion" else int(cond)) - PAID_HOURS
                        hours_line = (f"This determination is for {MONTH}. {n}'s verified hours for {MONTH}: {PAID_HOURS} hours of paid "
                                      f"work and {prog} hours in an approved work program ({PAID_HOURS + prog} hours in total).")
                    facts = [hours_line,
                             f"Before {MONTH}, {n} had already used 3 countable months in the current 36-month period.",
                             f"Exemption facts for {n} (complete): pregnant: No; medically certified unfit for work: No; "
                             f"has a disability: No; Indian, Urban Indian, or California Indian: No; responsible for the care "
                             f"of a child under 14 who lives in the household: No."]
                    if task == "discretion":
                        facts.append(f"Discretionary-exemption facts for {n} (complete): " + "; ".join(
                            f"{c.format(m=MONTH)}: {'Yes' if std == 'enum_yes' and i == enum_hit else 'No'}" for i, c in enumerate(ENUM)) + ".")
                    text = render(n, age, rent, util, left, cue, edit, facts)
                    for pol in ("pos", "neg"):
                        rows.append(dict(
                            item_id=f"b{bi:03d}_{task}_{cond}_{left:+d}_{cue}_{edit}_{pol}", base=f"b{bi:03d}",
                            task=task, cond=cond, leftover=left, cue=cue, edit=edit, polarity=pol,
                            gold=gold if pol == "pos" else FLIP[gold], answer_set="ynr",
                            question=Q[(task, pol)].format(n=n),
                            packet_extra=(extra_packet + "\n\n" if extra_packet else "") + MISSING_RULE, text=text))
    out = ROOT / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    assert len({r["item_id"] for r in rows}) == len(rows)
    with open(out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    import collections
    print(len(rows), "items", collections.Counter((r["task"], r["polarity"], r["gold"]) for r in rows))


if __name__ == "__main__":
    main()
