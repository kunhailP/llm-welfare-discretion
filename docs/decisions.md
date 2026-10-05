# Decision log (newest first)

| Date | Decision | Why | Status |
| --- | --- | --- | --- |
| 2026-10-05 | Pin transformers==5.14.1 (vLLM 0.30.0). 5.17+ renamed PixtralRotaryEmbedding and broke Ministral. Qwen3-8B pilot 1 ran on 5.18.0, so rerun it on the pinned env before any reported numbers | Environment consistency across models | done |
| 2026-10-05 | Before the pilot, add label-order counterbalancing (SUFFICIENT listed first) and a yes/no wording of Q1 | Smoke test (Qwen3-8B, 2 bases only, not a result): on sufficient cases Q3 extracted correct totals (2180 vs 1450) but answered SHORTFALL; Q1 said SHORTFALL on 12/14 sufficient items, including with no activity info. Possible label/answer-order prior must be separated from the effort effect | proposed |
| 2026-10-05 | Fix profile_id collision (shortfall/sufficient both coded "s"); ids now use rS/rF and aH/aL/aN codes; uniqueness assert added; smoke results discarded | Found in smoke test: merge mapped outputs to wrong profiles | done |
| 2026-10-05 | Add Q4 need severity (1-7) as co-primary DV; binary Q1-Q3 kept as factual/comprehension measures | Ceiling risk on explicit arithmetic items (docs/01_critical_review.md R1) | proposed |
| 2026-10-05 | Add valence-matched non-moral negative control (elevator broken vs inspected) | Neutral-detail control does not address valence confound (R3) | proposed |
| 2026-10-05 | Add FairFund-Bench need-only probe (150 unmodified stimuli, 2 name cells) | Closest prior work holds material situation fixed across framings (R2) | proposed |
| 2026-10-05 | Pilot includes all controls (700 profiles) to decide go/no-go by 10/6 | Cheap on L40; decision needs control contrasts | proposed |
| 2026-10-05 | Pin model revisions in configs/models.yaml | Reproducibility | done |
| 2026-10-05 | Use template generator (no LLM) for pilot; paraphrase set for main still TODO | Avoid "LLM-generated data" critique | done |
