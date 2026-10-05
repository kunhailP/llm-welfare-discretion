#!/usr/bin/env bash
# Audit before scaling (2026-10-05):
#  (a) order x vocabulary cross on the oracle ladder (sequence-level),
#  (b) effort within the unemployed context on pilot profiles (sequence-level),
#  (c) greedy generation on the ladder to check generated answers agree with probability verdicts.
set -u
cd /workspace/welfare-need-naacl
source /workspace/venv/bin/activate
export HF_HOME=/workspace/hf
# Design-B pilot runs first (inserted 2026-10-05; higher priority than this v1 audit)
bash src/run/run_rules_pilot.sh qwen3-8b qwen3-14b qwen3-32b-awq ministral3-8b > logs/run_rules_pilot.log 2>&1
Q6=q1_direct,q1_direct_rev,q1_yesno,q1_yesno_rev,q1_ab,q1_ab_rev
while pgrep -f "^python src/run/(run_vllm|score_labels_vllm)\.py" > /dev/null; do sleep 15; done
for m in "$@"; do
  echo "[$(date -Is)] seq $m"
  python src/run/score_labels_vllm.py --model $m \
    --spec "data/diagnostic/oracle_ladder.jsonl|q1_yesno_rev,q1_ab,q1_ab_rev|results/diagnostic_seq/${m}__audit.jsonl" \
    --spec "data/pilot/profiles.jsonl|$Q6|results/pilot_seq/$m.jsonl" \
    > logs/audit_seq_$m.log 2>&1 && echo "[$(date -Is)] seq done $m" || echo "[$(date -Is)] seq FAILED $m"
  echo "[$(date -Is)] gen $m"
  python src/run/run_vllm.py --model $m \
    --spec "data/diagnostic/oracle_ladder.jsonl|$Q6|results/diagnostic_gen/$m.jsonl" \
    > logs/audit_gen_$m.log 2>&1 && echo "[$(date -Is)] gen done $m" || echo "[$(date -Is)] gen FAILED $m"
done
echo "[$(date -Is)] ALL DONE"
