"""Hardship (need) control on the ABAWD cells of the one leak (2026-10-08, blind-review round 4; pre-registered reading rule in
docs/decisions.md). For Qwen3-32B-AWQ: car-sentence verdicts from the queue-6 runs vs the baseline / fired / blameless verdicts of
the matching existing run (same seed, same prompt, same answer order), on the four non-trap 72-hour cells and on all non-trap cells.
Prints up/down flip counts (up = sentence YES, baseline NO) and applies the rule:
  (i)  car down-flips >= fired down-flips at both seeds            -> "hardship/valence sentence effect"
  (ii) |car up - car down| <= 3 at each seed while fired asymmetric -> "deservingness reading stands"
  (iii) otherwise                                                   -> "not separable"
Usage: python src/eval/score_abawd_hardship.py  (writes results/rules_think/abawd_hardship_summary.json)"""
import json, pathlib, sys
import pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src/eval")); sys.path.insert(0, str(ROOT / "src/run"))
from score_common_scale import gen_verdicts  # noqa: E402
from run_rules_think import subsample  # noqa: E402

RUNS = {  # tag: (existing run with none/fired/blameless, new run with the car sentence)
    "off_s0": ("results/rules_think/qwen3-32b-awq_off.jsonl", "results/rules_think/qwen3-32b-awq_off_abawd_hardship.jsonl"),
    "off_s1": ("results/rules_think/qwen3-32b-awq_off_s1.jsonl", "results/rules_think/qwen3-32b-awq_off_s1_abawd_hardship.jsonl"),
    "on_s0": ("results/rules_think/qwen3-32b-awq.jsonl", "results/rules_think/qwen3-32b-awq_abawd_hardship.jsonl"),
}


def items():
    rows = [json.loads(l) for l in open(ROOT / "data/rules_pilot/pilot_plus_abawd_hardship.jsonl")]
    sub = {r["item_id"] for r, _ in subsample(rows)}
    d = pd.DataFrame([{k: v for k, v in r.items() if k not in ("text", "facts")} for r in rows])
    d = d[d.item_id.isin(sub) & (d.task == "abawd") & (d.status != "child_15_trap")].copy()
    d["cell"] = d.status.astype(str) + "|" + d.hours.astype(str)
    return d


def updown(d, v, cue, ref="none"):
    x = d.copy(); x["v"] = x.item_id.map(v)
    a = x[x.cue == cue].set_index(["base", "cell"]).v; b = x[x.cue == ref].set_index(["base", "cell"]).v
    j = pd.concat([a, b], axis=1, keys=["a", "b"]).dropna()
    return int(((j.a == "YES") & (j.b == "NO")).sum()), int(((j.a == "NO") & (j.b == "YES")).sum()), int(len(j))


def main():
    d = items(); out = {}
    for tag, (old, new) in RUNS.items():
        if not (ROOT / new).exists():
            continue
        v = gen_verdicts(ROOT / old); v.update(gen_verdicts(ROOT / new))
        inv = sum(1 for r in map(json.loads, open(ROOT / new)) if r["verdict"] not in ("YES", "NO"))
        out[tag] = {"invalid_car": inv}
        for scope, dd in (("72h_nontrap", d[d.hours == 72]), ("all_nontrap", d)):
            out[tag][scope] = {c: updown(dd, v, c) for c in ("valence_neg", "control_low", "control_high", "effort_low", "effort_high")}
            out[tag][scope]["control_high-control_low"] = updown(dd, v, "control_high", "control_low")
            out[tag][scope]["control_high-valence_neg"] = updown(dd, v, "control_high", "valence_neg")
            out[tag][scope]["control_low-valence_neg"] = updown(dd, v, "control_low", "valence_neg")
    # reading rule on the four non-trap 72h cells, thinking-off seeds
    if all(t in out for t in ("off_s0", "off_s1")):
        car = [out[t]["72h_nontrap"]["valence_neg"] for t in ("off_s0", "off_s1")]
        fired = [out[t]["72h_nontrap"]["control_low"] for t in ("off_s0", "off_s1")]
        if all(c[1] >= f[1] for c, f in zip(car, fired)):
            verdict = "(i) hardship/valence sentence effect: the car sentence lowers YES at least as often as the fired sentence at both seeds"
        elif all(abs(c[0] - c[1]) <= 3 for c in car) and all(f[1] - f[0] >= 3 for f in fired):
            verdict = "(ii) deservingness reading stands: the car sentence is symmetric while the fired sentence is asymmetric at both seeds"
        else:
            verdict = "(iii) not separable"
        out["reading_rule"] = dict(car_up_down=car, fired_up_down=fired, verdict=verdict)
    json.dump(out, open(ROOT / "results/rules_think/abawd_hardship_summary.json", "w"), indent=1)
    for tag in out:
        if tag == "reading_rule":
            print("READING RULE:", json.dumps(out[tag])); continue
        print(f"== {tag} (INVALID car outputs: {out[tag]['invalid_car']})")
        for scope in ("72h_nontrap", "all_nontrap"):
            print(f"  {scope}: " + "; ".join(f"{k} {v[0]}/{v[1]} (n {v[2]})" for k, v in out[tag][scope].items()))


if __name__ == "__main__":
    main()
