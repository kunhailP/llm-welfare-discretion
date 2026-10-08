#!/usr/bin/env bash
# Paper 1 additions (2026-10-08, L40): seed replicate of the thinking subsample on 14B / 32B / 8B, the same-prompt
# thinking-off ladder on 14B / 32B, then the Design D smoke + competence runs for the evidence repo.
# Each step ~10-35 min (reference: seed-0 runs took 1509 s / 1932 s / 1278 s). Logs: /workspace/logs/paper1_<step>.log
set -u
export HF_HOME=/workspace/hf WN_ROOT=/root/llm-welfare-discretion
export PATH=/workspace/venv/bin:$PATH   # FlashInfer's sampling kernel is JIT-compiled and calls `ninja`, which lives in the venv bin
PY=/workspace/venv/bin/python
cd /root/llm-welfare-discretion
step() { echo "[$(date -Is)] START $1"; }
done_() { echo "[$(date -Is)] DONE $1 (exit $2)"; }

step 14b_seed1;  $PY src/run/run_rules_think.py --model qwen3-14b --seed 1 --out results/rules_think/qwen3-14b_s1.jsonl > /workspace/logs/paper1_14b_seed1.log 2>&1; done_ 14b_seed1 $?
step 14b_off;    $PY src/run/run_rules_think.py --model qwen3-14b --thinking off --out results/rules_think/qwen3-14b_off.jsonl > /workspace/logs/paper1_14b_off.log 2>&1; done_ 14b_off $?
step 32b_seed1;  $PY src/run/run_rules_think.py --model qwen3-32b-awq --seed 1 --out results/rules_think/qwen3-32b-awq_s1.jsonl > /workspace/logs/paper1_32b_seed1.log 2>&1; done_ 32b_seed1 $?
step 8b_seed1;   $PY src/run/run_rules_think.py --model qwen3-8b --seed 1 --out results/rules_think/qwen3-8b_s1.jsonl > /workspace/logs/paper1_8b_seed1.log 2>&1; done_ 8b_seed1 $?
step 32b_off;    $PY src/run/run_rules_think.py --model qwen3-32b-awq --thinking off --out results/rules_think/qwen3-32b-awq_off.jsonl > /workspace/logs/paper1_32b_off.log 2>&1; done_ 32b_off $?

# Design D (evidence repo): neutral smoke (22) then competence (352) on Qwen3-8B, as docs/RUNPOD_EVIDENCE_PILOT.md says.
cd /root/llm-welfare-evidence
step evidence_smoke; $PY src/run/run_evidence_pilot.py --model qwen3-8b --cue neutral --base-limit 3 --orders forward --out results/evidence_pilot/qwen3-8b_smoke.jsonl > /workspace/logs/evidence_smoke.log 2>&1; done_ evidence_smoke $?
step evidence_neutral; $PY src/run/run_evidence_pilot.py --model qwen3-8b --cue neutral --orders forward,reverse --out results/evidence_pilot/qwen3-8b_neutral.jsonl > /workspace/logs/evidence_neutral.log 2>&1; done_ evidence_neutral $?
echo "[$(date -Is)] QUEUE FINISHED"
