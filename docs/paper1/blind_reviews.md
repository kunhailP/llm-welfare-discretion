# Blind reviews of paper/main.tex v0 (2026-10-08) and the response plan

Two independent reviewers (fresh agents given only the paper, tables, results notes and code; no author conclusions),
in the ARR form. Scores: R1 (CSS track) Soundness 3 / Excitement 3 / Overall 3 / Confidence 4.
R2 (evaluation & analysis) Soundness 3 / Excitement 3 / Overall 2.5 / Confidence 4.

## Weaknesses both reviewers raised (verified against the tables; all correct)
1. "Exactly 0" overclaims: Table 2 and T2 contain non-zero reasoning contrasts (8B elig effort +.041/-.041; 32B elig control
   -.027 at seed 1; 32B gross control -.017 at seed 0). A zero over 60-74 groups is absence of evidence: rule-of-three bound ~4-5 pp
   at item level, ~7-10 pp per base at cluster level, the size of the direct effects. Must be stated as bounds, not zero.
2. Scale mismatch: direct contrasts were in P(YES), reasoning in binary verdicts. On the verdict scale (results/common_scale/contrasts.md)
   the direct controllability effect is +0.068 [0, +0.186] for 14B elig and -0.167 [-0.298, -0.053] for 14B gross, 0 for 32B gross.
   The "one consistent signal" holds at probability level only; at verdict level the sign is task- and model-specific.
3. Consequence section: wrong N (27 bases, 74 pairs, not 40/37 households); per-100k figures are multiples of 1/74; CIs omitted;
   the baseline wrongful-denial rate under the direct readout (26-54 %) dwarfs the cue delta (4-8k) and must come first; 32B thinking
   seed 1 and 8B thinking are not zero.
4. Sanction confound: "fired for repeatedly missing shifts" may be legally cognisable under voluntary-quit / work-sanction rules; the
   packet was silent. -> configs/rule_packet_fy2026_nosanction.md (one added line) and a direct-readout rerun on all four models (queue 3).
5. Ladder confound: the first rung changes prompt, decoding and extraction at once. -> greedy (T=0) thinking run on 14B (queue 3) isolates
   decoding; the prompt difference is stated as a limitation.
6. Age-15 trap inside ABAWD metrics. -> report ABAWD with and without the trap (common-scale table): without it, reasoning runs have
   0 flips in 120 pairs for 14B and 32B at both seeds.
7. Multiplicity / selective emphasis (14B gross control significantly negative in P(YES); 24 direct contrasts, no correction).
8. Missing citations in text: Pan et al. 2026, Turpin et al. 2023, Chen et al. (LexGuard), first-token vs generated answer
   mismatch literature (Wang et al. 2024). Empty appendices; polarity numbers absent from the supplement; Ministral missing from the ladder
   (-> queue 3 runs Ministral on the step-by-step prompt).
9. Minor: Table 1 mixes balanced and mean cell accuracy; "gross 1.00 for 32B" vs .97; cue sentences contain numbers and assert a job
   loss "last summer" while the file shows current earnings (internal tension, absent in the none / car sentences).

## Response plan (v1 of the paper)
- Reframe the headline: direct verdicts move with cues in a task- and model-specific direction while the model is at chance;
  reasoning verdicts show no flips beyond the measured noise floor, with explicit upper bounds; outside the trap cell, no flips at all.
- Table 2 -> verdict scale for both readouts with clustered CIs and flips/pairs (T8); P(YES) contrasts move to the appendix.
- Add the bound paragraph (rule of three, cluster bound) and the multiplicity note.
- Consequence: N and CIs, baseline first, HWGT instability in Results.
- Sanction, greedy and Ministral results from queue 3 when available; trap-excluded ABAWD everywhere; citations added; appendices filled
  from tables.md and archive/stage2_design_c/docs/design_C_discretion.md (polarity numbers).
- Cue-sentence tension (job loss vs current earnings) is a limitation in this paper and a design fix for the evidence repo.

# Round 3: blind reviews of paper/main.tex v1 (2026-10-08, after queues 2-4) and the response

Two fresh reviewers again (paper, tables T1-T9, results notes 1-17, common_scale, consequence, scorers; no author notes).
R3 (CSS / NLP for policy): Soundness 3 / Excitement 3 / Overall 3.0 / Confidence 4 / Reproducibility 3.
R4 (evaluation & analysis, statistics): Soundness 3 / Excitement 3 / Overall 3.0 / Confidence 4 / Reproducibility 4.
Every numeric claim below was recomputed from the result files (scratch log: verify_r2.txt); "verified" = the reviewer is right.

## Verified errors in v1 (must fix)
1. **"26-54% of eligible households wrongly denied"** (abstract, competence, consequence). T6's wd/100k is a share of all paired
   cases, not of eligible households, and the range is the 14B-to-8B control rows only (full control range 14-54%, effort rows up to
   62%). Among gold-eligible households at the cue-free item the direct readout wrongly denies 8B 0.63, Ministral 0.63, 14B 0.50,
   32B 0.24. Verified (both reviewers).
2. **Table 1 mixes definitions**: direct = balanced accuracy on 6,376 items; reasoning = average of T1's cue-free cell mean (seed 0)
   and T7's all-item accuracy (seed 1). Verified. Fix: balanced accuracy on the 1,554 narrative items for every rung, two-seed mean
   where two seeds exist, ABAWD with and without the trap.
3. **"except three cells of 1-3 flips"**: five non-zero gross/elig reasoning cells (8B s0 elig effort 3/74; 8B s1 elig control 3/74;
   8B s1 elig effort 3/74; 32B s0 gross control 1/60; 32B s1 elig control 2/74). Verified.
4. **"8B ... opposite signs"**: 8B thinking-on ABAWD\trap control is +0.083 [+0.029, +0.136] at seed 0 (11 up / 1 down: pregnant 72h
   5/1, pregnant 88h 4/0, nonexempt 88h 2/0) and +0.000 [-0.060, +0.064] at seed 1 (7/7). Not opposite: directional at seed 0, not
   replicated at seed 1. Verified. By the paper's own sign-test logic this is a thinking-on directional contrast in a third model.
5. **Noise floor paragraph**: "0.992/1.000 for 32B" is all-item agreement; the cue-free flip rate on gross is 2/60 = 0.033. 8B's
   cue-free ABAWD flips are 8 trap + 4 nonexempt 88h + 1 pregnant 72h, so "almost entirely in the trap" holds for 14B (7/7) and 32B
   (4/4) only. The 8B elig effort (3/74) and 32B elig control s1 (2/74) contrasts exceed the cue-free elig flip rate (0/74 for both);
   what covers them is all-item agreement, which includes cued items. Verified.
6. **Ladder: "income contrasts of 1-2 flips in 74 pairs"** is 14B only. 32B thinking-off elig: 6/73 and 4/74 (s0), 3/74 and 4/74 (s1),
   effort s1 -0.054 [-0.114, -0.012]. Verified.
7. **Ladder sign tests are post hoc on selected cells**: 32B used "two" non-trap 72h cells (medical 72h, 1/1 at s0, 3/2 at s1, left out);
   Ministral used "three" (medical 72h +4/-0 included). Over all four non-trap 72h cells and both seeds 32B is 17 up / 3 down
   (binomial p = 0.0013, not 2^-12); Ministral over all non-trap cells 15/4 (p = 0.0096), and its +0.099 estimate is made of those 19
   flips, five of them on 88h cells, not "14 and none the other way". Only one household (b012, nonexempt 72h) flips up at both 32B
   seeds; the pregnant-72h households at s0 and s1 are disjoint. Verified.
8. **"none" is not cue-free**: it is a residence sentence ("lived in the same county for several years, rents from the same
   landlord"), and "car broke down ... not repaired" is a hardship sentence, i.e. a need cue in the CARIN sense. T3 measures
   "hardship sentence minus residence sentence", not "any added sentence". Verified (src/gen/make_rules_pilot.py CUES).
9. **Direct readout: the eligibility controllability contrast is consistent across models on the verdict scale too**: up/down flips on
   the thinking subsample 32B 12/0, 14B 5/0, Ministral 5/0, 8B 8/1; probability-scale CIs exclude 0 in all four (T2); survives the
   no-sanction packet (T9). The percentile-bootstrap lower bound of 0.000 reflects 2-4 flipping households among 27 clusters, not a
   null. v1's "a direction that differs by task and model" hides the one pre-specified-direction effect. Verified.
10. Smaller, verified: "majority label" is mean P(YES) over two orders > 0.5; INVALID handling unstated (pair dropped; 19 for
    Ministral off, 17 of them ABAWD); "survives unchanged" wrong for Ministral (+0.043 -> +0.101) and 14B ABAWD (+0.019 -> +0.074);
    "two models flip no verdict in 120 pairs" is ABAWD-outside-trap only; "7-10 points per household" is 7-11 (74-pair cluster bound
    0.105); T2's bases are 29 (gross) / 27 (elig) of 40 because the target margin is unreachable for some household structures
    (generator skips them); consequence caseload has 1-4 margins per household (11 x 4, 6 x 3, 2 x 2, 8 x 1), so "equal household
    weights" are margin-count weights; polarity paragraph has no method, n, or table in the paper; appendices B, F empty, C, D pointers.

## Judgement calls raised (PI decides; assistant's recommendation in brackets)
- R4 W1: apply one inferential standard to both readouts [adopt: report up/down flips for every contrast; use the same clustered
  CI + replication rule everywhere; state the direct elig controllability effect as the one cross-model consistent direct effect].
- R3 W3 / R4 Q7: 8B thinking-on seed-0 ABAWD contrast [adopt one explicit leak criterion: trap excluded, clustered CI excludes 0 at
  every seed run; 32B thinking-off passes (two seeds), 8B thinking-on fails (seed 1 = 0), Ministral decided by the seed-1 run now on
  the GPU (queue 5)].
- "Two model families" in the abstract [keep only if Ministral seed 1 passes the criterion; otherwise "replicated in one model,
  observed once in a second family"].
- R3 W2: rename valence_neg as a hardship (need) control and describe `none` as a residence sentence [adopt: wording only; no rerun].
- R3 W11: polarity paragraph [adopt: one method sentence + appendix table from the Design C archive; 14B and 32B numbers].
- R4 W6: a rung with free generation and no step-by-step instruction, or P(YES) from the ANSWER token [not for this paper; Paper 2].
- Missing references: add Röttger 2024, Lyu 2024, Zheng 2024, Tjuatja 2024, Sclar 2024, Shaikh 2023, Lanham 2023, Blair-Stanek 2023,
  Guha 2023, Holzenberger 2020 [adopt those the assistant can cite with certainty; verify the rest].

## Response plan (v2 of the paper)
- Abstract: direct readout = at chance, 24-63% wrongful denial of eligible households at the cue-free item, one cross-model
  consistent cue effect (controllability on eligibility) plus task/model-specific others; reasoning readout = at ceiling, contrasts
  within bounds, with the exceptions listed; leak criterion stated; "two model families" conditional on Ministral seed 1.
- Table 1 -> ladder table (direct / step-by-step / thinking) with one definition. Table 2 adds up/down flips.
- Cue-effects, noise-floor, ladder and consequence paragraphs rewritten with the verified numbers; sign tests over all non-trap 72h
  cells; 32B middle-rung elig contrasts reported; INVALID rule stated.
- Appendices B (cue sentences + item), C (T2 + T8), D (T7), E (polarity table), F (PolicyEngine scope) filled from the repo.

## Outcome of queue 5 (Ministral step-by-step, seed 1; 2026-10-08 13:55)
Does not replicate: ABAWD\trap controllability -0.009 [-0.086, +0.067], 11 up / 12 down; cue-free flip rate between seeds 0.28 on ABAWD
(results doc section 18). "Two model families" removed from the abstract and Discussion; Ministral is now the noise-floor example.
v2 of the paper (paper/main.tex) implements the response plan above; Table 1 is a one-definition ladder table, Table 2 carries up/down
flips for every rung, appendices B-F are filled (paper/appendix_tables.tex generated by src/eval/make_paper1_appendix.py).

# Round 4: blind reviews of paper v2 (2026-10-08, two fresh reviewers)

R5 (Ethics/Bias/Fairness, CSS): Soundness 3.5 / Excitement 3 / Overall 3.0 / Confidence 4 / Reproducibility 4.
R6 (Resources/Evaluation, statistics): Soundness 3.5 / Excitement 3 / Overall 3.0 / Confidence 4 / Reproducibility 4.
Both recomputed Table 1, every up/down count in Table 2, the 24-63% baseline, the 17/3 count and the Ministral seed-1 numbers from the raw
files and found them correct. Their objections converge; verified against the result files (verify_r2.txt continued):

## Verified and to fix in v3
1. **Leak criterion scope**: as written it also passes the eight starred direct cells (one run each). Intended scope = generated readouts
   with a second seed, on tasks where the rung is competent; must be stated. The 32B cell passes only with the trap excluded (all-cells
   seed 1 +0.033 [-0.018, +0.088]); its within-seed flip rate (9/120, 11/120) is at or below the cue-free ABAWD rate (0.093; 0.133 on the
   four non-trap 72h cells), so the evidence is the 17/3 asymmetry (15 households; two-sided binomial p = 0.003), not the size. Abstract
   "fixed before the cells are inspected" -> "adopted after seed 0 and applied to a second seed". Verified.
2. **No hardship control on ABAWD** (generator: valence_neg only for income tasks), so the leak cell lacks the paper's own control; the
   seed-1 asymmetry is mostly "fired lowers YES" (fired-minus-baseline 3/10; blameless 5/5), which a negative-valence sentence would also
   produce. Verified. -> queue 6 (pre-registered reading rule in decisions.md). Hardship control under thinking on (income) is 0 for
   8B/14B/32B and was not reported; add.
3. **Consequence paragraph**: "every one toward denying the applicant who was fired" is true of direction, false of harm: 32B's 12 flips are
   6 wrongful denials (gold YES) + 6 wrongful approvals of the blameless applicant (gold NO); 14B 3 + 2; 8B 5 + 4; Ministral 3 + 2.
   Verified. Replace the paragraph with that split.
4. **Direct eligibility controllability effect**: supported by no single-model clustered interval (flips in 2-4 of 27 households; bootstrap
   point mass at zero 0.04-0.14) but by a pooled cross-model sign count (30/1) over two families (three Qwen3 checkpoints). State as an
   exploratory pooled result with the family caveat. Verified.
5. **Hardship sentence claims**: "as much or more" holds for 14B only; for 8B the car sentence is the smallest shift (-0.091 vs -0.086 to
   -0.176). Rename as a need/hardship cue (CARIN): it is itself a deservingness criterion. Verified.
6. **Degenerate direct cells**: 8B ABAWD always NO (YES rate 0.00), 32B gross YES rate 0.99; their "0 (0/0)" is floor/ceiling, not
   robustness. Verified. Mark in Table 2.
7. Smaller, verified: three (not two) reasoning contrasts exceed the cue-free rate (add 8B elig control s1, 2/1); Ministral pair counts
   111/115/116/114; "one household flips in the same direction at both seeds" (b012; b020 flips in opposite directions); non-trap 72h
   accuracy range 0.64-0.92 (child<14 cell 0.92-0.97); Ministral cue-free rate 0.28 is all-ABAWD, 0.33 on the 72h cells; 8B's cue-free
   flips outside the trap are on the non-exempt 88h (hours) cell; eligibility is below chance (0.40-0.46), not at chance; two model
   families, not four independent models; bounds exclude direct-sized item rates but not direct-sized household rates (2-4 of 27).
8. Reproducibility: add the 15-groups-per-cell seeded sampling, bootstrap replicate count, logprob handling (0 missing rows in all four
   direct runs; P(YES) = softmax over the two tokens), AWQ caveat (the only model passing the criterion is the quantised one).
9. Ethics statement: add the risk that a null under the reasoning readout is read as clearance for LLM eligibility determination, and
   that the packet is federal rules only, not a legal reference.
10. References both reviewers want: Hofmann et al. 2024 (Nature), Haim et al. 2024, Chen et al. 2025 (reasoning models don't always say
    what they think), Lakens 2017 (equivalence tests), Hanley & Lippman-Hand 1983 (rule of three), Gelman & Loken 2014 (forking paths),
    Gaebler et al. 2024, Cameron, Gelbach & Miller 2008 (few-cluster bootstrap).

## Not adopted (with reason)
- ±1% margins to break the reasoning ceiling (R5 W3/Q5): a new item set; Paper 2 territory. The ceiling reading is carried into the
  abstract instead.
- A figure for the ladder (R5 W7): no page budget in the review version; revisit for camera-ready (+1 page).
- Dropping the all-zero thinking columns from Table 2: they are not all zero (8B, 32B), and the zeros are the point.

## Outcome of queue 6 (need control on the 32B ABAWD cells; 2026-10-08 14:46)
Pre-registered rule gives (iii) not separable (results doc section 19). Paper v3 states it in the abstract, the ladder paragraph and a new appendix; the 32B cell stays 'one replicated cell among 36 examined'.

# Round 5: external review of v3 (pasted by the PI, 2026-10-08) and the response

Mock score Overall ~3.0. Verified points: (1) the direct readout's probability verdict agrees with the greedy one-word answer 99.9-100%, so
the phenomenon is "asked for an answer vs asked to compute", not a first-token misreading (Wang et al. 2024 covers the latter); (2) the
title "Where Deservingness Leaks" is stronger than the need-control outcome (not separable); (3) the 3/n bound is per item, the household
bound is 10-11% and does not exclude the direct effects (the paper already says so; the abstract did not); (4) 17 up / 3 down come from
15 + 3 = 17 households (fixed: "17 household-cells in 15 households ... 3 in 3 other households"); (5) LexGuard already uses statute-based
gold (intro narrowed to: independent cross-check + non-demographic deservingness cues + response-protocol comparison); (6) release gaps:
Design C archive missing (now shipped: notes + score files), docs/ layout (now docs/paper1 and docs/results), README licence missing
(now: code MIT, data/outputs CC BY 4.0, PI may change); (7) abstract 354 words (now 273).
Adopted on the PI's go (15:10): free-generation rung (queue 7; pre-registered rule in decisions.md), new title "Leak or Readout?
Auditing Deservingness Cues in LLM Welfare Determinations Against a Computed Gold Standard", abstract and intro reframed around the
response protocol, recommendation reworded (report accuracy with every cue effect; restrict mechanism claims, not error reports, where
accuracy is low), track preference moved to Resources, Benchmarks and Evaluation. Not adopted: more models (API deferred by the PI).

## Outcome of queue 7 (free-generation rung; 2026-10-08 15:58)
Permission to generate suffices: without any instruction to reason the three models compute unprompted (income 0.98-1.00, contrasts 0-5 flips). The direct readout's cue effects come from the one-word instruction. Paper v4 states this in the abstract, Table 1, the ladder paragraph and Appendix F (results doc section 20).

# Round 6: external review of v4 (pasted by the PI, 2026-10-08) and the response
Verified and fixed: Ministral free-rung eligibility effort (3/4 = 7 flips) is 'graded' under the pre-stated rule, not 'permission suffices'; the body now says 0-8 flips with no stable sign; the Limitations 'future work' sentence about a free rung was removed; the 32B household count reads '15 households toward, 3 the other way, one in both sets, 17 distinct'. Adopted: free-rung seed 1 (queue 8): the income result replicates (14B exact; 32B/Ministral graded), 14B's ABAWD 18/8 does not (10/10). Frontier models remain deferred.
