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
| Discretion, first-token (psych set + v2, 4 models) | enum standards followed (14B/32B 100%); open standards flat in need; cue "effects" are a polarity-dependent yes-bias | docs/11 Results 2-4 |
| Discretion, thinking (primary test of H1-H3) | **not run: Design C stopped after audit blocker B1 (decision undefined in the prompt)** | docs/14 |
| Stage 1 (v1 need-vs-sufficiency probes) | explicit need items solved at 14B; 8B failures were format effects | archive/ |

## Read in this order
0. **docs/14_audit_stop_and_restart.md: why Design C stopped and the restart plan (start here)**
1. docs/00_NORTH_STAR.md: novelty + venue-fit criteria
2. docs/decisions.md: decision log, newest first (source of truth)
3. docs/13_preregistration_freeze.md: frozen task set, hypotheses H1-H3, analysis plan, pre-set fallback rule
4. docs/11_design_C_discretion.md: current design and results
5. docs/12_review2_response.md: external review 2 and what was adopted
6. docs/09_design_B.md, docs/10_rules_pilot_results.md: rule-computable reference (Design B)
7. archive/README.md: earlier stage (v1) and finished queues

## Layout
    configs/   models.yaml (pinned revisions), rule packets (fy2026 = Design B, fy2026_c = Design C), requirements lock
    src/rules/ SNAP rules-as-code + PolicyEngine cross-check      tests/  rule tests (pytest)
    src/gen/   item generators (rules pilot -> discretion pilot -> Design C v2 / psych)
    src/run/   first-token runner, thinking runner, live queue
    src/eval/  scorers (cluster bootstrap over bases)
    data/      generated items (rules_pilot, discretion_pilot, design_c_v2, design_c_psych); external/ not redistributed
    results/   model outputs + .meta.json provenance + scores, one folder per item set
    lit/       literature notes and references.bib
    archive/   finished stages, kept for the record
    logs/      run logs (not tracked)

## Active pipeline
| step | code | data / output |
| --- | --- | --- |
| SNAP rules-as-code (FY2026, P.L. 119-21 ABAWD) | src/rules/snap.py, tests/test_snap_rules.py | gold cross-checked with PolicyEngine-US (results/rules/crosscheck_pe.json) |
| Rule packets | configs/rule_packet_fy2026.md (Design B), configs/rule_packet_fy2026_c.md (Design C) | |
| Rule-computable reference (Design B) | src/gen/make_rules_pilot.py | data/rules_pilot/, results/rules_pilot/, results/rules_think/ |
| Discretion pilot v1 | src/gen/make_discretion_pilot.py | data/discretion_pilot/, results/discretion_pilot/ |
| Design C v2: enum/open standards + missing hours, YES/NO/REQUEST, polarity flip, noise edits | src/gen/make_design_c_v2.py | data/design_c_v2/, results/design_c_v2/ |
| Design C psych: shortfall ladder x prohibit x cue, PSE in dollars | src/gen/make_design_c_psych.py | data/design_c_psych/, results/design_c_psych/ |
| First-token runner (log-probs, both answer orders, thinking off) | src/run/run_rules_pilot.py | results/<set>/firsttoken/MODEL.jsonl (+ .meta.json) |
| Thinking runner (Qwen3 thinking on/off, gpt-oss) | src/run/run_rules_think.py | results/<set>/think/MODEL__<mode>_s<seed>.jsonl |
| Scorers | src/eval/score_rules_pilot.py, score_rules_think.py, score_discretion*.py, score_design_c_v2.py, score_design_c_psych.py | results/<set>/score*.json |
| Live queue | src/run/run_design_c_queue2.sh | logs/run_design_c_queue2.log |

Models (pinned in configs/models.yaml): Qwen3-8B / 14B / 32B-AWQ, Ministral-3-8B, gpt-oss-20b. Open models only
until the design is final (no paid APIs).

## Environment
    source /workspace/venv/bin/activate   # python 3.12, vllm 0.30.0, transformers 5.14.1
    export HF_HOME=/workspace/hf

## Reproduce Design C (psych set; v2 is the same with make_design_c_v2.py / score_design_c_v2.py)
    python src/gen/make_design_c_psych.py --bases 20 --seed 19 --out data/design_c_psych/items.jsonl
    python src/run/run_rules_pilot.py --model qwen3-14b --data data/design_c_psych/items.jsonl \
      --packet configs/rule_packet_fy2026_c.md --out results/design_c_psych/firsttoken/qwen3-14b.jsonl
    python src/run/run_rules_think.py --model qwen3-14b --data data/design_c_psych/think_subset.jsonl --no-subsample \
      --packet configs/rule_packet_fy2026_c.md --thinking on --seed 0 --out results/design_c_psych/think/qwen3-14b__on_s0.jsonl
    python src/eval/score_design_c_psych.py results/design_c_psych/think/qwen3-14b__on_s0.jsonl

Third-party data (SNAP QC public-use file, FairFund-Bench) is not redistributed; see archive/stage1_need_v1/docs/02_data_spec.md.
