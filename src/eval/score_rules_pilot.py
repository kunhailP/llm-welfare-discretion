"""Score the Design-B pilot (results/rules_pilot/<model>.jsonl against data/rules_pilot/pilot.jsonl).

Per item and answer order: P(YES) = softmax over {YES, NO} first-token log-probs. If YES or NO is missing
from the top-20 for an order, that order is MISSING (never imputed; revised 2026-10-05 after review_092727e,
which showed the old -30 fill turned double-missing rows into NO). Combined verdict = YES if the mean P(YES)
over both orders > 0.5, computed only when both orders are present; otherwise the item is MISSING and is
excluded from accuracy and reported as a count. Per-order verdicts are reported separately as well.
Input integrity is asserted: each item has exactly one row per order, no duplicates, no unknown ids.

Reports (per model):
- accuracy by task x margin (income tasks) and task x status x hours (ABAWD), split by style;
- error direction: wrongful denial (gold YES -> NO) vs wrongful approval (gold NO -> YES);
- cue effect = P(YES | cue) - P(YES | none), same base/task/margin/status/hours/style; base-clustered
  bootstrap CI; plus verdict flip rate vs none. All cues here are legally irrelevant ("should not change");
- hours effect (ABAWD, nonexempt): P(YES | 88h) - P(YES | 72h) -> "should change" (gold flips NO -> YES);
- exemption recognition: accuracy on exempt statuses at 72h, by cue.

Usage: python src/eval/score_rules_pilot.py --results results/rules_pilot/qwen3-8b.jsonl [...]
"""
import argparse, json
import numpy as np
import pandas as pd

DATA = "data/rules_pilot/pilot.jsonl"


def boot(df, f, n=1000, seed=0):
    g = {k: v for k, v in df.groupby("base")}
    keys = list(g)
    rng = np.random.default_rng(seed)
    vals = [f(pd.concat([g[k] for k in rng.choice(keys, len(keys))])) for _ in range(n)]
    return [round(float(f(df)), 4), *np.round(np.percentile(vals, [2.5, 97.5]), 4).tolist()]


def load(path, items):
    r = pd.read_json(path, lines=True)
    dup = r.duplicated(["model", "item_id", "order"]).sum()
    unknown = set(r.item_id) - set(items.item_id)
    per = r.groupby(["model", "item_id"]).order.nunique()
    assert dup == 0 and not unknown, f"{path}: {dup} duplicate rows, {len(unknown)} unknown ids"
    assert (per == 2).all() and per.groupby("model").size().eq(len(items)).all(), f"{path}: incomplete orders/items"
    r["missing"] = r.lp_yes.isna() | r.lp_no.isna()
    r["p_yes"] = np.where(r.missing, np.nan, 1 / (1 + np.exp(r.lp_no - r.lp_yes)))
    g = r.greedy.fillna("").str.strip().str.upper()
    r["greedy_valid"] = g.isin(["YES", "NO"])
    r["greedy_agree"] = r.greedy_valid & (g == np.where(r.p_yes > 0.5, "YES", "NO")) & ~r.missing
    p = r.groupby(["model", "item_id"]).agg(p_yes=("p_yes", "mean"), n_missing=("missing", "sum")).reset_index()
    p.loc[p.n_missing > 0, "p_yes"] = np.nan
    d = p.merge(items, on="item_id", validate="m:1")
    d["pred"] = np.where(d.p_yes.isna(), "MISSING", np.where(d.p_yes > 0.5, "YES", "NO"))
    d["ok"] = d.pred == d.gold
    ro = r.merge(items[["item_id", "gold", "task"]], on="item_id")
    ro["pred"] = np.where(ro.missing, "MISSING", np.where(ro.p_yes > 0.5, "YES", "NO"))
    return d, ro


def abawd_2x2(ab):
    """Exemption x hours (paid work and income fixed; only approved work-program hours vary).
    Gold: non-exempt 72 NO / 88 YES (should change); exempt 72 YES / 88 YES (should not change).
    Per base x cue x style x exempt status s, paired with the same base's non-exempt cells:
      interaction = (P88 - P72 | non-exempt) - (P88 - P72 | s); gold value 1
      correct_switch = non-exempt verdicts go NO -> YES
      all4 = all four cells correct."""
    k = ["base", "cue", "style"]
    w = ab.pivot_table(index=k + ["status"], columns="hours", values=["p_yes", "ok"], aggfunc="first")
    w.columns = [f"{a}{int(b)}" for a, b in w.columns]   # hours is float (NaN on income rows)
    w = w.reset_index()
    ne = w[w.status == "nonexempt"].set_index(k)
    rows = []
    for s in ("pregnant", "child_under_14", "medical"):
        e = w[w.status == s].set_index(k)
        j = ne.join(e, lsuffix="_ne", rsuffix="_ex", how="inner").reset_index()
        j["exempt_status"] = s
        rows.append(j)
    j = pd.concat(rows)
    j["interaction"] = (j.p_yes88_ne - j.p_yes72_ne) - (j.p_yes88_ex - j.p_yes72_ex)
    j["correct_switch"] = (j.ok72_ne.astype(bool) & j.ok88_ne.astype(bool)).astype(float)
    j["all4"] = j[["ok72_ne", "ok88_ne", "ok72_ex", "ok88_ex"]].astype(bool).all(axis=1).astype(float)
    out = {}
    for cue, c in j.groupby("cue"):
        c = c.dropna(subset=["interaction"])
        out[cue] = dict(interaction=boot(c, lambda t: t.interaction.mean()),
                        correct_switch=boot(c, lambda t: t.correct_switch.mean()),
                        all4=boot(c, lambda t: t.all4.mean()), n=int(len(c)))
    # cue effect on the 2x2 (should be 0): cue minus none, paired by base x style x exempt status
    kk = ["base", "style", "exempt_status"]
    b0 = j[j.cue == "none"].set_index(kk)[["interaction", "all4"]]
    x = j[j.cue != "none"].join(b0, on=kk, rsuffix="_none")
    x["d_inter"] = x.interaction - x.interaction_none
    x["d_all4"] = x.all4 - x.all4_none
    for cue, c in x.groupby("cue"):
        c = c.dropna(subset=["d_inter"])
        out[f"{cue}_minus_none"] = dict(d_interaction=boot(c, lambda t: t.d_inter.mean()),
                                        d_all4=boot(c, lambda t: t.d_all4.mean()), n=int(len(c)))
    return out


def summarize(d, ro=None):
    out = {}
    out["integrity"] = dict(items=int(len(d)), items_missing=int((d.pred == "MISSING").sum()),
                            order_rows_missing=int(ro.missing.sum()) if ro is not None else None,
                            greedy_invalid_rate=round(float(1 - ro.greedy_valid.mean()), 4) if ro is not None else None,
                            greedy_agree_rate=round(float(ro.greedy_agree.mean()), 4) if ro is not None else None)
    if ro is not None:
        out["accuracy_by_order"] = {f"{t}|{o}": round(float(v), 3) for (t, o), v in
                                    (ro.pred == ro.gold).groupby([ro.task, ro.order]).mean().items()}
    d = d[d.pred != "MISSING"]          # all metrics below exclude MISSING items (counted in integrity)
    out["balanced_accuracy"] = {t: round(float(g.groupby("gold").ok.mean().mean()), 3) for t, g in d.groupby("task")}
    out["yes_rate_vs_gold"] = {t: [round(float((g.pred == "YES").mean()), 3), round(float((g.gold == "YES").mean()), 3)]
                               for t, g in d.groupby("task")}
    inc = d[d.task != "abawd"]
    ab = d[d.task == "abawd"]
    out["accuracy_income"] = {f"{t}|{m:+.2f}|{s}": round(float(v), 3) for (t, m, s), v in
                              inc.groupby(["task", "margin", "style"]).ok.mean().items()}
    out["accuracy_abawd"] = {f"{st}|{h}|{s}": round(float(v), 3) for (st, h, s), v in
                             ab.groupby(["status", "hours", "style"]).ok.mean().items()}
    err = d[~d.ok]
    out["errors"] = dict(n=int(len(err)),
                         wrongful_denial=int(((err.gold == "YES") & (err.pred == "NO")).sum()),
                         wrongful_approval=int(((err.gold == "NO") & (err.pred == "YES")).sum()))
    # cue effects (all legally irrelevant)
    keys_inc = ["base", "task", "margin", "style"]
    keys_ab = ["base", "task", "status", "hours", "style"]
    eff = {}
    for name, sub, keys in (("income", inc, keys_inc), ("abawd", ab, keys_ab)):
        base = sub[sub.cue == "none"].set_index(keys)[["p_yes", "pred"]].rename(columns={"p_yes": "p0", "pred": "v0"})
        x = sub[sub.cue != "none"].join(base, on=keys)
        x["dp"] = x.p_yes - x.p0
        x["flip"] = (x.pred != x.v0).astype(float)
        for cue, c in x.groupby("cue"):
            eff[f"{name}|{cue}"] = dict(dP_yes=boot(c, lambda t: t.dp.mean()),
                                        flip_rate=round(float(c.flip.mean()), 4), n=int(len(c)))
    out["cue_effects_should_not_change"] = eff
    # hours effect (should change) for non-exempt
    ne = ab[ab.status.isin(["nonexempt", "child_15_trap"])]
    piv = ne.pivot_table(index=["base", "status", "cue", "style"], columns="hours", values="p_yes").reset_index()
    piv["base"] = piv["base"]
    out["hours_effect_should_change"] = {st: boot(g, lambda t: (t[88] - t[72]).mean())
                                         for st, g in piv.groupby("status")}
    ex = ab[(ab.status.isin(["pregnant", "child_under_14", "medical"])) & (ab.hours == 72)]
    out["exemption_recognition_72h"] = {cue: round(float(g.ok.mean()), 3) for cue, g in ex.groupby("cue")}
    out["exemption_recognition_by_status_cue"] = {f"{s}|{c}": round(float(v), 3) for (s, c), v in
                                                  ex.groupby(["status", "cue"]).ok.mean().items()}
    out["abawd_exemption_x_hours"] = abawd_2x2(ab)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", action="append", required=True)
    ap.add_argument("--data", default=DATA)
    a = ap.parse_args()
    items = pd.read_json(a.data, lines=True)
    items = items.drop(columns=["text", "facts"])
    res = {}
    for path in a.results:
        d, ro = load(path, items)
        for m, g in d.groupby("model"):
            res[m] = summarize(g, ro[ro.model == m])
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
