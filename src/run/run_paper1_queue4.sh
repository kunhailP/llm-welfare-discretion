#!/usr/bin/env bash
# Paper 1 queue 4 (2026-10-08): the two Ministral steps of queue 3, rerun with the model cache on the local disk
# (/workspace hit its user quota while vLLM auto-downloaded Ministral). Waits for queue 3 and for the download.
set -u
export HF_HOME=/root/hf WN_ROOT=/root/llm-welfare-discretion PATH=/workspace/venv/bin:$PATH
PY=/workspace/venv/bin/python
cd /root/llm-welfare-discretion
until grep -q "QUEUE3 FINISHED" /workspace/logs/paper1_queue3.log && [ -f /root/hf/MINISTRAL_READY ]; do sleep 30; done
step() { echo "[$(date -Is)] START $1"; }
done_() { echo "[$(date -Is)] DONE $1 (exit $2)"; }
step ft_nosanction_ministral3-8b; $PY src/run/run_rules_pilot.py --model ministral3-8b --data data/rules_pilot/pilot.jsonl --packet configs/rule_packet_fy2026_nosanction.md --out results/rules_pilot_nosanction/ministral3-8b.jsonl > /workspace/logs/paper1_ft_nosanction_ministral3-8b_q4.log 2>&1; done_ ft_nosanction_ministral3-8b $?
step ministral_off; $PY src/run/run_rules_think.py --model ministral3-8b --thinking off --out results/rules_think/ministral3-8b_off.jsonl > /workspace/logs/paper1_ministral_off_q4.log 2>&1; done_ ministral_off $?
echo "[$(date -Is)] QUEUE4 FINISHED"
