# Reference works: Zhao et al. (framing → events) and FrECI

Compiled 2026-10-05 for the welfare-need NAACL 2027 project (ARR deadline 2026-10-12).
Method: I read the PDFs from the ACL Anthology in full and cloned the GitHub repos into
`/workspace/welfare-need-naacl/data/external/ref_repos/` (`attitude-detection-with-framing/`, `freci/`, `freco/`).
Anything I could not verify is marked **[unverified]**.

---

## 0. Identification (what "Zhao" and "FrECI" are)

| Work | Citation | Venue | Paper | Code |
|---|---|---|---|---|
| **Zhao 2024 (MAD)** | Jin Zhao, Jingxuan Tu, Han Du, Nianwen Xue. *Media Attitude Detection via Framing Analysis with Events and their Relations.* | EMNLP 2024 main, pp. 17197–17210 | https://aclanthology.org/2024.emnlp-main.954/ | https://github.com/jinzhao3611/attitude-detection-with-framing |
| **FrECI** | Jin Zhao, Jiayi Yao, Xinrui Hu, Nianwen Xue. *Reframing Responsibility: Framing-Aware Event Causality Identification.* | ACL 2026 main (long), pp. 46956–46977, DOI 10.18653/v1/2026.acl-long.2173 | https://aclanthology.org/2026.acl-long.2173/ (PDF: https://aclanthology.org/2026.acl-long.2173.pdf) | https://github.com/jinzhao3611/freci |

**FrECI is resolved.** It stands for **Fr**aming-aware **E**vent **C**ausality **I**dentification. It is the same author's follow-up (Brandeis, Xue lab). The PDF footnote links the GitHub repo above. I found no competing "FrECI" acronym in web search; the closest unrelated hits were generic ECI resources such as the Causal News Corpus.

**Other follow-ups by Jin Zhao, 2024–2026** (from the ACL Anthology page for Nianwen Xue, https://aclanthology.org/people/nianwen-xue/):
- **FRECO**: Zhao, Hu, Xue. *Seeing the Same Story Differently: Framing-Divergent Event Coreference for Computational Framing Analysis.* EMNLP 2025 main, pp. 28356–28371. https://aclanthology.org/2025.emnlp-main.1440/ ; code https://github.com/jinzhao3611/freco (cloned). This is the bridge between MAD and FrECI and is summarized in §3.
- *Beyond Benchmarks: Building a Richer Cross-Document Event Coreference Dataset with Decontextualization.* NAACL 2025 long. https://aclanthology.org/2025.naacl-long.178/ ; repo https://github.com/jinzhao3611/cdec-with-decontextualization (README only read). This is CDEC infrastructure, not framing.
- UMR-related papers (LREC-COLING 2024, DMR 2024/2026, TLT 2025, TextGraphs 2024). Not relevant here.
- The GitHub account also has an undescribed `CDEC` repo (10 news stories, 9,503 mentions; README read, no paper linked) **[paper unverified]**.
- arXiv 2604.10368 (*A Structured Clustering Approach for Inducing Media Narratives*, ACL 2026) came up in search but is by Das, …, Pacheco, not Zhao. It is relevant as a competitor, not as a follow-up.

The line of work runs: **MAD (2024, framing devices as event structure → attitude) → FRECO (2025, same event framed differently) → FrECI (2026, causal claims carrying responsibility/blame/credit/source/certainty).**

---

## 1. Zhao et al. 2024 — Media Attitude Detection (EMNLP 2024)

### Research question and operationalization
- **RQ.** Can framing (Entman 1993), conceptualized as *how* a story is told rather than *what* topic it covers, be captured computationally through events and event relations? Does it predict an article's attitude toward a main event?
- **Task.** Classify each article as **supportive / skeptical / neutral** toward a target event.
- **Concept → representation.** The key move is to translate three *framing devices* from communication theory (Van Gorp 2006; Entman 1993; Gamson & Modigliani 1989) into three alternative **input encodings** of the same article:
  - **Device 1, selection/omission of events.** The article is represented as the list of GPT-4o-written *descriptors* of the cross-document event-coreference clusters it mentions. These are neutralized, corpus-level names for events.
  - **Device 2, linguistic information (word choice).** Each event is represented by its original trigger plus SRL arguments, formatted `[ARG0] [trigger] [ARG1] [ARG2] [ARG3]`. This keeps loaded wording ("murdered" vs "death").
  - **Device 3, cause and effect.** The article is represented as GPT-4o-extracted causal pairs, rendered as `descriptor(cause) → descriptor(effect)`.
- The **baseline** is the raw article text. Comparing encodings works as a *representation ablation*: each device isolates one theoretical mechanism.

### Data
- 1,609 articles on three contentious international events: Putin's 2024 election win (495), the Al-Shifa hospital raid (643), and the HK July 1 2019 protest (471).
- Sources: 7 aggregators and 98 outlets (CNN, BBC, Sputnik, Xinhua, Al Jazeera, Times of Israel…). Articles were in EN/ZH/RU, translated into English with the Google Translate API.
- Dedup used a 60% sentence-overlap threshold. Excluded: opinion pieces, editorials, episodic pieces, transcripts, and moral-judgment pieces without events.
- **Annotation.** Two CL graduate students; 50 trial items; a qualification bar of ≥90% accuracy on assessment examples; full double annotation followed by adjudication. **Cohen's κ = 0.92.** The authors note that strong stances make the task easy.
- Pipeline stats (Table 1): roughly 7–8 events and 7–9 causal relations per article after filtering; 310–450 clusters per topic.

### Models and methods
- **Event detection.** Modal-dependency event extractor (Yao et al. 2021). Uninformative verb classes are filtered out (aspectual, copular, mental, modal-like, reporting).
- **SRL.** `cu-kairos/propbank_srl_seq2seq_t5_large`.
- **CDEC.** Pairwise cross-encoder (Yu et al. 2022) plus agglomerative clustering. Candidate pairs are pruned for precision: same trigger with frequency >5, or cross-trigger pairs linked via the AIDA ontology or VerbNet.
- Cluster descriptors and causal relations both come from **GPT-4o**.
- **Classifiers.** Fine-tuned RoBERTa-base (classification) and T5-base (QA-style generation); zero-shot FlanT5-XL and GPT-4o. Split is 70/30 random per topic. Metric is accuracy.

### Key results (Table 2, accuracy)

| Setting | Putin | Al-Shifa | HK |
|---|---|---|---|
| GPT-4o baseline (raw text) | 59.5 | 52.3 | 52.5 |
| GPT-4o Device 1 | 81.4 | 80.0 | 78.2 |
| RoBERTa baseline | 75.0 | 81.9 | **97.2** |
| RoBERTa Device 1 | 82.1 | 80.9 | 93.0 |

- Devices help **zero-shot LLMs** a lot (+13 to +28 points). For **fine-tuned** models the result is mixed: better on Putin, worse on HK.
- Device inputs are 43–87% shorter than raw text (Table 3).

### How they argue the representation matters (analyses)
1. **Device-wise ablation.** Three encodings, each tied to one theoretical mechanism, are compared against raw text across 4 models × 3 topics.
2. **Compression analysis.** Similar accuracy is reached with far fewer tokens, which suggests the devices carry the attitude-relevant information.
3. **Typed error analysis (Table 4).** Errors are traced to the pipeline stage that caused them:
   - a CDEC error (Israel vs Hamas "destroy facilities" merged into one cluster);
   - an SRL error (a missing location argument);
   - a causal error (wrong direction of the extradition bill → order relation).
4. **Qualitative contrast across encodings (Table 5).** The same Navalny item is shown under each encoding. Raw text gets "neutral"; all three devices get "skeptical".
5. **"Learning patterns or knowledge?"** Jensen–Shannon divergence between the train and test token distributions is lower (8–9) than between the event distributions (14–15). They use this to explain why fine-tuned models exploit surface lexical overlap, while LLMs use the abstracted structure.

### Code (repo read)
- `prepare_device_data/` builds the three device inputs: clustering, descriptor prompts, SRL, and causal output.
- `source_data/<topic>/` ships everything precomputed:
  - `parsed.json` (events), `srl.jsonl`, `cluster_0.8_0.5.txt` (CDEC clusters), `descriptors.json`;
  - `train/test.jsonl` and `{train,test}_device_{1,2,3}.jsonl`, with fields `language, url, title, stance, content, translation, uid, input`.
- `bert_modeling/`, `t5_modeling/`, `flan_t5_modeling/`, `gpt_modeling/` hold the four model families. `scripts/jsd_analysis.py` covers the JSD analysis, and `scripts/evaluate_model_out.py` is the scorer.
- Reproducibility comes mainly from shipping the **intermediate structures**, so nobody has to rerun the GPT-4o and CDEC steps.

**Caveats found in the code** (worth knowing; not stated in the paper):
- `scripts/data_split.py` calls `train_test_split(test_size=0.3)` with no seed. The shipped split files are therefore the only record of the split.
- The device test files have fewer rows than the raw-text test files (Al-Shifa 180 vs 193; Putin 145 vs 148; HK 142 vs 142). Baseline and device accuracies are therefore not computed on exactly the same articles.
- `gpt_modeling/prompts.py` injects **topic-specific labeling hints** (`TOPIC_INSTRUCT`) into the raw-text baseline and Devices 1 and 2, but **not** into Device 3.
- `descriptors.json` stores per-cluster stance percentages derived from the labels (e.g., `["neg", 80.0]`). I checked that they are *not* concatenated into the model inputs, but this is a leakage risk to avoid when copying the design.

### Depth moves (MAD)
- Theory → named mechanisms → one input encoding per mechanism, so each comparison is a test of one mechanism.
- The intermediate structure is made explicit and released (events, clusters, causal pairs).
- Errors are attributed to specific pipeline components (CDEC, SRL, causal).
- Behaviour of fine-tuned models and zero-shot LLMs is compared, with a distributional (JSD) explanation of the difference.
- Efficiency (compression) is argued alongside accuracy.
- **Weaknesses a reviewer would flag:**
  - no gold-vs-predicted structure comparison;
  - no random-event control in MAD itself (FRECO adds it later);
  - single split, no seeds or variance;
  - κ = 0.92 on an easy, polarized task.

---

## 2. FrECI — Framing-Aware Event Causality Identification (ACL 2026)

### Research question and operationalization
- **RQ.** Standard event causality identification (ECI) treats causality as a neutral binary link. In political narratives, causal claims are *framed*: who is held responsible, whether they are blamed or credited, who makes the claim, and how certain it is. Can models recover these *framed causal claims*? And do such claims enable measurement of contested attribution across narratives?
- **Concept → representation.** Each social-science construct is mapped to one slot in a structured tuple:
  - responsibility attribution (Iyengar 1993) → **responsibility target t**;
  - moral evaluation (Entman 1993) → **framing effect f_t**;
  - epistemic stance → **epistemic modality a_s**;
  - source legitimacy (Tuchman 1972) → **source type s**.
- **Atomic unit.** `(e_cause, e_effect, s, a_s, t, f_t)`, one tuple per target. `s` and `a_s` are *claim-level* (shared across all targets of a link); `f_t` is *target-specific*.
  - s ∈ {Author, Target, Ally, Opponent, Third_Party}
  - a_s ∈ {Full_Aff, Partial_Aff, Neutral, Partial_Neg, Full_Neg}
  - f ∈ {Blame, Credit, Undermine_Credit, Exonerate_Blame, Framing_Neutral}
  - Default rule: if there is no explicit agent and the effect is a broad societal outcome, the target defaults to "Incumbent".
- **Anchor-based setting.** Gold anchor event mentions are given. This deliberately isolates framed-causal reasoning from upstream extraction errors.

### Data
- **Seed corpus.** 51 politically contentious MAVEN-ERE (English Wikipedia) articles with gold events and causality. Parallel Chinese and Arabic Wikipedia articles are segmented and translated to English with GPT-4o, using a "faithful causal translation" prompt that keeps passive voice and loaded terms. Translations were validated by fluent annotators, and a targeted audit found no reversal of framing polarity.
- **Non-English events.** Extracted with OmniEvent and aligned to the English anchors via CDEC (Yu et al. 2022).
- **Causal links.** GPT-4o proposes a high-recall candidate set. Humans then do two passes: validate and prune, then read the full document to add missed links.
- **Framing attributes.** SRL proposes candidate agents and rule-based detectors flag source and certainty cues; humans validate both.
- **Size.**
  - 661 documents (EN 51 / ZH 612 / AR 21) and 440k tokens;
  - 5,520 events, 756 cross-document coreference chains (569 non-singleton);
  - **2,203 framed causal relations** and **4,775 responsibility targets**.
- **Label skew (Table 2).** Source is Author 92.3%; certainty is Full_Aff 90.9%. Framing is more balanced: Neutral 30.7, Credit 24.2, Blame 21.4, Exonerate 13.9, Undermine 9.8.
- **Annotation.** Three CL annotators, a 40-document pilot, 20% of topics double-annotated, senior adjudication.
- **Agreement, reported per component (Table 3):**

| Component | Metric | Agreement |
|---|---|---|
| Causal link | pairwise link F1 | 0.65 |
| Target spans | span F1 | 0.71 |
| Framing effect | κ, on matched targets | 0.62 |
| Source | κ | 0.74 |
| Modality | κ | 0.88 |

### Models and evaluation
- **GPT-4o, zero-shot and CoT.** Outputs constrained JSON.
- **Joint FrECI model.**
  - Shared RoBERTa-large encoder with anchor markers.
  - Heads for directed link, source, modality, SRL-candidate target selection, and target-conditional framing.
  - Multi-task loss, with attribute losses masked to causal pairs.
- **Pipeline ablation.** Same heads without joint training.
- **SFT baseline.** Llama-3.1-8B-Instruct with QLoRA, generating claim JSON directly.
- **Splits.** Topic-held-out: 36/5/10 topics, with all languages of a topic in the same split.
- **Metrics.** The scoring decomposes the structure:
  - link P/R/F1;
  - target span F1 (IoU ≥ 0.5), conditional on a correct link;
  - framing macro-F1 on matched targets;
  - source and modality macro-F1;
  - **Full-Claim Exact Match.**

Results (Table 4):

| Model | Link F1 | Target T | Framing f | Source s | Modality m | Full-claim EM |
|---|---|---|---|---|---|---|
| GPT-4o zero-shot | 37.4 | 73.1 | 28.4 | 74.4 | 91.5 | 14.6 |
| GPT-4o CoT | 26.6 (P 61.5 / R 17.0) | 81.4 | 29.1 | 79.4 | 98.5 | 15.2 |
| **Joint FrECI** | **59.0** | 77.3 | **73.1** | 75.6 | 96.0 | **27.4** |
| Pipeline (no joint training) | 58.7 | 78.0 | 71.6 | 78.6 | 94.9 | 26.0 |
| SFT Llama-3.1-8B | 56.5 | 80.8 | 61.2 | 72.3 | 96.0 | 26.7 |

- **Headline.** LLM prompting finds plausible causal links and targets but fails at **framing effect** (~28 macro-F1). Structured supervision raises this to 73.
- **Use case: causal fragmentation.** Fragmentation is defined as Frag(E) = H(p(C|E)) / log|C(E)|, the normalized entropy over cause clusters for a shared effect cluster. The mean is 0.44. This turns the extracted structure into a substantive social-science measurement.

### Code (repo read; single "Initial commit", pushed after ACL)
- **Files:**
  - `prepare_data.py` builds the splits, `instances.jsonl`, SFT JSONL, and candidate pairs within a 3-sentence window;
  - `roberta_joint.py` uses a BIO framing-typed span tagger, described in its own docstring as a "lightweight stand-in";
  - `roberta_srl.py` is the paper's §3.7 SRL-candidate head;
  - `srl_candidates.py`; `sft_train.py` and `sft_infer.py` (QLoRA); `gpt4o_infer.py`; `eval.py` (the metrics harness).
- **Data and checkpoints** are on Google Drive (https://drive.google.com/drive/folders/1Izmvy8F_vyYDhukNWXW2s0DjzhSb9bOE). An unauthenticated curl returned a Google sign-in page, so **public access is unverified**. The expected format is `<topic>.freci.json` with `documents` (sentences, anchor events) and `framed_causal_claims`.
- **Code vs. paper discrepancies to note:**
  - `make_split` *randomly shuffles* topic names (seed 13) rather than hard-coding the named split in the paper's Table 5. Whether it reproduces Table 5 is unverified.
  - `eval.py` matches targets by token-Jaccard ≥ 0.5 on text (because offsets are not stored), not by the paper's token-offset IoU.
  - The GPT-4o baseline reuses the SFT instruction, which lists label *names* but gives no *definitions* (the paper says definitions were provided). This may depress GPT-4o's framing score, e.g. on "Undermine_Credit".
- **What supports reproducibility:**
  - one schema shared by all three model families;
  - one prediction format consumed by a single `eval.py`;
  - topic-held-out splitting;
  - "invalid JSON = empty prediction" as a stated rule.

### Depth moves (FrECI)
- **Theory → typed slots.** Each slot is tied to a citation in communication theory; claim-level and target-level attributes are separated.
- **Agreement reported per slot.** This shows *which* construct is hard (framing κ 0.62) instead of a single κ.
- **Factorized metrics plus strict end-to-end EM.** These localize where models fail: LLMs fail on framing, not on targets.
- **Gold anchors as a controlled setting.** Upstream extraction errors are removed by design (an oracle-input setup), with end-to-end extraction left for future work.
- **Joint vs. pipeline ablation.** This separates the gain from the factorization itself from the gain from joint training.
- **Topic-held-out generalization.** This guards against lexical memorization.
- **Per-origin breakdown** (EN vs zh→en vs ar→en; Appendix A.7).
- **A downstream measurement (fragmentation)** shows that the structure answers a social-science question rather than only producing a benchmark number.
- **Model-in-the-loop annotation with human correction** (LLM high recall → human prune/add; SRL/rule proposals → human validation).

---

## 3. FRECO (EMNLP 2025), the bridge paper — brief
- **Task.** Binary classification: are two event mentions *coreferent but framed differently* ("acted decisively to neutralize the threat" vs "opened fire on the unarmed man")?
- **Data.** 3,800 pairs from RECB (Putin, Al-Shifa, HK, Rittenhouse); 46.5% positive. Pairs were preselected by CDEC similarity, so many negatives are hard negatives. κ = 0.76 for FRECO and 0.81 for event attitude.
- **Models.** Llama-3.2-3B and 3.1-8B with SFT / DPO / SFT→DPO / DPO→SFT under an **equalized training budget**, 3 seeds, leave-one-topic-out. SRL-augmented input adds about 1–3 F1. The best setting reaches 80.6–85.0 F1; GPT-4 zero-shot gets 52–64.
- **Depth moves:**
  - **Equal-budget comparison** of training regimes.
  - **SRL-structure ablation.**
  - **Error analysis** showing the model treats framing opposition as sufficient evidence of coreference, and that SRL fixes the soldier-vs-patient false positive.
  - **Bootstrapped mining** with explicit stopping diagnostics (Jaccard between rounds, validation loss, 70.5% human-estimated precision).
  - **Downstream test on MAD with a *random-events control*.** Random events reach only 38–53%, while FRECO events reach 73–79%. This shows the *selection* of structure, not just compression, carries the signal.
- Repo: `scripts/` (SFT, DPO, predict, bootstrap selection), `slurm/`; data on Drive. The gold schema records `final_class` ∈ {NOT_COREF, COREF_NOT_DIVERGENT, FRECO}, i.e. a 3-way underlying label collapsed to binary.

---

## 4. Cross-cutting "depth move" checklist (from all three papers)
1. **Construct decomposition.** Split a fuzzy social concept (framing) into named sub-mechanisms (selection, wording, causality; target, blame, source, certainty), each with one representation slot.
2. **Representation-as-input ablation.** Feed the model *only* one structured slot at a time and compare against raw text (MAD).
3. **Gold-structure oracle setting.** Give gold anchors to separate reasoning failures from extraction failures (FrECI).
4. **Factorized and conditional metrics plus strict EM.** These show *where* in the structure models fail (FrECI).
5. **Per-component agreement.** This shows which constructs humans themselves find fuzzy (FrECI).
6. **Controls.** A random-structure control (FRECO→MAD), equalized training budgets, seeds (FRECO), and joint vs. pipeline training (FrECI).
7. **Held-out-topic generalization** (FrECI, FRECO).
8. **Typed error attribution** to pipeline stages (MAD).
9. **Structure → substantive measurement** for social science (fragmentation index).
10. **Hybrid LLM-propose / human-verify annotation** with a stated recall-recovery pass.

---

## 5. Transfer to our project: LLMs judging welfare need

**Our situation.** Qwen3-8B extracts the correct totals (funds $2,140 vs. bills $1,360, so a surplus) but still answers SHORTFALL. Job-search effort barely moves the judgments. The hypothesis is that the social frame ("unemployed, applying for aid") overrides arithmetic. In CARIN/NICER terms, **Need** (cost-resource gap) is a separate criterion from **Effort, Control, Identity, Reciprocity**. In MAD/FrECI terms, the model fuses *facts* with *framing cues*, and we want to show which one drives the verdict.

### Proposal A — A FrECI-style structured "need claim" representation
- **Schema.** Each vignette yields:
  - (i) **need facts**: typed tuples `(item, category ∈ {resource, cost}, amount, period, certainty)`, plus a derived `gap = Σcosts − Σresources`;
  - (ii) **deservingness cues**, one slot per CARIN criterion: `(criterion ∈ {Control, Attitude, Reciprocity, Identity, Effort}, span, valence ∈ {+, −, 0})`;
  - (iii) **verdict**.
- **Why it mirrors FrECI.** Facts sit at claim level and cues at target level. In FrECI, framing is a separate slot from the causal link. Here, the deservingness valence is separate from the arithmetic gap.
- **Experiment.** Have models fill the schema. Report factorized metrics: fact-extraction F1, gap correctness, cue F1, verdict accuracy, and **Full-Case EM**.
- **Key analysis.** Show the dissociation directly: P(verdict wrong | gap correct). Our pilot suggests this is high.
- **Novelty for reviewers.** This is the first factorized evaluation of welfare-need judgment that separates *computing need* from *being persuaded by deservingness framing*, with each slot tied to CARIN theory.

### Proposal B — Gold-vs-predicted-structure oracle ladder (FrECI's anchor setting, MAD's device inputs)
Feed the same model five conditions:
- **(1)** raw vignette;
- **(2)** raw vignette plus its *own* extracted facts;
- **(3)** raw vignette plus **gold** facts and gold gap;
- **(4)** *facts only*: a de-framed, MAD-Device-1-style neutral descriptor ("resources $2,140; costs $1,360"), with no unemployment or aid context;
- **(5)** facts plus deservingness cues only.

How to read the outcomes:
- If (3) still fails while (4) succeeds, **the context overrides correct facts**. That is a reasoning/framing failure, not an extraction failure. This is our core claim, and it is tested causally.
- MAD showed that structure helps zero-shot LLMs; we test whether structure *without the social frame* restores correct need judgments.
- **Novelty.** An oracle decomposition that localizes the failure: extraction vs. integration vs. frame override.

### Proposal C — Controlled perturbations crossing need × cue (MAD/FRECO controls, made causal)
- **Design.** A factorial vignette set: gap ∈ {large surplus, small surplus, break-even, small deficit, large deficit} × frame ∈ {unemployed+aid application, employed+budgeting, neutral "household"} × effort ∈ {high, low, absent} × control ∈ {job loss by layoff, by quitting}.
- **Measures.** Hold the numbers fixed and compute (i) **frame-flip rate**, (ii) psychometric curves of P(SHORTFALL) as a function of the true gap per frame (does the frame *shift the threshold*?), and (iii) effort sensitivity.
- **Controls.** Include a random-irrelevant-detail control, the analogue of FRECO's random-events control: does *any* extra sentence move the verdict, or only deservingness cues?
- **Equal-budget rule.** Use the same prompts and decoding across models, as in FRECO's equalized budgets.
- **Novelty.** Threshold-shift curves give an interpretable, theory-grounded effect size: "the unemployment frame moves the need threshold by $X". That is much stronger than a single accuracy number.

### Proposal D — Annotation schema with per-slot agreement plus a human comparison
- **Annotation.** A small gold set (~200–300 vignettes or real-style case notes), annotated with the Proposal A schema by 2–3 annotators. Report **per-slot agreement**, as FrECI does: expect high κ for amounts and gap, lower κ for effort/control valence.
- **Human baseline.** Collect human verdicts under the same frame manipulation, e.g. 3 raters per item or a small crowd sample.
- **Analysis.** Compare human vs. LLM frame sensitivity. Do humans also over-weight context? Distinguish a "model bias" from "model mirrors known human deservingness heuristics".
- **Novelty.** Human-vs-model comparison on an identical factorial design, with agreement reported per construct. This answers the reviewer question "maybe humans do that too".

### Proposal E — Typed error attribution, plus a structure-guided fix as the method contribution
- **Error attribution (MAD Table 4 style).** Assign each error to one stage:
  - extraction error (wrong amount);
  - aggregation error (wrong sum or period mismatch, e.g. monthly vs. weekly);
  - comparison error (correct gap, wrong sign reading);
  - **frame override** (correct gap stated in the reasoning, verdict contradicts it).
  - Report the distribution per model and per frame. Qwen3-8B's thinking traces make the "stated vs. used" check possible.
- **Method (FrECI joint-vs-pipeline analogue).** Compare a *pipeline* (extract structure → deterministic gap → LLM decides only with the cues separated) against end-to-end prompting.
  - Optionally, fine-tune a small model jointly on the slots, mirroring FrECI's Joint vs. Pipeline vs. SFT comparison.
  - Show which gains come from factorization and which from joint training.
- **Downstream measure (fragmentation analogue).** A "deservingness override index": the share of correctly computed cases whose verdict is flipped by cues, reported per criterion.
- **Novelty.** Diagnosis, then a theory-motivated intervention, then a measurement that policy scholars can interpret.

### Practical lessons from the repos (avoid their weak points)
- Fix and store seeds and split files. Run baseline and structured conditions on **identical** item sets. Do not leak label-derived statistics into inputs.
- Give LLM baselines full label *definitions*, and keep prompts identical across conditions apart from the manipulated slot. The MAD code put topic hints into some devices but not others.
- Ship the intermediate structures (gold facts, cues, gaps) so the oracle conditions can be reproduced without API calls.
- Release a single `eval.py` with factorized metrics plus strict EM.
- Caveat on scale: the pilot covers one model and the dev set only. For NAACL, run the oracle ladder (B) and the factorial design (C) on at least 3–4 model families/sizes and report bootstrap CIs.
