"""Diagnostic set (dev only): where does social context override stated need facts?

Reuses the 50 dev bases (same seed/pool as data/pilot) so nothing touches the future test split.
Axes:
  context : unemployed (full vignette, high job search) | employed | none (bare household)
  level   : L0 facts in prose | L2 prose + gold facts block | L3 gold facts block only (no context)
            | L4 prose + computed gap stated
  gap     : funds - bills, as a fraction of bills, on a fixed grid around 0 (threshold curve)
L1 (model's own extracted facts fed back) needs a two-pass run and is built separately.

Usage: python src/gen/make_diagnostic.py --out data/diagnostic/oracle_ladder.jsonl
"""
import argparse
import json
import random
import sys

sys.path.insert(0, "/workspace/welfare-need-naacl/src/gen")
from make_profiles import POOLS, activity_sentences, make_base, money  # noqa: E402

GAPS = [-0.40, -0.20, -0.10, -0.05, -0.02, 0.02, 0.05, 0.10, 0.20, 0.40]


def context_prose(b, ctx):
    first = b["name"].split()[0]
    if ctx == "unemployed":
        return (f"{b['name']} worked as {b['job']} until {b['loss']}. "
                f"In the past four weeks, {first} received no job offers and did no paid work. "
                + activity_sentences(b, "high"))
    if ctx == "employed":
        return (f"{b['name']} works full time as {b['job']} "
                f"and is paid every two weeks; the next paycheck arrives after the bills below are due. ")
    return ""


def subject(b, ctx):
    return "This household" if ctx == "none" else b["name"].split()[0]


def money_prose(b, ctx, funds):
    s = subject(b, ctx)
    poss = "This household's" if ctx == "none" else f"{s}'s"
    return (f"{poss} essential bills due today total {money(b['expenses'])}. "
            f"All the money {s.lower() if ctx == 'none' else s} can access today (income, savings, and any outside help combined) "
            f"totals {money(funds)}. No additional money will arrive before the bills are due.")


def facts_block(b, funds):
    return (f"Facts: accessible funds today = {money(funds)}; essential bills due today = {money(b['expenses'])}; "
            f"no other money arrives before the bills are due.")


def gap_sentence(b, funds):
    d = funds - b["expenses"]
    return (f"Computed: accessible funds exceed the bills by {money(d)}." if d > 0
            else f"Computed: accessible funds fall short of the bills by {money(-d)}.")


def render(b, ctx, level, funds):
    prose = context_prose(b, ctx) + money_prose(b, ctx, funds)
    if level == "L0":
        return prose
    if level == "L2":
        return prose + "\n\n" + facts_block(b, funds)
    if level == "L3":
        return facts_block(b, funds)
    if level == "L4":
        return prose + "\n\n" + gap_sentence(b, funds)
    raise ValueError(level)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rng = random.Random(1)  # identical to pilot generation -> same 50 dev bases
    fmts = ["numeric", "itemized", "textual"]
    rows = []
    for i in range(50):
        b = make_base(rng, POOLS["pilot"], i, "pilot", fmts[i % 3])
        for g in GAPS:
            funds = int(round(b["expenses"] * (1 + g), -1))
            assert funds != b["expenses"]
            gold = "SUFFICIENT" if funds > b["expenses"] else "SHORTFALL"
            for ctx in ("unemployed", "employed", "none"):
                for level in ("L0", "L2", "L3", "L4"):
                    if level == "L3" and ctx != "none":
                        continue  # L3 has no context by construction; keep one copy
                    rows.append(dict(profile_id=f"{b['base_id']}__g{g:+.2f}__{ctx}__{level}", base_id=b["base_id"],
                                     split="pilot", context=ctx if level != "L3" else "facts_only", level=level,
                                     gap_frac=g, funds=funds, expenses=b["expenses"], gold_shortfall=gold,
                                     text=render(b, ctx, level, funds)))
    ids = [r["profile_id"] for r in rows]
    assert len(ids) == len(set(ids))
    with open(a.out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"wrote {len(rows)} rows -> {a.out}")


if __name__ == "__main__":
    main()
