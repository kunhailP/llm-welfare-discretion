# Archive

Finished stages kept for the record (pilot history, appendix material). Nothing here is used by the active
pipeline. Code was moved as-is, so paths inside it still point at the old locations
(e.g. `src/gen/make_profiles.py`, `data/pilot/`, `results/v2/`); prefix them with `archive/stage1_need_v1/` to rerun.
Old paths cited in docs/decisions.md map the same way.

## stage1_need_v1 (2026-10-05, before the retarget)
Question: do LLMs separate material need from deservingness when the funds-vs-bills arithmetic is explicit?
Outcome: Qwen3-14B is 100% correct on explicit yes/no need items; the 8B failures were format effects (v2 money-fact
surface), not deservingness. This led to the retarget and Design B/C (see docs/decisions.md).

| what | where |
| --- | --- |
| v0.1 design, critical review, data spec, pilot audit, data-quality plan, old paper outline | docs/ |
| controlled_v2 design (length-matched contexts, blind-review sheets) | docs/07_controlled_v2.md, data/controlled_v2, data/review |
| full audit of the stage (2026-10-05) | docs/08_audit_2026-10-05.md |
| generators: profiles, controlled_v2, oracle-ladder diagnostic, FairFund need probe, review sheets | src/gen/ |
| runners (vLLM generation / label scoring), wording probe, stage queues | src/run/ |
| scorers | src/eval/ |
| prompt grids | configs/prompts.yaml, configs/prompts_v2.yaml |
| results: pilot, diagnostic, diagnostic_seq, fairfund, v2 (dev, wording probe) | results/ |

## old_queues
Finished GPU queues of Design B / C (rules pilot, thinking queue, discretion queue, Design C queue 1).
The live queue is src/run/run_design_c_queue2.sh.
