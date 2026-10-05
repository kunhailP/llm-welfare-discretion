#!/usr/bin/env bash
# controlled_v2 DEV only (test set stays unseen until human review is complete).
set -u
cd /workspace/welfare-need-naacl
source /workspace/venv/bin/activate
export HF_HOME=/workspace/hf
V2Q=v2_need_shortfirst,v2_need_sufffirst,v2_yn_can_yesfirst,v2_yn_can_nofirst,v2_yn_short_yesfirst,v2_yn_short_nofirst,v2_ab_Acannot_first,v2_ab_Bcannot_second,v2_ab_Bcannot_first,v2_ab_Acannot_second
while pgrep -f "^python src/run/(run_vllm|score_labels_vllm)\.py" > /dev/null; do sleep 15; done
for m in "$@"; do
  echo "[$(date -Is)] seq $m"
  python src/run/score_labels_vllm.py --model $m --prompts configs/prompts_v2.yaml \
    --spec "data/controlled_v2/dev.jsonl|$V2Q|results/v2/dev_seq/$m.jsonl" > logs/v2dev_seq_$m.log 2>&1 \
    && echo "[$(date -Is)] seq done $m" || echo "[$(date -Is)] seq FAILED $m"
  echo "[$(date -Is)] gen+extract $m"
  python src/run/run_vllm.py --model $m --prompts configs/prompts_v2.yaml \
    --spec "data/controlled_v2/dev.jsonl|$V2Q|results/v2/dev_gen/$m.jsonl" \
    --spec "data/controlled_v2/dev.jsonl|v2_extract|results/v2/dev_extract/$m.jsonl" > logs/v2dev_gen_$m.log 2>&1 \
    && echo "[$(date -Is)] gen done $m" || echo "[$(date -Is)] gen FAILED $m"
done
echo "[$(date -Is)] ALL DONE"
