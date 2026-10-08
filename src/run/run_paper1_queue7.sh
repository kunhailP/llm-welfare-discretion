#!/usr/bin/env bash
# Paper 1 queue 7 (2026-10-08, review round 5): free-generation rung (thinking off, no step-by-step instruction), seed 0.
set -u
export HF_HOME=/workspace/hf WN_ROOT=/root/llm-welfare-discretion PATH=/workspace/venv/bin:$PATH
PY=/workspace/venv/bin/python
cd /root/llm-welfare-discretion
step() { echo "[$(date -Is)] START $1"; }
done_() { echo "[$(date -Is)] DONE $1 (exit $2)"; }
step 32b_free; $PY src/run/run_rules_think.py --model qwen3-32b-awq --thinking off --prompt free --seed 0 --out results/rules_think/qwen3-32b-awq_free.jsonl > /workspace/logs/paper1_32b_free.log 2>&1; done_ 32b_free $?
step 14b_free; $PY src/run/run_rules_think.py --model qwen3-14b --thinking off --prompt free --seed 0 --out results/rules_think/qwen3-14b_free.jsonl > /workspace/logs/paper1_14b_free.log 2>&1; done_ 14b_free $?
step ministral_free; HF_HOME=/root/hf $PY src/run/run_rules_think.py --model ministral3-8b --thinking off --prompt free --seed 0 --out results/rules_think/ministral3-8b_free.jsonl > /workspace/logs/paper1_ministral_free.log 2>&1; done_ ministral_free $?
echo "[$(date -Is)] QUEUE7 FINISHED"
