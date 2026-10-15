# NLP novelty check for three candidate add-on contributions (A: reasoning/CoT faithfulness, B: fact-verdict probing, C: legally grounded erasure/steering)

Date: 2026-10-05. Target: ARR Jan-2027 -> ACL 2027. Core paper: docs/09_design_B.md.
Scope: items **not already in** lit/rule_reasoning_review.md (checked by grep: none of the papers below appear there or in references.bib).

Verification convention (same as rule_reasoning_review.md): **Verified: yes** = I opened the arXiv abstract page (and, where noted, the HTML full text) on 2026-10-05. **Verified: snippet** = seen only in search results. Venue claims for arXiv papers come from the arXiv Comments field unless marked "(memory)".

---

## A. Test-time reasoning (thinking on/off) and CoT faithfulness for irrelevant social/moral cues

### Closest work

| # | Paper | Verified | One line | Overlap |
|---|---|---|---|---|
| A1 | Pan, Germino, Ma, Daly, Moniz, Hua, Chawla (2026). *Does Thinking Help Fairness? Reasoning Tokens Resolve Some Biases but Create More.* Findings of EMNLP 2026 (per arXiv). arXiv:2609.30768. https://arxiv.org/abs/2609.30768 | yes (abstract + HTML) | **Within-model thinking vs non-thinking ablation** on QwQ-32B, R1-Distill-Qwen-32B and **Qwen3-32B**; Adult/COMPAS/Credit serialized to prose; sex/race counterfactual swaps. Thinking resolves some flips but creates ~5x more. Tools: Counterfactual Depth Probability Gap (truncate trace, re-score) and a Bias Transition Matrix. They do **not** analyze whether traces verbalize the attribute; no rule-derived gold; tasks are statistical predictions, not rule application. | **High** for "does thinking reduce/increase cue sensitivity in Qwen3" as a stand-alone claim. Posted 10 days ago; reviewers will know it. |
| A2 | Arcuschin, Chanin, Garriga-Alonso, Camburu (2026). *Biases in the Blind Spot: Detecting What LLMs Fail to Mention.* ICML 2026. arXiv:2602.10117. https://arxiv.org/abs/2602.10117 | yes | Automated black-box pipeline finds **unverbalized biases** (concept changes decision, CoT never mentions it) in 7 LLMs on hiring, loan approval, admissions. | **High** for "the cue changes the answer but the CoT does not say so" in decision tasks. |
| A3 | Karvonen & Marks (2025). *Robustly Improving LLM Fairness in Realistic Settings via Interpretability.* arXiv:2506.10922 (OpenReview version exists). https://arxiv.org/abs/2506.10922 | yes | Hiring: anti-bias prompts fail once realistic context is added; demographic bias is **invisible in CoT**; affine concept editing of race/gender directions removes it (<2.5%). | Medium-high for A (unfaithful CoT under social cues) and **high for C** (see below). |
| A4 | Matton, Ness, Guttag, Kıcıman (2025). *Walk the Talk? Measuring the Faithfulness of LLM Explanations.* ICLR 2025 (spotlight). arXiv:2504.14150. https://arxiv.org/abs/2504.14150 | yes | Concept-level faithfulness: compare concepts the explanation *claims* mattered vs concepts that *causally* mattered (LLM-made counterfactuals + Bayesian hierarchical model). Social-bias tasks: explanations hide gender influence. | Medium: the "explanation cites X / X causally matters" 2x2 is theirs; we would reuse it as method. |
| A5 | Turpin, Michael, Perez, Bowman (2023). *Language Models Don't Always Say What They Think.* NeurIPS 2023. arXiv:2305.04388; Chen, Benton, …, Perez (2025). *Reasoning Models Don't Always Say What They Think.* arXiv:2505.05410 (no venue listed). | yes (both) | Foundational unfaithful-CoT results (BBQ stereotypes; hint verbalization <20% in reasoning models). | Background; must cite, not a threat to a domain contribution. |

Also relevant (cite in one sentence each):
- Wu, Nian, Wei, Tao, Wu, Fang (2025). *Does Reasoning Introduce Bias?* Findings of EMNLP 2025 (per arXiv). arXiv:2502.15361. Verified: yes. Stereotyped reasoning steps on BBQ in R1/o1; ADBP mitigation.
- Apsel & Jones (2026). *Inference-Time Reasoning Selectively Reduces Implicit Social Bias in LLMs.* arXiv:2602.04742. Verified: yes. Reasoning lowers IAT-style bias for some model classes.
- Young (2026). *Why Models Know But Don't Say: CoT Faithfulness Divergence Between Thinking Tokens and Answers in Open-Weight Reasoning Models.* arXiv:2603.26410. Verified: yes. 12 open models: 55% of hint-influenced cases acknowledge the hint only in thinking tokens, not the visible answer. Relevant for "decision memo vs thinking trace" contrast.
- Sun et al. (2026). *Beyond Accuracy: Measuring Bias Acknowledgment in CoT.* ICML 2026 workshop. arXiv:2606.15127. Verified: yes. Susceptibility vs acknowledgment metrics (GSM8K).
- Gema et al. (2025). *Inverse Scaling in Test-Time Compute.* TMLR 12/2025. arXiv:2507.14417. Verified: yes. Longer reasoning -> more distraction by irrelevant information (Claude), spurious features.
- Suttle & Lillis (2026). *Assessing and Explaining the Persuadability of LLMs as Legal Decision Tools.* ICAIL 2026. arXiv:2604.26233. Verified: yes. Higher reasoning budget -> lower persuadability in most closed models (snippet-level claim; not checked in full text).
- Benevolence-bias paper (Li et al. 2026, arXiv:2608.24912, verified: yes) appears in search snippets as reporting thinking-on reduces bias in Qwen3-14B/GLM-5/DeepSeek-V4; the abstract does not mention thinking, so treat that attribution as **unverified**.

### Threat level: **Medium-high for the generic question, low for the legally indexed version.**
"Thinking on/off changes counterfactual flips" (A1) and "cue influence is unverbalized" (A2, A3, A4) are both taken as stand-alone contributions.

### What remains novel
1. **Two-sided verbalization standard set by law.** All prior faithfulness work treats verbalizing the biasing feature as uniformly desirable (or treats the feature as uniformly illegitimate). In our design the rule says when a cue *must* figure in the reasoning (ABAWD hours; exemption status) and when citing it is itself a legal error (job-search effort of an exempt person; any cue in the income tests). That gives a 2x2x2 cell structure: {cue legally material / immaterial} x {cue changed verdict / not} x {trace/memo cites cue / not}. "Legally improper rationale" (memo cites an immaterial factor even when the verdict is correct) and "silent leakage" (verdict moved, cue not cited) are new, operationally defined, and directly tied to due-process notice requirements for benefit denials. No paper found does this.
2. **Rule-derived gold, not counterfactual-consistency only.** A1 measures flips between counterfactual pairs with no ground truth; we can say whether thinking created *wrong* answers and in which direction (wrongful denial vs approval).
3. **Decision memo as the deployment surface.** NJ's funded "decision memos" use case (why_now_policy.md) makes memo-level citation of irrelevant factors a policy-relevant measurement; Young (2026) suggests thinking trace and final answer diverge, so compare trace vs memo.
4. **Margin x thinking interaction.** Does thinking help most near thresholds (arithmetic) but hurt on exemption chains (more room for moral narrative)? Not tested anywhere.

### Feasibility on one L40 (48 GB)
- Qwen3-8B/14B in BF16 (16/28 GB) and Qwen3-32B-AWQ fit under vLLM; `enable_thinking` toggles the mode within the same weights (the cleanest ablation; A1 used the same lever, so cite and position as replication+extension).
- Qwen3 thinking mode should not use greedy decoding (model card: T=0.6, top-p 0.95). Need k samples per item and a sampling-noise flip baseline; or generate the trace once, then append `</think>` + answer prompt and do **label scoring conditioned on the trace** (keeps v1's sequence-level scoring and enables A1-style truncation curves).
- Traces 1-4k tokens: ~10-20k items x 2 modes x 3 sizes is a few GPU-days with vLLM. Feasible.
- Verbalization coding: rule-based keyword pass + LLM judge, validated on ~300 human-coded traces (report kappa). Add an R1-distill or a second hybrid family (e.g. GLM/DeepSeek hybrid via API) for generality.
- Effort: **low-moderate** (re-uses the core pipeline).

---

## B. Fact-verdict dissociation via probing ("knows but says otherwise")

### Closest work

| # | Paper | Verified | One line | Overlap |
|---|---|---|---|---|
| B1 | Orgad, Toker, Gekhman, Reichart, Szpektor, Kotek, Belinkov (2024/25). *LLMs Know More Than They Show: On the Intrinsic Representation of LLM Hallucinations.* ICLR 2025 (venue from a notes page + memory). arXiv:2410.02707. | snippet (title, arXiv id, finding) | Probes show models can encode the correct answer while consistently generating a wrong one. | Establishes the generic "encodes correct, outputs wrong" phenomenon. |
| B2 | Sun, Stolfo, Sachan (2025). *Probing for Arithmetic Errors in Language Models.* EMNLP 2025 (main). arXiv:2507.12379; https://aclanthology.org/2025.emnlp-main.411/ | snippet (Anthology + arXiv listing) | Probes recover correct arithmetic results even when the output is wrong; probes transfer to word problems (>80%) and detect wrong intermediate results. | High for "probe the computed quantity". |
| B3 | Yuchi, Du, Eisner (2026). *LLMs Know More About Numbers than They Can Say.* EACL 2026 (oral). arXiv:2602.07812. https://arxiv.org/abs/2602.07812 | yes | Linear probes decode log-magnitude and pairwise **number comparison** (>90%) while verbalized comparison is 50-70%. | High for "income vs threshold comparison is linearly decodable". Directly predicts our probe would succeed even without any social cue. |
| B4 | Wang, Li, Yang, Zhang, Wang (2025). *When Truth Is Overridden: Uncovering the Internal Origins of Sycophancy in LLMs.* arXiv:2508.02087 (no venue in Comments; an AAAI-proceedings PDF appears in search, unverified). Plus Pandey (2026) *LLMs Know They're Wrong and Agree Anyway*, arXiv:2604.19117 (snippet). | yes / snippet | Logit lens + patching: correct answer encoded early, overridden in late layers by a social signal (user opinion). | **Closest mechanistic analogue**: a *social* cue overriding an internally correct fact. Our cue is about the applicant, not the user. |
| B5 | Tripathy & Buckmann (2026). *Fair Outputs, Biased Internals: Causal Potency and Asymmetry of Latent Bias in LLMs for High-Stakes Decisions.* arXiv:2605.15217. https://arxiv.org/abs/2605.15217 | yes | Mortgage underwriting with name swaps: no output bias, but demographic representations retained and amplified; re-injecting them by steering reverses decisions, asymmetrically. | Medium: the inverse dissociation (fair output, biased internals) in a decision task. |

Also relevant:
- Villuri, Shaik, Doboli (2026). *When Do Internal Probes Beat Reading the Answer? Miscalibrated Readouts and Behavior-Concealed Knowledge.* arXiv:2609.04582. Verified: yes. Probes hit 0.96 AUC while behaviour is chance; the cause is a **shifted decision threshold** in the readout, fixable with one parameter; they warn that surface features can reproduce probe results. Important caution: a "knows but says otherwise" finding may be a readout-calibration artifact, not a "social override".
- Qu & Gomes (2026). *A Four-Stage Decomposition of Word-Problem Solving and Mechanistic Fragility.* arXiv:2609.17804. Verified: yes. Distractor clauses corrupt the "operation planning" stage (specific heads). Closest mechanistic account of irrelevant-context failures in arithmetic.
- Xu et al. (2026). *Inside the Unfair Judge.* arXiv:2607.11871. Verified: yes. Bias as low-dimensional activation displacement in LLM judges; steering reproduces and reverses bias.
- Pearman et al. (2026). *Mechanics of Bias and Reasoning: CoT and Gender Bias.* ICLR 2026 workshop. arXiv:2605.20410. Verified: yes. Probes show gender bias persists internally under CoT.

### Threat level: **Medium.** No paper probes a *rule-computed* quantity (income vs. statutory threshold, exemption status) under a deservingness cue, but every ingredient is established (B2, B3 for the arithmetic; B4 for social override; B5 for decision tasks). Reviewers in Interpretability & Analysis will read it as "known phenomenon, new domain" unless the causal story is sharper than a probe.

### What remains novel
- A localization result that separates **two failure loci** for the same wrong verdict: (i) the threshold comparison itself is corrupted by the cue (probe for `income < limit` drops under the cue) vs (ii) the comparison is intact but the verdict readout is overridden (probe stays correct, verdict flips). This maps cleanly onto H4 (extract-then-compute fixes (ii) but not (i)?) and is a nice bridge to the behavioral result.
- The same question for **exemption status** (is the person exempt?) under low-effort cues = mechanistic test of H3.
- Must include Villuri et al.'s calibration control (logit-margin AUC, threshold shift) and Hewitt-Liang-style control tasks, or the result is vulnerable.

### Feasibility
- Qwen3-8B/14B in BF16 with hooks (nnsight/TransformerLens/plain HF hooks) fits easily; 32B needs 4-bit (bitsandbytes/AWQ) — probing on quantized activations is OK but patching is slower. Non-thinking mode only (thinking traces make the probe position ill-defined).
- Data are already near-perfect for probing: gold quantities come from rules-as-code, and income is perturbed around thresholds (margin manipulation = built-in difficulty control).
- Effort: **moderate** (1-2 weeks incl. patching), main risk is a null/ambiguous probe result (the comparison may be decodable everywhere, as B3 predicts, making (i) vs (ii) hard to separate without patching).

---

## C. Legally grounded concept erasure / steering

### Closest work

| # | Paper | Verified | One line | Overlap |
|---|---|---|---|---|
| C1 | Karvonen & Marks (2025), arXiv:2506.10922 (see A3). | yes | Affine concept editing of race/gender directions, derived from a toy dataset, generalizes to realistic hiring prompts in open models and keeps general performance. | **High** for "erase an illegitimate social direction in a decision task". They assume the attribute is *never* legitimate. |
| C2 | Wang, Phan, Ho, Koyejo (2025). *Fairness through Difference Awareness: Measuring Desired Group Discrimination in LLMs.* ACL 2025 (**Best Paper**). arXiv:2502.01926. https://arxiv.org/abs/2502.01926 | yes | 16k-question suite, 8 scenarios, including legal ones (e.g. draft applies to men): fairness sometimes *requires* differentiating; standard debiasing **backfires** on difference awareness. | **High for framing**: the "should differentiate vs should not" idea is prized and owned at ACL. Also bears on the core paper's two-sided test (they are a must-cite there too; not in rule_reasoning_review.md). |
| C3 | Holstege, Ravfogel, Wouters (2025). *Preserving Task-Relevant Information Under Linear Concept Removal* (SPLINCE). NeurIPS 2025. arXiv:2506.10703. https://arxiv.org/abs/2506.10703 | yes | Oblique projection that removes linear predictability of a concept while **exactly preserving its covariance with a target label**. | High on method: it is the off-the-shelf tool for "erase but keep task-relevant part". |
| C4 | Lee et al. (2025). *Programming Refusal with Conditional Activation Steering* (CAST). ICLR 2025. arXiv:2409.05907. | snippet (ICLR page + arXiv listing) | Condition vector gates a behavior vector: steer only when the input matches a condition. | Medium: a ready mechanism for "steer only where the rule makes the cue immaterial". |
| C5 | Kilbertus et al. (2017). *Avoiding Discrimination through Causal Reasoning.* NeurIPS 2017. arXiv:1706.02744 (verified: yes); Chiappa & Gillam (2018/19). *Path-Specific Counterfactual Fairness.* arXiv:1802.08139 (verified: yes; AAAI 2019 from memory). | yes | Resolving variables / path-specific fairness: a sensitive attribute may act through some paths but not others. | Conceptual ancestor; never applied with a statute as the path specification or to LLM representations (no such paper found). |

Also relevant:
- Shan & Mueller (2025). *Measuring Mechanistic Independence: Can Bias Be Removed Without Erasing Demographics?* arXiv:2512.20796. Verified: yes. SAE feature ablations in Gemma-2-9B remove bias while keeping demographic recognition; effects are task-specific.
- Ahsan & Wallace (2026). *Can SAEs reveal and mitigate racial biases of LLMs in healthcare?* ICLR 2026. arXiv:2511.00177. Verified: yes. SAEs diagnose demographic reliance; steering mitigation is "of marginal utility for realistic tasks". Useful negative prior for SAE-based C.
- Tripathy & Buckmann (2026) (B5): steering re-injects latent bias in mortgage decisions.
- Shao, Zhao, Korhonen, Ziser, Cohen (2026). *Debiasing Without Protected Attributes: Latent Concept Erasure from Textual Profiles.* arXiv:2606.12088. Verified: yes. Erasure from implicit self-descriptions (relevant because our cues are implicit narratives, not labels).
- Feng, Fang, Evans (2026). *The Illusion of Debiasing: Persona Steering Redistributes Rather Than Reduces Bias.* arXiv:2609.07117. Verified: yes.
- Belrose et al. (2023). *LEACE.* NeurIPS 2023. arXiv:2306.03819. Verified: snippet (NeurIPS proceedings + arXiv listing).

### Threat level: **Low-medium for the exact idea; high for any generic "we debias with steering" version.**
I found no paper that (a) uses an external legal/normative specification to decide which information must be invariant and which must be used, and (b) evaluates an erasure/steering intervention on **both** should-not-change and should-change gold. C2 shows the two-sided evaluation matters (and that debiasing backfires), but it is behavioural and about group membership; C1/C3 do erasure but without a legally specified "must still use" side.

### What remains novel
- **"Statute-specified erasure" evaluation:** erase/steer the deservingness direction (e.g. LEACE or ACE on a job-search-effort/blame concept) and report the two-sided matrix: does it remove leakage in D1-D3 and D4-exempt *without* destroying correct use of hours worked in D4? The interesting result is a trade-off or entanglement (effort direction overlaps the legally material work-hours direction), i.e. "debiasing backfires on legally material cues" — the C2 claim transported to representations and to welfare law.
- Use SPLINCE with the **rule gold** as the preserved target, vs plain LEACE, vs CAST gated by an "exempt / income-test context" condition. This makes the statute literally the specification of the projection.

### Feasibility
- LEACE/SPLINCE need only class-conditional activation statistics: cheap on Qwen3-8B/14B BF16 (EleutherAI `concept-erasure` package). Steering at inference via HF hooks; vLLM does not support hooks easily -> HF generate or scoring only, so restrict to non-thinking label scoring.
- The concept dataset for "deservingness" can come from the cue bank (high vs low cue, cue-irrelevant items), with held-out templates to avoid template leakage (v1 lesson).
- Effort: **moderate-high** (2-3 weeks), with real risk that erasure either does nothing (cues act via many features) or wrecks arithmetic. Either outcome is reportable only if the two-sided evaluation is the point.

---

## Recommendation

**Do A as the main add-on; add a small, tightly scoped C as the second; fold B into C as a diagnostic only if time allows.**

1. **A (highest novelty per unit effort).** It re-uses the existing generation pipeline and the within-model `enable_thinking` toggle. The novelty is not "does thinking help fairness" (A1 owns this, 10 days old) nor "CoT hides bias" (A2-A4) but the **legally indexed verbalization standard**: the rule specifies when a cue must and must not appear in the reasoning/memo, so we can measure *silent leakage*, *legally improper rationales* and *correct material use* against rule gold. Frame as "Does thinking make LLM caseworkers more formalist? Verdicts, traces and decision memos under a legal relevance standard". Cite A1 as the closest prior and position as: gold-scored, direction-of-error, rule-relevance-indexed, plus verbalization. Must-cite set: Turpin 2023, Chen 2025, Arcuschin 2026, Matton 2025, Pan 2026, Young 2026.
2. **C (second; distinctive but riskier).** Only one experiment: LEACE vs SPLINCE(gold-preserving) vs CAST on Qwen3-8B/14B, evaluated on the two-sided matrix. The payoff is a crisp, reviewer-legible claim ("removing deservingness representations also removes legally required use of work effort" or "a statute-specified projection avoids this"). Cite Wang et al. 2025 (ACL Best Paper) and Karvonen & Marks 2025 prominently. Wang et al. 2025 should also be added to the **core** related-work section, since the two-sided "should/should not differentiate" test is their framing in a different form.
3. **B (lowest marginal novelty).** Generic "knows but says otherwise" is well established (B1-B4) and the calibration critique (Villuri et al. 2026) is a live trap. Keep at most one figure: probe accuracy for `income < limit` and `exempt?` with vs without cue, in the appendix, used to motivate C. Do not sell it as a contribution.

**Framing/track.** Keep the paper's identity as a measurement paper; A and C are analyses of *why* and *what fixes it*. Submit to **Computational Social Science / NLP for Social Good** (or Ethics, Bias & Fairness) as primary area; A+C make it credible to Interpretability & Analysis reviewers, but an I&A primary area would expect deeper mechanistic work (circuits/patching) than this timeline allows, and would weigh A1/A2/B-literature more heavily against us. A 4.5 needs one clean, surprising headline per add-on; avoid three half-done analyses.

**Timeline fit (vs docs/09 §10).** A can run inside the Nov 3-23 full-run window (add thinking arm + memo prompt; human-code 300 traces in late Nov). C needs ~2 weeks in Nov 24-Dec 14 alongside the consequence analysis. B only if C finishes early.

## Watch list (re-check before submission, Dec 2026)
- Follow-ups to Pan et al. 2609.30768 (thinking x fairness) and Arcuschin et al. (unverbalized bias) in legal/benefits domains.
- Any "difference awareness" follow-up from Wang/Ho/Koyejo applying it to rules or representations.
- Any statute-specified or path-specific erasure work in LLMs (none found as of 2026-10-05).
