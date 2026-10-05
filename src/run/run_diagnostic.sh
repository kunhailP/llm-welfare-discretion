#!/usr/bin/env bash
# Oracle ladder x context x gap grid, first-token label probabilities. Waits for any running vLLM job first.
set -u
cd /workspace/welfare-need-naacl
source /workspace/venv/bin/activate
export HF_HOME=/workspace/hf
while pgrep -f "src/run/run_vllm.py" > /dev/null; do sleep 10; done
for m in "$@"; do
  echo "[$(date -Is)] start $m"
  python src/run/run_vllm.py --model $m --first-token-logprobs \
    --spec "data/diagnostic/oracle_ladder.jsonl|q1_yesno,q1_direct,q1_direct_rev|results/diagnostic/$m.jsonl" \
    > logs/diagnostic_$m.log 2>&1 && echo "[$(date -Is)] done $m" || echo "[$(date -Is)] FAILED $m (see logs/diagnostic_$m.log)"
done
