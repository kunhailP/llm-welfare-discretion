"""Controlled item set v2: separate the parts of the "unemployed context" and test new fact surfaces.

Design (fixes from the 2026-10-05 review):
  * Same named subject in every context (no "This household" switch).
  * Length-matched context block: always 4 sentence slots. Content sentences fill slots from the start;
    the remaining slots take neutral filler sentences fixed per base.
  * Context ladder, one component added at a time:
      none            F F F F
      employed        E F F F        (works full time as <job>)
      unemp_status    U F F F        (is currently unemployed)
      unemp_cause     L U F F        (+ job loss event)
      unemp_nopay     L U N F        (+ no paid work for four weeks)
      search_high     L U N S+       (+ applied to all 8 openings)   } effort minimal pair
      search_low      L U N S-       (+ applied to 1 of 8 openings)  }
      lexical_closure C F F F        (a bakery "closed": negative, closure wording, no money/employment content)
    Non-welfare control task (same money structure, a community project instead of a person):
      budget_none     P P P P ;  budget_loss  K P P P (main sponsor withdrew funding)
  * New fact surfaces, balanced across bases: totals vs itemized, funds-first vs bills-first.
  * Funds grid includes exact equality (gap 0 -> SUFFICIENT: the bills can be paid in full).
  * Amount range differs from the pilot ($600-$3,600 vs $800-$2,400).
  * Slot pools: dev uses the pilot pools (already seen); test uses new, disjoint pools and seed.

Usage:
  python src/gen/make_controlled_v2.py --split dev  --n-bases 20 --seed 11 --out data/controlled_v2/dev.jsonl
  python src/gen/make_controlled_v2.py --split test --n-bases 60 --seed 23 --out data/controlled_v2/test.jsonl
"""
import argparse
import json
import random

GAPS = [-0.20, -0.05, -0.02, 0.00, 0.02, 0.05, 0.20, 0.40]
PERSON_CONTEXTS = ["none", "employed", "unemp_status", "unemp_cause", "unemp_nopay",
                   "search_high", "search_low", "lexical_closure"]
BUDGET_CONTEXTS = ["budget_none", "budget_loss"]

POOLS = {
    "dev": {  # same pools as the pilot: dev only
        "names": ["Alex Morgan", "Jordan Lee", "Sam Rivera", "Taylor Brooks", "Casey Patel",
                  "Riley Chen", "Jamie Novak", "Morgan Diaz", "Avery Kim", "Quinn Foster"],
        "jobs": [("a warehouse associate", "the distribution center closed permanently"),
                 ("a bookkeeper", "the accounting firm shut down its local office"),
                 ("a line cook", "the restaurant went out of business"),
                 ("a machine operator", "the factory closed after the company relocated production"),
                 ("a retail supervisor", "the store closed when the chain went bankrupt")],
        "bills": [("rent", "electricity"), ("rent", "water and heating"), ("mortgage payment", "electricity")],
        "projects": ["the Riverside community garden project", "the Elm Street youth soccer league"],
    },
    "test": {  # disjoint from pilot and from make_profiles 'main' pools
        "names": ["Sydney Clarke", "Logan Reyes", "Blair Sutton", "Charlie Okafor", "Kendall Hart",
                  "Peyton Larsen", "Ari Mendez", "Remy Walsh", "Shawn Ibarra", "Devon Pryor",
                  "Marlowe Quist", "Tatum Rhee"],
        "jobs": [("a bank teller", "the bank closed its neighborhood branch"),
                 ("a forklift operator", "the lumber yard shut down"),
                 ("a medical biller", "the billing company lost its main contract and closed"),
                 ("a school bus driver", "the transport contractor went out of business"),
                 ("a bakery packer", "the packaging plant closed"),
                 ("a pharmacy technician", "the pharmacy closed when the owner sold the building"),
                 ("a call-center scheduler", "the scheduling office was shut down")],
        "bills": [("rent", "the electric bill"), ("rent", "the heating bill"), ("the mortgage payment", "the water bill"),
                  ("rent", "the phone bill")],
        "projects": ["the Maple Hill neighborhood library fund", "the Lakeside volunteer food pantry",
                     "the Northgate community theater group"],
    },
}

PROJECT_BILLS = [("the venue rent", "the insurance premium"), ("the equipment lease", "the utility bill"),
                 ("the storage unit rent", "the printing invoice")]

PERSON_FILLERS = [
    "{f} lives in a second-floor apartment near the public library.",
    "{f} usually walks to the grocery store on Saturday mornings.",
    "{f} has a younger cousin who lives in another state.",
    "{f} keeps a few potted plants on the kitchen windowsill.",
    "{f} grew up in a small town about an hour away.",
    "{f} prefers tea to coffee on most days of the week.",
    "{f} often listens to the radio while making breakfast.",
    "{f}'s building has a small shared courtyard with two benches.",
]
PROJECT_FILLERS = [
    "The project meets on the first Tuesday of every month.",
    "The project's volunteers keep a shared calendar of events.",
    "The project started about six years ago in a church basement.",
    "The project publishes a short newsletter twice a year.",
    "The project's logo was designed by a local art student.",
    "The project keeps its records in a small filing cabinet.",
]


def money(x):
    return f"${x:,}"


def context_sentences(b, ctx):
    f, job, loss = b["first"], b["job"], b["loss"]
    E = f"{f} works full time as {job}."
    U = f"{f} is currently unemployed."
    L = f"{f} worked as {job} until {loss}."
    N = f"{f} has done no paid work in the past four weeks."
    S_hi = f"{f} applied to all 8 suitable job openings posted during those four weeks."
    S_lo = f"{f} applied to 1 of the 8 suitable job openings posted during those four weeks."
    C = f"{f}'s favorite neighborhood bakery closed for good last month."
    K = "The project's main sponsor withdrew its funding last month."
    content = {"none": [], "employed": [E], "unemp_status": [U], "unemp_cause": [L, U],
               "unemp_nopay": [L, U, N], "search_high": [L, U, N, S_hi], "search_low": [L, U, N, S_lo],
               "lexical_closure": [C], "budget_none": [], "budget_loss": [K]}[ctx]
    fill = b["project_fillers"] if ctx.startswith("budget") else b["person_fillers"]
    sents = content + [s.format(f=f) for s in fill[len(content):]]
    if ctx.startswith("budget"):  # introduce the project by name in the first sentence
        name = b["project"][0].upper() + b["project"][1:]
        sents[0] = sents[0].replace("The project", name, 1)
    return sents


def money_block(b, ctx, funds):
    budget = ctx.startswith("budget")
    who = b["project"][0].upper() + b["project"][1:] if budget else b["first"]
    poss = f"{who}'s" if not budget else "The project's"
    holder = "the project committee" if budget else b["first"]
    e = b["expenses"]
    if b["format"] == "totals":
        bills = f"{poss} essential bills due today total {money(e)}."
        funds_s = (f"All the money {holder} can access today, including income, savings, and any outside help, "
                   f"totals {money(funds)}.")
    else:
        ba, bb = b["project_bills"] if budget else b["bills"]
        ea = b["bill_share"]
        bills = f"Due today: {ba} of {money(ea)} and {bb} of {money(e - ea)}."
        cash = int(round(funds * b["cash_share"], -1))
        funds_s = (f"{holder[0].upper() + holder[1:]} has {money(funds - cash)} in a checking account and {money(cash)} in cash, "
                   f"and these are the only funds {holder} can access today.")
    parts = [bills, funds_s] if b["order"] == "bills_first" else [funds_s, bills]
    return " ".join(parts + ["No additional money will arrive before the bills are due."])


def make_base(rng, pool, i, split):
    name = rng.choice(pool["names"])
    job, loss = rng.choice(pool["jobs"])
    expenses = rng.randrange(60, 361) * 10
    return dict(
        base_id=f"v2{split}_{i:03d}", split=split, name=name, first=name.split()[0], job=job, loss=loss,
        bills=rng.choice(pool["bills"]), project=rng.choice(pool["projects"]), expenses=expenses,
        project_bills=rng.choice(PROJECT_BILLS),
        bill_share=int(round(expenses * rng.uniform(0.55, 0.75), -1)), cash_share=rng.uniform(0.15, 0.4),
        format=["totals", "itemized"][i % 2], order=["funds_first", "bills_first"][(i // 2) % 2],
        person_fillers=rng.sample(PERSON_FILLERS, 4), project_fillers=rng.sample(PROJECT_FILLERS, 4),
    )


def funds_for(e, g):
    if g == 0:
        return e
    f = int(round(e * (1 + g), -1))
    if f == e:  # rounding collapsed a nonzero gap
        f = e + (10 if g > 0 else -10)
    return f


def check(rows):
    """Within base x gap: identical money block across contexts; exactly 4 context sentences;
    gold matches arithmetic; report max word-count spread of context blocks per base."""
    by = {}
    for r in rows:
        by.setdefault((r["base_id"], r["gap_frac"], r["task"]), []).append(r)
    spread = []
    for k, rs in by.items():
        assert len({r["money_text"] for r in rs}) == 1, k
        for r in rs:
            assert len(r["context_sentences"]) == 4, r["item_id"]
            assert r["gold"] == ("SUFFICIENT" if r["funds"] >= r["expenses"] else "SHORTFALL"), r["item_id"]
        wc = [len(" ".join(r["context_sentences"]).split()) for r in rs]
        spread.append(max(wc) - min(wc))
    return max(spread), sum(spread) / len(spread)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["dev", "test"], required=True)
    ap.add_argument("--n-bases", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    rows = []
    for i in range(a.n_bases):
        b = make_base(rng, POOLS[a.split], i, a.split)
        for g in GAPS:
            funds = funds_for(b["expenses"], g)
            for ctx in PERSON_CONTEXTS + BUDGET_CONTEXTS:
                task = "budget" if ctx.startswith("budget") else "person"
                cs = context_sentences(b, ctx)
                mt = money_block(b, ctx, funds)
                rows.append(dict(
                    item_id=f"{b['base_id']}__g{g:+.2f}__{ctx}", base_id=b["base_id"], split=a.split, task=task,
                    context=ctx, format=b["format"], order=b["order"], gap_frac=g, funds=funds,
                    expenses=b["expenses"], gold="SUFFICIENT" if funds >= b["expenses"] else "SHORTFALL",
                    context_sentences=cs, money_text=mt, text=" ".join(cs) + " " + mt,
                    subject=b["project"] if task == "budget" else b["name"]))
    ids = [r["item_id"] for r in rows]
    assert len(ids) == len(set(ids))
    mx, mean = check(rows)
    with open(a.out, "w") as f:
        for r in rows:
            r["profile_id"] = r["item_id"]  # runner/scorer key
            f.write(json.dumps(r) + "\n")
    print(f"wrote {len(rows)} items ({a.n_bases} bases x {len(GAPS)} funds levels x "
          f"{len(PERSON_CONTEXTS) + len(BUDGET_CONTEXTS)} contexts) -> {a.out}; "
          f"context word-count spread within base: max {mx}, mean {mean:.1f}")


if __name__ == "__main__":
    main()
