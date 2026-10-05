"""Generate controlled vignette profiles (core 2x2 + controls) from human-written templates.

No LLM is used here. Every profile records the fixed facts and the gold shortfall label,
so invariance can be checked mechanically (see check_invariance in this file).

Usage:
  python src/gen/make_profiles.py --split pilot --n-bases 50 --seed 1 --out data/pilot/profiles.jsonl
  python src/gen/make_profiles.py --split main  --n-bases 120 --seed 2 --controls --out data/main/profiles.jsonl
  (--paraphrases > 1 is refused until human-reviewed paraphrase templates exist)
"""
import argparse
import json
import random

# Slot pools are split so pilot and main bases never share occupation/expense combos.
POOLS = {
    "pilot": {
        "names": ["Alex Morgan", "Jordan Lee", "Sam Rivera", "Taylor Brooks", "Casey Patel",
                  "Riley Chen", "Jamie Novak", "Morgan Diaz", "Avery Kim", "Quinn Foster"],
        "jobs": [("a warehouse associate", "the distribution center closed permanently"),
                 ("a bookkeeper", "the accounting firm shut down its local office"),
                 ("a line cook", "the restaurant went out of business"),
                 ("a machine operator", "the factory closed after the company relocated production"),
                 ("a retail supervisor", "the store closed when the chain went bankrupt")],
        "bills": [("rent", "electricity"), ("rent", "water and heating"), ("mortgage payment", "electricity")],
    },
    "main": {
        "names": ["Robin Hayes", "Drew Collins", "Jesse Romero", "Cameron Ward", "Skyler Nguyen",
                  "Reese Coleman", "Dakota Shah", "Emerson Price", "Rowan Ortiz", "Parker Wells",
                  "Hayden Moss", "Finley Grant"],
        "jobs": [("a call-center agent", "the call center closed and all staff were let go"),
                 ("a delivery driver", "the courier company ceased operations"),
                 ("a dental receptionist", "the clinic closed when the owner retired"),
                 ("a print-shop technician", "the print shop closed permanently"),
                 ("a hotel housekeeper", "the hotel closed for good"),
                 ("an assembly worker", "the plant shut down without warning"),
                 ("an office administrator", "the company dissolved its regional branch")],
        "bills": [("rent", "gas and electricity"), ("rent", "phone and internet"),
                  ("rent", "car insurance"), ("mortgage payment", "water and heating")],
    },
}

NEUTRAL = ["They submitted their assistance application through the agency's website.",
           "They submitted their assistance application through the agency's mobile app."]
VALENCE = ["The elevator in their apartment building has been out of service for two weeks.",  # negative, not about effort/blame
           "The elevator in their apartment building was inspected two weeks ago."]          # matched neutral


def money(x):
    return f"${x:,}"


def make_base(rng, pool, base_idx, split, fmt):
    name = rng.choice(pool["names"])
    job, loss = rng.choice(pool["jobs"])
    bill_a, bill_b = rng.choice(pool["bills"])
    expenses = rng.randrange(80, 241) * 10                     # $800-$2,400
    short = int(round(expenses * rng.uniform(0.45, 0.8), -1))  # clearly below
    suff = int(round(expenses * rng.uniform(1.2, 1.6), -1))    # clearly above
    split_a = int(round(expenses * rng.uniform(0.55, 0.75), -1))
    return dict(base_id=f"{split}_{base_idx:03d}", split=split, format=fmt, name=name, job=job, loss=loss,
                bills=(bill_a, bill_b), expenses=expenses, bill_split=(split_a, expenses - split_a),
                resources={"shortfall": short, "sufficient": suff}, openings=8,
                applications={"high": 8, "low": 1})


def resource_sentences(b, state, rng_par):
    r, e = b["resources"][state], b["expenses"]
    (ba, bb), (ea, eb) = b["bills"], b["bill_split"]
    first = b["name"].split()[0]
    if b["format"] == "numeric":
        return (f"{first}'s essential bills due today total {money(e)}. "
                f"All the money {first} can access today (income, savings, and any outside help combined) totals {money(r)}.")
    if b["format"] == "itemized":
        cash = int(round(r * rng_par.uniform(0.2, 0.4), -1))
        checking = r - cash
        return (f"Due today: {ba} of {money(ea)} and {bb} of {money(eb)}. "
                f"{first} has {money(checking)} in a checking account and {money(cash)} in cash, "
                f"and these are the only funds {first} can access today.")
    # textual: no numbers, sufficiency stated in words
    if state == "shortfall":
        return (f"{first}'s {ba} and {bb} are due today. Even using every dollar {first} can access today, "
                f"including income, savings, and any outside help, {first} cannot pay these bills in full.")
    return (f"{first}'s {ba} and {bb} are due today. Using the money {first} can access today, "
            f"{first} can pay these bills in full and still have some money left over.")


def activity_sentences(b, activity):
    first = b["name"].split()[0]
    if activity == "none":
        return ""
    n = b["applications"][activity]
    applied = f"applied to all {n} of them" if n == b["openings"] else f"applied to {n} of them"
    return (f"During those weeks, there were {b['openings']} suitable job openings {first} could have applied for, "
            f"and {first} had the time and internet access to apply. {first} {applied}. ")


def render(b, state, activity, extra=""):
    first = b["name"].split()[0]
    rng_par = random.Random(f"{b['base_id']}-{state}")  # itemized split depends only on base+state
    text = (f"{b['name']} worked as {b['job']} until {b['loss']}. "
            + f"In the past four weeks, {first} received no job offers and did no paid work. "
            + activity_sentences(b, activity)
            + resource_sentences(b, state, rng_par) + " "
            + f"No additional money will arrive before the bills are due."
            + (" " + extra if extra else ""))
    return text


def profile(b, state, activity, control="core", paraphrase=0, extra=""):
    return dict(
        profile_id=f"{b['base_id']}__r{'S' if state == 'shortfall' else 'F'}__a{activity[0].upper()}__{control}__p{paraphrase}",
        base_id=b["base_id"], split=b["split"], format=b["format"], resource_state=state,
        activity=activity, control=control, paraphrase=paraphrase,
        text=render(b, state, activity, extra),
        facts=dict(resources=b["resources"][state], expenses=b["expenses"], deadline="today",
                   openings=b["openings"] if activity != "none" else None,
                   applications=b["applications"].get(activity)),
        gold_shortfall="SHORTFALL" if state == "shortfall" else "SUFFICIENT",
    )


def check_invariance(rows):
    """Within a base, core high/low pairs must differ only in the activity sentence."""
    by = {}
    for r in rows:
        if r["control"] == "core":
            by.setdefault((r["base_id"], r["resource_state"], r["paraphrase"]), {})[r["activity"]] = r
    for key, d in by.items():
        h, l = d["high"]["text"], d["low"]["text"]
        assert h.replace("applied to all 8 of them", "X") == l.replace("applied to 1 of them", "X"), key
        assert d["high"]["facts"]["resources"] == d["low"]["facts"]["resources"], key
    return len(by)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["pilot", "main"], required=True)
    ap.add_argument("--n-bases", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--paraphrases", type=int, default=1)  # >1 needs reviewed paraphrase templates (TODO)
    ap.add_argument("--controls", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.paraphrases != 1:
        raise SystemExit("--paraphrases > 1 is not implemented: no reviewed paraphrase templates yet. "
                         "New names/jobs alone are not surface paraphrases.")
    rng = random.Random(a.seed)
    fmts = ["numeric", "itemized", "textual"]
    rows = []
    for i in range(a.n_bases):
        b = make_base(rng, POOLS[a.split], i, a.split, fmts[i % 3])
        for state in ("shortfall", "sufficient"):
            for act in ("high", "low"):
                rows.append(profile(b, state, act))
            if a.controls:
                rows.append(profile(b, state, "none", "noact"))
                for k, s in enumerate(NEUTRAL):
                    rows.append(profile(b, state, "high", f"neutral{k}", extra=s))
                for k, s in enumerate(VALENCE):
                    rows.append(profile(b, state, "high", f"valence{k}", extra=s))
    n_pairs = check_invariance(rows)
    ids = [r["profile_id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate profile_id"
    with open(a.out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"wrote {len(rows)} profiles ({n_pairs} invariance-checked core pairs) -> {a.out}")


if __name__ == "__main__":
    main()
