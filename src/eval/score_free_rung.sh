#!/usr/bin/env bash
# Score the free-generation rung (queue 7, 2026-10-08) and regenerate every derived table. CPU only.
set -u
PY=${PY:-/workspace/venv/bin/python}
cd /root/llm-welfare-discretion
for m in qwen3-32b-awq qwen3-14b ministral3-8b; do
  f=results/rules_think/${m}_free.jsonl
  [ -f $f ] || continue
  $PY src/eval/score_rules_think.py $f > results/rules_think/score_${m}_free.json && echo "scored $m free"
  [ -f results/rules_think/${m}_off.jsonl ] && $PY src/eval/score_seed_agreement.py results/rules_think/${m}_off.jsonl $f > results/rules_think/agreement/${m}_off_vs_free.json && echo "agreement $m step vs free"
done
$PY src/eval/score_common_scale.py > /dev/null && echo "common scale"
$PY src/eval/make_paper1_tables.py > /dev/null && $PY src/eval/make_paper1_appendix.py > /dev/null && echo "tables + appendix regenerated"
grep -E "^\| (qwen3-32b-awq|qwen3-14b|ministral3-8b) \| free_s0" results/common_scale/contrasts.md
