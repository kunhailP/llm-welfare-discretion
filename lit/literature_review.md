# Literature review: Separating Material Need from Deservingness in LM Evaluation

Survey date: 2026-10-05. Target: NAACL 2027 via ARR October 2026 cycle.

**How things were checked.** "Verified = yes" means I opened the primary page myself: the arXiv abstract or HTML, the ACL Anthology page, the GitHub repo or raw files, the publisher PDF, or the Crossref, OSF, Dataverse or Hugging Face API record. I did not rely on search snippets. Where a publisher page blocked access (HTTP 403), I checked the metadata through the Crossref API record for the DOI, and the entry says so. For arXiv-only papers, venue claims come from the arXiv "Comments" field and are noted as such.

---

## 1. Closest competitor: FairFund-Bench

### Lukk (2026). *FairFund-Bench: Evaluating Distributive Bias in LLM Resource Allocation.* arXiv:2607.28934 (v1 31 Jul 2026, v2 11 Sep 2026). The arXiv comment says "Accepted to Findings of the ACL: EMNLP 2026".
- URL: https://arxiv.org/abs/2607.28934 · code/data: https://github.com/martinlukk/fairfund-bench · Zenodo DOI 10.5281/zenodo.21959599
- Verified: **yes**. I opened the arXiv abstract, the HTML full text, the repo README, `data/codebook.md`, `benchmark/prompts.yaml`, `CITATION.cff` and the head of `stimuli.csv`.
- **What it measures.** Distributive bias in LLM allocation of scarce aid. There are 600 human-authored first-person crowdfunding-style appeals in 3 need domains (Medical, Rent, Education), with 5 scenarios per domain. Each appeal is crossed with 4 races × 2 genders (signalled by validated names from Elder & Hayes 2023) and with 5 **causal framings of need** that operationalise the CARIN *Control* criterion: no_cause, structural, self_cause, stigma_no_redemption, and stigma_redemption (e.g., alcoholism plus treatment). With 5 names per cell this gives 3,000 stimuli. Three elicitation tasks: Rate (1–5 "funding priority"), Rank (bundles of 2/4/5), and Allocate ($10,000 across a bundle). Bundles are either "transparent" (only the focal axis varies) or "disguised" (Latin-square co-variation). The paper tests 14 API models, collected April 2026 at temperature 0. Scoring has four pillars: demographic bias, deservingness alignment, cross-task consistency and cross-context consistency.
- **Key findings.** The audit format flips the direction of demographic bias: models favour minorities on Rate and penalise some groups on Rank. Disguised audits show larger bias than transparent ones. Effects of causal framing are about an order of magnitude larger than demographic effects, so "LLMs robustly reproduce human deservingness evaluations."
- **Data format and license.** `data/outcomes.csv` (107,940 rows × 28 columns; one row per claimant-response with rating/rank/dollars plus covariates and validity flags), `data/stimuli.csv` (3,000 rows; full appeal text), `data/models.csv`, `codebook.md` and `benchmark/prompts.yaml`. Code is MIT and data is CC BY 4.0. Model outputs are also subject to the providers' terms of service.
- **Notable detail.** `prompts.yaml` contains `need` ("who would benefit most from receiving the funds") and `merit` ("who is most deserving of support") wording variants of the *task instruction*. These were collected but are **not analysed in the paper** (per the codebook). They change the decision criterion. They do not test a factual judgment.
- **Overlap and threat assessment (precise).**
  - *Shared:* welfare-deservingness theory (CARIN, van Oorschot) as the framing, controlled vignettes, open release, and the finding that LLMs respond strongly to deservingness cues. Reviewers will cite FairFund to say "LLMs follow deservingness heuristics is already known."
  - *Not shared, and defensible:* (i) FairFund **never holds material need fixed and verifiable**. Need magnitude is not manipulated, and its outputs are normative priority or allocation judgments where a deservingness effect is arguably *legitimate*. (ii) It has **no factual target with a ground truth**, so it cannot show that a deservingness cue *distorts a factual judgment*. Our SHORTFALL/SUFFICIENT label is computable from the stated numbers, so any effort effect is an error by construction. (iii) It manipulates *Control* (cause of need) but not *Effort* (current job search); in NICER terms those are distinct criteria. (iv) It does not frame LLMs as **measurement instruments or annotators** and does not study spurious group differences in downstream inference. (v) It has no factual-versus-normative prompt dissociation, no number-free textual condition, no neutral-irrelevant-detail control, and no open-weight 8–32B local models (its open-weight models are DeepSeek V3.2, Llama 4 Maverick and Mistral Large).
  - **Verdict:** moderate topical overlap and low methodological overlap. It must be cited prominently and positioned as complementary: FairFund shows LLMs make *deservingness-sensitive normative allocations*, and we test whether that sensitivity *leaks into factual need classification*. Use FairFund's "framing effects ≫ demographic effects" result as motivation.

### Other adjacent allocation/fairness papers (low overlap)
- **Han, Hosseini, Kavner, Khanna, Sikdar, Xia (2026). *Fair Like Us? Auditing LLM Alignment in Resource Allocation.*** arXiv:2609.29692 (submitted 31 Aug 2026; arXiv comment says EMNLP 2026 main). https://arxiv.org/abs/2609.29692. Verified: yes (abstract and HTML). The scenarios are stylised fair division (4 agents, 10 items) and explicitly "do not incorporate contextual factors such as need, merit, or prior disadvantage." Threat: low. Cite for "LLMs are sensitive to how information is framed in allocation."
- **Hosseini & Khanna (2025). *Distributive Fairness in Large Language Models: Evaluating Alignment with Human Values.*** NeurIPS 2025 (per arXiv comments). https://arxiv.org/abs/2502.00313. Verified: yes. Covers equitability, envy-freeness and Rawlsian maximin, and finds LLMs misaligned with human distributional preferences and sensitive to semantic and non-semantic variation. Threat: low.

---

## 2. Welfare deservingness theory

- **van Oorschot, W. (2000). Who should get what, and why? On deservingness criteria and the conditionality of solidarity among the public. *Policy & Politics* 28(1):33–48.** DOI 10.1332/0305573002500811. Verified: yes (Crossref). Origin of the five criteria (control, attitude, reciprocity, identity, need). This is the theoretical basis for treating "need" as one criterion that is conceptually separate from the others.
- **van Oorschot, W. (2006). Making the difference in social Europe: deservingness perceptions among citizens of European welfare states. *Journal of European Social Policy* 16(1):23–42.** DOI 10.1177/0958928706059829. Verified: yes (Crossref). Cross-national evidence on the deservingness ranking (elderly > sick/disabled > unemployed > immigrants). It establishes that the unemployed are a low-deservingness group, which is relevant to choosing an unemployed vignette.
- **Knotz, C. M., Gandenberger, M. K., Fossati, F., Bonoli, G. (2022). A Recast Framework for Welfare Deservingness Perceptions. *Social Indicators Research* 159(3):927–943** (online 20 Aug 2021). DOI 10.1007/s11205-021-02774-9. https://link.springer.com/article/10.1007/s11205-021-02774-9 (open access, CC BY 4.0). Verified: **yes**. I read the full OA PDF via d-nb.info/1245275992/34.
  - Proposes **NICER**: Need, Identity, Control, Effort, Reciprocity. It drops Attitude and splits the old "reciprocity" into past reciprocity and current **Effort** ("current acts that contribute to others in the future", e.g., active job search).
  - Defines need as "degree of hardship"; it explicitly includes "the current gap between one's costs of living and the available resources". Footnote 2, following Delton et al. 2018, distinguishes absolute need ("the amount of resources they need to have available but do not") from relative need. **Our resource-versus-expense shortfall is exactly their absolute-need definition. Quote it.**
  - Design: vignette experiments on unemployment benefit claimants in the US (AMT pre-test N=313 retained; Qualtrics N=356) and Germany (N=396), 2019. **Effort was operationalised as job applications per week:** "not looking", "1–2", "3–4" or "5–6 applications per week". Need was operationalised as *number of dependents*.
  - Findings: Control and Effort have the strongest effects on deservingness, and need effects were "ambiguous". Only the most extreme dependents condition was significant.
  - Relation: this directly motivates our Effort manipulation (8 vs 1 applications). Consider matching their wording (e.g., applications per week) for construct validity. It is also a critical contrast. In humans, effort drives *deservingness* while need (as dependents) barely does. We ask whether LLMs let effort drive *factual need*.
  - **Public data: yes.** OSF project https://osf.io/37me5/ ("Replication materials for 'A recast framework…'"), which is public (checked via the OSF API). It contains `Data/` (DesRecast_GER_Qualtrics.dta, DesRecast_US_Qualtrics.dta, DesRecast_US_AMT.dta), `Do Files/` (3 Stata scripts) and `Vignettes/SIR_vignettes.xlsx`. **No license is set on the OSF node**, so ask the authors before redistributing. Reusing the vignette wording or using the human effect sizes as reference values should be fine with citation.
- **Petersen, M. B. (2012). Social Welfare as Small-Scale Help: Evolutionary Psychology and the Deservingness Heuristic. *American Journal of Political Science* 56(1):1–16.** DOI 10.1111/j.1540-5907.2011.00545.x. Verified: yes (Crossref). The deservingness heuristic: lazy versus unlucky (effort) cues automatically drive welfare opinions.
- **Petersen, M. B., Slothuus, R., Stubager, R., Togeby, L. (2011). Deservingness versus values in public opinion on welfare: The automaticity of the deservingness heuristic. *European Journal of Political Research* 50(1):24–52.** DOI 10.1111/j.1475-6765.2010.01923.x. Verified: yes (Crossref). Deservingness cues override values and operate automatically. This is the human analogue of "effort cues dominate".
- **Petersen, M. B., Sznycer, D., Cosmides, L., Tooby, J. (2012). Who Deserves Help? Evolutionary Psychology, Social Emotions, and Public Opinion about Welfare. *Political Psychology* 33(3):395–418.** DOI 10.1111/j.1467-9221.2012.00883.x. Verified: yes (Crossref).
- **Aarøe, L., Petersen, M. B. (2014). Crowding Out Culture: Scandinavians and Americans Agree on Social Welfare in the Face of Deservingness Cues. *Journal of Politics* 76(3):684–697.** DOI 10.1017/s002238161400019x. Verified: yes (Crossref). A lazy versus unlucky unemployed recipient eliminates cross-cultural differences. **This is the canonical "effort cue for an unemployed person" manipulation.** I found no Dataverse entry for it (Harvard Dataverse search returned 0 hits).
- **Meuleman, B., Roosma, F., Abts, K. (2020). Welfare deservingness opinions from heuristic to measurable concept: The CARIN deservingness principles scale. *Social Science Research* 85:102352.** DOI 10.1016/j.ssresearch.2019.102352. Verified: yes (Crossref). Optional: a scale for the normative prompt.
- **Other public deservingness data (Harvard Dataverse; verified via the Dataverse API):**
  - Hsieh & Kline, "Replication Data for: Deservingness Heuristics Drive Redistributive Choices, But Weights on Recipient Effort Vary", doi:10.7910/DVN/AOT2JW (CC0; MTurk and student data, observable/unobservable effort). I did not verify the associated paper's venue.
  - Jensen & Petersen 2017 AJPS 61(1):68–83, "The Deservingness Heuristic and the Politics of Health Care", doi:10.7910/DVN/TIXGF8 (4 studies plus ESS data; no license field shown).
- Background (optional): **Allhutter et al. (2020), Algorithmic Profiling of Job Seekers in Austria, *Frontiers in Big Data* 3:5**, DOI 10.3389/fdata.2020.00005; **Desiere & Struyven (2021), Using AI to classify jobseekers: the accuracy-equity trade-off, *J. Social Policy* 50(2):367–385**, DOI 10.1017/s0047279420000203. Both verified via Crossref. They motivate the claim that algorithmic tools already sit in unemployment administration.

---

## 3. LLMs in welfare, social-policy and public-administration judgments

- **Pokharel, Farabi, Fowler, Das (2025). Street-Level AI: Are Large Language Models Ready for Real-World Judgments?** AIES 2025 (per arXiv). https://arxiv.org/abs/2508.08193. Verified: yes. Compares LLM prioritisation of households experiencing homelessness with vulnerability scoring systems and caseworker decisions. LLMs are inconsistent across runs, across models and against the scoring systems, though qualitatively aligned with lay pairwise judgments. Relation: motivates the run-to-run and duplicate-run controls. Threat: low, because it has no factual-versus-normative split and no controlled irrelevant cue.
- **Gosciak, Giannella, Guo, Chen, Koenecke (2026). LLMs in social services: How does chatbot accuracy affect human accuracy?** arXiv:2603.11213. https://arxiv.org/abs/2603.11213. Verified: yes. 770 SNAP questions; caseworker accuracy rises 27 pp with high-quality chatbots, and wrong suggestions harm accuracy. Relation: shows LLMs are used for *rule-based factual eligibility* in welfare, which is the deployment context where factual-need errors matter. Threat: low.
- **Le Coz, Liu, Bhattacharjya, Curto, Stinckwich (2025/26). What Would an LLM Do? Evaluating Large Language Models for Policymaking to Alleviate Homelessness.** arXiv:2509.03827. Verified: yes. Policy-level recommendations, not individual need. Threat: low.
- **Karr Jr. et al. (2025/26). "Not in My Backyard": LLMs Uncover Online and Offline Social Biases Against Homelessness.** arXiv:2508.13187. Verified: yes. Notes that LLM annotators "over-tag NIMBY (+11.5 pp) and under-detect factual claims (−30.5 pp)", an example of systematic LLM-annotation error on poverty-related text. Threat: low. Useful for the annotation-error motivation.
- **Li et al. (2026). Analyzing and Correcting Benevolence Bias in Large Language Models.** arXiv:2608.24912. Verified: yes (abstract). Aligned LLMs favour "kinder, safer, more socially approved" answers on value-laden survey items. Relation: a possible mechanism (prosocial bias) for normative leakage. Threat: low.
- I did **not find** any paper (as of 2026-10-05) that holds a verifiable material shortfall fixed and tests whether job-search effort shifts LLM *factual* need classification. Searches covering "LLM need deservingness", "welfare vignette LLM", "unemployed effort LLM", "caseworker LLM bias" and "benefit eligibility LLM" surfaced only the papers above. This is a search-based negative result, not proof of absence.

---

## 4. Irrelevant-context distraction

- **Shi, Chen, Misra, Scales, Dohan, Chi, Schärli, Zhou (2023). Large Language Models Can Be Easily Distracted by Irrelevant Context.** ICML 2023. https://arxiv.org/abs/2302.00093. Verified: yes. GSM-IC: irrelevant sentences degrade arithmetic reasoning. Relation: the closest methodological ancestor. Threat: the "irrelevant info changes answers" phenomenon is known. Our novelty is that the distractor is *normatively valenced* (morally relevant, materially irrelevant) rather than topically irrelevant, and that it has a directional (motivated) effect rather than generic noise. The neutral-detail control is what lets us show this.
- **Mirzadeh, Alizadeh, Shahrokhi, Tuzel, Bengio, Farajtabar (2025). GSM-Symbolic: Understanding the Limitations of Mathematical Reasoning in LLMs.** ICLR 2025 (arXiv comment: "ICLR camera ready"). https://arxiv.org/abs/2410.05229. Verified: yes. GSM-NoOp: "a single clause that seems relevant … causes significant performance drops (up to 65%)". Relation: the closest analogue to a "seemingly relevant" distractor. Our effort clause is a seemingly relevant clause with *moral* valence.
- **Wu, Xie, Chen, Zhu, Zhang, Xiao (2024). How Easily do Irrelevant Inputs Skew the Responses of Large Language Models?** COLM 2024. https://arxiv.org/abs/2404.03302. Verified: yes. Semantically related irrelevant information is the most distracting.
- **Yang, Huang, Zhang, Surdeanu, Wang, Pan (2025). How Is LLM Reasoning Distracted by Irrelevant Context? An Analysis Using a Controlled Benchmark.** EMNLP 2025 main, pp. 13329–13347. DOI 10.18653/v1/2025.emnlp-main.674. https://aclanthology.org/2025.emnlp-main.674/. Verified: yes. GSM-DC uses graph-controlled distractors.

---

## 5. Behavioural testing and counterfactual invariance

- **Ribeiro, Wu, Guestrin, Singh (2020). Beyond Accuracy: Behavioral Testing of NLP Models with CheckList.** ACL 2020, pp. 4902–4912. DOI 10.18653/v1/2020.acl-main.442. Verified: yes (Crossref). Our design is an INV test (effort must not change the factual label) plus a DIR test (resources must change it).
- **Gardner et al. (2020). Evaluating Models' Local Decision Boundaries via Contrast Sets.** Findings of EMNLP 2020, pp. 1307–1323. DOI 10.18653/v1/2020.findings-emnlp.117. Verified: yes (Crossref). The shortfall/sufficient minimal pairs are contrast sets.
- **McCoy, Pavlick, Linzen (2019). Right for the Wrong Reasons: Diagnosing Syntactic Heuristics in NLI.** ACL 2019, pp. 3428–3448. DOI 10.18653/v1/P19-1334. Verified: yes (Crossref). High accuracy can hide heuristic use. In our setting, models may be accurate on average while still using effort.
- **Garg, Perot, Limtiaco, Taly, Chi, Beutel (2019). Counterfactual Fairness in Text Classification through Robustness.** AIES 2019, pp. 219–226. DOI 10.1145/3306618.3317950. Verified: yes (Crossref).
- **Kaushik, Hovy, Lipton (2020). Learning the Difference that Makes a Difference with Counterfactually-Augmented Data.** ICLR 2020. https://arxiv.org/abs/1909.12434. Verified: yes.
- **Veitch, D'Amour, Yadlowsky, Eisenstein (2021). Counterfactual Invariance to Spurious Correlations: Why and How to Pass Stress Tests.** NeurIPS 2021. https://arxiv.org/abs/2106.00545. Verified: yes. Formal definition of counterfactual invariance that we can adopt: the factual need label should be invariant to the effort intervention.
- **Feder et al. (2022). Causal Inference in NLP: Estimation, Prediction, Interpretation and Beyond.** TACL 10:1138–1158. DOI 10.1162/tacl_a_00511. Verified: yes (Crossref).
- **Gururangan et al. (2018). Annotation Artifacts in NLI Data.** NAACL 2018, pp. 107–112. DOI 10.18653/v1/N18-2017. Verified: yes (Crossref). Optional.

---

## 6. LLMs as annotators: measurement error and biased downstream inference

- **Egami, Hinck, Stewart, Wei (2023). Using Imperfect Surrogates for Downstream Inference: Design-based Supervised Learning for Social Science Applications of LLMs.** NeurIPS 2023. https://arxiv.org/abs/2306.04746. Verified: yes. DSL corrects bias from imperfect LLM labels using a gold subsample. Relation: our spurious-group-difference result motivates DSL/PPI-style correction. Show what DSL does and does not fix, e.g., it requires random gold sampling across the effort strata.
- **Angelopoulos, Bates, Fannjiang, Jordan, Zrnic (2023). Prediction-Powered Inference.** *Science* 382(6671):669–674. DOI 10.1126/science.adi6000. Verified: yes (Crossref).
- **Ziems, Held, Shaikh, Chen, Zhang, Yang (2024). Can Large Language Models Transform Computational Social Science?** *Computational Linguistics* 50(1):237–291. DOI 10.1162/coli_a_00502. Verified: yes (Crossref and arXiv 2305.03514).
- **Gilardi, Alizadeh, Kubli (2023). ChatGPT outperforms crowd workers for text-annotation tasks.** *PNAS* 120(30):e2305016120. DOI 10.1073/pnas.2305016120. Verified: yes (Crossref). The optimistic baseline we push against.
- **Pangakis, Wolken, Fasching (2023). Automated Annotation with Generative AI Requires Validation.** arXiv:2306.00176. Verified: yes.
- **Baumann, Röttger, Urman, Wendsjö, Plaza-del-Arco, Gruber, Hovy (2025). Large Language Model Hacking: Quantifying the Hidden Risks of Using LLMs for Text Annotation.** arXiv:2509.08825 (v2 6 Oct 2025; I did not verify a venue). https://arxiv.org/abs/2509.08825. Verified: yes. 37 tasks from 21 studies, 18 models and 2,361 hypotheses. Incorrect conclusions in about 31% of hypotheses for SOTA models and about 50% for small models (Type I/II/S/M errors). Relation: the **most important framing citation for the spurious-group-difference claim**. Threat: medium on framing ("LLM annotation causes wrong conclusions" is known). Our distinction is that Baumann's errors come from *configuration variance* (prompt, model choice), whereas ours is a **content-driven, theoretically predicted, directional bias** whose true group difference is known to be 0 by construction.
- **Messing, S. (2026). Hidden Measurement Error in LLM Pipelines Distorts Annotation, Evaluation, and Benchmarking.** arXiv:2604.11581 (v1 13 Apr 2026, v6 13 May 2026). Verified: yes (abstract). Total evaluation error; naive SEs are 40–60% too small. Relation: supports reporting run-to-run and configuration variance.
- **Camuffo, Gambardella, Kazemi, Malachowski, Pandey (2025/26). Variance-Aware LLM Annotation for Strategy Research.** arXiv:2601.02370. Verified: yes (abstract). Explicitly states that "annotation errors correlated with covariates" bias econometric estimates regardless of average accuracy. This is the **exact econometric mechanism** of our spurious-difference argument (non-classical, differential measurement error).
- **Vallejo Vera & Driggers (2024). Bias in LLMs as Annotators: The Effect of Party Cues on Labelling Decisions by LLMs.** arXiv:2408.15895. Verified: yes. LLM annotators use party cues (contextual, label-irrelevant information) when coding statements. **This is the closest analogue in the annotation literature**: irrelevant context shifts labels. Threat: medium for the general idea. Our domain, the factual-versus-normative split and the known-zero group difference are new.
- **Kotte (2026). Two Wrongs, No Right: Auditing Social-Desirability Bias in LLM Annotators for CSS.** arXiv:2606.12426. Verified: yes. Aligned 7B annotators show directional, class-level errors that can cancel in aggregate metrics, so aggregate accuracy hides substantive distortion. Supports our point that accuracy is not enough.
- **Pita (2026). Correct codes for the wrong reasons? Validating LLMs as measurement instruments for theoretical constructs.** arXiv:2606.28574. Verified: yes. Construct validity beyond agreement.
- **Argyle et al. (2023). Out of One, Many: Using Language Models to Simulate Human Samples.** *Political Analysis* 31(3):337–351. DOI 10.1017/pan.2023.2. Verified: yes (Crossref). Optional (silicon samples).
- **Ludwig, Mullainathan, Rambachan (2025). Large Language Models: An Applied Econometric Framework.** NBER WP 33344. DOI 10.3386/w33344. Verified: yes (Crossref). Prediction versus estimation uses of LLM outputs and when LLM labels bias estimates.
- **I found no paper that constructs a known-zero true group difference and shows that LLM annotation creates a spurious one through a moral cue.** Baumann (Type I errors in real tasks) and Vallejo Vera & Driggers (party cues) are the closest.

---

## 7. Moral contamination of factual judgments: humans and LLMs

Humans:
- **Knobe, J. (2003). Intentional action and side effects in ordinary language.** *Analysis* 63(3):190–194. DOI 10.1093/analys/63.3.190. Verified: yes (Crossref).
- **Alicke, M. D. (2000). Culpable control and the psychology of blame.** *Psychological Bulletin* 126(4):556–574. DOI 10.1037/0033-2909.126.4.556. Verified: yes (Crossref). Blame-validation: evaluative reactions distort causal and control judgments. This is the closest human analogue to "deservingness distorts need".
- **Alicke, Rose, Bloom (2011). Causation, norm violation, and culpable control.** *Journal of Philosophy* 108(12):670–696. DOI 10.5840/jphil20111081238. Verified: yes (Crossref).
- **Kunda, Z. (1990). The case for motivated reasoning.** *Psychological Bulletin* 108(3):480–498. DOI 10.1037/0033-2909.108.3.480. Verified: yes (Crossref).
- **Ditto, Pizarro, Tannenbaum (2009). Motivated moral reasoning.** *Psychology of Learning and Motivation*, pp. 307–338. DOI 10.1016/S0079-7421(08)00410-6. Verified: yes (Crossref). Crossref gives no volume number; I believe it is vol. 50, but that is not verified.

LLMs:
- **Cho, Li, Leshinskaya (2026). Value Entanglement: Conflation Between Different Kinds of Good In (Some) Large Language Models.** arXiv:2602.19101 (v1 22 Feb 2026, rev. 3 Jun 2026). https://arxiv.org/abs/2602.19101. Verified: yes (abstract). LLM grammatical and **economic** value judgments are "unduly swayed by moral considerations"; ablating a morality direction reduces the conflation. **This is the most conceptually similar prior work: moral information contaminates non-moral value judgments.** Threat: **medium-high for the general claim** "LLMs conflate moral and non-moral evaluations". Our differentiators: a factual (ground-truth, arithmetic) target rather than graded value; an applied welfare and measurement-validity framing; a crossed factorial with known-zero estimands; and downstream inference consequences. Must cite and contrast.
- **Raimondi, Dalbagno, Gabbrielli (2025/26). Analysing Moral Bias in Finetuned LLMs through Mechanistic Interpretability.** arXiv:2510.12229 (v3 17 Jul 2026). Verified: yes. The Knobe effect appears in fine-tuned but not pretrained LLMs and can be removed by patching a few layers. Relation: predicts that instruct-tuned models show more moral leakage. A base-versus-instruct comparison would be a cheap extension if time allows.
- **Nie, Zhang, Amdekar, Piech, Hashimoto, Gerstenberg (2023). MoCa: Measuring Human-Language Model Alignment on Causal and Moral Judgment Tasks.** NeurIPS 2023. https://arxiv.org/abs/2310.19677. Verified: yes. Factors from cognitive science (norm violation and others) influence LLM causal judgments.
- **Almeida, Nunes, Engelmann, Wiegmann, de Araújo (2024). Exploring the psychology of LLMs' moral and legal reasoning.** *Artificial Intelligence* 333:104145. DOI 10.1016/j.artint.2024.104145. Verified: yes (Crossref and arXiv 2308.01264). Replicates 8 experimental-psychology studies, including the Knobe-type effects; LLMs exaggerate human effects.
- **Cheung, Maier, Lieder (2025). Large language models show amplified cognitive biases in moral decision-making.** *PNAS* 122(25). DOI 10.1073/pnas.2412015122. Verified: yes via Crossref (the PNAS page returned 403). Amplified omission bias and yes/no framing bias. Relation: response-format controls (a yes/no bias could interact with the SHORTFALL label wording; counterbalance the label order and names).
- **Liu, S. S. (2026). Assessing Cognitive Biases in LLMs for Judicial Decision Support: Virtuous Victim and Halo Effects.** arXiv:2603.10016 (arXiv says IEEE ICDM 2025). Verified: yes. Character information (virtue, prestige) sways LLM legal judgments. A halo-type analogue.

---

## 8. Moral reasoning and social-norm benchmarks (secondary)

- **Chakraborty, Wang, Jurgens (2025). Structured Moral Reasoning in Language Models: A Value-Grounded Evaluation Framework.** EMNLP 2025 main, pp. 30295–30323. DOI 10.18653/v1/2025.emnlp-main.1541. https://aclanthology.org/2025.emnlp-main.1541/. Verified: yes. 12 open models on 4 moral datasets; structured prompting (first-principles, Schwartz plus care ethics) improves accuracy. Relation: a candidate *mitigation* (structured reasoning prompt) to test. Threat: none.
- **Hendrycks et al. (2021). Aligning AI With Shared Human Values (ETHICS).** ICLR 2021. https://arxiv.org/abs/2008.02275. Verified: yes.
- **Forbes et al. (2020). Social Chemistry 101.** EMNLP 2020, pp. 653–670. DOI 10.18653/v1/2020.emnlp-main.48. Verified: yes (Crossref).
- **Emelin et al. (2021). Moral Stories.** EMNLP 2021, pp. 698–718. DOI 10.18653/v1/2021.emnlp-main.54. Verified: yes (Crossref).
- **Lourie, Le Bras, Choi (2021). SCRUPLES.** AAAI 35(15):13470–13479. DOI 10.1609/aaai.v35i15.17589. Verified: yes (Crossref).
- **Jin et al. (2022). When to Make Exceptions: Exploring LMs as Accounts of Human Moral Judgment.** NeurIPS 35:28458–28473. Verified: yes (Crossref).
- **Tennant, Henke, Keshmirian, Shanahan, Rieser, Lum, Levine, Haas (2026). Normative Robustness as a Frontier for Non-Verifiable Reasoning in LLMs.** arXiv:2606.12731. Verified: yes. Models ignore *morally irrelevant* distractors but shift toward users' stated moral views. Relation: the mirror image of our design. They test whether moral judgments are robust to irrelevant information, and we test whether factual judgments are robust to moral information.
- **van Nuenen & Sachdeva (2026). The Fragility of Moral Judgment in LLMs.** arXiv:2603.05651. Verified: yes. **Sauter & Schirmer (2026). On the Context Sensitivity of LLM Moral Judgment.** arXiv:2603.23114 (arXiv says EMNLP 2026). Verified: yes.

---

## 9. NAACL 2027 / ARR: verified dates

Sources opened: https://2027.naacl.org/, https://2027.naacl.org/calls/main_conference_papers/ and https://aclrollingreview.org/dates.
- **ARR submission deadline: 12 October 2026, 23:59 AoE (UTC−12).** The reviewer registration deadline is the same day.
- ARR reviews are due 16 Nov. The author response period is 24–30 Nov 2026.
- Meta-reviews are released 18 Dec 2026 according to the NAACL page. The ARR dates page says **17 Dec**, so the two pages disagree by one day. The ARR cycle ends 20 Dec.
- **NAACL commitment deadline: 23 December 2026.** Notifications go out 10 Feb 2027 and camera-ready is due 3 Mar 2027.
- Conference: **1–5 June 2027, San Francisco, CA, USA.**
- Long papers are 8 pages (9 in the final version); short papers are 4 (5 in the final version). A Limitations section and the Responsible NLP checklist are mandatory. There is no anonymity period.
- The October cycle is **shared with COLING 2027**. You designate a primary venue at commitment, and dual commitment is not allowed.
- Special theme: "Language as a Medium for Agentic Communication". It is not relevant here.

---

## 10. Model availability (Hugging Face API, checked 2026-10-05)

| Repo | Exists | Arch / type | License | Notes |
|---|---|---|---|---|
| `Qwen/Qwen3-8B` | yes, not gated | Qwen3ForCausalLM / qwen3 | Apache-2.0 | thinking on by default; set `enable_thinking=False` for non-thinking |
| `Qwen/Qwen3-14B` | yes, not gated | Qwen3ForCausalLM | Apache-2.0 | same |
| `Qwen/Qwen3-32B-AWQ` | yes, not gated | Qwen3ForCausalLM; AWQ 4-bit, group 128, GEMM | Apache-2.0 | README: `vllm>=0.8.5`; `vllm serve Qwen/Qwen3-32B-AWQ --enable-reasoning --reasoning-parser deepseek_r1`; "DO NOT use greedy decoding" in thinking mode (T=0.6, top-p 0.95, top-k 20) |
| `mistralai/Ministral-3-8B-Instruct-2512-BF16` | **yes**, not gated (created 2025-10-31) | **Mistral3ForConditionalGeneration** (`mistral3`; text `ministral3`, 34 layers; **pixtral vision encoder**, i.e. multimodal: 8.4B LM + 0.4B vision); 256k context | Apache-2.0 | library tag `vllm`. The non-BF16 repo `mistralai/Ministral-3-8B-Instruct-2512` is the **FP8** "no-loss" version. Its README: **vllm >= 0.12.0**, `vllm serve mistralai/Ministral-3-8B-Instruct-2512 --tokenizer_mode mistral --config_format mistral --load_format mistral`; recommended **temperature < 0.1**. For Transformers it needs transformers from git plus `mistral-common`. Tech report: "Ministral 3", arXiv:2601.08584 (Liu et al., Jan 2026). |

Implications: for the BF16 repo, use the same vLLM flags. Since the model is multimodal, vLLM loads the vision tower; `--limit-mm-per-prompt` can be set to 0 images to save memory (I have not verified this flag on this exact model). The model ships a `SYSTEM_PROMPT.txt` default system prompt, so decide whether to use it and report the choice. For Qwen3, document the thinking-mode choice. Thinking versus non-thinking is a natural ablation, since reasoning could reduce or amplify leakage. Qwen3 tech report: arXiv:2505.09388 (verified).

---

## Novelty risk assessment

**What reviewers will say is not new**
1. "LLMs respond to deservingness cues (control or effort) the way humans do." FairFund-Bench (EMNLP 2026 Findings) already shows framing effects ≫ demographic effects, and the human literature (Petersen; Aarøe & Petersen; Knotz et al.) predicts this. A finding that the *normative deservingness score* moves with effort is **expected and not a contribution**. Treat it as a manipulation check.
2. "Irrelevant information changes LLM answers." GSM-IC, GSM-Symbolic (NoOp) and GSM-DC cover this. Showing *any* sensitivity to an added clause is not new.
3. "LLM annotations can produce wrong scientific conclusions." Baumann et al. (LLM hacking), Egami et al. (DSL), Camuffo et al. (covariate-correlated error) and Vallejo Vera & Driggers (party cues) cover this.
4. "Moral considerations contaminate non-moral judgments in LLMs." Value Entanglement (Cho et al. 2026; moral → economic/grammatical value), Knobe effect in LLMs (Raimondi et al.; Almeida et al.) and MoCa cover this.
5. Small open models only (8–32B, one 32B quantised) could be called weak. The likely question is "does it hold for frontier models?"

**What is defensibly new (lead with these)**
1. **A factual target with arithmetic ground truth inside a welfare-deservingness vignette.** No verified prior work holds a *stated, computable* material shortfall fixed and crosses it with an Effort (NICER) cue. Any effort effect on the SHORTFALL/SUFFICIENT label is an **error by construction**. Neither FairFund nor the human vignette literature can make that claim, because their outcomes are normative.
2. **The factual-versus-normative dissociation within the same items.** A separate deservingness prompt shows the model *knows* effort is a deservingness cue, while the factual prompt tests whether it *leaks*. This operationalises the NICER separation of the Need and Effort criteria for LMs, using Knotz et al.'s own absolute-need definition (the gap between costs and resources).
3. **A known-zero estimand for group differences.** When LLM labels are used as a measurement instrument, groups that differ only in job-search activity have a true shortfall-rate difference of 0. Any estimated difference is a spurious finding with a known sign. This turns Baumann-style "LLM hacking" from configuration variance into a **content-driven, theory-predicted, directional bias**, which is a cleaner demonstration of differential (non-classical) measurement error.
4. **A control battery that isolates *moral* leakage from generic distraction.** It includes a neutral irrelevant-detail change (a GSM-IC-style control), removal of the activity clause, duplicate runs (stochastic noise floor) and number-free textual statements (separating arithmetic failure from moral leakage). This answers the obvious objection "it is just distraction" and is what distinguishes the work from GSM-IC and NoOp.
5. Optional but strong additions: (a) show that DSL/PPI correction with a small gold set removes, or fails to remove, the spurious difference; (b) a thinking-versus-non-thinking ablation for Qwen3; (c) a dose-response over application counts (0/1–2/3–4/5–6 per week, mirroring Knotz et al.); (d) a comparison with human NICER effect sizes from the public OSF data.

**Overall risk:** moderate. The core experiment (a factual need judgment with known ground truth, crossed with an effort cue, with spurious-group-difference framing) **does not appear to exist**. The paper must explicitly position itself against FairFund-Bench, Value Entanglement, GSM-IC/GSM-Symbolic and LLM hacking in the introduction, not only in related work.

---

## Must-cite list
1. Lukk 2026, FairFund-Bench (arXiv:2607.28934; EMNLP 2026 Findings per arXiv)
2. Knotz et al. 2022, NICER (Soc. Indic. Res.), and quote its need definition and effort operationalisation
3. van Oorschot 2000 (CARIN); van Oorschot 2006
4. Petersen 2012 (AJPS); Aarøe & Petersen 2014 (JOP)
5. Shi et al. 2023 (GSM-IC); Mirzadeh et al. 2025 (GSM-Symbolic/NoOp)
6. Ribeiro et al. 2020 (CheckList); Gardner et al. 2020 (contrast sets); McCoy et al. 2019; Veitch et al. 2021 (counterfactual invariance)
7. Baumann et al. 2025 (LLM hacking); Egami et al. 2023 (DSL); Ziems et al. 2024; Gilardi et al. 2023
8. Vallejo Vera & Driggers 2024 (party cues bias LLM annotators); Camuffo et al. 2025/26 (covariate-correlated annotation error)
9. Cho, Li, Leshinskaya 2026 (Value Entanglement)
10. Alicke 2000 (culpable control); Knobe 2003; Raimondi et al. 2025/26 or Almeida et al. 2024 (Knobe effect in LLMs)
11. Pokharel et al. 2025 (Street-Level AI) for the deployment context
12. Qwen3 tech report (arXiv:2505.09388); Ministral 3 (arXiv:2601.08584)
13. Optional: Chakraborty et al. 2025 (Structured Moral Reasoning) as a mitigation; Cheung et al. 2025 PNAS (yes/no bias, which motivates counterbalancing the labels)
