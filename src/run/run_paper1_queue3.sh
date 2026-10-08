#!/usr/bin/env bash
# Paper 1 queue 3 (2026-10-08, after the blind reviews): confound checks.
#  (1) sanction clarification in the packet, direct readout, 4 models (does the controllability contrast survive?)
#  (2) decoding control: Qwen3-14B thinking on, greedy (T=0), same prompt
#  (3) Ministral-3-8B on the step-by-step prompt (no thinking mode): completes the ladder for the 4th model
set -u
export HF_HOME=/workspace/hf WN_ROOT=/root/llm-welfare-discretion PATH=/workspace/venv/bin:$PATH
PY=/workspace/venv/bin/python
cd /root/llm-welfare-discretion
until grep -q "QUEUE2 FINISHED" /workspace/logs/paper1_queue2.log; do sleep 30; done
step() { echo "[$(date -Is)] START $1"; }
done_() { echo "[$(date -Is)] DONE $1 (exit $2)"; }
mkdir -p results/rules_pilot_nosanction
for m in qwen3-14b qwen3-32b-awq qwen3-8b ministral3-8b; do
  step ft_nosanction_$m; $PY src/run/run_rules_pilot.py --model $m --data data/rules_pilot/pilot.jsonl --packet configs/rule_packet_fy2026_nosanction.md --out results/rules_pilot_nosanction/$m.jsonl > /workspace/logs/paper1_ft_nosanction_$m.log 2>&1; done_ ft_nosanction_$m $?
done
step 14b_greedy; $PY src/run/run_rules_think.py --model qwen3-14b --greedy --out results/rules_think/qwen3-14b_greedy.jsonl > /workspace/logs/paper1_14b_greedy.log 2>&1; done_ 14b_greedy $?
step ministral_off; $PY src/run/run_rules_think.py --model ministral3-8b --thinking off --out results/rules_think/ministral3-8b_off.jsonl > /workspace/logs/paper1_ministral_off.log 2>&1; done_ ministral_off $?
echo "[$(date -Is)] QUEUE3 FINISHED"
