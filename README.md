# Deservingness in LLM welfare decisions: computation vs. discretion — research hub

Target: ACL 2027 via the January 2027 ARR cycle, at EMNLP-main quality. Hardware: RunPod 1x L40 48GB;
only /workspace persists.

## Current question (Design C, docs/11)
When an LLM makes a welfare (SNAP) decision, do legally irrelevant deservingness cues (job-search effort,
controllability of job loss) move the decision? Where does that happen: in rule-computable determinations,
or where the rules leave discretion or the facts are incomplete? Does reasoning remove it, and does an explicit
legal instruction to ignore the cue remove it?

## What we know so far (2026-10-05)
| setting | result | where |
| --- | --- | --- |
| Rule-computable eligibility, thinking off (4 models) | income tests at chance; cue effects exist, but on near-chance verdicts | docs/10 §1-2 |
| Same, thinking on (Qwen3-14B, 32B-AWQ) | income tests ~100% correct; cue effects 0 | docs/10 §5-6 |
| v1/v2 need-vs-sufficiency probes | direct-answer verdicts on aggregated facts follow a prior; wording/filler are not the cause | docs/decisions.md |
| Discretion + incomplete facts (Design C v2) | running | docs/11, docs/12 |

## Read in this order
1. docs/00_NORTH_STAR.md: novelty + venue-fit criteria
2. docs/decisions.md: decision log, newest first (source of truth)
3. docs/10_rules_pilot_results.md: rule-computable pilot, thinking off and on
4. docs/11_design_C_discretion.md: current design
5. docs/12_review2_response.md: external review 2 and what was adopted
6. Earlier stages: docs/01-09 (v1 need/deservingness profiles, controlled_v2, Design B)

## Active pipeline
| step | code | data / output |
| --- | --- | --- |
| SNAP rules-as-code (FY2026, P.L. 119-21 ABAWD) | src/rules/snap.py, tests/test_snap_rules.py | gold cross-checked with PolicyEngine-US (results/rules/crosscheck_pe.json) |
| Rule packet | configs/rule_packet_fy2026.md | |
| Rule-computable pilot | src/gen/make_rules_pilot.py | data/rules_pilot/pilot.jsonl |
| Discretion pilot (v1) | src/gen/make_discretion_pilot.py | data/discretion_pilot/ |
| Design C v2: discretion + missing facts, YES/NO/REQUEST, polarity flip, noise edits | src/gen/make_design_c_v2.py | data/design_c_v2/ |
| First-token runner (log-probs, both answer orders, thinking off) | src/run/run_rules_pilot.py | results/*/MODEL.jsonl (+ .meta.json provenance) |
| Thinking runner (Qwen3 thinking, gpt-oss) | src/run/run_rules_think.py | results/rules_think/, results/design_c_v2/think/ |
| Scorers (cluster bootstrap over bases) | src/eval/score_rules_pilot.py, score_rules_think.py, score_discretion.py, score_design_c_v2.py | results/*/score*.json |
| Queues | src/run/run_think_queue.sh, src/run/run_design_c_queue.sh | logs/ (not tracked) |

Models (pinned in configs/models.yaml): Qwen3-8B / 14B / 32B-AWQ, Ministral-3-8B, gpt-oss-20b. Open models only
until the design is final (no paid APIs).

## Environment
    source /workspace/venv/bin/activate   # python 3.12, vllm 0.30.0, transformers 5.14.1
    export HF_HOME=/workspace/hf

## Reproduce Design C v2
    python src/gen/make_design_c_v2.py --bases 40 --seed 17 --out data/design_c_v2/items.jsonl
    python src/run/run_rules_pilot.py --model qwen3-14b --data data/design_c_v2/items.jsonl \
      --out results/design_c_v2/firsttoken/qwen3-14b.jsonl
    python src/run/run_rules_think.py --model qwen3-14b --data data/design_c_v2/think_subset.jsonl --no-subsample \
      --out results/design_c_v2/think/qwen3-14b.jsonl
    python src/eval/score_design_c_v2.py results/design_c_v2/firsttoken/qwen3-14b.jsonl

Third-party data (SNAP QC public-use file, FairFund-Bench) is not redistributed; see docs/02_data_spec.md.
