#!/usr/bin/env bash
# Design C queue 2 (2026-10-05, after review of 370c219): if-and-only-if standards, packet without the
# "case file is complete" line (configs/rule_packet_fy2026_c.md), psychometric set first.
#  1) psych first-token (4 models)      2) v2 first-token (4 models)
#  3) gpt-oss-20b smoke on psych         4) psych thinking subset (3,072): 14B on s0, 14B OFF s0 (same CoT prompt),
#     14B on s1 (seed baseline), gpt-oss-20b (if smoke ok), 32B on s0      5) v2 thinking subset: 14B on s0
set -u
cd /workspace/welfare-need-naacl
source /workspace/venv/bin/activate
export HF_HOME=/workspace/hf
PK=configs/rule_packet_fy2026_c.md
while pgrep -f "^python src/run/" > /dev/null; do sleep 15; done
ft() {  # data out-dir model
  python src/run/run_rules_pilot.py --model $3 --data $1 --packet $PK --out $2/$3.jsonl > logs/ft_$(basename $2)_$3.log 2>&1 \
    && echo "[$(date -Is)] ft done $2 $3" || echo "[$(date -Is)] ft FAILED $2 $3"
}
th() {  # data out-file model extra-args...
  d=$1; o=$2; m=$3; shift 3
  python src/run/run_rules_think.py --model $m --data $d --no-subsample --packet $PK --out $o "$@" > logs/th_$(basename $o .jsonl).log 2>&1 \
    && echo "[$(date -Is)] th done $o" || echo "[$(date -Is)] th FAILED $o"
}
for m in qwen3-14b qwen3-32b-awq qwen3-8b ministral3-8b; do ft data/design_c_psych/items.jsonl results/design_c_psych/firsttoken $m; done
for m in qwen3-14b qwen3-32b-awq qwen3-8b ministral3-8b; do ft data/design_c_v2/items.jsonl results/design_c_v2/firsttoken $m; done
th data/design_c_psych/think_subset.jsonl results/design_c_psych/smoke/gpt-oss-20b.jsonl gpt-oss-20b --limit 16
OSS_OK=$(python -c "
import json
r=[json.loads(l) for l in open('results/design_c_psych/smoke/gpt-oss-20b.jsonl')]
print(int(sum(x['verdict'] in ('YES','NO') for x in r) >= 12))" 2>/dev/null || echo 0)
echo "[$(date -Is)] gpt-oss smoke ok=$OSS_OK"
S=data/design_c_psych/think_subset.jsonl; R=results/design_c_psych/think
th $S $R/qwen3-14b__on_s0.jsonl qwen3-14b --thinking on --seed 0
th $S $R/qwen3-14b__off_s0.jsonl qwen3-14b --thinking off --seed 0
th $S $R/qwen3-14b__on_s1.jsonl qwen3-14b --thinking on --seed 1
[ "$OSS_OK" = "1" ] && th $S $R/gpt-oss-20b__s0.jsonl gpt-oss-20b --seed 0
th $S $R/qwen3-32b-awq__on_s0.jsonl qwen3-32b-awq --thinking on --seed 0
th data/design_c_v2/think_subset.jsonl results/design_c_v2/think/qwen3-14b__on_s0.jsonl qwen3-14b --thinking on --seed 0
echo "[$(date -Is)] DESIGN C QUEUE2 ALL DONE"
