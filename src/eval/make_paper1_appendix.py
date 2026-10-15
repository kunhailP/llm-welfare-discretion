"""Generate paper/appendix_tables.tex from docs/paper1/tables.md.
Run after make_paper1_tables.py. Markdown tables -> LaTeX tabular (booktabs, at natural width)."""
import pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[2]
MD = (ROOT / "docs/paper1/tables.md").read_text().split("\n")

def esc(s):
    return s.replace("\\", "").replace("%", "\\%").replace("_", "\\_").replace("&", "\\&").replace("|", "$\\mid$").replace("<=", "$\\le$").replace("->", "$\\to$")

def has_section(title_prefix):
    return any(l.startswith("## " + title_prefix) for l in MD)


def section(title_prefix):
    start = next(i for i, l in enumerate(MD) if l.startswith("## " + title_prefix))
    rows, notes = [], []
    for l in MD[start + 1:]:
        if l.startswith("## "):
            break
        if l.startswith("|"):
            l = l.replace("abawd|all", "abawd (all)").replace("abawd|no_trap", "abawd (no trap)")
            rows.append([c.strip() for c in l.strip().strip("|").split("|")])
        elif l.strip():
            notes.append(l.strip())
    return rows, notes

def tabular(rows, caption, label, width="\\textwidth", font="\\scriptsize", max_rows=38):
    """One table* per chunk of at most max_rows body rows, natural width (no \resizebox: 2026-10-12,
    'tables shrunk to 5.4-6.2pt, float too large'); the first chunk carries the label, later ones say (continued)."""
    rows = [r for r in rows if not all(set(c) <= set("-: ") for c in r)]
    head, body = rows[0], rows[1:]
    if sum(len(c) for c in head) > 110:   # header too wide at natural width: abbreviate the task triples, say so in the caption
        head = [c.replace("gross / elig / ABAWD", "g / e / A") for c in head]
        caption += " Column triples are gross / eligibility / ABAWD."
    cols = "l" * len(head)
    out = []
    chunks = [body[k:k + max_rows] for k in range(0, len(body), max_rows)] or [[]]
    for ci, chunk in enumerate(chunks):
        cap = caption if ci == 0 else f"(continued, {ci + 1} of {len(chunks)}) " + caption.split(":")[0] + "."
        out += [f"\\begin{{table*}}[t]\\centering{font}\\setlength{{\\tabcolsep}}{{3pt}}", f"\\begin{{tabular}}{{{cols}}}", "\\toprule",
                " & ".join(esc(c) for c in head) + " \\\\", "\\midrule"]
        out += [" & ".join(esc(c) for c in r) + " \\\\" for r in chunk]
        out += ["\\bottomrule", "\\end{tabular}", f"\\caption{{{cap}}}", f"\\label{{{label}{'' if ci == 0 else '-' + str(ci + 1)}}}", "\\end{table*}", ""]
    return "\n".join(out)

parts = []
r, n = section("T2.")
parts.append(tabular(r, "Direct readout, probability scale: paired deservingness contrasts, $\\Delta$P(YES) high minus low, 95\\% household-clustered bootstrap CI, all 6,376 items. " + esc(" ".join(n)), "tab:t2"))
r, n = section("T8.")
parts.append(tabular(r, "Both readouts on the verdict scale (1,554-item narrative subsample): paired high-minus-low verdict differences with clustered CIs, flips per pair, and the largest flip rate consistent with an observed zero (rule of three per item; $1-0.05^{1/n_h}$ per household). Readouts: direct = first-token; think = step-by-step with thinking on (s0, s1 = seeds; greedy = $T=0$); off = same prompt, thinking off.", "tab:t8"))
r, n = section("T7.")
parts.append(tabular(r, "Noise floor: verdict agreement between runs on all items, flip rate on cue-free items, and accuracy of the second run.", "tab:t7"))
r, n = section("T9.")
parts.append(tabular(r, "Sanction check: direct-readout paired contrasts (P(YES), clustered CI) with the original packet and with the packet line stating that the reason for a past job loss triggers no sanction.", "tab:t9"))
r, n = section("T6.")
parts.append(tabular(r, "Consequence on the eligibility caseload (27 households, 74 cue pairs, equal pair weights): spurious eligibility-rate gap, verdicts changed, wrongful denials per 100k paired cases under each cue, and the survey-weighted gap.", "tab:t6"))
if has_section("T10."):
    r, n = section("T10.")
    parts.append(tabular(r, "Computation-burden experiment, verdict scale: balanced accuracy and paired contrasts with the case file as in the paper (original), with the block of correct intermediate quantities appended (+ block), the same block without the authority wording (+ plain block), and on new households (s12 = seed 12) under the paper's cue phrasing (v1) and a second phrasing (v2). Eligibility contrasts: high minus low verdict difference, 95\\% household-clustered CI, flips toward YES / toward NO; g. ctrl, g. eff. = the gross controllability and effort contrasts as flips; pairs = gross/eligibility pairs scored; miss. = rows dropped for want of a YES/NO token (direct) or a parsable verdict (free).", "tab:t10"))
if has_section("T11."):
    r, n = section("T11.")
    parts.append(tabular(r, "Confirmation study on 128 new households (seed 13; eligibility; 353 pairs per contrast; verdict scale). Primary rung: free generation, seeds 0 and 1, phrasing v1; a contrast is a leak if its household-clustered 95\\% CI excludes zero at both seeds. Household-level bound on an observed zero: $1-0.05^{1/128} = 0.023$. Direct and v2 rows are secondary.", "tab:t11"))
if has_section("T12."):
    r, n = section("T12.")
    parts.append(tabular(r, "Change of each paired cue contrast when the computation block is supplied (verdict scale; the pairs scored in both files): before and after are the mean high-minus-low verdict differences; change is the per-pair difference, after minus before, with its 95\\% household-clustered bootstrap CI. An interval reaching zero means the observed removal (Table~\\ref{tab:t10}) is not a precise estimate of the decrease. s12 = seed-12 households; plain block = the block without the authority wording.", "tab:t12"))
(ROOT / "paper").mkdir(exist_ok=True)   # the anonymised release ships no paper/ folder
(ROOT / "paper/appendix_tables.tex").write_text("% generated by src/eval/make_paper1_appendix.py; do not edit\n" + "\n".join(parts))
print("wrote paper/appendix_tables.tex")
