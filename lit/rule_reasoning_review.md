# Rule-application reasoning, irrelevant social cues, and eligibility determination: literature review

Survey date: 2026-10-05. Target: ACL 2027 (ARR January 2027).

**Planned paper.** When strong LLMs apply an official welfare eligibility rule (for example the SNAP income tests or the ABAWD 80 hours/month work requirement), do deservingness cues (effort, cause of hardship, responsibility, identity) change determinations where the rule makes those cues legally irrelevant? And do models use the same cues correctly where the rule makes them relevant? Gold labels are computed from the rule. The measures are rule-relevance-conditioned invariance, directional errors, and effects on group-level eligibility rates.

**Scope.** This file adds to `lit/literature_review.md`, which already covers FairFund-Bench, Street-Level AI, Gosciak et al., GSM-IC, GSM-Symbolic, GSM-DC, Wu et al. 2024, CheckList, contrast sets, Veitch et al., the LLM-annotation and measurement-error literature (Baumann, Egami, Camuffo, Vallejo Vera, Kotte, Pita, Messing), Value Entanglement, the Knobe-effect-in-LLMs papers, Liu 2026 (virtuous victim / halo), and Tennant et al. 2026. None of those entries are repeated here.

**How things were checked.** "Verified: yes" means I opened the primary page myself: the arXiv abstract or HTML (scraped from arxiv.org/abs), the ACL Anthology page, the publisher or PMC page, a Crossref API record, or the full-text PDF. "Verified: partial" means I confirmed the metadata (for example through Crossref or a repository page) but the publisher page returned 403. "Verified: no" means I saw the item only in search snippets. Venue claims for arXiv-only papers come from the arXiv Comments field.

---

## 1. Statutory and rule-application reasoning benchmarks, and benefits/tax calculation

### Holzenberger, Blair-Stanek, Van Durme (2020). *A Dataset for Statutory Reasoning in Tax Law Entailment and Question Answering* (SARA).
- arXiv:2005.05257. https://arxiv.org/abs/2005.05257
- Verified: yes (arXiv abstract). I believe it appeared at the NLLP 2020 workshop (KDD), but I did **not** verify that venue; dblp was unreachable.
- Summary: Nine sections of the US tax code and 376 hand-built cases (entailment and tax-amount questions). Machine-reading baselines perform poorly, while a hand-written Prolog system solves the task. It is the canonical "apply a statute to stated facts" benchmark.
- Relation: This is the genre ancestor, since our gold is likewise computable from the rule. Overlap is low: SARA has no social or moral cues, no invariance test and no group-level outcomes. Cite it as the origin of statutory reasoning with symbolic gold.

### Blair-Stanek, Holzenberger, Van Durme (2023). *Can GPT-3 Perform Statutory Reasoning?*
- arXiv:2302.06100. https://arxiv.org/abs/2302.06100
- Verified: yes (arXiv). I believe it appeared at ICAIL 2023, but the venue is not verified.
- Summary: text-davinci-003 sets a new SARA state of the art but fails on simple *synthetic* statutes. This suggests real-statute performance partly reflects memorised legal knowledge.
- Relation: This motivates our use of real rules (SNAP and ABAWD) alongside controls. Prior knowledge of SNAP may help models, or it may import lay deservingness priors. Threat: none.

### Zou, Zhang, Weir, Van Durme, Holzenberger (2024). *Reframing Tax Law Entailment as Analogical Reasoning.*
- arXiv:2401.06715. https://arxiv.org/abs/2401.06715
- Verified: yes (arXiv). Summary: Recasts SARA as an analogy task and expands the data by two orders of magnitude. Relation: peripheral. Threat: none.

### Jurayj, Holzenberger, Van Durme (2025/26). *Language Models and Logic Programs for Trustworthy Tax Reasoning.* AAAI 2026 (per arXiv).
- arXiv:2508.21051. https://arxiv.org/abs/2508.21051
- Verified: yes (arXiv).
- Summary: A neuro-symbolic pipeline: the LM translates statutes and cases into logic programs and a solver computes tax liability, evaluated on SARA with a cost metric based on real tax penalties.
- Relation: Represents the "rules as code + LLM" mitigation. It is a candidate mitigation arm for us (LLM extracts facts, the solver decides), which by construction removes cue leakage at the decision step but not at the extraction step. Threat: none.

### Guha et al. (2023). *LegalBench: A Collaboratively Built Benchmark for Measuring Legal Reasoning in LLMs.* NeurIPS 2023 Datasets and Benchmarks (venue from memory).
- arXiv:2308.11462. https://arxiv.org/abs/2308.11462
- Verified: yes (arXiv; 162 tasks, 40 authors).
- Summary: 162 tasks across six types of legal reasoning, including "rule-application" and "rule-conclusion" tasks, plus SARA-derived tasks (sara_entailment, sara_numeric).
- Relation: Our task is a rule-application task in IRAC terms. LegalBench has no welfare-eligibility tasks and no controlled irrelevant social cues. Threat: low.

### Servantez, Barrow, Hammond, Jain (2024). *Chain of Logic: Rule-Based Reasoning with Large Language Models.* Findings of ACL 2024, pp. 2721–2733. DOI 10.18653/v1/2024.findings-acl.159.
- https://aclanthology.org/2024.findings-acl.159/
- Verified: yes (ACL Anthology).
- Summary: A prompting method that decomposes compositional rules into element-wise threads and recombines them (IRAC-style). It outperforms CoT on eight LegalBench rule tasks.
- Relation: A natural **mitigation baseline**: does element-wise decomposition remove deservingness leakage? Threat: none.

### Zhou, Hua, Pan, Cheng, Wu, Yu, Wang (2025). *RuleArena: A Benchmark for Rule-Guided Reasoning with LLMs in Real-World Scenarios.* ACL 2025 (Long), pp. 550–572. DOI 10.18653/v1/2025.acl-long.27.
- https://aclanthology.org/2025.acl-long.27/ ; arXiv:2412.08972
- Verified: yes (Anthology and arXiv).
- Summary: Real-world rule sets (airline baggage fees, NBA transactions, **tax regulations**). LLMs fail to identify and apply the right rules and make computation errors. Irrelevant but plausible *rules* degrade performance, while meaningless filler does not.
- Relation: This is the closest ACL-main "real rules + distractor" benchmark. Its distractors are irrelevant **rules**. Ours are legally irrelevant **facts about the person** with moral valence, conditioned on whether the rule makes them relevant. Threat: low-medium on the framing "LLMs apply real rules poorly". Cite as the main ACL anchor.

### Servantez, Lawsky, Jain, Linna, Hammond (2026). *OpenExempt: A Diagnostic Benchmark for Legal Reasoning and a Framework for Creating Custom Benchmarks on Demand.*
- arXiv:2601.13183 (19 Jan 2026; no venue listed). https://arxiv.org/abs/2601.13183
- Verified: yes (arXiv abstract and HTML).
- Summary: Expert-written symbolic encodings of US Bankruptcy Code exemption statutes generate natural-language tasks with machine-computed answers. Diagnostic suites include **Distractor Robustness** (legally immaterial facts such as property not owned, or travel that does not change domicile), **Sycophancy Robustness** (opinions about eligibility that have no legal force) and their combination. On the hardest task, frontier models drop sharply (GPT-5 0.844 → 0.621 with distractors and → 0.507 combined; Gemini-2.5-Pro 0.938 → 0.714). Simple tasks are barely affected.
- Relation: **Methodologically the closest rule benchmark**: symbolic gold, statute-derived eligibility (exemptions), and controlled legally-irrelevant facts. But its distractors are financial and legal, explicitly **not social, moral, sympathetic or demographic**. It has no relevant-cue condition, no directional (pro- or anti-claimant) analysis and no group rates. Threat: **medium** on method. What we add: valenced deservingness distractors, rule-conditioned relevance (ABAWD), directional error, and population consequences. Design lesson: the effect appears mainly in **multi-step** tasks, so our items need enough rule depth.

### Simpson, Kozak, Doake (2026). *Confidently Wrong: Exception Chain Collapse in Frontier LLM Rule Evaluation.* Working paper v3.13.0.
- arXiv:2607.23386 (25 Jul 2026). https://arxiv.org/abs/2607.23386
- Verified: yes (arXiv abstract and HTML). The authors are from a company (Aethis) that sells the neuro-symbolic system the paper evaluates, and the paper is not peer reviewed.
- Summary: Frontier models (Claude Opus 4.6/4.7, GPT-5.x) fail on nested UNLESS chains ("exception chain collapse") and on "exemption anchoring", where they treat exemption routes as secondary once the primary route fails. Domains: UK nationality requirements, a synthetic spacecraft statute and construction insurance. The paper says the repository has a benefits domain, but the paper does not test it.
- Relation: Directly relevant to **ABAWD exemptions** (age, pregnancy, medical certification, a child in the household, waived areas), which are exemption routes. Exemption anchoring predicts errors on our relevant-cue items that are not about deservingness at all, so we need this control. Threat: low (no social cues). Cite with care because of the commercial authorship.

### Bock, Molisee, Ozer, Shah (2025). *TaxCalcBench: Evaluating Frontier Models on the Tax Calculation Task.*
- arXiv:2507.16126 (22 Jul 2025). https://arxiv.org/abs/2507.16126
- Verified: yes (arXiv).
- Summary: 51 synthetic federal returns verified by a deterministic tax engine. The best model gets under one-third fully correct. Models misuse tax tables, make arithmetic errors, and "incorrectly determine eligibility" for credits (EITC, CTC).
- Relation: Evidence that frontier models fail at benefit-like eligibility computations even without distractors, so we must separate the base error rate from cue-induced error. Our paired design does this (an invariance violation is computed within item). Threat: low.

### Gogani-Khiabani, Trivedi, Chyi, Tizpaz-Niari (2025). *Performance of LLMs on VITA test: potential for AI-assisted tax returns for low income taxpayers.* *Artificial Intelligence and Law* (online 8 Jul 2025). DOI 10.1007/s10506-025-09465-7.
- Verified: partial (Crossref record only).
- Relation: Low-income tax assistance (the VITA certification test). Low threat. Optional citation for the deployment context.

### Gogani-Khiabani, Trivedi, Saha, Tizpaz-Niari (2025/26). *An LLM Agentic Approach for Legal-Critical Software: A Case Study for Tax Prep Software.* ICSE 2026 (per arXiv).
- arXiv:2509.13471. https://arxiv.org/abs/2509.13471
- Verified: yes (arXiv).
- Summary: Uses **higher-order metamorphic relations** that compare tax outputs across structured shifts among similar individuals to test LLM-generated tax software.
- Relation: Metamorphic testing ("similar individuals should get related outputs") is the software-engineering name for our invariance and directional tests. Cite it to connect with SE testing. Threat: low.

### PolicyEngine (2026). *PolicyBench.* Benchmark website and repository (no paper found).
- https://policybench.org/ ; https://github.com/PolicyEngine/policybench (Unlicense). Snapshot dated 30 Sep 2026.
- Verified: yes (opened site and README). I found **no arXiv or academic paper**.
- Summary: Frontier models (46 listed) estimate household taxes and benefits **without tools** for households sampled from PolicyEngine-US microdata under 2026 rules. Outputs include SNAP, SSI, TANF, Medicaid, CHIP, WIC, school meals, refundable credits and state taxes. Headline exact-match accuracy is about 95% for the leaders, but positive-amount cases are much worse (state refundable credits 17.2% on positive cases versus 98.8% on zero cases). There is no manipulation of irrelevant or social cues.
- Relation: **Important infrastructure and a positioning anchor.** (a) PolicyEngine-US can serve as an independent gold oracle for our SNAP items. (b) PolicyBench establishes accuracy on clean household facts, so our contribution is what happens when those same facts come with deservingness narratives. (c) Its finding of asymmetric accuracy (zeros easy, positives hard) parallels our "directional errors" measure. Threat: low-medium. A reviewer might say "benefit-calculation accuracy is already benchmarked". The answer is that PolicyBench measures accuracy, not invariance to legally irrelevant social information.

### Bao et al. (2026). *PolicyLLM: Towards Excellent Comprehension of Public Policy for Large Language Models.* Findings of ACL 2026 (per arXiv).
- arXiv:2604.12995. https://arxiv.org/abs/2604.12995
- Verified: yes (arXiv). The first author is Han Bao, with 11 co-authors.
- Summary: A 21K-case US–China policy-comprehension benchmark (also confusingly named "PolicyBench") organised by Bloom levels (memorisation, understanding, application), plus a PolicyMoE model.
- Relation: A general policy QA benchmark with no eligibility determination under social cues. Threat: low. Note the name clash with PolicyEngine's PolicyBench.

### Kennan, Singh, Garcia Guevara, Ahmed, Goodman (2025). *AI-Powered Rules as Code: Experiments with Public Benefits Policy.* Beeck Center / Digital Benefits Network / Georgetown MDI report, 24 Mar 2025.
- https://digitalgovernmenthub.org/publications/ai-powered-rules-as-code-experiments-with-public-benefits-policy/
- Verified: yes (report page).
- Summary: Four experiments on SNAP and Medicaid in seven states with GPT-4o, ChatGPT and Gemini: chatbot eligibility Q&A, RAG summaries, rule extraction and code generation. Web chatbots give confidently wrong answers. RAG gives high accuracy but low completeness.
- Relation: Grey literature on Rules as Code + LLM for SNAP and Medicaid. It motivates the deployment pathway. Threat: none.

### Ratna, Weeks, Lavista Ferres, Chopra, Pereira (2024). *A Methodology for Using LLMs to Create User-Friendly Applications for Medicaid Redetermination and Other Social Services.* *International Journal of Public Health* 69. DOI 10.3389/ijph.2024.1607317.
- https://pmc.ncbi.nlm.nih.gov/articles/PMC11361957/
- Verified: yes (PMC).
- Summary: GPT-4o extracts Medicaid rules for WA, ND and SC and generates Python eligibility apps.
- Relation: Deployment context (LLM-built eligibility tools). Threat: none.

### Magesh, Martin, Surani, Perez, Rodolfa, Ho (2026). *Evaluating Generative AI in Benefits Administration: A Demonstration Project.* Proc. ACM Symposium on Computer Science and Law (CSLAW '26), pp. 86–100. DOI 10.1145/3788646.3789527.
- Verified: yes (full PDF from dho.stanford.edu and Crossref).
- Summary: A collaboration with the US DOL and Colorado on **unemployment-insurance adjudication**. A fine-tuned LLM assists fact-finding, evaluated in an RCT on historical cases. It improves on observational baselines but not on the sandbox control.
- Relation: The strongest evidence that LLMs are entering **benefits adjudication**, which strengthens our motivation. It does not test cue invariance. Threat: none.

### Steenhuis & Westermann (2024). *Getting in the Door: Streamlining Intake in Civil Legal Services with LLMs.*
- arXiv:2410.03762. Verified: yes (arXiv). Summary: A combination of logical rules and LLMs gives eligibility recommendations for legal-aid intake (8 LLMs, best F1 0.82). Relation: eligibility screening with open-textured criteria. Threat: none.

### Jo, Zhang, Cai, Goyal (2025). *AI Trust Reshaping Administrative Burdens: Understanding Trust-Burden Dynamics in LLM-Assisted Benefits Systems.* FAccT 2025 (per arXiv).
- arXiv:2505.22418. Verified: yes (arXiv). Summary: 10 interviews with SNAP applicants. Relation: deployment and HCI context. Threat: none.

### Grey literature on Medicaid work requirements (context, not prior work)
- Stanford Law "Legal Aggregate" blog (3 Sep 2026), *Roles for AI in Implementation of Medicaid Work Requirements*, https://law.stanford.edu/2026/09/03/roles-for-ai-in-implementation-of-medicaid-work-requirements/ ; CBPP, *Assessing the Medicaid Work Requirement Vendor Landscape*. Verified: no (search snippets only). Both say that under H.R. 1 (2025), Medicaid's 80 hours/month community-engagement requirement starts on 31 Dec 2026, that several states plan to use AI, and that vendors use AI to classify documents and extract hours.
- Relation: **This is a strong timeliness hook.** The 80-hours rule is exactly our "relevant-cue" condition, and its deployment starts during the ACL 2027 review cycle. Verify these sources before citing them.

---

## 2. Distractors and irrelevant *social* information in rule-governed decisions

(GSM-IC, GSM-Symbolic, GSM-DC and Wu et al. 2024 are covered in the existing review and are not repeated.)

### Tamkin, Askell, Lovitt, Durmus, Joseph, Kravec, Nguyen, Kaplan, Ganguli (2023). *Evaluating and Mitigating Discrimination in Language Model Decisions.*
- arXiv:2312.03689 (6 Dec 2023). https://arxiv.org/abs/2312.03689
- Verified: yes (arXiv).
- Summary: 70 LM-generated decision scenarios (financing, housing eligibility and others) with age, gender and race varied explicitly or implicitly, analysed with mixed-effects models. Claude 2.0 shows positive and negative discrimination in some settings, and prompt interventions reduce it.
- Relation: The canonical **decision-discrimination template**. Its scenarios have **no gold and no rule**, so every demographic effect is "discrimination" by assumption. We add a rule-computed gold, which separates error from discretion and lets the cue be relevant or irrelevant by statute. Threat: low-medium (it is the generic method). Must cite.

### Kearney, Binns, Gal (2025). *Language Models Change Facts Based on the Way You Talk.*
- arXiv:2507.14238 (v1 17 Jul 2025; no venue listed). https://arxiv.org/abs/2507.14238
- Verified: yes (arXiv abstract and HTML).
- Summary: Real user conversations from PRISM, which carry implicit race, gender and age markers, are prepended to queries in five domains, including **US government benefits eligibility**: 50 USAGov benefits, each with a "Yes" and a "No" scenario that has an objective answer. Llama3-70B and Qwen3-32B are **less likely to tell female and non-binary users that they are eligible**, even though eligibility does not depend on gender.
- Relation: **The closest prior result**: identity cues shift rule-governed benefits eligibility answers. However, it (a) reports consistency across identities, **not accuracy or error direction** against gold (confirmed in the HTML), (b) manipulates identity only, implicitly through dialect, with no effort, cause, responsibility or deservingness cues, (c) has no relevant-cue condition, (d) has no group-level eligibility-rate analysis, (e) tests two open models only, and (f) uses short USAGov criteria rather than multi-step statutory tests. Threat: **high** for the headline "LLMs let social cues change benefits eligibility". Our paper must cite it prominently and position itself as a test of deservingness cues conditioned on whether the rule makes them relevant, with gold-based directional error, on frontier models.

### Salinas, Haim, Nyarko (2024). *What's in a Name? Auditing Large Language Models for Race and Gender Bias.*
- arXiv:2402.14875. Verified: yes (arXiv).
- Summary: Name-based audit across 42 templates (including GPT-4). Advice disadvantages Black and female names. **Numerical, decision-relevant anchors counteract the bias, while qualitative details have inconsistent effects and can increase disparities.**
- Relation: Directly predictive for us. Numeric rule inputs should suppress cue effects, so leakage should concentrate where facts are qualitative or the computation is long. This informs the design (numeric versus narrative fact presentation as a factor). Threat: low.

### An, Acquaye, Wang, Li, Rudinger (2024). *Do Large Language Models Discriminate in Hiring Decisions on the Basis of Race, Ethnicity, and Gender?* ACL 2024 (Short), pp. 386–397. DOI 10.18653/v1/2024.acl-short.37.
- Verified: yes (Anthology). Summary: Name-based hiring audit. Effects are idiosyncratic and sensitive to the prompt. Relation: ACL precedent for name audits and prompt sensitivity. Threat: low.

### Hofmann, Kalluri, Jurafsky, King (2024). *AI generates covertly racist decisions about people based on their dialect.* *Nature* 633(8028):147–154. DOI 10.1038/s41586-024-07856-5.
- Verified: yes (Crossref).
- Relation: Implicit identity (dialect) drives consequential decisions. Cite for implicit cues. Threat: low.

### Bai, Wang, Sucholutsky, Griffiths (2025). *Explicitly unbiased large language models still form biased associations.* *PNAS* 122(8). DOI 10.1073/pnas.2416228122.
- Verified: yes (Crossref). Relation: Explicit fairness can coexist with implicit bias in decisions, which motivates testing implicit deservingness cues. Threat: low.

### Shafiei, Li, Tsvetkov (2026). *Moral Safety in LLMs: Exposing Performative Compliance with Puzzled Cues.*
- arXiv:2606.31644 (30 Jun 2026). Verified: yes (arXiv).
- Summary: Models look fair when identity is an explicit label and become less fair when identity must be inferred (+4.4 pp harmful decisions). They call this "performative compliance".
- Relation: Important for design. Explicit "race: X" fields will understate leakage, so cues should be embedded naturally. It also gives a reviewer-proof argument for narrative cues. Threat: low.

### Vohra & Ravikiran (2026). *The Audit Decides the Verdict: Instrument Effects Rival Demographic Bias in LLM Decision Audits.* REALM workshop @ EMNLP 2026 (per arXiv).
- arXiv:2609.09048. Verified: yes (arXiv).
- Summary: The direction of demographic bias in charitable aid flips between one-at-a-time rating and side-by-side ranking. Across hiring, lending and triage, audit construction (listing order, transparency) matters as much as demographics, and models recognise audits.
- Relation: Methodological warning. We should fix the decision format to the deployment format (single-case determination) and report audit-recognition checks. Threat: low.

### Basu & Chakraborty (2026). *When Names Change Verdicts: Intervention Consistency Reveals Systematic Bias in LLM Decision-Making* (ICE-Guard).
- arXiv:2603.18530. Verified: yes (arXiv).
- Summary: 3,000 vignettes, 10 domains, 11 LLMs. Authority bias (5.8%) and framing bias (5.0%) exceed demographic bias (2.2%). **Structured decomposition (LLM extracts features, a deterministic rubric decides) cuts flip rates.**
- Relation: Supports our claim that non-demographic cues (framing, effort) matter more than demographics, which echoes FairFund. Also gives a mitigation baseline. No legal gold. Threat: low-medium.

### Morla, Bellibatlu, Singh, Kapoor (2026). *AgentFairBench: Do LLM Agents Discriminate When They Act?* and Bellibatlu et al. (2026). *Instability Floors… FairMedAgent.*
- arXiv:2606.16723; arXiv:2609.03221. Verified: yes (arXiv).
- Relation: Counterfactual flip-rate audits in hiring, lending and triage. The second paper shows that flip rates need a **measured run-to-run instability floor** (2.5–23.7%). We already plan duplicate runs, so cite the second for that. Threat: low.

### Soffer, Omar, Efros, Apakama, Mudrik, et al. (2026). *Sociodemographic bias in large language model clinical trial screening.* *JAMIA* 33(8):1504–1509. DOI 10.1093/jamia/ocag058 (medRxiv 10.1101/2025.11.15.25340177, Nov 2025).
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12668082/
- Verified: yes (PMC and Crossref).
- Summary: 58 RCT protocols × 15 vignettes × 34 identity labels (including low-income, **unemployed** and **homeless**) × 9 LLMs, for 5.3M evaluations. **Eligibility judgments under fixed criteria were largely stable** (only homelessness passed the triviality threshold, −0.121). Large SES gradients appeared in judgments **outside** the criteria (adherence −0.595, resources −0.715 for homeless). The authors conclude that bias is "conditional": consistent within fixed criteria, and echoing inequities outside them.
- Relation: **The closest analogue in another domain** (rule-governed eligibility with SES and identity cues), and it predicts a **null** inside rule-governed eligibility. That is both a threat and an opportunity. Our relevance-conditioned design tests exactly the boundary they describe (criteria-governed versus discretionary). ABAWD-type rules, where effort is *inside* the criteria, are the case they do not test. Threat: **medium-high**. Must cite and engage.

### Hu, Xue, Li, Zheng, et al. (2025). *LLMs on Trial: Evaluating Judicial Fairness for Large Language Models* (JudiFair).
- arXiv:2507.10852 (v2 2 Aug 2025). Verified: yes (arXiv). The venue is not verified.
- Summary: 177,100 counterfactual Chinese case facts that swap 65 **legally irrelevant** labels (demographic, substantive, procedural) across 16 LLMs. Inconsistency, bias and imbalanced inaccuracy are pervasive, demographic labels are the most biased, and the bias direction mirrors human sentencing biases.
- Relation: A large legal "legally irrelevant label" counterfactual benchmark. Criminal sentencing, Chinese law, no computable gold, and no relevance conditioning. Threat: medium on the "legally irrelevant factors" framing.

### Chen, Cai, Hou, Dong (2026). *Which Changes Matter? Towards Trustworthy Legal AI via Relevance-Sensitive Evaluation and Solver-Grounded Reasoning* (LexGuard).
- arXiv:2605.26530 (26 May 2026). Verified: yes (arXiv abstract and HTML).
- Summary: Explicit **should-change versus should-not-change** evaluation for legal AI. Should-not-change perturbations include judicial-fairness (demographic and procedural) counterfactuals, paraphrase, inapplicable statutes and irrelevant opinions. Should-change perturbations include statutory elements, thresholds, mental state and exceptions. The setting is Chinese criminal law (LeCaRDv2, LEEC, an 8,000-case perturbation set), with an SMT-grounded multi-agent system.
- Relation: **Conceptually the closest to "rule-relevance-conditioned invariance"**. They also require both invariance to legally irrelevant changes and sensitivity to material ones. But it is criminal law, not welfare. The same *type* of cue is never relevant in one rule and irrelevant in another, there is no deservingness or moral-cue taxonomy, no directional or group-rate analysis, and it is primarily a system paper. Threat: **medium-high on framing**. We must cite it and say what differs: we hold the cue fixed and switch its **legal relevance** across rules (SNAP income test versus ABAWD), which they do not.

### Posner & Saran (2025/2026). *Judge AI: A Case-Study of Large Language Models as Judges.* *Journal of Law & Empirical Analysis* 3(1) (published 19 Mar 2026). DOI 10.1177/2755323X261433614. Working paper: Coase-Sandor WP 25-03, SSRN 5098708.
- https://chicagounbound.uchicago.edu/law_and_economics/1044/
- Verified: partial. Crossref confirms the journal record. I read the abstract on Chicago Unbound. SAGE and SSRN returned 403.
- Summary: Replicates Spamann & Klöhn's 2×2 experiment (sympathetic versus unsympathetic defendant × precedent) with GPT-4o. **GPT-4o follows precedent and ignores the legally irrelevant sympathy cue**, like law students and unlike federal judges. Prompting it to behave like judges barely changes this.

### Posner & Saran (2026). *Silicon Formalism: Rules, Standards, and Judge AI.* SSRN 6155012 (29 Jan 2026). DOI 10.2139/ssrn.6155012.
- Verified: partial (Crossref record; the SSRN page returned 403; content from a news report and search snippets).
- Summary: Replicates the 61-judge choice-of-law experiment (rule versus standard × party sympathy × accident location). **GPT-5 and Gemini 3 Pro give the legally correct outcome 100% of the time**, against 52% for judges. Weaker models do worse (GPT-4.1 50%, o4-mini 79%).
- Relation for both papers: **This is the strongest null-risk evidence.** Frontier models are "formalist" and ignore sympathy when the law is clear. Threat to novelty: **medium**, because the sympathy-versus-legal-rule manipulation exists, though with a single case, tiny N and no welfare domain. Threat to the *expected result*: **high**. The paper must be framed so that either outcome is informative. Our likely added value: (a) a population of computable cases, (b) multi-step means tests and exemption logic, where OpenExempt and "Confidently Wrong" show frontier degradation, (c) relevance conditioning, since a perfectly formalist model must *use* effort under ABAWD, and (d) group-rate consequences. Human baselines: Spamann & Klöhn (2016), *J. Legal Studies* 45(2):255–280, DOI 10.1086/688861 (verified via Crossref), and Spamann & Klöhn (2024), *J. Law & Empirical Analysis* 1(1):149–161, DOI 10.1177/2755323X231210467 (verified via Crossref).

### Huang et al. (2026). *Beyond the Binary: Gender Bias in LLM-Evaluated Insurance Claims.* Working paper (CRAI PDF).
- https://media.crai.com/wp-content/uploads/2026/07/29155621/Beyond-the-Binary_-Gender-Bias-in-LLM-Evaluated-Insurance-Claims.pdf
- Verified: **no** (search snippet only).
- Summary (per the snippet): 1,388 vehicle claims × 4 gender conditions × name and narrative presence across 6 LLMs. Claim eligibility and amount show no male/female gap under full information, but gaps appear under other prompt configurations.
- Relation: Claims adjudication with an eligibility outcome. Low-medium threat. Verify before citing.

### Gender-bias study in Czech family law (2026). arXiv:2601.05879 (AIDA2J @ JURIX 2025).
- Verified: yes (arXiv metadata only). Low relevance.

---

## 3. Moral and deservingness cues, and separating factual determination from normative judgment

### Hosseini, Khanna, Pierce (2026). *The Judgment-Consequence Gap: LLM Moral Reasoning in Healthcare Decisions.* AIES 2026 (per arXiv).
- arXiv:2608.05583 (6 Aug 2026). Verified: yes (arXiv).
- Summary: In scarce-treatment vignettes, LLMs agree with humans that patients are **responsible** for health-harming behaviour but **refuse to let responsibility affect allocation** (they randomise instead). The divergence grows with capability.
- Relation: **Directly relevant to the factual/normative split.** It shows a dissociation between a normative judgment (responsibility) and a decision, which is the mirror of our design (a deservingness judgment versus a rule determination). It predicts that frontier models suppress responsibility cues in decisions, which is another null-risk signal. But there the suppression is normatively contested, whereas in our setting the rule decides when suppression is correct. Threat: medium (conceptual). Must cite.

### Sun, Wu, Guo, Pei, Echizen, El Ali, Sugawara (2026). *When Trust Meets Truth: Trust–Truth Separability in LLM-as-Judge.*
- arXiv:2608.21097 (21 Aug 2026). Verified: yes (arXiv).
- Summary: Changing only the source cue (human versus AI) shifts both trust scores and **binary truth verdicts** and logit probabilities. Judgment dimensions that should be separable are not.
- Relation: An analogous "separability" test (normative signal leaking into a factual verdict) in a different domain. Cite it for the general separability construct. Threat: low-medium.

### Kim & Flanigan (2026). *Right or Wrong, Models Comply: Directional Blindness in LLM Moral Judgment.*
- arXiv:2606.14037. Verified: yes (arXiv).
- Summary: Models follow helpful nudges more than harmful ones on factual questions (A = 1.58) but not on moral questions (A = 1.04).
- Relation: Evidence of a factual-versus-moral asymmetry in robustness. It supports the hypothesis that a determination framed as normative ("should this person get SNAP?") leaks more than one framed as factual ("does this household pass the gross income test?"). This framing manipulation is cheap to add. Threat: low.

### Shaw, Hahn, Rasgaitis, Mishra, Liu, Jaques, Tsvetkov, Zhang (2026). *Are Language Models Sensitive to Morally Irrelevant Distractors?*
- arXiv:2602.09416 (v2 20 Jun 2026). Verified: yes (arXiv).
- Summary: 60 situationist distractors (for example, smells or ambient noise) shift LLM moral judgments by more than 30%.
- Relation: Moral judgment is affected by morally irrelevant information. Our direction is the reverse (rule judgment affected by moral information). It complements Tennant et al. (already covered). Threat: low.

### Kilov, Hendy, Guyot, Snoswell, Lazar (2025). *Discerning What Matters: A Multi-Dimensional Assessment of Moral Competence in LLMs* (arXiv:2506.13082), and Kilov, Guyot, Hendy, Li, Lazar (2026). *A Scalable Approach to Evaluating Moral Sensitivity in LLMs* (arXiv:2607.02972).
- Verified: yes (arXiv).
- Summary: Moral sensitivity is the ability to identify morally relevant features among irrelevant noise, framed as an **invariance** property.
- Relation: Philosophical grounding for "relevance-conditioned" evaluation: competence means using a feature exactly when it is relevant. Threat: low.

### Wu & Xiao (2026). *Proxy reliance in large language model decisions is uncalibrated to predictive evidence.*
- arXiv:2608.22887 (24 Aug 2026). Verified: yes (arXiv abstract and HTML).
- Summary: Clinical-ranking task with a synthetic generating process, so the **evidence-warranted reliance on each proxy is computed exactly** (an ideal Bayesian learner). One audit yields over-reliance, warranted reliance or under-reliance. With zero-information proxies, every model relies on them (+11–23 pp). Social field names suppress reliance, and in-context examples restore it. Accuracy and proxy reliance are independent. Models: Claude Sonnet 4.5, DeepSeek-V4-Flash, Qwen3.7-max and GPT-5.6.
- Relation: **The closest framework for "use the cue exactly as much as warranted"**, with a three-way verdict (over, warranted, under) that maps onto our relevant and irrelevant conditions. The differences: warrant is *statistical* (predictive value), not *legal* (statutory relevance); the domain is clinical triage; there is no moral or deservingness content; and there are no welfare consequences. Threat: **medium-high on framing**. We should adopt its over/warranted/under vocabulary and contrast statistical with legal warrant explicitly.

### Weller & Barkett (2026). *Whose Alignment? Comparing LLM Process Alignment Across Diverse Organizational Decision Contexts.* Pluralistic Alignment Workshop @ ICML 2026 (per arXiv).
- arXiv:2605.25256. Verified: yes (arXiv).
- Summary: Policy-capturing regression measures whether an LLM reproduces an organisation's decision policy (attribute weights), not only its outcomes, including ECHR Article 6 decisions. Models adopt the legitimate policy component and resist protected attributes.
- Relation: "Process alignment" to a *specified policy* is close to our "apply the official rule's weights". Cite it for the method (attribute-weight recovery). Threat: low-medium.

### Freedman & Toni (2026). *Superficial Beliefs in LLM Decision-Making.* COLM 2026 (per arXiv).
- arXiv:2606.11016. Verified: yes (arXiv).
- Summary: Model self-reports of which attribute mattered only partly match the behaviourally inferred driver.
- Relation: Justifies measuring cue use behaviourally rather than from rationales. Threat: none.

### Human anchors for the factual/normative split (not LLM work)
- Spamann & Klöhn (2016, 2024): see Section 2. Judges, but not students, are moved by legally irrelevant sympathy.
- Alecu, Sadeghi, Terum (2025). *Street-level bureaucrats' attitudes towards clients in discretionary decision-making: Evidence from the Norwegian labour and welfare administration.* *Public Policy and Administration*. DOI 10.1177/09520767241299078. **Verified: no** (search snippet). A vignette experiment with 925 NAV caseworkers in which perceived client responsibility shifts discretionary decisions. It would be a good human comparator for an "effort or responsibility" cue in welfare administration. Verify before citing.

---

## 4. Measurement validity of LLMs as instruments (2024–2026)

### Halterman & Keith (2026). *Codebook LLMs: Evaluating LLMs as Measurement Tools for Political Science Concepts.* *Political Analysis* 34(2):188–204. DOI 10.1017/pan.2025.10017.
- https://www.cambridge.org/core/journals/political-analysis/article/codebook-llms-evaluating-llms-as-measurement-tools-for-political-science-concepts/7B323A0E47F782F2698A0AE849EA00DE
- Verified: yes (Cambridge page).
- Summary: A five-stage framework, including **label-free behavioural tests**, for whether LLMs follow codebook operationalisations. LLMs often fall back on lexical heuristics or *background concepts* instead of the codebook definition.
- Relation: **The best measurement-validity analogue.** An eligibility rule is a codebook, and "deservingness leakage" is the model substituting the lay background concept ("needy and deserving") for the operational definition ("gross income ≤ 130% FPL"). This framing is strong for ACL/CSS reviewers. Threat: low (no welfare, no invariance with moral cues).

### Wallach, Desai, Cooper, Wang, … Jacobs (2025). *Position: Evaluating Generative AI Systems Is a Social Science Measurement Challenge.* ICML 2025, PMLR 267:82232–82251.
- arXiv:2502.00561. Verified: yes (arXiv). Relation: The general framework (systematised concept → measurement instrument → validity). Threat: none.

### Jacobs & Wallach (2021). *Measurement and Fairness.* FAccT 2021, pp. 375–385. DOI 10.1145/3442188.3445901.
- Verified: yes (Crossref). Relation: Foundational for construct validity in fairness. Our "legal relevance" is the operationalisation that defines which invariances are required. Threat: none.

### Bean, Kearns, Romanou, et al. (2025). *Measuring what Matters: Construct Validity in Large Language Model Benchmarks.* NeurIPS 2025 Datasets and Benchmarks.
- arXiv:2511.04703. Verified: yes (arXiv). Summary: A review of 445 benchmarks with eight recommendations. Relation: a checklist to follow (define the phenomenon, justify the metric). Threat: none.

### Salaudeen, Reuel, Ahmed, … Koyejo (2025). *Measurement to Meaning: A Validity-Centered Framework for AI Evaluation.*
- arXiv:2505.10573. Verified: yes (arXiv). Relation: Validity of the claims made from benchmark scores. Threat: none.

### Desai, Card, Jacobs (2026). *Validating LLMs in social science: Epistemic threats and emerging norms.*
- arXiv:2607.07915 (8 Jul 2026). Verified: yes (arXiv).
- Summary: A systematic review of LLM validation practices in eight social-science journals finds validation inconsistent and limited.
- Relation: Motivates our "LLM as eligibility instrument" framing. Threat: none.

### TeBlunthuis, Hase, Chan (2024). *Misclassification in Automated Content Analysis Causes Bias in Regression. Can We Fix It? Yes We Can!* *Communication Methods and Measures* 18(3):278–299. DOI 10.1080/19312458.2023.2293713.
- arXiv:2307.06483. Verified: yes (arXiv; the journal details come from the arXiv comment and a search snippet).
- Relation: Differential misclassification biases downstream regressions. This is the statistical basis for our group-level eligibility-rate consequence. It complements Egami and Camuffo (already covered). Threat: none.

### Liu, J. (2026). *What Is Actually Being Annotated? Inter-Prompt Reliability as a Measurement Problem in LLM-Based Social Science Labeling* (arXiv:2604.16413), and Humblot-Renaux et al. (2026). *LLMs as annotators of credibility assessment in Danish asylum decisions* (LAW-XX @ ACL 2026; arXiv:2605.13412).
- Verified: yes (arXiv). Relation: Prompt variance and error analysis "beyond aggregated metrics" in legal annotation. Threat: none.

### Purushothama, Min, Waldon, Schneider (2025/26). *Prompting from the bench: Large-scale pretraining is not sufficient to prepare LLMs for ordinary meaning analysis.* FAccT 2026 (per arXiv; earlier title "Not ready for the bench…", NLLP 2026).
- arXiv:2510.25356. Verified: yes (arXiv). Relation: Legal interpretation by LLMs is unstable under question format. It supports reporting format robustness. Threat: none.

---

## 5. Near neighbours on welfare and allocation (2025–2026) not in the existing review

- **Shi, Ma, Huang, et al. (2025).** *Social Welfare Function Leaderboard: When LLM Agents Allocate Social Welfare.* arXiv:2510.01164. Verified: yes. An efficiency-versus-Gini allocation simulation with 20 LLMs. No rules, no gold eligibility. Threat: low.
- **Benavides Cantos & Garrido-Merchán (2026).** *Social Policy of LLMs: How GPT, Claude, DeepSeek and Grok Allocate Social Budgets in Spain and Germany.* arXiv:2605.10234. Verified: yes. Macro budget allocation. Threat: none.
- **Moon, Tamura, Zhai, Habib, Shirazi, Kassam, Saxena, Guha (2026).** *The Promises and Perils of using LLMs for Effective Public Services.* arXiv:2601.15163 (ACM DOI 10.1145/3772318.3790297). Verified: yes (arXiv). Child-welfare casenotes. LLMs fail where discretionary judgment is needed. Threat: none.
- **Castleman, Shen, Metevier, Springer, Korolova (2026).** *Measuring Validity in LLM-based Resume Screening.* arXiv:2602.18550. Verified: yes. Synthetic resumes with **known qualification ground truth** test whether models pick the more qualified candidate, and demographic selection rates vary. It is a "known-gold + demographic" design in hiring. Threat: low-medium (it shows the "gold + identity" design exists outside welfare).

---

## Ranked top-5 novelty threats

1. **Kearney, Binns & Gal (2025), arXiv:2507.14238.** Implicit identity markers make Llama3 and Qwen3 less likely to say women and non-binary users are **eligible for US government benefits** whose criteria ignore gender.
   - *Why it threatens:* It already shows that social cues shift rule-governed benefits eligibility.
   - *What we add:* deservingness cues (effort, cause, responsibility), not only identity; gold-based **accuracy and error direction** (false denial versus false approval), which they do not compute; multi-step statutory tests (SNAP gross and net income, ABAWD); the relevant-cue condition; group eligibility-rate consequences; and frontier models.
2. **Soffer et al. (2026), JAMIA 33(8).** For trial eligibility under fixed criteria, LLMs are **stable** across SES and identity, including unemployed and homeless. Bias appears only outside the criteria.
   - *Why it threatens:* It is a large-scale (5.3M) direct analogue that predicts a null inside rule-governed eligibility.
   - *What we add:* a test of the boundary they hypothesise, with a cue that is irrelevant under one rule and **relevant inside the criteria** under another (ABAWD hours, exemptions); welfare deservingness cues rather than identity labels; and computable gold rather than a 1–5 rating.
3. **Chen, Cai, Hou & Dong (2026), "Which Changes Matter?", arXiv:2605.26530.** Should-change and should-not-change evaluation of legal AI, including demographic counterfactuals and threshold or exception changes.
   - *Why it threatens:* It is the same two-sided "relevance-sensitive" evaluation idea.
   - *What we add:* the *same* cue switches legal relevance across rules (a within-cue, between-rule design); a welfare domain with official US rules; a morally valenced deservingness taxonomy; directional bias; and population-level eligibility consequences. Theirs is a Chinese criminal-law system paper.
4. **Wu & Xiao (2026), "Proxy reliance… uncalibrated", arXiv:2608.22887.** Exact computation of **warranted reliance**, with over, warranted and under verdicts.
   - *Why it threatens:* It is the closest formal framing of "use a cue exactly as much as warranted".
   - *What we add:* *legal* warrant (statutory relevance) instead of *statistical* warrant. These can conflict, since effort may be predictive but legally irrelevant. We also add moral and deservingness content, welfare rules and frontier determinations. We should adopt and cite their vocabulary.
5. **Posner & Saran (2025/2026), Judge AI (J. Law & Empirical Analysis 3(1)) and Silicon Formalism (SSRN 6155012).** GPT-4o and GPT-5 ignore legally irrelevant **sympathy** and apply the rule, in GPT-5's case 100% correctly.
   - *Why it threatens:* The sympathy-versus-law manipulation exists, and it predicts that frontier models are formalist (null risk).
   - *What we add:* many computed cases instead of one replicated vignette; multi-step means tests and exemptions, where frontier models do degrade (OpenExempt; Confidently Wrong); relevance conditioning, since a formalist must still *use* effort under ABAWD; directional errors; and group rates.

Close runners-up:
- **OpenExempt (arXiv:2601.13183).** Symbolic statute gold plus legally irrelevant distractors, but no social or moral distractors.
- **Hosseini, Khanna & Pierce (AIES 2026).** Responsibility is judged but not used in allocation.
- **Tamkin et al. 2023.**
- **PolicyBench (PolicyEngine).** Tool-free SNAP and Medicaid calculation accuracy, with no cue manipulation.
- **FairFund-Bench** (already covered).

## The gap our paper fills

No verified prior work does all of the following on **official welfare eligibility rules**:
- (i) It holds the legally material facts fixed, so that the gold is **computed from the rule**.
- (ii) It manipulates **deservingness cues** (effort, cause of hardship, responsibility, identity), not only demographics, and checks that the manipulation registers on a normative probe.
- (iii) It **conditions the required behaviour on legal relevance**: invariance where the rule makes the cue irrelevant (SNAP income tests) and correct use of the *same kind of cue* where the rule makes it relevant (ABAWD 80 hours/month and its exemptions).
- (iv) It scores **directional error** against gold (wrongful denial versus wrongful approval) rather than only flip rates.
- (v) It translates item-level leakage into **group-level eligibility-rate distortions** for populations that differ only in legally irrelevant attributes.

Kearney et al. come closest on (i) and (ii, identity only). Chen et al. and Wu & Xiao come closest on (iii) in other domains. Soffer et al. and Posner & Saran supply the competing null hypothesis ("within clear criteria, models are formalist"). Our paper can therefore claim to be **the first relevance-conditioned test of deservingness leakage in statutory eligibility determination**. It is informative under either result: leakage is a validity failure with known-sign consequences, and formalism is good news only if the model also uses cues correctly when the law requires them.

## Design implications drawn from this review
1. **Plan for a null on simple items.** Posner & Saran, Soffer et al. and Haim et al. all suggest that clear numeric criteria suppress cue effects. Include multi-step items (net income with deductions, ABAWD exemption chains), where OpenExempt and Confidently Wrong show frontier degradation, and qualitative fact presentation (Haim et al.).
2. **Use implicit as well as explicit cues** (Shafiei et al.: performative compliance), and add an audit-recognition check (Vohra & Ravikiran).
3. **Report a run-to-run instability floor** (Bellibatlu et al.) before interpreting flip rates.
4. **Control for exemption anchoring** on ABAWD items (Confidently Wrong). Otherwise errors in the relevant-cue condition could be logic errors rather than deservingness effects.
5. **Factual versus normative question framing** ("does the household pass the test?" versus "should they receive SNAP?") is a cheap manipulation motivated by Kim & Flanigan and by Hosseini et al.
6. **Mitigation arms:** Chain of Logic (Findings ACL 2024), and "LLM extracts, rules engine decides" (Jurayj et al.; ICE-Guard structured decomposition), with PolicyEngine-US as the rules engine.
7. **Timeliness hook:** H.R. 1 Medicaid community-engagement (80 h/month) requirements start on 31 Dec 2026, and several states plan AI-assisted verification. Verify the Stanford Law and CBPP sources before citing them.

## Items to verify before citing (not fully verified here)
- SARA and Blair-Stanek et al. 2023 venues (NLLP 2020 and ICAIL 2023, from memory).
- LegalBench venue (NeurIPS 2023 D&B, from memory).
- LLMs on Trial venue.
- Huang et al. insurance-claims paper (snippet only).
- Alecu et al. 2025 (snippet only).
- Stanford Law blog and CBPP pages on Medicaid work requirements (snippet only).
- Silicon Formalism full text (SSRN 403; metadata via Crossref).
