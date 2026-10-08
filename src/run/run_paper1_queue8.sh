#!/usr/bin/env bash
# Paper 1 queue 8 (2026-10-08, round 6): free-generation rung, seed 1 (replicate of queue 7). Last run before the pod shutdown.
set -u
export HF_HOME=/workspace/hf WN_ROOT=/root/llm-welfare-discretion PATH=/workspace/venv/bin:$PATH
PY=/workspace/venv/bin/python
cd "$(dirname "$0")/../.."
step() { echo "[$(date -Is)] START $1"; }
done_() { echo "[$(date -Is)] DONE $1 (exit $2)"; }
step 32b_free_s1; $PY src/run/run_rules_think.py --model qwen3-32b-awq --thinking off --prompt free --seed 1 --out results/rules_think/qwen3-32b-awq_free_s1.jsonl > /workspace/logs/paper1_32b_free_s1.log 2>&1; done_ 32b_free_s1 $?
step 14b_free_s1; $PY src/run/run_rules_think.py --model qwen3-14b --thinking off --prompt free --seed 1 --out results/rules_think/qwen3-14b_free_s1.jsonl > /workspace/logs/paper1_14b_free_s1.log 2>&1; done_ 14b_free_s1 $?
step ministral_free_s1; HF_HOME=/root/hf $PY src/run/run_rules_think.py --model ministral3-8b --thinking off --prompt free --seed 1 --out results/rules_think/ministral3-8b_free_s1.jsonl > /workspace/logs/paper1_ministral_free_s1.log 2>&1; done_ ministral_free_s1 $?
echo "[$(date -Is)] QUEUE8 FINISHED"
