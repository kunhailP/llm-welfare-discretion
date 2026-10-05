#!/usr/bin/env bash
# Design C queue (2026-10-05). Replaces run_discretion_queue.sh (its thinking runs are superseded by v2).
#  1) v1 discretion pilot, first-token, 4 models (fast first look)
#  2) gpt-oss-20b smoke (16 items) -> parse check
#  3) Design C v2 first-token, 4 models (12,160 items x 2 orders)
#  4) Design C v2 thinking subset (bases 0-9, 3,040 items): qwen3-14b, gpt-oss-20b (if smoke passed), qwen3-32b-awq
set -u
cd /workspace/welfare-need-naacl
source /workspace/venv/bin/activate
export HF_HOME=/workspace/hf
until grep -q "THINK QUEUE ALL DONE" logs/run_think_queue.log; do sleep 30; done
while pgrep -f "^python src/run/" > /dev/null; do sleep 15; done
for m in qwen3-14b qwen3-32b-awq qwen3-8b ministral3-8b; do
  python src/run/run_rules_pilot.py --model $m --data data/discretion_pilot/pilot.jsonl \
    --out results/discretion_pilot/$m.jsonl > logs/discretion_pilot_$m.log 2>&1 \
    && echo "[$(date -Is)] v1 firsttoken done $m" || echo "[$(date -Is)] v1 firsttoken FAILED $m"
done
python src/run/run_rules_think.py --model gpt-oss-20b --data data/design_c_v2/think_subset.jsonl --no-subsample --limit 16 \
  --out results/design_c_v2/smoke/gpt-oss-20b.jsonl > logs/smoke_gptoss.log 2>&1
OSS_OK=$(python -c "
import json
r=[json.loads(l) for l in open('results/design_c_v2/smoke/gpt-oss-20b.jsonl')]
print(int(sum(x['verdict'] in ('YES','NO','REQUEST') for x in r) >= 12))" 2>/dev/null || echo 0)
echo "[$(date -Is)] gpt-oss smoke ok=$OSS_OK"
for m in qwen3-14b qwen3-32b-awq qwen3-8b ministral3-8b; do
  python src/run/run_rules_pilot.py --model $m --data data/design_c_v2/items.jsonl \
    --out results/design_c_v2/firsttoken/$m.jsonl > logs/design_c_v2_ft_$m.log 2>&1 \
    && echo "[$(date -Is)] v2 firsttoken done $m" || echo "[$(date -Is)] v2 firsttoken FAILED $m"
done
TM="qwen3-14b"; [ "$OSS_OK" = "1" ] && TM="$TM gpt-oss-20b"; TM="$TM qwen3-32b-awq"
for m in $TM; do
  python src/run/run_rules_think.py --model $m --data data/design_c_v2/think_subset.jsonl --no-subsample \
    --out results/design_c_v2/think/$m.jsonl > logs/design_c_v2_think_$m.log 2>&1 \
    && echo "[$(date -Is)] v2 think done $m" || echo "[$(date -Is)] v2 think FAILED $m"
done
echo "[$(date -Is)] DESIGN C QUEUE ALL DONE"
