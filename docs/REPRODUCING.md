# Reproducing the paper

Run commands from the repository root. Extract the software and data archives into the same parent directory if using the anonymous release.

## Analysis from saved outputs (CPU)

```bash
python -m pip install -r configs/requirements-cpu.txt
python src/eval/reproduce.py
make -C paper
```

`reproduce.py` runs the 12 existing rule tests and rebuilds the common verdict scale, household sign test, ABAWD need control, tables T1–T12 and LaTeX appendix tables. The consequence table uses its shipped summary; add `--full` to recompute that slow bootstrap. Some original-run tables read saved score summaries; computation-supply and confirmation tables are rescored directly from raw output files. The script does not claim to rerun model inference. `make` requires `latexmk` and TeX Live.

In a Git checkout, `make -C paper sync PY=python3` regenerates the common scale and tables, builds the PDF, and fails if the generated files differ from their tracked versions. A diff after an intentional documentation edit still needs review.

## Inference environment

The original open-model runs used one NVIDIA L40 (48 GB), Python 3.12 and `configs/requirements.lock.txt`. Install that environment separately from the optional PolicyEngine environment in `configs/requirements_policyengine.lock.txt`. Models and revisions are pinned in `configs/models.yaml`; `bash src/run/download_models.sh` downloads the pinned weights using the active Python interpreter (`PY` overrides it).

These commands are examples of each protocol, not an instruction to run every paid or GPU experiment:

```bash
mkdir -p reruns
python src/run/run_rules_pilot.py --model qwen3-14b --data data/rules_pilot/pilot.jsonl --out reruns/14b_direct.jsonl
python src/run/run_rules_think.py --model qwen3-14b --out reruns/14b_think_s0.jsonl
python src/run/run_rules_think.py --model qwen3-14b --thinking off --out reruns/14b_step_s0.jsonl
python src/run/run_rules_think.py --model qwen3-14b --thinking off --prompt free --seed 0 --out reruns/14b_free_s0.jsonl
```

Use `--seed 1` for the second generated seed and `--greedy` for the greedy control. The main generated runner selects the same stratified subsample automatically. For the sanction control, add `--packet configs/rule_packet_fy2026_nosanction.md`. For the API replicate, the paper used `run_rules_api.py --model gpt-5-2025-08-07` with the defaults described in the appendix; this requires separate credentials and incurs API charges.

For an already selected computation-supply or confirmation file, generated inference requires `--no-subsample`:

```bash
python src/run/run_rules_pilot.py --model qwen3-14b --data data/rules_pilot/sub_income_computed.jsonl --out reruns/14b_computed_direct.jsonl
python src/run/run_rules_think.py --model qwen3-14b --data data/rules_pilot/sub_income_computed.jsonl --thinking off --prompt free --no-subsample --seed 0 --out reruns/14b_computed_free_s0.jsonl
python src/run/run_rules_think.py --model qwen3-14b --data data/rules_pilot/conf13_elig.jsonl --thinking off --prompt free --no-subsample --seed 0 --out reruns/14b_confirmation_free_s0.jsonl
```

The archived filenames and their `.meta.json` files identify the completed model, input, protocol and seed combinations. `docs/EXPERIMENTS.md` states unrun conditions. The queue scripts in `src/run/` (`queue_lib.sh`, `run_paper1_queue6.sh` to `run_paper1_queue12.sh`) are the run records of the controls, the computation-supply experiment and the confirmation study, as cited by the pre-registration files; they take the repository root from their own location, expect the inference environment and model weights described above, and are not needed by the standalone runners.

## Regenerating inputs

Download the source CSV as described in `data/external/SOURCES.md`. Write regenerated files to a new directory for comparison:

```bash
mkdir -p regenerated
python src/gen/make_rules_pilot.py --bases 40 --seed 11 --out regenerated/pilot.jsonl
python src/gen/make_rules_pilot.py --bases 40 --seed 12 --base-offset 100 --out regenerated/pilot_seed12.jsonl
python src/gen/make_rules_pilot.py --bases 180 --seed 13 --base-offset 200 --out regenerated/pilot_seed13.jsonl
python src/gen/make_computed_variant.py --data regenerated/pilot.jsonl --out-dir regenerated --tag sub
python src/gen/make_computed_variant.py --data regenerated/pilot.jsonl --out-dir regenerated --tag sub --plain
```

`--cue-set v2` produces the secondary phrasing at a given seed. `make_computed_variant.py` selects the original income subsample; use tag `sub12` with the seed-12 pilot for its extension. The confirmation consists of all narrative eligibility items from the seed-13 pilot, rather than the smaller main-paper subsample. The generated files shipped with the release are the inputs actually used for scoring.

## Limits

Greedy first-token inference was not bit-identical across batch compositions; the manuscript reports the observed variation. Table 1 uses the full original run on matched items, while the computation-supply table uses reruns on the 804-item subset. Invalid generated answers and missing direct tokens are excluded by the scoring rules. Neither those responses nor the historical plans have been rewritten during cleanup.
