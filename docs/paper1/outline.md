# Paper 1 outline (NAACL 2027 via ARR Oct 2026): draft v0, 2026-10-08

Tables: docs/paper1/tables.md (generated; regenerate with `python src/eval/make_paper1_tables.py`).
Form: short paper (4 pages + references + appendix). Every number below is from the tables or docs/results/design_B_rules_pilot.md.

## Working titles
- Where Deservingness Leaks: Direct and Reasoning Verdicts of LLMs on Rule-Computable Welfare Determinations
- Reading the Verdict Right: First-Token Audits Mismeasure LLM Welfare Decisions
- Deservingness Cues Move LLM Welfare Verdicts Only Where the Model Is Not Computing

## Abstract (draft)
LLMs are entering welfare eligibility work. We ask whether legally irrelevant deservingness cues (job-search effort,
controllability of job loss) move their determinations, using a SNAP FY2026 rules-as-code testbed in which the law fixes
which facts a decision may use and gold is computed and cross-checked against PolicyEngine-US. With direct answers
(first-token log-probs, both answer orders), four open models are at chance on income tests, any added sentence moves the
verdict as much as a deservingness cue, and the one consistent signal is a controllability contrast on eligibility
(+0.04 to +0.09, base-clustered CIs exclude 0 in all models). With reasoning, the same models are at ceiling, every paired
cue contrast on income tests is 0 across two seeds, and no residual contrast keeps its sign between seeds; a same-prompt
thinking-off ladder shows that asking for steps removes most of the effect, and that the one directional leak appears where the
model is unstable on the work-requirement exemptions. A polarity
flip (grant? vs deny?) on a discretionary variant shows that pooled first-token numbers can present a yes-bias as a
calibrated judgment. We conclude that audits of LLM benefit decisions must use the readout the deployment uses and
report cue effects only where the model is competent; we release the testbed.

## 1 Introduction (0.75p)
- Hook: P.L. 119-21 expands SNAP work requirements (18-64, child under 14), Medicaid 80 h/month from Jan 2027, states fund
  LLM tools for verification and decision memos (lit/why_now_policy.md, verified items only). USDA warns of bias in
  eligibility determinations.
- Question: do deservingness cues (CARIN control and effort; van Oorschot; Petersen) enter determinations where the rule
  excludes them, and does the answer depend on how the verdict is read out?
- Contributions: (1) a gold-verified SNAP testbed with cue manipulations; (2) the readout result: direct vs reasoning;
  (3) measurement lessons for LLM decision audits (sentence-addition control, paired contrasts, polarity flip).

## 2 Testbed (0.75p)
- Rules: FY2026 federal SNAP, no state options; packet shown to the model (configs/rule_packet_fy2026.md).
- Gold: src/rules/snap.py; cross-check vs PolicyEngine-US 2.24.5 on 500 households (0 mismatches in scope; 29 cases differ
  by $1 from rounding), 9 unit tests; scope limits stated (ABAWD path, some deductions not cross-checked).
- Households: structures sampled from the SNAP QC FY2024 public-use file (40 bases), income rescaled to margins
  -15/-4/+4/+15 % of the decisive limit.
- Tasks: gross test, income eligibility, ABAWD (exemption x 72/88 h, paid work fixed). 6,376 items, structured and narrative.
- Cues: none / effort hi-lo / controllability hi-lo / non-moral negative control; same slot, similar length, no money facts.
- Readouts: (a) first-token P(YES) over both answer orders, thinking off; (b) thinking on, verdict parsed after </think>,
  T=0.6, one seed, 1,554-item stratified subsample.
- Stats: base-clustered bootstrap for every CI; paired hi-lo contrasts are the only interpretable cue effect (T3).

## 3 Results (1.5p)
- 3.1 Competence by readout (T1). Direct: income at chance for all four models; ABAWD heuristics differ by scale
  (14B ignores exemptions; 32B treats a 15-year-old as exempting). Reasoning: gross/elig 1.00 at 14B and 32B, 0.98-1.00
  at 8B; ABAWD errors only in the child-15 trap.
- 3.2 Cue effects by readout (T2). Direct: controllability on eligibility positive in all four models with clustered CIs
  excluding 0; effort inconsistent in sign. Reasoning: 0 on gross and elig for every model and contrast; ABAWD 14B
  control -0.04 [-0.075, -0.007], entirely from the trap cell.
- 3.3 Sentence-addition control (T3). Cue minus none has the same sign and size as the non-moral control within each
  model (negative for 8B/Ministral, positive for 14B/32B): an unpaired audit would report a deservingness effect that is a
  length/attention effect.
- 3.4 Reasoning mentions the cue without using it (T4). effort_low is mentioned in 38-78 % of eligibility traces; it pulls
  the model into an off-question ABAWD check and the income verdict does not change.
- 3.5 Consequence on a synthetic caseload (results/consequence/elig_narrative.md, README there). First-token readout:
  controllability changes 7k-16k verdicts per 100k near-threshold cases (14B / 32B), always toward denying the "fired"
  applicant, +4k-8k wrongful denials per 100k; thinking readout: 0. Flips concentrate in 2-4 of 37 bases (near-tie
  households). Equal base weights primary; HWGT weights as robustness (unstable with 40 bases).
- 3.6 Seed replicate and protocol ladder (docs/results/design_B_rules_pilot.md sections 8-12; T7). Seed 1 on 8B/14B/32B:
  income verdict agreement with seed 0 is 0.975-1.000, cue-free flip rate 0 on elig for every model; no reasoning-mode cue contrast
  keeps its sign across seeds (8B elig effort +0.041 -> -0.041; 14B ABAWD control -0.040 -> +0.007). Thinking off with the same
  step-by-step prompt (14B, 32B): income tests 0.93-1.00 and cue contrasts at the noise floor, so asking for steps does most of
  the work; exemption cells degrade (trap 0.15-0.55, 32B nonexempt 72h 0.83), and there 32B shows the one directional leak in the
  ladder: controllability +0.060 [+0.013, +0.109] on ABAWD, blameless -> wrongful approval, fired -> wrongful denial of an exempt
  pregnant adult (exploratory; one model, one seed).
- 3.7 Polarity flip on a discretionary variant (appendix table from archive/stage2_design_c/docs/design_C_discretion.md,
  Results 2-3). Qwen3-14B answers NO to both "grant?" and "deny?"; pooled P(grant) ~0.49 looks calibrated. Cue "effects"
  reverse sign across polarities (acquiescence). First-token cannot measure a judgment that is not computed.

## 4 Discussion (0.5p)
- Consistent with Posner & Saran (formalism under clear rules) and Soffer et al. (stability inside criteria), now with
  multi-step rules, gold, and a non-reasoning contrast that shows where the leakage reports in the literature come from.
- For audits: use the deployment readout; pair cues; include a non-moral sentence control; flip the polarity.
- What this does not show (hand-off to the follow-up): behaviour when the record is incomplete, open standards, frontier
  models, consequences at caseload level.

## 5 Limitations
One program, federal rules only; four open models <= 32B, one AWQ-quantised; two thinking seeds (noise floor measured once); cue bank is template-based (no paraphrases); the child-15 trap is a checklist-vs-age conflict and may be read as
adversarial; no human baseline; consequence caseload is near-threshold by construction.

## Ethics / Responsible NLP
No real individuals (QC is de-identified; names are placeholders). Public-domain federal data; SNAP QC file not
redistributed. Conflict of interest: none (no Anthropic model used). Intended use: audit methodology, not deployment.

## Appendix
A. Rule packet. B. Cue sentences and item example. C. Full accuracy by cell (both readouts). D. ABAWD exemption x hours
2x2 (interaction, correct switch, all-4-correct; cue minus none). E. Design C first-token polarity results.
F. PolicyEngine cross-check scope.

## To do before 2026-10-12 (no GPU)
1. Write the paper from this outline (LaTeX, ACL template, anonymised).
2. Anonymised release repo: src/rules, src/gen/make_rules_pilot.py, src/run, src/eval, configs, data/rules_pilot, results, tests.
3. Responsible NLP checklist; Limitations section is mandatory.
4. Register all authors as ARR reviewers on submission day (reciprocal reviewing).
5. Decide short vs long (docs/TWO_PAPER_PLAN.md).
GPU (L40, 2026-10-08, all finished): run_paper1_queue.sh (seed 1 on 14B/32B/8B, thinking off on 14B/32B), queue2 (thinking-off seed 1 on 32B/14B), queue3/4 (no-sanction packet x 4 models, 14B greedy, Ministral step-by-step). Nothing queued.
