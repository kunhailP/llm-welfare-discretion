#!/bin/bash
# Paper 1 queue 11 (pre-registered 2026-10-12 17:30 UTC, docs/paper1/computed_burden.md addendum; trimmed 18:00 on the PI's call;
# robust skip / fail / lock logic 18:20). Completes the computation-burden experiment after queue 10:
# the computed block without the authority wording (direct on four models, free on 14B, 32B, Ministral), Ministral direct+free,
# free on the seed-12 households for 14B (phrasing v1). Deferred: seed-12 free for 32B and phrasing v2.
set -u
source /workspace/logs/env.sh
REPO=${WN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}; export WN_ROOT=$REPO; cd "$REPO"
source src/run/queue_lib.sh
LOG=/workspace/logs/queue10.log; OUT=results/computed; mkdir -p $OUT
D=data/rules_pilot
# 2026-10-13 01:05 UTC: launched by hand after the PI asked; queue 12 finished by hand-verified outputs, so no marker wait
say "queue 11 start"
for m in qwen3-14b qwen3-32b-awq qwen3-8b ministral3-8b; do
  run_model ${m}_sub_income_computed_plain_direct $D/sub_income_computed_plain.jsonl 2 \
    $PY src/run/run_rules_pilot.py --model $m --data $D/sub_income_computed_plain.jsonl --out $OUT/${m}_sub_income_computed_plain_direct.jsonl
done
for m in qwen3-14b qwen3-32b-awq; do for s in 0 1; do
  run_model ${m}_sub_income_computed_plain_free_s$s $D/sub_income_computed_plain.jsonl 1 \
    $PY src/run/run_rules_think.py --model $m --prompt free --thinking off --no-subsample --seed $s --data $D/sub_income_computed_plain.jsonl --out $OUT/${m}_sub_income_computed_plain_free_s$s.jsonl
done; done
for f in sub12_income sub12_income_computed; do for s in 0 1; do
  run_model qwen3-14b_${f}_free_s$s $D/$f.jsonl 1 \
    $PY src/run/run_rules_think.py --model qwen3-14b --prompt free --thinking off --no-subsample --seed $s --data $D/$f.jsonl --out $OUT/qwen3-14b_${f}_free_s$s.jsonl
done; done
# 18:05 UTC: the Ministral weights were missing from this pod's HF cache (queue 10 marked its six direct runs FAILED); downloaded at
# the pinned revision, so the direct runs are repeated here under the completeness check before the Ministral free runs.
for f in sub_income sub_income_computed sub12_income sub12_income_computed sub12v2_income sub12v2_income_computed; do
  run_model ministral3-8b_${f}_direct $D/$f.jsonl 2 $PY src/run/run_rules_pilot.py --model ministral3-8b --data $D/$f.jsonl --out $OUT/ministral3-8b_${f}_direct.jsonl
done
for f in sub_income sub_income_computed sub_income_computed_plain; do for s in 0 1; do
  run_model ministral3-8b_${f}_free_s$s $D/$f.jsonl 1 \
    $PY src/run/run_rules_think.py --model ministral3-8b --prompt free --thinking off --no-subsample --seed $s --data $D/$f.jsonl --out $OUT/ministral3-8b_${f}_free_s$s.jsonl
done; done
finish "queue 11"
