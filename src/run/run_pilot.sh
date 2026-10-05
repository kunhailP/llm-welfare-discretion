#!/usr/bin/env bash
# Pilot: all 700 dev profiles x 7 queries + FairFund probe x 2 queries, one model load per model.
set -u
cd /workspace/welfare-need-naacl
source /workspace/venv/bin/activate
export HF_HOME=/workspace/hf
Q=q1_direct,q1_direct_rev,q1_yesno,q2_definition,q3_extraction,q4_need_severity,q5_deservingness
for m in "$@"; do
  echo "[$(date -Is)] start $m"
  python src/run/run_vllm.py --model $m \
    --spec "data/pilot/profiles.jsonl|$Q|results/pilot/$m.jsonl" \
    --spec "data/external/fairfund_need_probe.jsonl|q4_need_severity,q5_deservingness|results/fairfund/$m.jsonl" \
    > logs/pilot_$m.log 2>&1 && echo "[$(date -Is)] done $m" || echo "[$(date -Is)] FAILED $m (see logs/pilot_$m.log)"
  python src/eval/score.py --data data/pilot/profiles.jsonl --results results/pilot/$m.jsonl > results/pilot/$m.score.json 2> logs/score_$m.log
  python src/eval/score_fairfund.py --results results/fairfund/$m.jsonl > results/fairfund/$m.score.json 2>> logs/score_$m.log
done
