#!/usr/bin/env bash
# Queue (2026-10-05, user-approved): v1 audit dropped. 14B wording probe, then thinking-mode rules subsample 14B -> 32B -> 8B.
set -u
cd /workspace/welfare-need-naacl
source /workspace/venv/bin/activate
export HF_HOME=/workspace/hf
while pgrep -f "^python src/run/" > /dev/null; do sleep 15; done
python src/run/run_v2_wording_probe.py --model qwen3-14b --out results/v2/wording_probe/qwen3-14b.jsonl > logs/v2_wording_probe_qwen3-14b.log 2>&1 \
  && echo "[$(date -Is)] probe done qwen3-14b" || echo "[$(date -Is)] probe FAILED qwen3-14b"
for m in qwen3-14b qwen3-32b-awq qwen3-8b; do
  echo "[$(date -Is)] think $m"
  python src/run/run_rules_think.py --model $m --out results/rules_think/$m.jsonl > logs/rules_think_$m.log 2>&1 \
    && echo "[$(date -Is)] think done $m" || echo "[$(date -Is)] think FAILED $m"
done
echo "[$(date -Is)] THINK QUEUE ALL DONE"
