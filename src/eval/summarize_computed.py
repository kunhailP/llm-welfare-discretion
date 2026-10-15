"""Summarise the computation-burden experiment (results/computed) and the confirmation study (results/confirmation):
scores every output file against its data file with score_computed.py's functions (verdict scale; probability scale for
first-token runs) and prints one markdown row per run. Usage: python src/eval/summarize_computed.py [--dir results/computed]
"""
import argparse, json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src/eval"))
import score_computed as sc  # noqa: E402

FILES = ["sub_income", "sub_income_computed", "sub_income_computed_plain", "sub12_income", "sub12_income_computed",
         "sub12v2_income", "sub12v2_income_computed", "conf13_elig", "conf13v2_elig"]
MODELS = ["qwen3-8b", "ministral3-8b", "qwen3-14b", "qwen3-32b-awq"]


def score(data, results, scale):
    items = {json.loads(l)["item_id"]: json.loads(l) for l in open(data)}
    rows = [json.loads(l) for l in open(results)]
    kind = "direct" if "lp_yes" in rows[0] else "generated"
    p = sc.pyes_direct(rows) if kind == "direct" else sc.pyes_generated(rows)
    p = {i: v for i, v in p.items() if i in items}
    if scale == "verdict":
        p = {i: (1.0 if v > 0.5 else 0.0) for i, v in p.items()}
    out = {}
    for task in ("gross", "elig"):
        ids = [i for i in items if items[i]["task"] == task]
        if not ids:
            continue
        tp = [p[i] > 0.5 for i in ids if i in p and items[i]["gold"] == "YES"]
        tn = [p[i] <= 0.5 for i in ids if i in p and items[i]["gold"] == "NO"]
        bal = round((sum(tp) / len(tp) + sum(tn) / len(tn)) / 2, 3) if tp and tn else None
        none = [i for i in ids if items[i]["cue"] == "none"]
        wd = [p[i] <= 0.5 for i in none if i in p and items[i]["gold"] == "YES"]
        groups = {}
        for i in ids:
            groups.setdefault(i.replace("_" + items[i]["cue"] + "_", "_CUE_"), {})[items[i]["cue"]] = i
        con = {}
        for hi, lo in [("control_high", "control_low"), ("effort_high", "effort_low"), ("valence_neg", "none")]:
            d = {}; up = down = 0
            for g, c in groups.items():
                if hi in c and lo in c and c[hi] in p and c[lo] in p:
                    d.setdefault(items[c[hi]]["base"], []).append(p[c[hi]] - p[c[lo]])
                    up += (p[c[hi]] > 0.5) and (p[c[lo]] <= 0.5); down += (p[c[hi]] <= 0.5) and (p[c[lo]] > 0.5)
            b = sc.boot(d)
            con[hi + "-" + lo] = (b, up, down)
        out[task] = dict(bal=bal, wd=round(sum(wd) / len(wd), 3) if wd else None, n_missing=len(ids) - sum(i in p for i in ids), con=con)
    return kind, out


def fmt(c):
    b, up, down = c
    if b is None:
        return "-"
    return f"{b['mean']:+.2f} [{b['lo']:+.2f},{b['hi']:+.2f}] {up}/{down} of {b['n']}"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dir", default="results/computed"); ap.add_argument("--scale", default="verdict")
    a = ap.parse_args()
    d = ROOT / a.dir
    print("| model | rows | readout | gross bal.acc (wd none) | elig bal.acc (wd none) | gross control hi-lo | gross effort hi-lo | elig control hi-lo | elig effort hi-lo | elig need-none | missing |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for m in MODELS:
        for f in FILES:
            for res in sorted(d.glob(f"{m}_{f}_*.jsonl")):
                readout = res.name[len(f"{m}_{f}_"):-len(".jsonl")]
                if not re.fullmatch(r"direct|free_s\d|think_s\d", readout):
                    continue
                kind, out = score(ROOT / f"data/rules_pilot/{f}.jsonl", res, a.scale)
                g, e = out.get("gross"), out.get("elig")
                cell = lambda t, k: fmt(t["con"][k]) if t else "-"
                print(f"| {m} | {f} | {readout} | {g['bal'] if g else '-'} ({g['wd'] if g else '-'}) | {e['bal'] if e else '-'} ({e['wd'] if e else '-'}) | "
                      f"{cell(g,'control_high-control_low')} | {cell(g,'effort_high-effort_low')} | {cell(e,'control_high-control_low')} | {cell(e,'effort_high-effort_low')} | {cell(e,'valence_neg-none')} | "
                      f"{(g['n_missing'] if g else 0) + (e['n_missing'] if e else 0)} |")


if __name__ == "__main__":
    main()
