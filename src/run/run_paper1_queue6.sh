#!/usr/bin/env bash
# Paper 1 queue 6 (2026-10-08, blind-review round 4): hardship control (car sentence) on the ABAWD subsample cells, Qwen3-32B-AWQ.
set -u
export HF_HOME=/workspace/hf WN_ROOT=/root/llm-welfare-discretion PATH=/workspace/venv/bin:$PATH
PY=/workspace/venv/bin/python; D=data/rules_pilot/pilot_plus_abawd_hardship.jsonl
cd /root/llm-welfare-discretion
step() { echo "[$(date -Is)] START $1"; }
done_() { echo "[$(date -Is)] DONE $1 (exit $2)"; }
step 32b_off_s0_hardship; $PY src/run/run_rules_think.py --model qwen3-32b-awq --thinking off --seed 0 --data $D --only-cues valence_neg --only-tasks abawd --out results/rules_think/qwen3-32b-awq_off_abawd_hardship.jsonl > /workspace/logs/paper1_32b_off_hardship.log 2>&1; done_ 32b_off_s0_hardship $?
step 32b_off_s1_hardship; $PY src/run/run_rules_think.py --model qwen3-32b-awq --thinking off --seed 1 --data $D --only-cues valence_neg --only-tasks abawd --out results/rules_think/qwen3-32b-awq_off_s1_abawd_hardship.jsonl > /workspace/logs/paper1_32b_off_s1_hardship.log 2>&1; done_ 32b_off_s1_hardship $?
step 32b_on_s0_hardship; $PY src/run/run_rules_think.py --model qwen3-32b-awq --thinking on --seed 0 --data $D --only-cues valence_neg --only-tasks abawd --out results/rules_think/qwen3-32b-awq_abawd_hardship.jsonl > /workspace/logs/paper1_32b_on_hardship.log 2>&1; done_ 32b_on_s0_hardship $?
echo "[$(date -Is)] QUEUE6 FINISHED"
