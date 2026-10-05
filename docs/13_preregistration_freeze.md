# Design C: NLP contribution, hypotheses, and freeze (2026-10-05)

Written after review of 370c219 (pasted by the user). That review's warning is adopted as a rule: **no more task
changes to chase an effect.** From here only measurement fixes are allowed, and each is logged in decisions.md.

## Where the novelty is (NLP, not welfare politics)
Welfare is the domain because the law supplies ground truth on which facts a decision may use. The contribution
claims are about language models:
1. **Boundary-conditioned feature use.** The same social cue (job-search effort, controllability of job loss) is
   (a) excluded by computation (rule-bound decisions), (b) permitted by an open discretionary standard, or
   (c) explicitly prohibited by the standard's text. Test: does the model's use of the cue follow the boundary
   that the text sets? Prior work tests invariance to irrelevant changes or sensitivity to relevant ones
   (Kearney et al. 2025; LexGuard, Chen et al. 2026 for the two-sided version). Here the SAME cue switches between
   permitted and prohibited only through the instruction text, so following the boundary is the measured skill.
2. **Psychometric measurement in task units.** Decision boundary (PSE) in dollars of monthly shortfall; a cue's
   effect is the PSE shift in dollars. This avoids tail log-odds effects that change no decision (docs/11, Result 1).
3. **Inference protocol ladder.** First-token direct answer / same step-by-step prompt with thinking off /
   thinking on (+ a second seed) / gpt-oss reasoning. Claims stay at "the protocols differ" unless the ladder
   isolates the step (review of 370c219, point 3).
4. **Faithfulness of exclusion.** When a prohibited cue moves the decision, does the reasoning cite it?

## Task set (frozen)
- Rule-bound reference: rules pilot (docs/10), already run.
- data/design_c_psych: discretion psychometric set (3 leniency x prohibit no/yes x 8 shortfall levels x 6 cues x 2 polarities x 20 bases).
- data/design_c_v2: enum standards (gold, competence check), open/open_need, and missing work-program hours (gold REQUEST).
- Packet configs/rule_packet_fy2026_c.md; standards worded "grants if, and only if"; question "Under these rules, does the agency grant/deny ...".

## Hypotheses (primary)
- H1 (permission): under the open standard, effort hi - lo shifts the PSE (dollars) in thinking mode.
- H2 (boundary following): the H1 shift is smaller under the prohibition than without it. A model that follows the
  boundary shows shift(prohibit) ~ 0; we report shift(prohibit) / shift(no prohibition).
- H3 (missing facts): with work-program hours missing, a low-effort cue lowers P(REQUEST) and raises P(deny).
Secondary / exploratory: controllability, leniency levels, scale, protocol ladder, CoT citation of the cue,
polarity gap, noise floor (name/order edits, seed).

## Analysis
- Primary unit: thinking-mode verdicts; first-token log-odds reported as secondary.
- Cluster bootstrap over bases (1,000-2,000 resamples). Primary family H1-H3 per model: Holm. Exploratory: BH-FDR 0.05.
- A null for H1 under thinking is a reportable result ("reasoning models do not use the cue even where permitted"),
  and the paper is then about boundary-following when cues are permitted vs prohibited at the first-token level
  and in missing-fact cases.

## Pre-set measurement-fix rule (2026-10-05, before any thinking result was read)
See decisions.md, same date. Read 30 stratified CoTs from qwen3-14b__on_s0 before scoring. Only if there is no need
slope AND >= 10/30 CoTs treat the caseworker's judgment as a missing fact, apply exactly one fix (judge-role line in
the packet), rerun 14B on_s0, and report both versions. Otherwise no change.
