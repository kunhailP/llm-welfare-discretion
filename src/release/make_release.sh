#!/usr/bin/env bash
# Build the anonymised code+data release for the ARR submission of Paper 1 (2026-10-08).
# Copies only what the paper uses, strips git history, and checks for author identifiers before packing.
# Usage: bash src/release/make_release.sh [/path/to/output_dir]
set -eu
HUB=$(cd "$(dirname "$0")/../.." && pwd)
OUT=${1:-/workspace/release/llm-welfare-rules-anon}; export OUT
rm -rf "$OUT"; mkdir -p "$OUT"
cd "$HUB"
# code and configs
for p in src/rules src/gen/make_rules_pilot.py src/run/run_rules_pilot.py src/run/run_rules_think.py src/run/run_rules_api.py \
         src/eval/score_rules_pilot.py src/eval/score_rules_think.py src/eval/score_seed_agreement.py src/eval/consequence.py \
         src/eval/make_paper1_tables.py src/eval/score_common_scale.py src/eval/score_abawd_hardship.py src/eval/make_paper1_appendix.py tests/test_snap_rules.py configs/rule_packet_fy2026.md configs/rule_packet_fy2026_nosanction.md configs/models.yaml \
         configs/requirements.lock.txt configs/requirements_policyengine.lock.txt; do
  mkdir -p "$OUT/$(dirname "$p")"; cp -r "$p" "$OUT/$p"
done
# data (generated items; the QC public-use file is not redistributed, see README) and results
mkdir -p "$OUT/data/rules_pilot" "$OUT/data/external/snap_params" "$OUT/results"
cp data/rules_pilot/pilot.jsonl data/rules_pilot/pilot_bases_hwgt.json data/rules_pilot/pilot_plus_abawd_hardship.jsonl "$OUT/data/rules_pilot/"
cp data/external/snap_params/*.pdf "$OUT/data/external/snap_params/"
cp -r results/rules results/rules_pilot results/rules_pilot_nosanction results/rules_think results/common_scale results/consequence "$OUT/results/"
# tables and results notes
mkdir -p "$OUT/docs/paper1" "$OUT/docs/results" "$OUT/archive/stage2_design_c/docs" "$OUT/archive/stage2_design_c/results"
cp docs/paper1/tables.md "$OUT/docs/paper1/"; cp docs/results/design_B_rules_pilot.md "$OUT/docs/results/"
# Appendix E (polarity flip): Design C notes and score files only (raw generations stay out: 115 MB)
cp archive/stage2_design_c/docs/*.md "$OUT/archive/stage2_design_c/docs/"
find archive/stage2_design_c/results -name "score*" -exec sh -c 'mkdir -p "$OUT/$(dirname "$1")" && cp "$1" "$OUT/$1"' _ {} \;
cat > "$OUT/README.md" <<'R'
# Anonymised release: deservingness cues in LLM welfare determinations (SNAP FY2026 rules-as-code testbed)

Code, items, model outputs and scores for the paper. Reproduce:
    unzip the SNAP QC FY2024 public-use CSV (https://snapqcdata.net/datafiles) into data/external/candidates/snap_qc_fy2024/
    python src/gen/make_rules_pilot.py --bases 40 --seed 11 --out data/rules_pilot/pilot.jsonl    # byte-identical to the shipped file
    pytest tests
    python src/run/run_rules_pilot.py --model qwen3-14b --data data/rules_pilot/pilot.jsonl --out results/rules_pilot/qwen3-14b.jsonl
    python src/run/run_rules_think.py --model qwen3-14b [--seed 1] [--thinking off] --out results/rules_think/qwen3-14b.jsonl
    python src/eval/score_rules_pilot.py --results results/rules_pilot/qwen3-14b.jsonl
    python src/eval/score_rules_think.py results/rules_think/qwen3-14b.jsonl
    python src/eval/score_seed_agreement.py results/rules_think/qwen3-14b.jsonl results/rules_think/qwen3-14b_s1.jsonl
    python src/eval/consequence.py && python src/eval/make_paper1_tables.py
Environment: Python 3.12, configs/requirements.lock.txt (vLLM 0.30.0), model revisions pinned in configs/models.yaml.
Gold: src/rules/snap.py (FY2026 FNS parameters in data/external/snap_params; P.L. 119-21 ABAWD rules), cross-checked
against PolicyEngine-US (results/rules/crosscheck_pe.json; src/rules/crosscheck_pe.py).
R
find "$OUT" -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
# identifier check: fail if any author / account identifier survives
if grep -rIl -iE "kunhail|/root/" "$OUT" ; then echo "IDENTIFIERS FOUND (above): fix before packing"; exit 1; fi
# ARR wants software and data as two separate single archives; results go with the data.
B=$(basename "$OUT"); D=$(dirname "$OUT")
rm -rf "$D/$B-software" "$D/$B-data"; mkdir -p "$D/$B-software" "$D/$B-data"
cp -r "$OUT/src" "$OUT/configs" "$OUT/tests" "$OUT/docs" "$OUT/archive" "$OUT/archive" "$OUT/README.md" "$D/$B-software/"
cp -r "$OUT/data" "$OUT/results" "$D/$B-data/"; cp "$OUT/README.md" "$D/$B-data/"
( cd "$D" && rm -f "$B.zip" "$B-software.zip" "$B-data.zip" && zip -qr "$B.zip" "$B" && zip -qr "$B-software.zip" "$B-software" && zip -qr "$B-data.zip" "$B-data" )
du -sh "$OUT" "$OUT.zip" "$D/$B-software.zip" "$D/$B-data.zip"; echo "release at $OUT.zip (+ -software.zip and -data.zip for the ARR upload)"
