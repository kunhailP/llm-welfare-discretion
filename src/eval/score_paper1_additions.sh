#!/usr/bin/env bash
# Score everything the L40 queue produced (2026-10-08) and regenerate the paper 1 tables. CPU only.
set -u
PY=${PY:-/workspace/venv/bin/python}
cd /root/llm-welfare-discretion
for f in qwen3-14b_s1 qwen3-32b-awq_s1 qwen3-8b_s1 qwen3-14b_off qwen3-32b-awq_off; do
  [ -f results/rules_think/$f.jsonl ] && $PY src/eval/score_rules_think.py results/rules_think/$f.jsonl > results/rules_think/score_$f.json && echo "scored $f"
done
mkdir -p results/rules_think/agreement
for m in qwen3-14b qwen3-32b-awq qwen3-8b; do
  [ -f results/rules_think/${m}_s1.jsonl ] && $PY src/eval/score_seed_agreement.py results/rules_think/$m.jsonl results/rules_think/${m}_s1.jsonl > results/rules_think/agreement/${m}_s0_vs_s1.json && echo "agreement $m s0 vs s1"
  [ -f results/rules_think/${m}_off.jsonl ] && $PY src/eval/score_seed_agreement.py results/rules_think/$m.jsonl results/rules_think/${m}_off.jsonl > results/rules_think/agreement/${m}_on_vs_off.json && echo "agreement $m on vs off"
done
$PY src/eval/consequence.py > /dev/null && echo "consequence rerun"
$PY src/eval/make_paper1_tables.py > /dev/null && echo "tables regenerated: docs/paper1/tables.md"
