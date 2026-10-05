# Pilot 1 audit (Qwen3-8B only, dev set, 2026-10-05)

Scope: 50 dev bases, 700 profiles, 7 queries, greedy decoding, thinking off. Ministral run FAILED
(vLLM 0.30 + installed transformers: `PixtralRotaryEmbedding` import error) -> no cross-model evidence yet.
Everything below is a diagnostic of one model on dev items, not a result.

## What the data show

1. **Effort barely moves binary factual judgments.** Core high/low pairs that flip: q1_direct 8/100
   (3 of them truncation noise), q1_yesno 2/100 (both SUFFICIENT->UNKNOWN), q3_extraction 1/100.
2. **The big error is on SUFFICIENT items, and it depends on question form and text format, not on effort.**

   | format / state | q1_direct | q1_direct_rev | q1_yesno | q2_definition | q3_extraction |
   | --- | --- | --- | --- | --- | --- |
   | numeric / sufficient | 0.29 | 0.12 | 0.94 | 0.15 | 1.00 |
   | itemized / sufficient | 0.26 | 0.06 | 0.00 | 0.00 | 0.26 |
   | textual / sufficient | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
   | all shortfall rows | 0.62-1.00 | 0.88-1.00 | 1.00 | 1.00 | 1.00 |

   - In itemized items q3 extracts both totals correctly (e.g. 2140 vs 1360) and still answers SHORTFALL (25/68 rows).
   - Errors occur equally with activity info removed -> not an effort effect.
3. **Q4 and Q5 collapse to 2-3 values under greedy decoding.** Q4 is almost only {5, 6}; Q5 only {75, 85, 95}.
   The "-0.25 activity effect" on Q4 is a handful of 6->5 switches.

## Design flaws found (mine)

| # | Flaw | Consequence | Fix |
| --- | --- | --- | --- |
| F1 | Q4 wording presupposes a shortfall ("how far their available money falls short") | Sufficient cases still rated 5/7; scale cannot track facts | Neutral wording, no presupposition |
| F2 | Greedy argmax on labels and scales | Discards graded shifts; Q4/Q5 near-binary; effort effect invisible unless argmax flips | Read token log-probabilities: P(SHORTFALL), expected scale value |
| F3 | max_tokens=16 | 46 truncated answers | Logprob scoring needs 1 token; free-text runs get 64 |
| F4 | Valence control (elevator) is itself a plausible hardship | Cannot separate valence from legitimate non-material hardship under a "hardship" question | Re-select valence control after Q4 is fixed; must be negative but irrelevant to money AND hardship |
| F5 | Only one model ran | No generality claim possible | Fix Ministral env (pin transformers) |

## Open diagnostic question (decides the paper's core)

Why does the model call clearly sufficient cases SHORTFALL while extracting the correct numbers?
Candidate explanations, each testable cheaply on existing items:
- H-context: the social context (unemployed, bills due, applying for assistance) creates a "this person is in need" prior that overrides stated numbers.
  Test: same money sentences with the context removed, and with an employed person.
- H-label: the SHORTFALL/SUFFICIENT label vocabulary is misread. Test: q1_yesno already partly separates this (numeric 0.94) but itemized stays 0.00.
- H-aggregation: itemized sums are not compared. Test: give the totals pre-summed in the same itemized frame.

## Oracle-ladder diagnostic, Qwen3-8B, sequence-level label scoring (2026-10-05)

Dev bases only (50), 5,000 items x 3 queries, full-label log-probabilities (prefix check: 0 mismatches).
First-token scoring was discarded: SHORTFALL/SUFFICIENT share the first token "S" (47% of mass unassignable).

Accuracy on SUFFICIENT items (all SHORTFALL items: 1.00 everywhere):

| condition | q1_yesno | q1_direct | q1_direct_rev |
| --- | --- | --- | --- |
| none / L0 | 1.00 | 1.00 | 1.00 |
| employed / L0 | 1.00 | 1.00 | 1.00 |
| unemployed / L0 | 1.00 | 0.40 | 0.37 |
| unemployed / L2 (+ facts block) | 1.00 | 0.99 | 1.00 |
| unemployed / L4 (+ computed gap) | 1.00 | 1.00 | 1.00 |

- unemployed minus none, SUFFICIENT accuracy, L0: q1_direct -0.60 [-0.66, -0.53]; q1_direct_rev -0.63 [-0.71, -0.54] (base-clustered bootstrap, 2000).
- employed minus none: 0.00 at every level.
- Anti-monotonic: in unemployed/L0, mean P(SUFFICIENT) falls as the surplus grows (+2%: 0.83, +5%: 0.59, +10%: 0.28, +20%: 0.26, +40%: 0.15). Not a threshold shift. Unexplained; must be explained or controlled before any claim.

Open confounds before this can be a finding:
- C1 length/content: the unemployed prose adds job-loss and job-search sentences; employed adds one sentence. Need length-matched contexts.
- C2 which sentence drives it: job loss vs. "no job offers / no paid work" vs. the job-search sentences.
- C3 one model only (Ministral rerun in progress).

## Oracle-ladder diagnostic, Ministral-3-8B, sequence-level (2026-10-05)

Prefix check: 0 mismatches. SUFFICIENT-item accuracy:

| condition | q1_yesno | q1_direct | q1_direct_rev |
| --- | --- | --- | --- |
| none / L0 | 0.98 | 0.81 | 1.00 |
| employed / L0 | 0.88 | 0.51 | 1.00 |
| unemployed / L0 | 1.00 | 0.60 | 0.99 |
| unemployed / L2 | 1.00 | 1.00 | 1.00 |
| unemployed / L4 | 1.00 | 1.00 | 1.00 |

- q1_direct L0: unemployed-none -0.21 [-0.31, -0.10]; employed-none -0.30 [-0.37, -0.22]. Reversing option order removes it -> option-order prior, not social context.
- Shared across both models: errors are one-directional (toward SHORTFALL); structured restatement (L2/L4) removes them; yes/no is robust.
- NOT shared: unemployed-specific failure (Qwen3-8B only so far).
