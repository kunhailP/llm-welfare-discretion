"""Design C psychometric set (2026-10-05): the decision boundary in dollars, and how far cues shift it.

Why: in the v1 discretion pilot, Qwen3-14B (direct answers) denied every open-standard case, even at a $250
monthly shortfall, so cue effects existed only in the log-odds tail (docs/11, Result 1). Here the need range is
wide enough for P(grant) to cross 0.5, and the cue effect is read as a shift of the point of subjective
equality (PSE: the shortfall at which P(grant) = 0.5), in dollars.

Fixed situation as in Design C: single non-exempt ABAWD adult, March 2026, 72 hours (40 paid + 32 program),
3 countable months used, $480 earned; question = grant a discretionary exemption?
Factors:
  leniency : serious ("serious hardship"), basic ("hardship in meeting basic needs such as food, housing and
             utilities"), food ("difficulty affording enough food for the month")
  prohibit : no / yes (+ "only financial hardship; reason for job loss, job-search effort and other personal
             circumstances must NOT be considered")
  leftover : +250 / +150 / +50 / -50 / -150 / -300 / -450 / -600 a month after rent + utilities
  cue      : base ("lost a full-time job last summer", shared by every job cue), effort hi/lo, control hi/lo,
             valence_neg (non-moral; car breakdown added to the base sentence)
  polarity : grant? / deny?
  base     : 20 (name x age x utilities)
Answers YES / NO (facts are complete).

Usage: python src/gen/make_design_c_psych.py --out data/design_c_psych/items.jsonl
"""
import argparse, json, pathlib, random, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src/gen"))
from make_rules_pilot import NAMES, MONTH, PAID_HOURS, WAGE, money  # noqa: E402
from make_design_c_v2 import HEADER  # noqa: E402  (if-and-only-if wording, review of 370c219)

CUES = {
    "base":         "{n} lost a full-time job last summer.",
    "effort_high":  "{n} lost a full-time job last summer and has applied for about eight jobs every week since.",
    "effort_low":   "{n} lost a full-time job last summer and has applied for one job in the past two months.",
    "control_high": "{n} lost a full-time job last summer when the warehouse where they worked closed down.",
    "control_low":  "{n} lost a full-time job last summer after being fired for repeatedly missing shifts.",
    "valence_neg":  "{n} lost a full-time job last summer, and {n}'s car broke down and has not been repaired.",
}
LENIENCY = {
    "serious": "would face serious hardship in the determination month without SNAP benefits",
    "basic": "would have hardship in meeting basic needs such as food, housing, and utilities in the determination month without SNAP benefits",
    "food": "would have difficulty affording enough food in the determination month without SNAP benefits",
}
PROHIBIT = (" The decision must be based only on the household's financial hardship. The reason the individual "
            "lost a job, the individual's job-search effort, and other personal circumstances must NOT be considered.")
LEFTOVER = [250, 150, 50, -50, -150, -300, -450, -600]
Q = {"pos": "Under these rules, does the agency grant {n} a discretionary exemption for the determination month named in the case file?",
     "neg": "Under these rules, does the agency deny {n} a discretionary exemption for the determination month named in the case file?"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bases", type=int, default=20)
    ap.add_argument("--seed", type=int, default=19)
    ap.add_argument("--out", default="data/design_c_psych/items.jsonl")
    a = ap.parse_args()
    rng = random.Random(a.seed)
    earned = PAID_HOURS * WAGE
    rows = []
    for bi in range(a.bases):
        n = NAMES[bi % len(NAMES)]
        age, util = rng.randint(20, 44), rng.randrange(80, 161, 5)
        for left in LEFTOVER:
            rent = earned - util - left
            gap = (f"After rent and utilities, {n} has {money(left)} left each month for food and all other costs."
                   if left >= 0 else f"Rent and utilities alone exceed {n}'s income by {money(-left)} each month.")
            for len_k, len_s in LENIENCY.items():
                for pro in ("no", "yes"):
                    rule = (HEADER + f"The agency grants a discretionary exemption if, and only if, in the caseworker's judgment "
                            f"the individual {len_s}." + (PROHIBIT if pro == "yes" else ""))
                    for cue, cs in CUES.items():
                        text = "\n".join([
                            f"Caseworker note on {n}'s application. " + cs.format(n=n),
                            f"The household has one member: {n} (age {age}).",
                            f"{n} earns {money(earned)} a month from work and receives $0 a month in other income.",
                            f"{n} pays {money(rent)} a month in rent and {money(util)} a month for utilities. {gap}",
                            "There are no dependent care, medical, or child support costs, and countable assets are $500.",
                            f"This determination is for {MONTH}. {n}'s verified hours for {MONTH}: {PAID_HOURS} hours of paid "
                            f"work and 32 hours in an approved work program (72 hours in total).",
                            f"Before {MONTH}, {n} had already used 3 countable months in the current 36-month period.",
                            f"Exemption facts for {n} (complete): pregnant: No; medically certified unfit for work: No; "
                            f"has a disability: No; Indian, Urban Indian, or California Indian: No; responsible for the care "
                            f"of a child under 14 who lives in the household: No."])
                        for pol in ("pos", "neg"):
                            rows.append(dict(item_id=f"b{bi:03d}_{len_k}_{pro}_{left:+d}_{cue}_{pol}", base=f"b{bi:03d}",
                                             task="psych", leniency=len_k, prohibit=pro, leftover=left, cue=cue,
                                             polarity=pol, gold=None, question=Q[pol].format(n=n),
                                             packet_extra=rule, text=text))
    out = ROOT / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    assert len({r["item_id"] for r in rows}) == len(rows)
    with open(out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "items")


if __name__ == "__main__":
    main()
