"""Blind review sheets for two independent human reviewers (no gold, no model output).
Sheet A: single items -> reviewer decides SHORTFALL/SUFFICIENT/UNDETERMINED + flags.
Sheet B: high/low activity pairs -> are protected facts identical? is the activity difference clear?
"""
import csv, json, random
rows = [json.loads(l) for l in open("data/pilot/profiles.jsonl")]
core = [r for r in rows if r["control"] == "core"]
rng = random.Random(7)
a = core[:]; rng.shuffle(a)
with open("data/review/pilot_sheetA_items.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item_no", "text", "shortfall_judgment(SHORTFALL/SUFFICIENT/UNDETERMINED)", "ambiguous_or_contradictory(Y/N)", "comment"])
    for i, r in enumerate(a):
        w.writerow([i + 1, r["text"], "", "", ""])
key = {i + 1: r["profile_id"] for i, r in enumerate(a)}
json.dump(key, open("data/review/pilot_sheetA_KEY_do_not_share.json", "w"))
pairs = {}
for r in core:
    pairs.setdefault((r["base_id"], r["resource_state"]), {})[r["activity"]] = r
p = list(pairs.items()); rng.shuffle(p)
with open("data/review/pilot_sheetB_pairs.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["pair_no", "text_1", "text_2", "money_facts_and_deadline_identical(Y/N)", "only_job_search_differs(Y/N)", "job_search_difference_clear(Y/N)", "comment"])
    for i, (k, d) in enumerate(p):
        t = [d["high"]["text"], d["low"]["text"]]; rng.shuffle(t)
        w.writerow([i + 1, t[0], t[1], "", "", "", ""])
print(len(a), "items;", len(p), "pairs")
