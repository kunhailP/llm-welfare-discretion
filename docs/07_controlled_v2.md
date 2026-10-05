# Controlled item set v2 (2026-10-05)

Purpose: separate the parts of the bundled "unemployed context" and test new fact surfaces, as the
external review required. Generator: src/gen/make_controlled_v2.py. Prompts: configs/prompts_v2.yaml.
Scorer: src/eval/score_controlled_v2.py (passes an oracle check: accuracy 1.00, 0 monotonicity
violations, all context differences 0).

## Items

| split | bases | funds levels | contexts | items | pools | status |
| --- | --- | --- | --- | --- | --- | --- |
| dev | 20 | 8 | 10 | 1,600 | pilot pools (already seen) | run queued after audit |
| test | 60 | 8 | 10 | 4,800 | new disjoint pools, seed 23 | **unseen; run only after human review** |

- Funds levels (funds - bills) / bills: -0.20, -0.05, -0.02, 0 (exactly equal, gold SUFFICIENT), +0.02, +0.05, +0.20, +0.40.
  True shortfall share is 3/8 in every context, so every context difference is 0 by design.
- Bills $600-$3,600 (pilot was $800-$2,400). Surfaces balanced across bases: totals vs itemized x funds-first vs bills-first.
- Same named subject in every person context. Context block always has 4 sentences (content first, neutral fillers after);
  word-count spread within a base: mean 5, max 13 words (report as a covariate).

## Context ladder (4 sentence slots)

| context | slots | isolates |
| --- | --- | --- |
| none | F F F F | baseline |
| employed | E F F F | employment status (employed) |
| unemp_status | U F F F | "is currently unemployed" alone |
| unemp_cause | L U F F | + job-loss event |
| unemp_nopay | L U N F | + no paid work for four weeks |
| search_high / search_low | L U N S | effort minimal pair (8 of 8 vs 1 of 8 openings) |
| lexical_closure | C F F F | negative "closed" wording without money/employment content |
| budget_none / budget_loss | P P P P / K P P P | non-welfare task: a community project; sponsor withdrew funding |

## Queries (each a separate conversation; argmax over full candidate strings, mapped to meaning)

vocabulary {need labels, YES/NO, A/B} x option order; YES/NO also x question polarity ("can be paid" vs "will fall short");
A/B also x letter assignment ("cannot" = A or B) x position (first/second). Plus v2_extract (model extracts totals; code compares) for the mitigation bundle.

## Human review (before any test run)

data/review/v2_test_sheet.csv: 600 rows (one funds level per test base, all 10 contexts, shuffled), blind to gold and models.
Columns: can the bills be paid (gold check), contradictory/unclear, naturalness 1-5, and a manipulation check
(employment stated, effort 1-5, responsibility 1-5). Key file is git-ignored.
