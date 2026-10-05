#!/usr/bin/env bash
# Design-B pilot (2026-10-05): rule-relevance x deservingness cues, YES/NO first-token scoring.
set -u
cd /workspace/welfare-need-naacl
source /workspace/venv/bin/activate
export HF_HOME=/workspace/hf
while pgrep -f "^python src/run/(run_vllm|score_labels_vllm|run_rules_pilot)\.py" > /dev/null; do sleep 15; done
for m in "$@"; do
  echo "[$(date -Is)] rules pilot $m"
  python src/run/run_rules_pilot.py --model $m --data data/rules_pilot/pilot.jsonl \
    --out results/rules_pilot/$m.jsonl > logs/rules_pilot_$m.log 2>&1 \
    && echo "[$(date -Is)] done $m" || echo "[$(date -Is)] FAILED $m"
done
R=""; for m in "$@"; do [ -s results/rules_pilot/$m.jsonl ] && R="$R --results results/rules_pilot/$m.jsonl"; done
python src/eval/score_rules_pilot.py $R > results/rules_pilot/score.json 2> logs/score_rules_pilot.log && echo "[$(date -Is)] scored" || echo "[$(date -Is)] scoring FAILED"
echo "[$(date -Is)] RULES PILOT ALL DONE"
