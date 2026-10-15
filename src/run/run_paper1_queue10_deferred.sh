#!/bin/bash
# Deferred runs (not launched automatically): Ministral free on the seed-12 households is not needed; seed-12 free for 32B and
# phrasing v2 (14B, 32B); confirmation study thinking-on (14B, 32B) and Ministral free. Waits for queue 12 (fixed 18:20: wait before any run).
set -u
source /workspace/logs/env.sh
REPO=${WN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}; export WN_ROOT=$REPO; cd "$REPO"
source src/run/queue_lib.sh
LOG=/workspace/logs/queue10.log; D=data/rules_pilot
wait_for "queue 12 done" "queue 12 FAILED"
say "deferred start"
OUT=results/computed; mkdir -p $OUT
for m in qwen3-32b-awq; do for f in sub12_income sub12_income_computed; do for s in 0 1; do
  run_model ${m}_${f}_free_s$s $D/$f.jsonl 1 $PY src/run/run_rules_think.py --model $m --prompt free --thinking off --no-subsample --seed $s --data $D/$f.jsonl --out $OUT/${m}_${f}_free_s$s.jsonl
done; done; done
for m in qwen3-14b qwen3-32b-awq; do for f in sub12v2_income sub12v2_income_computed; do for s in 0 1; do
  run_model ${m}_${f}_free_s$s $D/$f.jsonl 1 $PY src/run/run_rules_think.py --model $m --prompt free --thinking off --no-subsample --seed $s --data $D/$f.jsonl --out $OUT/${m}_${f}_free_s$s.jsonl
done; done; done
OUT=results/confirmation; mkdir -p $OUT
for m in qwen3-14b qwen3-32b-awq; do
  run_model ${m}_conf13_elig_think_s0 $D/conf13_elig.jsonl 1 $PY src/run/run_rules_think.py --model $m --thinking on --no-subsample --seed 0 --data $D/conf13_elig.jsonl --out $OUT/${m}_conf13_elig_think_s0.jsonl
done
run_model ministral3-8b_conf13_elig_free_s0 $D/conf13_elig.jsonl 1 $PY src/run/run_rules_think.py --model ministral3-8b --prompt free --thinking off --no-subsample --seed 0 --data $D/conf13_elig.jsonl --out $OUT/ministral3-8b_conf13_elig_free_s0.jsonl
finish "deferred"
