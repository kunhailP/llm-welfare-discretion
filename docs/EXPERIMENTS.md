# Experiment map

| Analysis | Inputs | Model outputs | Scorer / report |
| --- | --- | --- | --- |
| Original protocol comparison | `data/rules_pilot/pilot.jsonl`; stratified subsample in `src/run/run_rules_think.py` | `results/rules_pilot/`, `results/rules_think/` | `score_common_scale.py`; tables T2, T7, T8 |
| Sanction clarification | Original items; `configs/rule_packet_fy2026_nosanction.md` | `results/rules_pilot_nosanction/`; `results/rules_think/*nosanction*` | `score_rules_pilot.py`, `score_rules_think.py`; T9 |
| Need-sentence control | `pilot_plus_abawd_hardship.jsonl` | `results/rules_think/*abawd_hardship.jsonl` and matched original runs | `score_abawd_hardship.py` |
| Consequences and direction | Original eligibility pairs | Original direct and generated runs | `consequence.py`; T6; `score_household_sign.py` |
| Computation supply | `sub_income*.jsonl`, `sub12*.jsonl` | `results/computed/` | `score_computed.py`, `summarize_computed.py`, `score_block_delta.py`; T10, T12; main-text supply table |
| Confirmation | `conf13_elig.jsonl`, `conf13v2_elig.jsonl` | `results/confirmation/` | `score_computed.py`, `summarize_computed.py`; T11 |
| Independent gold check | Generated random households under the stated cross-check scope | `results/rules/crosscheck_pe.json` | `src/rules/crosscheck_pe.py` |

Paths without a directory prefix in the inputs column are under `data/rules_pilot/`; scorer filenames are under `src/eval/`.

## Samples

- Original testbed: 6,376 items from 40 sampled household structures. Margin filtering leaves 31 structures for gross income and 27 for eligibility.
- Main generated comparison: 1,554 narrative items; 60 gross, 74 eligibility and 150 ABAWD cue groups. Gross uses 29 structures; eligibility uses 27.
- Original computation-supply comparison: 804 income items, 60 gross and 74 eligibility groups. Direct inference was rerun on these rows; small numerical differences from the full-batch direct run are documented in the manuscript.
- Seed-12 extension: 786 income items, 39 usable structures across tasks (29 gross, 24 eligibility), 60 gross and 71 eligibility groups. Original and secondary cue phrasing are supplied.
- Seed-13 confirmation: 128 usable structures, 2,118 eligibility items and 353 groups per phrasing. The primary analysis uses free generation at two seeds in Qwen3-14B and Qwen3-32B-AWQ with the original phrasing.

## Interpretation and coverage

The main analysis compares high-minus-low cues on the binary verdict scale and bootstraps households, not individual repeated items. The original generated-run criterion was chosen after initial results and applied to replication seeds. The later confirmation has a dated pre-run plan. These have different evidential status.

The supplied block includes correct intermediate quantities without an answer. Its plain version omits both `under the rules in the packet` and `(verified)` from the prefix. It does not control the information or salience added by the quantities. The original plan's numerical decision rules are descriptive thresholds, not tests of a change in effect or equivalence.

Free generation with the secondary phrasing was not completed. The confirmation has no thinking-mode, Ministral or API run. Missing/invalid outputs remain in the released files and are excluded by the documented parsers, rather than silently repaired.
