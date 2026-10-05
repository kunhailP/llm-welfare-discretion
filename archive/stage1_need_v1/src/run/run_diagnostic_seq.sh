#!/usr/bin/env bash
set -u
cd /workspace/welfare-need-naacl
source /workspace/venv/bin/activate
export HF_HOME=/workspace/hf
while pgrep -f "src/run/run_vllm.py|run_diagnostic.sh" > /dev/null; do sleep 10; done
for m in "$@"; do
  echo "[$(date -Is)] start $m"
  python src/run/score_labels_vllm.py --model $m \
    --spec "data/diagnostic/oracle_ladder.jsonl|q1_yesno,q1_direct,q1_direct_rev|results/diagnostic_seq/$m.jsonl" \
    > logs/diagnostic_seq_$m.log 2>&1 && echo "[$(date -Is)] done $m" || echo "[$(date -Is)] FAILED $m"
done
