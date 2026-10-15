#!/bin/bash
# Paper 1 queue 10 (2026-10-12 16:20 UTC): computation burden x response format (pre-registered in docs/paper1/computed_burden.md).
# Direct (first-token) and free (generation, no instruction to reason, thinking off) readouts on the income rows of the
# thinking subsample, with and without a block of correct intermediate quantities; then the same on a new household set
# (seed 12, bases b100-b139) under the original (v1) and a second (v2) cue phrasing.
set -u
source /workspace/logs/env.sh
REPO=${WN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}; export WN_ROOT=$REPO; cd $REPO
PY=/workspace/venv_evidence/bin/python
LOG=/workspace/logs/queue10.log; OUT=results/computed; mkdir -p $OUT
say () { echo "=== $* $(date -u +%H:%M:%S)" | tee -a $LOG; }
direct () { local m=$1 f=$2; local name=${m}_${f}_direct
  [ -f $OUT/$name.jsonl ] && { say "skip $name"; return; }
  say "start $name"; $PY src/run/run_rules_pilot.py --model $m --data data/rules_pilot/$f.jsonl --out $OUT/$name.jsonl > /workspace/logs/paper1_q10_$name.log 2>&1 && say "done $name" || say "FAILED $name"; }
free () { local m=$1 f=$2 s=$3; local name=${m}_${f}_free_s$s
  [ -f $OUT/$name.jsonl ] && { say "skip $name"; return; }
  say "start $name"; $PY src/run/run_rules_think.py --model $m --prompt free --thinking off --no-subsample --seed $s --data data/rules_pilot/$f.jsonl --out $OUT/$name.jsonl > /workspace/logs/paper1_q10_$name.log 2>&1 && say "done $name" || say "FAILED $name"; }
FILES="sub_income sub_income_computed sub12_income sub12_income_computed sub12v2_income sub12v2_income_computed"
for m in qwen3-14b qwen3-32b-awq qwen3-8b ministral3-8b; do for f in $FILES; do direct $m $f; done; done
# Trimmed 15:40 UTC on the PI's call: free only on the original pair for 14B and 32B; the rest is in queue10_deferred.sh.
for m in qwen3-14b qwen3-32b-awq; do for f in sub_income sub_income_computed; do for s in 0 1; do free $m $f $s; done; done; done
say "queue 10 done"
