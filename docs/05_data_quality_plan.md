# Data quality plan, written against ARR review criteria (2026-10-05)

ARR reviewers score Soundness, Excitement, Reproducibility, and dataset/software contributions, and flag ethics.
For each criterion: what reviewers will attack in our current data, and the fix.

## 1. Soundness: is the effect real, or an artifact of our templates?

| Risk in current data | Evidence it matters | Fix | Status |
| --- | --- | --- | --- |
| Few templates (pilot: 5 jobs, 3 bill pairs, 1 sentence frame per role) | The effect could be one template's quirk | Hand-written paraphrase families: >=4 surface variants per sentence role (job loss, no-income, job search, money, closing). Report variance across template families (mixed-effects or per-family table) | todo |
| Unemployed vs employed contexts differ in length and content (C1) | Unemployed prose has 3-4 extra sentences | Length-matched contexts; neutral filler of equal length for none/employed | todo |
| Which sentence causes the error is unknown (C2) | Effect could be "no paid work" (an income cue), not unemployment as a category | Sentence-level ablation: job loss only / + no offers / + no paid work / + job search; and an employed person with a neutral irrelevant event of equal length | todo |
| Anti-monotonic curve (more surplus, more SHORTFALL) | Unexplained; reviewers will ask | Must be reproduced or explained (amount magnitude vs ratio; absolute surplus grid crossed with ratio grid) before any claim | todo |
| Names carry demographic signals | FairFund shows names shift outputs | Unisex names (pilot) + balanced name pools; report a name-swap check | partly |
| Unrealistic amounts | Reviewers ask "are these plausible households?" | Anchor bill and fund ranges in public statistics (e.g., HUD fair market rents, BLS Consumer Expenditure Survey); cite source | todo |
| Dev/test leakage | Prompt tuning on test inflates claims | Pilot bases are permanent dev; test bases from a disjoint slot pool + seed; analysis plan frozen (commit hash) before the test run | ready |

## 2. Ecological validity: does it happen outside templates?

- FairFund-Bench stimuli (have; CC BY 4.0) — natural-style appeals.
- Candidate natural corpora and human-judgment data: see lit/candidate_datasets.md (search in progress).
- Claim scope stays "controlled test distribution" unless a natural corpus replicates it.

## 3. Human validation

- Two independent reviewers, blind sheets already generated (data/review/). Report agreement (Cohen's kappa) on gold and on pair invariance, plus counts of edited/removed items and reasons.
- Optional human baseline on the key contrast (label wording x context) if IRB/time allow; otherwise a stated limitation.

## 4. Reproducibility

- Pinned model revisions (configs/models.yaml), pinned environment (configs/requirements.lock.txt), deterministic generation (seeds), greedy + sequence-level scoring code.
- Release: data + generator + prompts + scoring under CC BY 4.0 / MIT, with a datasheet (Gebru et al. format) in the appendix.

## 5. Ethics (welfare is a sensitive domain)

- No real applicant data in the controlled set. Natural corpora: only licensed, de-identified sources; no re-identification.
- Frame findings as measurement validity for research and administrative use, not as advice on eligibility.
