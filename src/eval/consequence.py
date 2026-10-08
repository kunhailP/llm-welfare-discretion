"""Consequence analysis for Paper 1 (2026-10-08): what a cue effect means on a synthetic caseload.

Caseload: the 40 pilot bases. Primary weighting = equal (the bases were sampled in proportion to the QC household-size
strata, so the equal-weight mean is size-stratified); secondary = HWGT of the source SNAP QC FY2024 record
(data/rules_pilot/pilot_bases_hwgt.json), reported as robustness because 40 weights with a 800x range make it unstable.
Incomes were moved to chosen margins (-15/-4/+4/+15 %) of the net limit, so the
caseload is "near-threshold applicants with the QC household-structure mix", not the applicant population; rates are per
100k cases of that stated caseload. Task: income eligibility (elig), narrative style, the set both readouts cover.

For each model and readout (first-token both orders, thinking off; generated verdict, thinking on) and each paired cue
contrast (controllability hi-lo, effort hi-lo), reports with base-clustered bootstrap CIs:
  gap_pp        weighted P(YES | hi) - P(YES | lo) in percentage points: the spurious "group" eligibility-rate gap an
                audit would report between applicants who differ only in the cue;
  changed_100k  weighted share of paired cases whose verdict differs between hi and lo, per 100k;
  wd_100k_{hi,lo}  weighted wrongful denials (gold YES -> NO) per 100k under each cue.
Usage: python src/eval/consequence.py --models qwen3-8b ministral3-8b qwen3-14b qwen3-32b-awq
"""
import argparse, json, pathlib
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[2]
PAIRS = {"control": ("control_high", "control_low"), "effort": ("effort_high", "effort_low")}


def items():
    d = pd.read_json(ROOT / "data/rules_pilot/pilot.jsonl", lines=True).drop(columns=["text", "facts"])
    w = json.load(open(ROOT / "data/rules_pilot/pilot_bases_hwgt.json"))
    d = d[(d.task == "elig") & (d.style == "narrative")].copy()
    d["w"] = d.base.map(lambda b: w[b]["hwgt"])
    return d


def firsttoken_verdicts(model, d):
    r = pd.read_json(ROOT / f"results/rules_pilot/{model}.jsonl", lines=True)
    r = r[r.item_id.isin(d.item_id)]
    r["p"] = np.where(r.lp_yes.isna() | r.lp_no.isna(), np.nan, 1 / (1 + np.exp(r.lp_no - r.lp_yes)))
    p = r.groupby("item_id").p.mean()          # NaN if either order missing
    return p.map(lambda x: "MISSING" if pd.isna(x) else ("YES" if x > 0.5 else "NO"))


def thinking_verdicts(path, d):
    r = pd.read_json(path, lines=True)
    r = r[r.item_id.isin(d.item_id)].set_index("item_id").verdict
    return r.where(r.isin(["YES", "NO"]), "MISSING")


def wmean(x, w):
    return float(np.sum(x * w) / np.sum(w))


def boot(df, f, n=2000, seed=0):
    bases = df.base.unique(); g = {b: df[df.base == b] for b in bases}
    rng = np.random.default_rng(seed)
    vals = [f(pd.concat([g[b] for b in rng.choice(bases, len(bases))])) for _ in range(n)]
    return [round(f(df), 2), *np.round(np.percentile(vals, [2.5, 97.5]), 2).tolist()]


def analyse(d, verdict, weighting="equal"):
    d = d.copy(); d["pred"] = d.item_id.map(verdict)
    if weighting == "equal":
        d["w"] = 1.0
    d = d[d.pred != "MISSING"]
    out = {}
    for name, (hi, lo) in PAIRS.items():
        key = ["base", "margin"]
        h = d[d.cue == hi].set_index(key)[["pred", "gold", "w"]]
        l = d[d.cue == lo].set_index(key)[["pred", "gold"]].rename(columns={"pred": "pred_lo", "gold": "gold_lo"})
        j = h.join(l, how="inner").reset_index()
        j["yes_hi"] = (j.pred == "YES").astype(float); j["yes_lo"] = (j.pred_lo == "YES").astype(float)
        j["changed"] = (j.pred != j.pred_lo).astype(float)
        j["wd_hi"] = ((j.gold == "YES") & (j.pred == "NO")).astype(float)
        j["wd_lo"] = ((j.gold == "YES") & (j.pred_lo == "NO")).astype(float)
        out[name] = dict(
            n_pairs=int(len(j)), n_bases=int(j.base.nunique()),
            gap_pp=boot(j, lambda t: 100 * (wmean(t.yes_hi, t.w) - wmean(t.yes_lo, t.w))),
            changed_100k=boot(j, lambda t: 1e5 * wmean(t.changed, t.w)),
            wd_100k_hi=boot(j, lambda t: 1e5 * wmean(t.wd_hi, t.w)),
            wd_100k_lo=boot(j, lambda t: 1e5 * wmean(t.wd_lo, t.w)),
            unweighted_gap_pp=round(100 * float(j.yes_hi.mean() - j.yes_lo.mean()), 2))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=["qwen3-8b", "ministral3-8b", "qwen3-14b", "qwen3-32b-awq"])
    ap.add_argument("--out", default="results/consequence/elig_narrative.json")
    a = ap.parse_args()
    d = items()
    res = {"caseload": dict(bases=int(d.base.nunique()), items=int(len(d)), task="elig", style="narrative",
                            weight="HWGT of the source QC FY2024 household", note="near-threshold synthetic caseload")}
    for m in a.models:
        readouts = {"first_token": firsttoken_verdicts(m, d)}
        for tag, suffix in (("thinking_s0", ""), ("thinking_s1", "_s1"), ("thinking_off", "_off")):
            p = ROOT / f"results/rules_think/{m}{suffix}.jsonl"
            if p.exists():
                readouts[tag] = thinking_verdicts(p, d)
        res[m] = {ro: dict(equal=analyse(d, v, "equal"), hwgt=analyse(d, v, "hwgt")) for ro, v in readouts.items()}
    out = ROOT / a.out; out.parent.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(out, "w"), indent=1)
    rows = ["| model | readout | contrast | gap pp [95% CI] | verdicts changed /100k [CI] | wrongful denials /100k (hi / lo) | HWGT-weighted gap pp [CI] |",
            "| --- | --- | --- | --- | --- | --- | --- |"]
    for m in a.models:
        for ro, v in res[m].items():
            for c in PAIRS:
                x, y = v["equal"][c], v["hwgt"][c]
                rows.append(f"| {m} | {ro} | {c} | {x['gap_pp'][0]:+.1f} [{x['gap_pp'][1]:+.1f}, {x['gap_pp'][2]:+.1f}] | "
                            f"{x['changed_100k'][0]:,.0f} [{x['changed_100k'][1]:,.0f}, {x['changed_100k'][2]:,.0f}] | "
                            f"{x['wd_100k_hi'][0]:,.0f} / {x['wd_100k_lo'][0]:,.0f} | "
                            f"{y['gap_pp'][0]:+.1f} [{y['gap_pp'][1]:+.1f}, {y['gap_pp'][2]:+.1f}] |")
    (out.with_suffix(".md")).write_text("\n".join(rows) + "\n")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
