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
Mean dP(YES), cue_high minus cue_low, 95% item bootstrap (NOT yet clustered by base, so the CIs are too narrow).
| model | elig: control | elig: effort | gross: control | gross: effort | ABAWD: control | ABAWD: effort |
| --- | --- | --- | --- | --- | --- | --- |
| Qwen3-8B | +0.081 | +0.001 | +0.021 | -0.060 | +0.001 | -0.001 |
| Ministral-3-8B | +0.044 | +0.032 | +0.036 | +0.003 | +0.062 | -0.011 |
| Qwen3-14B | +0.048 | +0.069 | -0.035 | +0.069 | +0.019 | -0.025 |
| Qwen3-32B-AWQ | +0.091 | +0.015 | +0.000 | +0.008 | -0.019 | +0.004 |

control_high = job lost when the warehouse closed; control_low = fired for missing shifts. effort_high/low = 8 applications per week vs 1 in two months.
- **Only consistent signal: controllability on the eligibility question, +0.04 to +0.09 in all four models** (blameless job loss -> more YES). The sign holds whether or not the cue-free version was answered correctly.
- Effort: no consistent sign (8B gross -0.06, 14B +0.07).
- ABAWD (the work-requirement question, where deservingness should matter most to a human): small, mixed signs.
- Main effects vs cue=none (scorer `cue_effects_should_not_change`) are of the same size for the non-moral valence control (car broke down) as for the deservingness cues, so **adding any sentence moves the verdict**; only the hi-lo contrast is interpretable.

## 3. Reading
- With thinking off the task is beyond the models, so cue effects here are measured on near-chance verdicts. A reviewer will say this. The interference question must be asked where the model can do the task.
- Possible confound for control_low: real SNAP has voluntary-quit / reduction-of-work-effort rules that the packet does not mention. Federally a discharge for cause is not a voluntary quit and "last summer" is outside the window, but the packet should say so explicitly.

## 4. Next (proposed, not yet decided)
1. Competence first: thinking-mode generation on a stratified subsample (14B, 32B), extract the final YES/NO, then the hi-lo cue contrasts on that.
2. Cluster bootstrap by base for every CI.
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
