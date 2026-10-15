#!/usr/bin/env bash
# Paper 1 queue 9 (2026-10-12): no-sanction packet on the generated readout.
# The sanction-clarified packet was run only on the direct readout; the one replicated generated contrast (Qwen3-32B-AWQ,
# thinking off, ABAWD outside the trap, controllability) needs the same check. Same 150 subsample ABAWD groups, same answer
# order (--only-cues/--only-tasks keep group selection and order), seeds 0 and 1. Reading rule: docs/decisions.md 2026-10-12.
# Run 2026-10-12 08:02-08:24 UTC (results doc section 23). Needs Qwen3-32B-AWQ at the pinned revision in /workspace/hf and the vLLM 0.30.0 venv.
set -u
REPO=${WN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}
source /workspace/logs/env.sh; export WN_ROOT=$REPO
PY=/workspace/venv_evidence/bin/python
cd "$REPO"
mkdir -p /workspace/logs
step() { echo "[$(date -Is)] START $1"; }
done_() { echo "[$(date -Is)] DONE $1 (exit $2)"; }
for SEED in 0 1; do
  SUF=$([ "$SEED" = 0 ] && echo "" || echo "_s1")
  step 32b_off_s${SEED}_nosanction
  $PY src/run/run_rules_think.py --model qwen3-32b-awq --thinking off --seed $SEED \
    --packet configs/rule_packet_fy2026_nosanction.md --only-tasks abawd --only-cues control_high,control_low,none \
    --out results/rules_think/qwen3-32b-awq_off${SUF}_nosanction.jsonl > /workspace/logs/paper1_32b_off_s${SEED}_nosanction.log 2>&1
  done_ 32b_off_s${SEED}_nosanction $?
done
echo "[$(date -Is)] QUEUE9 FINISHED"
