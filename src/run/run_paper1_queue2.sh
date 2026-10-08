#!/usr/bin/env bash
# Paper 1 queue 2 (2026-10-08): replicate the thinking-off ladder with a second seed (32B first: the directional ABAWD leak).
set -u
export HF_HOME=/workspace/hf WN_ROOT=/root/llm-welfare-discretion PATH=/workspace/venv/bin:$PATH
PY=/workspace/venv/bin/python
cd /root/llm-welfare-discretion
step() { echo "[$(date -Is)] START $1"; }
done_() { echo "[$(date -Is)] DONE $1 (exit $2)"; }
step 32b_off_s1; $PY src/run/run_rules_think.py --model qwen3-32b-awq --thinking off --seed 1 --out results/rules_think/qwen3-32b-awq_off_s1.jsonl > /workspace/logs/paper1_32b_off_s1.log 2>&1; done_ 32b_off_s1 $?
step 14b_off_s1; $PY src/run/run_rules_think.py --model qwen3-14b --thinking off --seed 1 --out results/rules_think/qwen3-14b_off_s1.jsonl > /workspace/logs/paper1_14b_off_s1.log 2>&1; done_ 14b_off_s1 $?
echo "[$(date -Is)] QUEUE2 FINISHED"
