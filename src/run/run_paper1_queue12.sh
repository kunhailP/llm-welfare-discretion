#!/bin/bash
# Paper 1 queue 12 (pre-registered 2026-10-12 17:50 UTC, docs/paper1/confirmation_study.md; trimmed 18:00 on the PI's call; robust
# skip / fail / lock logic 18:20): confirmation study on new households after queue 11. Primary: free generation, seeds 0 and 1,
# Qwen3-14B and Qwen3-32B-AWQ, phrasing v1 (conf13_elig); secondary: direct readout, phrasing v2 on 14B. Deferred: thinking on, Ministral.
set -u
source /workspace/logs/env.sh
REPO=${WN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}; export WN_ROOT=$REPO; cd "$REPO"
source src/run/queue_lib.sh
LOG=/workspace/logs/queue10.log; OUT=results/confirmation; mkdir -p $OUT
D=data/rules_pilot
wait_for "queue 10 done" "queue 10 FAILED"  # 20:25 UTC: runs before queue 11 (Ministral weights had to be re-downloaded to /root; the confirmation study no longer depends on it)
say "queue 12 start"
for m in qwen3-14b qwen3-32b-awq; do for f in conf13_elig conf13v2_elig; do
  run_model ${m}_${f}_direct $D/$f.jsonl 2 $PY src/run/run_rules_pilot.py --model $m --data $D/$f.jsonl --out $OUT/${m}_${f}_direct.jsonl
done; done
for m in qwen3-14b qwen3-32b-awq; do for s in 0 1; do
  run_model ${m}_conf13_elig_free_s$s $D/conf13_elig.jsonl 1 \
    $PY src/run/run_rules_think.py --model $m --prompt free --thinking off --no-subsample --seed $s --data $D/conf13_elig.jsonl --out $OUT/${m}_conf13_elig_free_s$s.jsonl
done; done
run_model qwen3-14b_conf13v2_elig_free_s0 $D/conf13v2_elig.jsonl 1 \
  $PY src/run/run_rules_think.py --model qwen3-14b --prompt free --thinking off --no-subsample --seed 0 --data $D/conf13v2_elig.jsonl --out $OUT/qwen3-14b_conf13v2_elig_free_s0.jsonl
finish "queue 12"
