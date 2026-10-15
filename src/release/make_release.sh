#!/usr/bin/env bash
# Package the paper's software and data from an explicit allowlist.
# Usage: bash src/release/make_release.sh [/new/path/llm-welfare-rules-anon]
set -euo pipefail
REPO=$(cd "$(dirname "$0")/../.." && pwd)
OUT=${1:-"$REPO/release/llm-welfare-rules-anon"}
if [[ -e "$OUT" ]]; then
  echo "Output already exists; choose a new path: $OUT" >&2
  exit 1
fi
mkdir -p "$OUT"
OUT=$(cd "$OUT" && pwd)
cd "$REPO"
software=(
  src/rules src/gen src/run src/eval tests configs
  docs/EXPERIMENTS.md docs/REPRODUCING.md docs/PROVENANCE.md
  docs/design/design_B_rules.md docs/protocols/decision_records.md
  docs/paper1/tables.md docs/paper1/computed_burden.md docs/paper1/confirmation_study.md
  paper/main.tex paper/main.pdf paper/appendix_tables.tex paper/rule_packet_fy2026.md
  paper/references.bib paper/Makefile paper/README.md paper/acl.sty paper/acl_natbib.bst
  README.md LICENSE LICENSE-DATA
)
data=(
  data/rules_pilot data/external/SOURCES.md data/external/snap_params
  results/rules results/rules_pilot results/rules_pilot_nosanction results/rules_think
  results/common_scale results/consequence results/computed results/confirmation
)
for path in "${software[@]}" "${data[@]}"; do
  mkdir -p "$OUT/$(dirname "$path")"
  cp -R "$path" "$OUT/$path"
done
# Use release-specific instructions without a repository URL or build-only paths.
OUT="$OUT" python3 - <<'PYREADME'
import os
from pathlib import Path
p = Path(os.environ['OUT']) / 'README.md'
s = p.read_text()
a = s.index('## Supplementary archives')
b = s.index('## Licences', a)
s = s[:a] + '## Archive layout\n\nExtract the software and data ZIPs into the same directory. Both use the same top-level folder. From that folder, run the CPU commands above. `MANIFEST.sha256` covers the combined tree; verify it after extracting both archives.\n\n' + s[b:]
s = s.replace('Earlier unrelated pilots and working notes remain in Git history.', 'Earlier unrelated pilots and working notes are not included in these archives.')
p.write_text(s)
PYREADME
find "$OUT" -type d -name __pycache__ -prune -exec rm -rf {} +
# Known account/author identifiers and original private machine paths.
# A manual inspection is still needed; this is not a proof of anonymity.
if grep -rIl -iE 'kunhail|Kun[ -]?woo Park|/root/' "$OUT"; then
  echo "Known identifier found; inspect the files listed above before release." >&2
  exit 1
fi
OUT="$OUT" python3 - <<'PY'
import hashlib, os
from pathlib import Path
root = Path(os.environ['OUT'])
rows = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(root).as_posix()}"
        for p in sorted(root.rglob('*')) if p.is_file()]
(root / 'MANIFEST.sha256').write_text('\n'.join(rows) + '\n')
PY
name=$(basename "$OUT")
parent=$(dirname "$OUT")
(
  cd "$parent"
  zip -qr "$name-software.zip" "$name/src" "$name/tests" "$name/configs" "$name/docs" "$name/paper" \
    "$name/README.md" "$name/LICENSE" "$name/LICENSE-DATA" "$name/MANIFEST.sha256"
  zip -qr "$name-data.zip" "$name/data" "$name/results" "$name/README.md" "$name/LICENSE-DATA" "$name/MANIFEST.sha256"
)
printf 'Software: %s\nData: %s\n' "$parent/$name-software.zip" "$parent/$name-data.zip"
