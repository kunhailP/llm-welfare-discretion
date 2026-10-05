# Design B (draft v0, 2026-10-05): Rule-relevant vs rule-irrelevant deservingness in LLM eligibility determination

Target: ARR January 2027 cycle -> ACL 2027 (exact date TBA). Bar: ~4.5 overall.
Sources: lit/why_now_policy.md (policy evidence), lit/rule_reasoning_review.md (NLP threats),
lit/literature_review.md (deservingness theory), archive/stage1_need_v1/docs/08_audit_2026-10-05.md (what v1/v2 established).
Status: draft v1 for the user's review. Nothing here is decided until logged in decisions.md.

**Scope rule (user, 2026-10-05):** this is the foundational paper. It should dig ONE unexplored problem
deeply, at the level of a strong NAACL/EMNLP study; ACL-level work is the follow-up built on it.
The one problem: *does an LLM use a deservingness cue exactly where the rule makes it material, and
nowhere else?* Every element below must deepen that problem. Separate contributions go to section 12.

## 0. One-sentence claim (to be earned, not assumed)

When LLMs apply an official welfare rule, deservingness cues (effort, cause, responsibility) should
change the determination **only where the rule makes them material**. We measure whether models
(a) stay invariant where the cue is legally irrelevant, (b) use the same kind of cue correctly where
it is legally relevant, and (c) whether their errors run in a socially patterned direction that
changes group-level eligibility rates.

**Revised core (2026-10-05, after review_092727e).** A two-sided should-change / should-not-change test is
NOT new by itself (Chen et al. 2026 LexGuard; Kearney et al. 2025 already study welfare eligibility). The
candidate contribution is narrower and must be earned with data:
- The *same* work fact (approved work-program hours 72 vs 88; paid work and income fixed) must change the
  ABAWD decision for a non-exempt adult and must NOT change it for an exempt adult (exemption x hours 2x2).
- Job-search effort and cause-of-job-loss cues are a separate, always legally irrelevant variable laid on
  top. Question: do they disturb the rule's switch, i.e. the interaction and the all-four-cells-correct rate?
- Primary measures: the 2x2 interaction on P(YES) (gold value 1), correct-direction switch, all-4-correct,
  and their cue-minus-none differences. Raw accuracy is secondary (ABAWD gold is 80% YES).
- Hours and effort are different constructs; do not call hours "effort".

## 1. Why now (all items verified in lit/why_now_policy.md)

- **Effort just became legally material for far more people.** P.L. 119-21 (in effect 4 Jul 2025):
  - the SNAP ABAWD time limit now covers ages 18-64 (was 18-54);
  - the child exception now applies only for a child under 14 (was under 18);
  - the homeless, veteran and former-foster-youth exceptions were removed.

  The core rule is unchanged: 80 hours/month of work, or 3 months of benefits in 36. Medicaid work requirements start Jan 2027.
- **States now have money at stake, which pushes them toward automation.**
  - From FY2028, a state's share of benefit costs is tied to its payment error rate: 0% below 6%, then 5%, 10%, 15%.
  - The national rate in FY2025 was 10.62%; 43 of 53 jurisdictions are at 6% or higher.
  - The state share of administrative costs rose to 75% on 1 Oct 2026.
- **LLMs are already being used in exactly these decisions.**
  - Maryland uses an LLM for SNAP/Medicaid applications and caseworker eligibility checks. The vendor is Anthropic: disclose this as a possible conflict of interest.
  - A $8.5M program funds AI for SNAP work verification (MD, MS), notices (NM, OR) and decision memos (NJ).
  - New Mexico and Missouri plan AI for Medicaid work requirements.
  - USDA's 2025 memo warns such AI "may introduce bias or errors into eligibility determinations".
  - OMB M-25-21 presumes benefits-eligibility AI is high-impact.
  - EU AI Act Annex III 5(a) makes it high-risk, with obligations applying from 2 Dec 2027 after the Omnibus.
- **There are documented failures.**
  - Chatbot SNAP accuracy was 48-80% (Propel 2025).
  - The NYC MyCity chatbot was taken down.
  - Bias was found in the UK DWP fraud model.
  - Historical precedents: Robodebt and the Dutch toeslagenaffaire.

Framing for the intro: the expansion of work requirements multiplies the number of determinations
in which *need* and *effort* must be legally separated, at the moment these determinations are being
delegated to LLMs.

## 2. Theory (welfare politics side)

- **Need vs deservingness.**
  - CARIN / NICER (van Oorschot 2000; Knotz et al. 2022): need is the cost-resource gap, while Control and Effort carry the most weight in human deservingness judgments.
  - The deservingness heuristic is automatic (Petersen 2012; Petersen et al. 2011).
  - *Question:* do LLMs carry this heuristic into rule application?
- **Street-level discretion.**
  - Caseworkers apply discretion where rules leave room, and deservingness and race shape sanctioning: Lipsky; Soss, Fording & Schram, *Disciplining the Poor*. TODO: verify these citations.
  - LLM caseworker assistants are a new street-level actor.
  - *Question:* do they bring discretion into places where the rule leaves none?
- **Rule as codebook.**
  - Halterman & Keith 2026 (*Political Analysis*) treat an eligibility rule like a codebook.
  - Under this view, *leakage* means the model uses the lay concept of "need/deserving" instead of the rule's operational definition.
  - This gives a measurement-validity contribution for computational social science.

## 3. Novelty vs closest work (from lit/rule_reasoning_review.md)

| Work | What they show | What we add |
| --- | --- | --- |
| Kearney, Binns & Gal 2025 (arXiv 2507.14238) | Implicit identity markers change benefit-eligibility answers (Llama3-70B, Qwen3-32B); part of their benchmark has YES/NO gold | "First to study welfare eligibility" and "we have gold" are NOT differentiators. Ours: deservingness (not identity) cues, and the exemption-switched relevance of the same work fact |
| Soffer et al. 2026 (JAMIA) | Trial-screening eligibility is stable under SES/identity labels; bias appears only outside the criteria | We test the boundary they name: the same cue type *inside* the criteria (ABAWD) vs outside them (income tests) |
| Chen et al. 2026 "Which Changes Matter?" (LexGuard) | Should-change vs should-not-change perturbations with executable rules and a solver, Chinese criminal law | The two-sided test itself is THEIRS, not ours. We add only: an exemption that switches the relevance of one fixed work fact, and whether normatively loaded (deservingness) cues disturb that switch. "Welfare instead of criminal law" and "more models" are not contributions |
| Wu & Xiao 2026 (arXiv 2608.22887) | Over-, warranted and under-reliance on cues, with statistical warrant | Our warrant is legal, not statistical. Adopt their vocabulary and contrast the two |
| Posner & Saran 2026 (Judge AI; Silicon Formalism) | Frontier models are formalist and ignore sympathy under clear law | Strongest null risk. We test multi-step rules with exemption chains and implicit cues, not a single clear rule |
| PolicyBench (PolicyEngine 2026) | Frontier models reach ~95% exact match on SNAP/Medicaid/tax from clean facts | Clean facts are the ceiling condition. We add narrative case files, cues and exemption chains |
| Gosciak et al. 2026 | SNAP QA benchmark; wrong chatbot answers mislead caseworkers | Human-in-the-loop harm motivates our consequence analysis; they do not vary cues |
| FairFund-Bench (Lukk 2026) | Deservingness-sensitive allocation | Their outputs are normative. Ours are rule-determined with gold |

## 4. Task and data

**Households.**
- Source: SNAP QC FY2024 public-use file (44,891 real households, 1,177 variables, public domain).
- It contains household size, ages, disability, earned and unearned income, rent/utilities, each deduction, net income, the test flags, the benefit, and per-person ABAWD status (`ABWDST*`) and work registration (`WRKREG*`).
- Use: sample real household *structures*, then perturb income around thresholds. The sample is participants only, so near-threshold failures have to be constructed.

**Rule packet given in the prompt.**
- Federal FY2026 rules, stated explicitly. No broad-based categorical eligibility and no state options, so gold is unambiguous.
- Include the post-P.L. 119-21 ABAWD rules.
- Gold comes from our rules-as-code.
- Cross-checks:
  - (a) PolicyEngine-US;
  - (b) QC agency values (RAWNET, FSBEN) on unperturbed households.

**Determinations**, from easy to hard:

| ID | Determination | Cue legal relevance |
| --- | --- | --- |
| D1 | Gross income test (130% FPL) | irrelevant |
| D2 | Net income after deductions (earned 20%, standard, dependent care, medical for elderly/disabled, excess shelter with cap) | irrelevant |
| D3 | Monthly benefit amount | irrelevant |
| D4 | ABAWD: subject to the time limit? meets 80 h/month? exempt (disability, pregnancy, child <14, ...)? | **relevant (hours) / irrelevant (job-search effort when exempt)** |

D4 holds the sharpest contrast inside one rule:
- **Hours worked are legally relevant.**
- **Job-search effort is legally irrelevant when the person is exempt**, for example pregnant or caring for a child under 14.
- Hypothesis H3 below: low-effort or self-caused cues suppress recognition of exemptions. This links to "Confidently Wrong", where exemption routes are discounted.

## 5. Manipulations (within household, full factorial where affordable)

1. **Cue type.**
   - Effort: job search intensity, as in the Knotz wording of applications per week.
   - Control: cause of job loss, fired for cause vs layoff.
   - Responsibility.
   - Reciprocity: past work history.
   - Identity: implicit only, via names or dialect, since explicit labels make models act fairer.
   - Valence-matched non-moral negative control.
2. **Cue direction:** high vs low deservingness, plus a no-cue baseline.
3. **Legal relevance:** cue irrelevant (D1-D3; D4-exempt) vs relevant (D4 hours).
4. **Margin to threshold:** far / near / exact, using realized gaps. The v2 lesson is to record digit-count crossing.
5. **Presentation:**
   - structured fields;
   - caseworker narrative note;
   - applicant first-person statement, which is the real deployment surface.
6. **Question frame:** factual determination vs "should this person receive benefits" (normative). The normative frame is a manipulation check: cues *should* move it.

Leakage is measured, not built in. Every case file passes a gold check plus a blind human review before any test run, carried over from v2.

## 6. Models

- **Scale ladder.** Qwen3 4B / 8B / 14B / 32B (AWQ) on the L40. Larger open models (e.g. 70B-class) need more GPU memory or an API.
- **Other families.** Llama, Gemma and Mistral at matched sizes.
- **Frontier, 2-3 models via API: deferred (user, 2026-10-05).** Use APIs only after the design is solid enough to rank high at EMNLP/NAACL. Open models only until then. Disclose the conflict of interest if Claude is included.
- **Mitigation arms.**
  - Extract-then-compute: the model extracts facts, code applies the rule.
  - Tool use: the model calls a rules engine.
  - Structured restatement (L2/L4 from v1).
- **Readouts.**
  - Sequence-level label scoring for open models, as in v1 and verified in the audit.
  - Greedy generation for API models.
  - Run-to-run flip baseline.

## 7. Measures and hypotheses

- **Accuracy** by determination and margin: the ceiling map.
- **Cue-induced flip rate** in excess of the run-to-run baseline, split by legal relevance:
  - should-not-change violations;
  - should-change misses.
- **Error direction:** wrongful denial vs wrongful approval, conditioned on cue direction.
- **Exemption recognition rate** by cue condition (D4).
- **Consequence.**
  - Apply each model to a QC-weighted (`HWGT`) synthetic caseload.
  - Estimate wrongful-denial counts and group-level eligibility-rate distortions vs gold.
  - Report the distortions as "errors per 100k cases of a stated synthetic caseload". Incomes are moved to
    chosen threshold margins, so HWGT does not identify real wrongful denials in the applicant population.
    Source QC ids and HWGT must be kept in the generator first (the pilot does not keep them).
- Gross and elig items come from different base sets (31 vs 27 bases), so their gap is not a pure
  rule-complexity effect; compare only on shared bases.
- A null on strong models is reported with interval width against a pre-set smallest effect of interest.

Hypotheses (pre-register before the test split):
- **H1:** in rule-irrelevant determinations, low-deservingness cues raise wrongful denials, and the effect grows with rule complexity (D1 < D2 < D3) and near the threshold.
- **H2 (asymmetry):** models that are invariant where cues are irrelevant also under-use relevant cues *or* over-apply them. Report both sides of the matrix.
- **H3:** low-effort / self-caused cues suppress recognition of ABAWD exemptions.
- **H4:** compare gold facts -> model verdict, model extraction -> engine verdict, and direct verdict. Only this three-way split narrows where a failure happens; extract-then-compute improving alone does not show the error arises after extraction.
- **Null-tolerant design.** If frontier models are formalist (Posner & Saran), the paper still reports:
  - the scale/complexity boundary where leakage disappears;
  - whether the remaining errors are still socially directed.

  Both outcomes are informative. Do not rescue the result by redesigning after looking at test data.

## 8. Human baseline: DROPPED (user, 2026-10-05: too burdensome)

- Not run. Theory links to the human deservingness heuristic stay as citations (Petersen; Knotz et al.).

## 8b. Depth analysis inside the core problem: legal mention standard for reasoning (thinking on/off)

Kept because it deepens the core question rather than adding a new one (lit/nlp_novelty_check.md, angle A).
The rule defines what a determination's reasoning *must* mention (hours worked, exemption status) and
what it is an error to rely on (any cue in income tests; job-search effort of an exempt person).
- Same model, thinking on vs off (Qwen3), plus reasoning vs non-reasoning API models.
- Caveat (review_092727e): a correct answer need not mention every relevant fact (an exempt case can skip the
  hours), and mentioning an irrelevant cue to set it aside is not relying on it. Word presence in CoT is not
  scored as a legal "duty to mention"; reliance is judged from verdict changes, mention only describes.
- Measures:
  - unverbalized cue influence: the cue flips the verdict, but the reasoning never mentions it;
  - irrelevant-factor citation: the reasoning or memo cites a legally irrelevant cue, even when the verdict is right;
  - required-factor citation: the reasoning cites the material cue where the law requires it.
- Scored against rule gold, so we can say whether reasoning produces wrongful denials or wrongful approvals.
- Closest prior: Pan et al. 2026 (thinking on/off, no gold, no mention analysis). Also Arcuschin et al. 2026; Karvonen & Marks 2025; Matton et al. 2025.
- Cost: sample thinking traces (no greedy), about 300 human-coded traces to validate an LLM judge (coded by us, not crowd).

## 9. Risks

| Risk | Mitigation |
| --- | --- |
| Frontier null (formalism) | Complexity gradient, exemption chains, implicit cues; make the null boundary itself a result |
| Template artifacts (v1 lesson) | Many surface templates; templates decoupled from cues; blind review; artifact covariates |
| Gold ambiguity (BBCE, state options) | Explicit federal rule packet; three-way gold cross-check |
| Contamination / memorized limits | State the parameter year in the prompt; perturb amounts |
| API cost / reproducibility | Pin model versions and dates; cache all outputs |
| Conflict of interest (Maryland uses Claude) | Disclose; report Claude like any other model |
| Ethics | No real people (QC is de-identified); no individual-level release beyond public data |

## 10. Timeline (assuming a mid-January deadline; adjust when ARR posts dates)

| Weeks | Work |
| --- | --- |
| Oct 6-19 | Rules-as-code + PolicyEngine/QC gold cross-check; case-file generator (3 presentations); cue bank |
| Oct 20-Nov 2 | Dev pilot on open models; ceiling map; finalize design; blind human review of the test split; pre-register on OSF |
| Nov 3-23 | Full runs: open-model scale ladder + families; frontier API; mitigation arms |
| Nov 24-Dec 14 | Consequence analysis; human baseline (if approved); robustness |
| Dec 15-Jan | Writing, internal review, release package |

## 11. Decisions for the user

1. Are frontier API models in scope, and with what budget?
2. (Decided: no human baseline.)
3. Long paper (8p): recommended for this scope.
4. Is SNAP the only program, or SNAP plus Medicaid work requirements as a second rule set? A second set would test generalization.
5. Role of v1/v2: a mechanism appendix ("label vocabulary x context" in small models) or drop it.

## 12. Follow-up roadmap (NOT in this paper)

- **Legally grounded intervention (ACL-level follow-up).** Erase or steer a deservingness direction (LEACE / SPLINCE / CAST) so that leakage disappears where the rule makes the cue irrelevant, while correct use of hours under ABAWD is preserved. Chen et al. 2026 (LexGuard) already uses executable law for both sides of the test; the follow-up's novelty would be the intervention, not the two-sided evaluation (closest: Wang et al. 2025 "Fairness through Difference Awareness").
- **Fact-verdict dissociation probing.** Does the cue corrupt the income-threshold comparison, or override an intact comparison? Needs the Villuri et al. 2026 threshold control. Least novel: appendix at most.
- **Second rule system.** Medicaid work requirements (from Jan 2027), for generalization.
- **Human/caseworker comparison**, if resources appear later.
