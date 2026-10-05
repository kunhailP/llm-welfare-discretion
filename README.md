# Separating Material Need from Deservingness in LM Evaluation — research hub

Target: NAACL 2027 via ARR (deadline: see lit/literature_review.md, being verified).
Hardware: RunPod 1x L40 48GB. Persistent volume: /workspace (this folder). Container disk (/root) is NOT persistent.

## Start here
- docs/00_NORTH_STAR.md — novelty + NAACL fit criteria (read first, before any design decision)
- docs/00_source_design_v0.1_NOTE.md — summary of the v0.1 design received
- docs/01_critical_review.md — critique, required changes (R1-R6), go/no-go table
- docs/02_data_spec.md — datasets D0-D4, schema, queries
- docs/decisions.md — decision log (update on every design change)
- lit/literature_review.md, lit/references.bib — verified prior work

## Layout
| path | content |
| --- | --- |
| configs/models.yaml | pinned model revisions |
| configs/prompts.yaml | Q1-Q5 prompts (freeze after pilot) |
| data/external/fairfund-bench | FairFund-Bench clone (commit 74b75f3) |
| data/external/fairfund_need_probe.jsonl | D3: 150 FairFund stimuli for need-only probe |
| data/pilot/profiles.jsonl | D1-pilot + controls: 50 bases, 700 profiles (dev only; its 50 bases are reused by the oracle ladder) |
| src/gen/ | make_profiles.py, make_fairfund_probe.py |
| src/run/ | download_models.sh, run_vllm.py |
| src/eval/score.py | parsing, accuracy, flip rate, spurious gap with cluster bootstrap |
| results/, logs/ | outputs and logs |

## Environment
    source /workspace/venv/bin/activate   # python 3.12, vllm, pandas
    export HF_HOME=/workspace/hf           # model cache (persistent)

## Pilot commands
    python src/run/run_vllm.py --model qwen3-8b --data data/pilot/profiles.jsonl \
      --queries q1_direct,q2_definition,q3_extraction,q4_need_severity,q5_deservingness \
      --out results/pilot/qwen3-8b.jsonl
    python src/eval/score.py --data data/pilot/profiles.jsonl --results results/pilot/qwen3-8b.jsonl
    python src/run/run_vllm.py --model qwen3-8b --data data/external/fairfund_need_probe.jsonl \
      --queries q4_need_severity,q5_deservingness --out results/fairfund/qwen3-8b.jsonl
