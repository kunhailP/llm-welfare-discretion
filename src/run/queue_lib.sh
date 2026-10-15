#!/bin/bash
# Shared queue helpers (2026-10-12): a run is skipped only when its output is complete (every
# item of the data file present, two orders for the direct readout, every line valid JSON, meta file present); a failed or
# incomplete run marks the queue FAILED (exit 1 at the end, no "done" marker); each model run holds a lock so two queues
# cannot write the same outputs; downstream queues wait for the upstream "done" marker and abort on its "FAILED" marker.
PY=${PY:-/workspace/venv_evidence/bin/python}
LOCK=/workspace/logs/paper1_gpu.lock
QFAIL=0
say () { echo "=== $* $(date -u +%H:%M:%S)" | tee -a "$LOG"; }
complete () {  # complete <out.jsonl> <data.jsonl> <rows per item: 2 direct, 1 generated>
  [ -f "$1" ] && [ -f "$1.meta.json" ] && $PY - "$1" "$2" "$3" <<'PYEOF'
import json, sys
out, data, per = sys.argv[1], sys.argv[2], int(sys.argv[3])
ids = [json.loads(l)["item_id"] for l in open(data)]
try:
    rows = [json.loads(l) for l in open(out)]
except Exception:
    sys.exit(1)
got = {}
for r in rows:
    got[r["item_id"]] = got.get(r["item_id"], 0) + 1
sys.exit(0 if len(rows) == per * len(ids) and all(got.get(i) == per for i in ids) else 1)
PYEOF
}
wait_for () {  # wait_for "<queue N done>" "<queue N FAILED>"
  until grep -q "$1" "$LOG"; do grep -q "$2" "$LOG" && { say "upstream failed ($2): not starting"; exit 1; }; sleep 120; done
}
run_model () {  # run_model <name> <data file> <rows per item> <command...>; the command writes $OUT/<name>.jsonl
  local name=$1 data=$2 per=$3; shift 3
  if complete "$OUT/$name.jsonl" "$data" "$per"; then say "skip $name (complete)"; return 0; fi
  [ -f "$OUT/$name.jsonl" ] && { say "incomplete output for $name: rerunning"; rm -f "$OUT/$name.jsonl" "$OUT/$name.jsonl.meta.json"; }
  say "start $name"
  flock "$LOCK" "$@" > "/workspace/logs/paper1_$name.log" 2>&1
  if complete "$OUT/$name.jsonl" "$data" "$per"; then say "done $name"; else say "FAILED $name (see /workspace/logs/paper1_$name.log)"; QFAIL=1; fi
}
finish () {  # finish "<queue N>"
  if [ "$QFAIL" = 0 ]; then say "$1 done"; else say "$1 FAILED"; exit 1; fi
}
