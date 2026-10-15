# Response Protocols Shape Deservingness Effects in LLM Welfare Decisions

Code, data, model outputs and manuscript for a study of legally irrelevant deservingness cues in SNAP eligibility decisions. The testbed uses FY2026 federal rules, computed gold labels and paired changes to job-search effort or the cause of job loss.

[Paper](paper/main.pdf) · [Experiment map](docs/EXPERIMENTS.md) · [Reproduction instructions](docs/REPRODUCING.md) · [Data sources](data/external/SOURCES.md)

## Findings

- With one-word answers, four open models have gross-test balanced accuracy of 0.50–0.64 and eligibility accuracy of 0.40–0.46. Deservingness cues change some verdicts in both error directions.
- Allowing generation raises income accuracy to 0.97–1.00 in the three models tested without a thinking mode. No income contrast has a consistent direction across both seeds.
- Supplying intermediate quantities while retaining the one-word protocol raises Qwen3-14B/32B income accuracy to 0.95–1.00 and gives zero flips on the target eligibility controllability contrast. Other contrasts have 0–4 flips. Qwen3-8B remains less accurate on eligibility and its controllability contrast grows; Ministral improves but remains below the accuracy criterion.
- On 128 new households, no free-generation contrast meets the pre-specified replication criterion. Some pairs still flip; this is not a test of fairness equivalence.

The computation-supply control changes both computational demands and information presentation. Its plain-prefix variant removes two authority phrases, not the supplied quantities. The findings concern the stated federal-rule packet and response protocols, not deployment safety.

## Reproduce from the released outputs

CPU analysis needs Python with NumPy, pandas and PyYAML. The experiment versions are listed in `configs/requirements-cpu.txt`; GPU inference has a separate lock file.

```bash
python -m pip install -r configs/requirements-cpu.txt
python src/eval/reproduce.py
make -C paper
```

The first command installs analysis dependencies. The second runs the 12 existing rule tests and regenerates common-scale contrasts, the household sign test, control summaries and paper tables from the shipped outputs. The last builds the anonymous PDF and requires `latexmk` and TeX Live. No model calls occur in these steps. See [REPRODUCING.md](docs/REPRODUCING.md) for GPU runs, data regeneration and known reproducibility limits.

## Contents

| Path | Contents |
| --- | --- |
| `paper/` | Anonymous manuscript, cited bibliography, ACL style and generated appendix tables |
| `src/rules/`, `tests/` | SNAP implementation, PolicyEngine cross-check and hand-computed tests |
| `src/gen/`, `src/run/`, `src/eval/` | Item generators, inference runners and analysis |
| `configs/` | Rule packets, pinned model revisions and environments |
| `data/rules_pilot/` | Original, computation-supply and confirmation items |
| `results/` | Model outputs, run metadata and derived scores used by the paper |
| `docs/` | Experiment map, reproduction instructions and dated design records |

The original design and follow-up plans are preserved, including addenda and recorded outcomes. See [PROVENANCE.md](docs/PROVENANCE.md) for their status. Earlier unrelated pilots remain in Git history; the full decision log, results notes and literature notes stay in `docs/` and `lit/` and are not part of the release.

## Supplementary archives

```bash
bash src/release/make_release.sh /tmp/llm-welfare-rules-anon
```

Use a new output path. The script builds separate software and data ZIPs with a shared top-level directory, checks for known author identifiers and records file hashes. Extract both archives into the same directory. The source files, model outputs and pre-run records needed for the paper are included.

## Licences

Code: [MIT](LICENSE). Generated items, model outputs and analysis: [CC BY 4.0](LICENSE-DATA). The included FNS parameter PDFs are U.S. federal works. The SNAP QC source CSV is downloaded separately; [SOURCES.md](data/external/SOURCES.md) gives its location. PolicyEngine-US is separately distributed under AGPL-3.0.
