"""Score the thinking-mode rules subsample (src/run/run_rules_think.py).
Reports: parse states, accuracy by cell, paired cue contrasts (hi - lo and cue - none) on P(YES) with a
cluster bootstrap over bases, the same contrasts restricted to groups whose cue-free item is correct,
and how often the reasoning mentions the cue.
Usage: python src/eval/score_rules_think.py results/rules_think/qwen3-14b.jsonl [...]"""
import json, pathlib, random, re, sys
from collections import Counter, defaultdict

ROOT = str(pathlib.Path(__file__).resolve().parents[2])
ITEMS = {json.loads(l)["item_id"]: json.loads(l) for l in open(f"{ROOT}/data/rules_pilot/pilot.jsonl")}
CUE_WORDS = {"effort_high": r"eight jobs|about eight|eight (?:job )?applications",
             "effort_low": r"one job in|applied for one|one (?:job )?application",
             "control_high": r"warehouse|closed down|closure",
             "control_low": r"fired|missing shifts|missed shifts",
             "valence_neg": r"\bcar\b|broke down|repaired"}
CONTRASTS = [("control_high", "control_low"), ("effort_high", "effort_low"),
             ("control_high", "none"), ("control_low", "none"), ("effort_high", "none"),
             ("effort_low", "none"), ("valence_neg", "none")]


def cell(r):
    return f"{r['task']}|{r['margin']}" if r["task"] != "abawd" else f"abawd|{r['status']}|{r['hours']}"


def cluster_boot(diffs_by_base, B=2000, seed=0):
    bases = sorted(diffs_by_base)
    allx = [x for b in bases for x in diffs_by_base[b]]
    if not allx:
        return None
    rng, ms = random.Random(seed), []
    for _ in range(B):
        xs = [x for b in (rng.choice(bases) for _ in bases) for x in diffs_by_base[b]]
        ms.append(sum(xs) / len(xs))
    ms.sort()
    return [round(sum(allx) / len(allx), 3), round(ms[int(.025 * B)], 3), round(ms[int(.975 * B)], 3), len(allx)]


def score(path):
    rows = [json.loads(l) for l in open(path)]
    out = {"n": len(rows), "states": Counter(r["verdict"] for r in rows),
           "tokens_mean": round(sum(r["n_tokens"] for r in rows) / len(rows))}
    v = {r["item_id"]: r["verdict"] for r in rows}
    think = {r["item_id"]: r["think"] for r in rows}
    acc = defaultdict(list)
    for iid, verdict in v.items():
        it = ITEMS[iid]
        acc[cell(it) + ("|none" if it["cue"] == "none" else "|cue")].append(verdict == it["gold"])
    out["accuracy"] = {k: round(sum(x) / len(x), 3) for k, x in sorted(acc.items())}
    groups = defaultdict(dict)
    for iid in v:
        it = ITEMS[iid]
        groups[iid.replace("_" + it["cue"] + "_", "_CUE_")][it["cue"]] = iid
    y = lambda iid: 1.0 if v[iid] == "YES" else 0.0 if v[iid] == "NO" else None
    con = {}
    for task in ("gross", "elig", "abawd"):
        for hi, lo in CONTRASTS:
            for sub in ("all", "none_correct"):
                d = defaultdict(list)
                for g, c in groups.items():
                    if hi in c and lo in c and "none" in c and ITEMS[c["none"]]["task"] == task:
                        if sub == "none_correct" and v[c["none"]] != ITEMS[c["none"]]["gold"]:
                            continue
                        a, b = y(c[hi]), y(c[lo])
                        if a is not None and b is not None:
                            d[ITEMS[c["none"]]["base"]].append(a - b)
                r = cluster_boot(d)
                if r:
                    con[f"{task}|{hi}-{lo}|{sub}"] = r
    out["contrasts_dPyes_[mean,lo,hi,n]"] = con
    men = defaultdict(list)
    for iid, t in think.items():
        cue = ITEMS[iid]["cue"]
        if cue in CUE_WORDS:
            men[f"{ITEMS[iid]['task']}|{cue}"].append(bool(re.search(CUE_WORDS[cue], t, re.I)))
    out["cue_mentioned_in_reasoning"] = {k: round(sum(x) / len(x), 3) for k, x in sorted(men.items())}
    return out


if __name__ == "__main__":
    print(json.dumps({p: score(p) for p in sys.argv[1:]}, indent=1))
