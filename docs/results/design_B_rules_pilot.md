# Design-B rules pilot: results (2026-10-05)

Setup: 6,376 items (gross test, eligibility, ABAWD), rule packet + case file, YES/NO first-token log-probs,
both answer orders, **thinking off**. Models: Qwen3-8B, Ministral-3-8B, Qwen3-14B, Qwen3-32B-AWQ.
Integrity: 0 missing items or order rows; greedy agrees with log-prob verdict 99.9-100%. Raw: results/rules_pilot/.

## 1. Baseline competence (no CoT)
| model | bal. acc gross | elig | ABAWD | YES rate vs gold (gross / elig / ABAWD) |
| --- | --- | --- | --- | --- |
| Qwen3-8B | 0.54 | 0.48 | 0.50 | 0.24/0.50, 0.09/0.62, 0.00/0.80 |
| Ministral-3-8B | 0.52 | 0.41 | 0.62 | 0.09/0.50, 0.42/0.62, 0.39/0.80 |
| Qwen3-14B | 0.58 | 0.42 | 0.80 | 0.77/0.50, 0.61/0.62, 0.49/0.80 |
| Qwen3-32B-AWQ | 0.52 | 0.44 | 0.70 | 0.97/0.50, 0.63/0.62, 0.83/0.80 |

- Income tasks are at chance (or below) for every model, and accuracy does not rise with distance from the limit
  (e.g. 14B elig: 0.47 at -15%, 0.17 at +15%). The models answer by a YES/NO prior, not by computing.
- ABAWD shows a different heuristic at each scale (narrative, cue=none):
  - 8B: always NO.
  - 14B: applies the hours rule correctly (72h->NO, 88h->YES; child-15 trap correct) but **ignores exemptions** (exempt at 72h: child<14 0.005, pregnant 0.00, medical 0.35).
  - 32B: recognises exemptions (1.00) but treats the 15-year-old child as exempting (trap 72h: 0.00), and says NO to nonexempt 88h (0.015). Hypotheses, unverified: (a) prior-law override (pre-P.L. 119-21 rule was "child under 18"); (b) "already used 3 countable months" read as decisive.
  - Spot check: b000_abawd_nonexempt_88_none_n is correct (40 paid + 48 program = 88 >= 80; gold YES). 14B and 32B both give P(NO) > 0.8.

## 2. Deservingness cues (paired hi-lo, same item otherwise)
Mean dP(YES), cue_high minus cue_low, 95% **base-clustered** bootstrap (recomputed 2026-10-08 with
src/eval/score_rules_pilot.py, key cue_contrasts_hi_minus_lo_clustered; the item-bootstrap table of 2026-10-05 had the
same means with CIs too narrow). Full table with CIs: docs/paper1/tables.md, T2.
| model | elig: control | elig: effort | gross: control | gross: effort | ABAWD: control | ABAWD: effort |
| --- | --- | --- | --- | --- | --- | --- |
| Qwen3-8B | +0.081 [+0.042, +0.115] | +0.001 | +0.021 [+0.002, +0.040] | -0.060 [-0.082, -0.041] | +0.001 | -0.001 |
| Ministral-3-8B | +0.043 [+0.032, +0.056] | +0.032 [+0.008, +0.057] | +0.036 [+0.023, +0.049] | +0.003 | +0.062 [+0.059, +0.066] | -0.011 |
| Qwen3-14B | +0.048 [+0.021, +0.078] | +0.069 [+0.040, +0.108] | -0.035 [-0.045, -0.024] | +0.069 [+0.043, +0.093] | +0.019 | -0.025 |
| Qwen3-32B-AWQ | +0.091 [+0.056, +0.133] | +0.015 [-0.006, +0.037] | +0.000 | +0.008 | -0.019 | +0.004 |

control_high = job lost when the warehouse closed; control_low = fired for missing shifts. effort_high/low = 8 applications per week vs 1 in two months.
- **Only consistent signal: controllability on the eligibility question, +0.04 to +0.09 in all four models, clustered CIs exclude 0** (blameless job loss -> more YES). The sign holds whether or not the cue-free version was answered correctly.
- Effort: no consistent sign (8B gross -0.06, 14B +0.07).
- ABAWD (the work-requirement question, where deservingness should matter most to a human): small, mixed signs.
- Main effects vs cue=none (scorer `cue_effects_should_not_change`) are of the same size for the non-moral valence control (car broke down) as for the deservingness cues, so **adding any sentence moves the verdict**; only the hi-lo contrast is interpretable.

## 3. Reading
- With thinking off the task is beyond the models, so cue effects here are measured on near-chance verdicts. A reviewer will say this. The interference question must be asked where the model can do the task.
- Possible confound for control_low: real SNAP has voluntary-quit / reduction-of-work-effort rules that the packet does not mention. Federally a discharge for cause is not a voluntary quit and "last summer" is outside the window, but the packet should say so explicitly.

## 4. Next (proposed, not yet decided)
1. Competence first: thinking-mode generation on a stratified subsample (14B, 32B), extract the final YES/NO, then the hi-lo cue contrasts on that.
2. Cluster bootstrap by base for every CI. (done 2026-10-08 for the hi-lo contrasts)
3. State in the packet that the job-loss reason does not trigger any sanction.
4. The 32B "prior-law override" is a separate contribution (knowledge conflict): follow-up roadmap unless it deepens the core question.

## 5. Thinking-mode subsample, Qwen3-14B (2026-10-05)
src/run/run_rules_think.py, 1,554 narrative items; scorer src/eval/score_rules_think.py (cluster bootstrap by base).
results/rules_think/score_qwen3-14b.json.
- Parse: 1,554/1,554 parsed (0 truncated, 0 invalid), mean 749 tokens, max 3,487.
- **Accuracy: gross 1.00 and elig 1.00 in every margin x cue cell; ABAWD 1.00 in 18 of 20 cells.** Every one of the 26 errors is in the child_15_trap cell (72h: 0.67 with no cue; one at 88h). The reasoning reads the checklist line "responsible for the care of a child who lives in the household: Yes" as "a child under 14", skipping the stated age 15 (5/26 mention "under 18").
- **Cue effects: exactly 0 on gross and elig** (no verdict changes across any cue pair, 60 + 74 groups). ABAWD: control hi-lo -0.040 [-0.075, -0.007]; effort hi-lo 0.000; all of it comes from the trap cell.
- The reasoning rarely mentions the cue (controllability 0-5%), but effort_low is mentioned in 38% of elig traces, where it pulls the model into an off-question ABAWD check without changing the income verdict.
- Reading: at 14B, reasoning removes both the errors and the interference. The no-thinking cue effects (section 2) belong to the regime where the model is not computing.
- Item note: the trap is a checklist-vs-age conflict ("child: Yes" with the child aged 15). A reviewer may call it adversarial; the checklist line should name the age bound or be dropped, and the trap reported as its own analysis.

## 6. Thinking-mode, Qwen3-32B-AWQ (2026-10-05)
results/rules_think/score_qwen3-32b-awq.json. 1,554/1,554 parsed, mean 617 tokens.
- elig 1.00 in every cell; gross 0.93-1.00 (scattered errors, no margin pattern); ABAWD 1.00 except the child-15 trap (72h: 0.87).
- Cue contrasts: every CI includes 0 (largest: gross control hi-lo -0.017 [-0.054, 0.000]; ABAWD |effect| <= 0.007).
- Same conclusion as 14B: with reasoning, rule-computable verdicts do not move with deservingness cues.
- Reasoning mentions effort_low in 49% of elig traces and control_low in 15%, without verdict changes.

## 7. Thinking-mode, Qwen3-8B (2026-10-05)
results/rules_think/score_qwen3-8b.json. 1,554/1,554 parsed, mean 1,014 tokens.
- gross 1.00, elig 0.98-1.00; ABAWD errors in the trap (72h 0.30-0.47), nonexempt 88h (0.80-0.93), pregnant (0.90-0.93).
- No cue contrast has a CI excluding 0.
- Scale curve with reasoning (8B -> 14B -> 32B): income verdicts at ceiling from 8B; ABAWD errors shrink with scale; cue effects null at every scale.

## 8. Seed replicate, Qwen3-14B (2026-10-08, L40; results/rules_think/qwen3-14b_s1.jsonl, seed 1)
Scores: results/rules_think/score_qwen3-14b_s1.json; agreement with seed 0: results/rules_think/agreement/qwen3-14b_s0_vs_s1.json.
- 1,554/1,554 parsed, mean 726 tokens. Income tasks: gross 1.00 and elig 1.00 in every cell again; **verdict agreement with
  seed 0 is 1.000 on gross and elig**, so the sampling-noise floor on income verdicts is 0 flips in 134 cue-free groups.
- ABAWD: agreement 0.952; flip rate at cue = none 0.047 (7/150), all inside the child-15 trap (72h: 0.93 cue-free, 0.68 with cues).
  16 bases have some disagreement, all in that cell.
- Cue contrasts, seed 1: gross and elig exactly 0 (every pair); ABAWD control hi-lo +0.007 [-0.027, +0.043], effort
  -0.013 [-0.051, +0.025]. **The seed-0 ABAWD control contrast (-0.040 [-0.075, -0.007]) does not replicate**: it sits inside the
  trap cell's seed-to-seed noise and should be reported as noise, not as a cue effect.
- Reading for the paper: with reasoning, the only non-zero contrast in any model/seed is within the measured noise floor of one
  adversarial cell. Report the noise floor next to every reasoning-mode contrast.

## 9. Protocol ladder, Qwen3-14B thinking OFF with the same step-by-step prompt (2026-10-08; results/rules_think/qwen3-14b_off.jsonl)
Same 1,554 items, same prompt ("reason through the rules step by step ... ANSWER:"), same sampling, Qwen3 thinking switch off,
so the visible reasoning is the only reasoning. Scores: score_qwen3-14b_off.json; agreement with thinking on: agreement/qwen3-14b_on_vs_off.json.
- Parsed 1,554/1,554, mean 462 tokens (vs 749 with thinking).
- Income: gross 0.99-1.00, elig 0.96-1.00 per cell; agreement with thinking on 0.997 / 0.991. Cue contrasts: gross 0; elig control
  +0.014 [0.000, +0.043], effort -0.027 [-0.064, 0.000]; flip rate at cue = none 0.014 (elig). The residual contrasts are the size of
  the noise floor.
- ABAWD: accuracy 0.90 overall, agreement with thinking on 0.899, flip rate at cue = none 0.107. Exemption cells drop: child<14 72h
  0.73 (none) / 0.85 (cue), pregnant 72h 0.93 / 0.80, trap 72h 0.40 / 0.55. Cue contrasts all include 0.
- Reading (ladder: first-token -> step-by-step without thinking -> thinking): asking for steps removes the income-test errors and the
  cue effects almost entirely; the thinking switch adds reliability on the exemption chain. So "reasoning removes the effect" is
  mostly "computing removes the effect": the first-token regime is the one in which the model answers from a prior.

## 10. Seed replicate, Qwen3-32B-AWQ (2026-10-08; results/rules_think/qwen3-32b-awq_s1.jsonl, seed 1)
- 1,554/1,554 parsed, mean 598 tokens. gross 1.00 in every cell (the seed-0 scattered gross errors, 0.93-1.00, do not recur:
  seed-to-seed flip rate at cue = none is 0.033 on gross, so they were sampling noise); elig 0.99-1.00; ABAWD 1.00 except the trap
  (72h: 0.87 none / 0.80 cue).
- Agreement with seed 0: gross 0.992, elig 0.996, ABAWD 0.977; cue-free flip rates 0.033 / 0.000 / 0.027.
- Contrasts: gross 0; elig control -0.027 [-0.085, 0.000] (two pairs in one base; seed 0 gave 0.000), effort 0; ABAWD control
  -0.013 [-0.049, +0.014], effort +0.013 [-0.012, +0.041]. Every non-zero value is within the cue-free seed-to-seed flip rate.

## 11. Seed replicate, Qwen3-8B (2026-10-08; results/rules_think/qwen3-8b_s1.jsonl, seed 1)
- 1,554/1,554 parsed, mean 1,028 tokens. gross 1.00; elig 0.96-1.00 (errors only in cue cells at the negative margins); ABAWD
  0.92 (trap 0.50-0.60, nonexempt 88h 0.93, pregnant 72h with cue 0.77).
- Agreement with seed 0: gross 1.000, elig 0.975, ABAWD 0.904; cue-free flip rates 0 / 0 / 0.087; 31 of 40 bases disagree somewhere
  on ABAWD.
- Contrasts: gross 0; **elig effort hi-lo -0.041 [-0.087, 0.000] at seed 1 vs +0.041 [0.000, +0.091] at seed 0: opposite signs**, each
  CI touching 0. ABAWD effort -0.047 [-0.100, +0.006] (seed 0: +0.027 [-0.014, +0.068]), control 0.000 [-0.068, +0.068].
- Reading: at 8B the residual contrasts are sampling noise with no stable sign. Across 8B / 14B / 32B and two seeds, no reasoning-mode
  cue contrast has a consistent sign, and every one is within the cue-free seed-to-seed flip rate of its task.

## 12. Protocol ladder, Qwen3-32B-AWQ thinking OFF (2026-10-08; results/rules_think/qwen3-32b-awq_off.jsonl)
- 1,553/1,554 parsed (1 INVALID), mean 474 tokens. gross 0.99-1.00; elig 0.93-1.00 (errors at the negative margins); ABAWD 0.89:
  trap collapses (72h: 0.27 none / 0.15 cue), nonexempt 72h 0.87 / 0.83, pregnant 72h 0.93, medical 72h 0.93-0.97.
- Agreement with thinking on: gross 0.989, elig 0.971, ABAWD 0.897; cue-free flip rates 0.033 / 0.014 / 0.100.
- Contrasts: gross effort +0.017 [0.000, +0.053]; elig control 0.000 [-0.069, +0.067], effort +0.027 [-0.024, +0.090];
  **ABAWD control hi-lo +0.060 [+0.013, +0.109]**, effort -0.027 [-0.064, +0.007].
- Where the ABAWD controllability effect sits (per cell, n = 15 groups each; sign = blameless minus fired):
  nonexempt 72h (gold NO) +0.267 (4 groups flip to YES under the blameless cue, 0 the other way); pregnant 72h (gold YES) +0.200
  (3 groups flip to NO under the fired cue, 0 the other way); trap 72h +0.133 (4 vs 2); medical 72h 0. With thinking on it is 0 in
  both seeds (trap only, mixed signs); 14B thinking off shows mixed signs.
- Reading: on the middle rung of the ladder (steps requested, no thinking), 32B computes the income tests but is unstable on the
  72-hour work-requirement cells, and there the controllability cue moves verdicts in the deservingness direction: wrongful approval
  of the blameless non-exempt adult, wrongful denial of the exempt pregnant adult who was fired. Exploratory (one model, one seed,
  pooled CI excludes 0 but the cue-free ABAWD flip rate is 0.10); report as the one place in the ladder where leakage is directional,
  and as the motivation for testing where the model is unsure rather than where it computes (Paper 2).

## 13. Replicate of the 32B thinking-off leak, seed 1 (2026-10-08; results/rules_think/qwen3-32b-awq_off_s1.jsonl)
- Agreement with seed 0: gross 0.997, elig 0.946, ABAWD 0.891; cue-free flip rates 0 / 0.027 / 0.093.
- ABAWD controllability hi-lo on the verdict scale (results/common_scale/contrasts.md): all cells +0.033 [-0.018, +0.088] (seed 0:
  +0.060 [+0.013, +0.109]); **trap excluded +0.058 [+0.008, +0.114] at seed 1 and +0.058 [+0.016, +0.103] at seed 0**.
- By cell, blameless minus fired, groups flipping each way: nonexempt 72h (gold NO) seed 0 +4/-0, seed 1 +3/-0; pregnant 72h (gold YES)
  +3/-0 and +2/-0; trap 72h +4/-2 then +3/-5 (sign flips: noise). Across both seeds, 12 groups flip in the deservingness direction and
  0 in the other direction on the two non-trap 72-hour cells (one-sided sign test p = 2^-12).
- Reading: the leak replicates outside the trap. On the middle rung (steps requested, no thinking), Qwen3-32B wrongly approves the
  blameless non-exempt adult and wrongly denies the exempt pregnant adult who was fired; with thinking on, both seeds show 0 flips in
  these cells. Effort shows no such asymmetry (-0.025 / -0.033, CIs include 0). Still one model; 14B thinking-off seed 1 is running.

## 14. Qwen3-14B thinking-off, seed 1 (2026-10-08; results/rules_think/qwen3-14b_off_s1.jsonl)
- Income: gross 0 flips in 60 pairs at both seeds; elig 0/1 flips (control 0.000, effort -0.013 [-0.047, 0.000]). Agreement with seed 0:
  gross 0.997, elig 0.984. The income-test result on the middle rung is stable at 14B.
- ABAWD: cue-free flip rate 0.14 (agreement 0.845), the noisiest cell of the whole study. Control hi-lo (trap excluded) -0.017 at seed 0,
  +0.058 [-0.017, +0.129] at seed 1: sign changes, CIs include 0. Unlike 32B (section 13), 14B thinking-off shows noise on the exemption
  cells, not a direction.
- Reading: the directional leak is a 32B result; at 14B the middle rung is simply unreliable on ABAWD. The paper states it as one model.

## 15. Decoding control: Qwen3-14B thinking on, greedy (T=0) (2026-10-08; results/rules_think/qwen3-14b_greedy.jsonl)
- 1,554/1,554 parsed, mean 714 tokens. Agreement with the sampled seed-0 run: gross 1.000, elig 1.000, ABAWD 0.951; cue-free flip
  rate 0 / 0 / 0.047 (trap only). Accuracy below 1.00 only in the trap cell (0.67 none / 0.77 cue).
- Contrasts: gross and elig 0 flips in 60 / 74 pairs; ABAWD outside the trap 0 flips in 120 pairs (all cells: control -0.007, effort
  +0.020, CIs include 0).
- Reading: the reasoning readout's result does not depend on sampling. The rung of the ladder that matters is the prompt (steps
  requested), not the decoding; the remaining confound between the direct and the step-by-step readouts is the prompt and the answer
  extraction, which cannot be separated without changing what is being measured.

## 16. Sanction check: direct readout with the no-sanction packet (2026-10-08; results/rules_pilot_nosanction/, T9)
Packet line added: "The reason a member lost or left a past job ... does NOT affect any determination in this packet: no voluntary-quit
or work-sanction rule applies." Everything else identical; first-token, both orders, all 6,376 items.
| model | elig control hi-lo, original | with the line |
| --- | --- | --- |
| Qwen3-8B | +0.081 [+0.042, +0.115] | +0.082 [+0.034, +0.128] |
| Qwen3-14B | +0.048 [+0.021, +0.078] | +0.064 [+0.032, +0.102] |
| Qwen3-32B-AWQ | +0.091 [+0.056, +0.133] | +0.094 [+0.057, +0.139] |
| Ministral-3-8B | +0.043 [+0.032, +0.056] | +0.101 [+0.087, +0.117] |
- The eligibility controllability contrast survives the clarification in all four models (Ministral's doubles; its ABAWD contrast goes +0.062 -> +0.123); 14B's negative gross contrast
  (-0.035) goes to -0.002 and its ABAWD contrast rises to +0.074; 8B's effort contrast on elig rises from 0 to +0.045.
- Reading: the direct-readout controllability effect is not rule knowledge about voluntary quit; stating that the reason is irrelevant
  does not remove it, which is what a deservingness heuristic predicts and a legal-relevance reading does not.

## 17. Ladder, 4th model: Ministral-3-8B on the step-by-step prompt (2026-10-08; results/rules_think/ministral3-8b_off.jsonl)
Ministral has no thinking mode, so its ladder is direct -> step-by-step (same sampling as the Qwen runs, seed 0, one run).
- 1,535/1,554 parsed (19 INVALID: 17 ABAWD, 2 gross; the answer never reaches an ANSWER line), mean 422 tokens.
- Income: gross 0.93-1.00, elig 0.96-1.00 per cell (direct readout: balanced accuracy 0.52 / 0.41). Contrasts on the verdict scale
  (results/common_scale/contrasts.md): gross control -0.017 [-0.059, 0.000] (1 flip / 59 pairs), effort -0.017 (1/60); elig control
  +0.013 [0.000, +0.047] (1/74), effort +0.013 (1/74). The direct readout on the same items had gross control +0.183 [+0.054, +0.317]
  (11 flips) and effort +0.133 (8 flips), elig control +0.068 (5 flips). Asking for the computation removes the income-test effects in
  the fourth model too, without any thinking mode.
- ABAWD: unreliable (nonexempt 72h 0.63-0.67, pregnant 72h 0.73-0.78, medical 72h 0.75-0.87, trap 72h 0.45-0.80). Controllability hi-lo
  **+0.107 [+0.022, +0.191] all cells (33 flips / 140 pairs); trap excluded +0.099 [+0.035, +0.164] (19/111)**; effort 0.000
  [-0.093, +0.091] with 50 flips / 143 pairs, i.e. the effort pairs flip symmetrically and give the noise level.
- By cell, blameless minus fired, groups flipping each way: nonexempt 72h (gold NO) +6/-0; pregnant 72h (gold YES) +4/-0; medical 72h
  (gold YES) +4/-0; trap 72h +5/-5; 88h cells +5/-4 pooled. On the three non-trap 72-hour cells controllability flips 14 groups in the
  deservingness direction and 0 the other way (one-sided sign test p = 2^-14); effort on the same cells flips +11/-10.
- Reading: the same pattern as Qwen3-32B thinking-off (sections 12-13) in a second model family: on the rung where the model computes
  the income tests but is unstable on the 72-hour exemption cells, controllability moves verdicts in the deservingness direction
  (wrongful approval of the blameless non-exempt adult, wrongful denial of the exempt adult who was fired), and effort does not. One seed;
  no cue-free flip rate for this run (no second Ministral run), so the effort pairs are the only noise reference. The paper reports it as
  the second model with the directional leak on the middle rung, not as a replicated estimate.

## 18. Ministral-3-8B step-by-step, seed 1 (2026-10-08; results/rules_think/ministral3-8b_off_s1.jsonl; queue 5, after blind-review round 3)
- 1,532/1,554 parsed (22 INVALID), mean 412 tokens. Agreement with seed 0: gross 0.992, elig 0.986, **ABAWD 0.755**; cue-free flip rate
  0.000 / 0.027 / **0.283** (results/rules_think/agreement/ministral3-8b_off_s0_vs_s1.json). Accuracy: gross 0.99, elig 0.99, ABAWD 0.82.
- Income: gross control 0/60 flips, effort 1/0; elig control 0/71, effort 0/74. The income-test result replicates.
- ABAWD, trap excluded, controllability hi-lo: **-0.009 [-0.086, +0.067], 11 up / 12 down** (seed 0: +0.099 [+0.035, +0.164], 15/4);
  on the 72h cells 8/6 (seed 0: 14/0). Effort -0.026 [-0.122, +0.062], 11/14.
- Reading: the seed-0 asymmetry does not replicate. Ministral's middle rung is a coin flip on the ABAWD exemption cells (cue-free flip
  rate 0.28), and a 15/4 split is within that noise. Under the leak criterion (trap excluded, clustered CI excludes 0 at every seed)
  Ministral fails; only Qwen3-32B thinking-off passes. Section 17's "second model family" reading is withdrawn; the paper reports
  Ministral as the noise-floor example (an asymmetry of the same size as the 32B leak that a second seed removes).

## 19. Need (hardship) control on the ABAWD cells of the 32B leak (2026-10-08; queue 6; src/eval/score_abawd_hardship.py)
Pre-registered rule and runs: docs/decisions.md (2026-10-08, "hardship control on the ABAWD cells"). Car sentence added to the same 150
subsample ABAWD groups (data/rules_pilot/pilot_plus_abawd_hardship.jsonl; pilot.jsonl byte-identical; group selection and order unchanged).
Qwen3-32B-AWQ, 150 items per run, 0 INVALID.
| run | need (car) - baseline | fired - baseline | blameless - baseline | fired - need | blameless - need |
| --- | --- | --- | --- | --- | --- |
| thinking off, seed 0 | 2 up / 4 down | 2 / 6 | 5 / 2 | 2 / 4 | 6 / 1 |
| thinking off, seed 1 | 5 / 0 | 3 / 10 | 5 / 5 | 0 / 12 | 2 / 7 |
| thinking on, seed 0 | 0 / 1 | 0 / 0 | 0 / 0 | 1 / 0 | 1 / 0 |
(four non-trap 72h cells, 60 pairs per sentence; the 88h cells add no flips, so all-non-trap counts are identical)
- Rule outcome: **(iii) not separable.** (i) fails: the car sentence's down-flips (4, 0) are fewer than fired's (6, 10) at seed 1. (ii) fails: the
  car sentence is not symmetric at seed 1 (5/0).
- Reading: the fired sentence lowers verdicts more than the need sentence at both seeds (fired minus need 2/4, 0/12), which is what the
  deservingness reading predicts, but the need sentence's own direction reverses between seeds (2/4 then 5/0), i.e. it behaves like the
  cue-free noise of this cell (8/60 between seeds). One control run per seed on a cell this noisy cannot separate the two readings; the
  paper says so and keeps the 32B cell as "one replicated cell among 36 examined". With thinking on, no sentence moves these cells.

## 20. Free-generation rung (2026-10-08; queue 7; src/run/run_rules_think.py --prompt free; seed 0)
Pre-registered rule and runs: docs/decisions.md (2026-10-08, "free-generation rung"). Thinking off, no instruction to reason, only the
ANSWER-line format; same subsample and answer order. Scores: results/rules_think/score_*_free.json; agreement with the step rung:
results/rules_think/agreement/*_off_vs_free.json; verdict-scale contrasts: results/common_scale/contrasts.md (free_s0).
| model | parsed | mean tokens | bal. acc gross / elig / ABAWD no-trap (all) | income contrasts (control; effort) | ABAWD no-trap (control; effort) | agreement with step gross / elig / ABAWD |
| --- | --- | --- | --- | --- | --- | --- |
| Qwen3-32B-AWQ | 1,553 | 403 | 1.00 / 0.98 / 0.87 (0.75) | gross 0/0; 0/0. elig 4/1 (+0.041 [0, +0.094]); 1/1 | 7/7; 5/6 | 0.997 / 0.946 / 0.872 |
| Qwen3-14B | 1,554 | 312 | 1.00 / 1.00 / 0.91 (0.72) | all 0/0 | 18/8 (+0.083 [+0.009, +0.161]); 16/9 | 0.997 / 0.989 / 0.804 |
| Ministral-3-8B | 1,536 | 236 | 1.00 / 0.98 / 0.67 (0.56) | gross 0/0; 0/0. elig 1/1; 3/4 | 19/14; 26/22 | 0.994 / 0.964 / 0.639 |
- No Qwen output is under 40 tokens; Ministral has 131 (of 1,554). Given permission to generate, the models reason step by step on their
  own; the outputs look like the step rung's.
- Rule outcome: **(a) permission to generate suffices** for 14B and for every gross contrast; graded for 32B eligibility controllability
  (5 flips, 4/1) and for Ministral eligibility effort (7 flips, 3/4, net -0.014): both exceed the rule's 3-flip cap although the net
  effect is small (correction 2026-10-08 after the round-6 review: v4 Appendix F had called Ministral 'permission suffices'). The direct readout's cue effects therefore come from the
  one-word instruction forbidding the computation, not from the absence of an instruction to compute, and not from the thinking switch.
- ABAWD outside the trap is as unstable as on the step rung (cue-free flip rate vs the step rung 0.12 / 0.15 / 0.40); 14B shows a one-seed
  controllability asymmetry (18/8) of the kind already seen for 8B thinking-on and 32B step; one seed cannot pass the leak criterion.
