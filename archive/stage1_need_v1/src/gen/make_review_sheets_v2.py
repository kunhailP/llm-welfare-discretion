"""Blind human review sheets for controlled_v2 TEST items (no model outputs, no gold).
One random funds level per base; all 10 context variants of that base, shuffled -> 600 rows for 60 bases.
Reviewers answer: can the bills be paid in full (gold check); is anything contradictory or unclear;
naturalness; and a manipulation check of what the context implies (employment, effort, responsibility),
so we know which constructs each context sentence moves for a human reader.
"""
import csv
import json
import random

rows = [json.loads(l) for l in open("data/controlled_v2/test.jsonl")]
rng = random.Random(31)
by = {}
for r in rows:
    by.setdefault(r["base_id"], {}).setdefault(r["gap_frac"], []).append(r)
picked = []
for b, gaps in sorted(by.items()):
    picked += gaps[rng.choice(sorted(gaps))]
rng.shuffle(picked)
cols = ["row", "text",
        "can_bills_be_paid_in_full (YES/NO/CANNOT_TELL)",
        "contradictory_or_unclear (Y/N)",
        "natural_1to5",
        "says_person_or_project_is_employed (YES/NO/NOT_STATED)",
        "how_hard_is_the_person_trying_to_find_work_1to5_or_NA",
        "how_responsible_for_own_financial_situation_1to5_or_NA",
        "comment"]
with open("data/review/v2_test_sheet.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(cols)
    for i, r in enumerate(picked):
        w.writerow([i + 1, r["text"]] + [""] * (len(cols) - 2))
json.dump({i + 1: r["item_id"] for i, r in enumerate(picked)}, open("data/review/v2_test_sheet_KEY_do_not_share.json", "w"))
print(len(picked), "rows")
