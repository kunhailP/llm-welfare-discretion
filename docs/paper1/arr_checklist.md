# ARR October 2026 submission: checklist answers, form fields, and the submission steps (drafted 2026-10-08; PI edits and submits)

Sources: ARR CFP (aclrollingreview.org/cfp), Responsible NLP Research checklist (aclrollingreview.org/responsibleNLPresearch/),
ACL Policy on Publication Ethics (generative assistance, section 4.2.2), ACL Peer Review Committee "Sustainable Peer Reviewing
Policy" (September 2026; in force from the October 2026 cycle per the CFP), NAACL 2027 call (2027.naacl.org).

## 1. Deadlines (all 11:59 pm UTC-12)
| date | what |
| --- | --- |
| 2026-10-12 | ARR submission (short paper, 4 pages) AND reviewer registration for designated service contributors; 48 h grace for the registration form |
| 2026-10-19 | all authors' OpenReview profiles complete (affiliation, ORCID, DBLP, ACL Anthology, email); incomplete = desk reject |
| 2026-12-18 | meta-reviews released |
| 2026-12-23 | commitment to NAACL 2027 (or COLING 2027; one primary venue, cannot be changed) |
| 2027-02-10 | notification; camera-ready 2027-03-03 (5 pages for short papers) |

## 2. The service-contributor requirement (what "submitting without one" means)
- Each submission names ONE designated service contributor (an author or a non-author) who is qualified and serves in the same
  cycle (5 reviews or 8 meta-reviews per designated paper; at most 2 papers per contributor). A submission is guaranteed reviewers
  only if it brings that capacity.
- Submissions with no qualified contributor go to a LOTTERY for the spare capacity; the ones not drawn are desk rejected. The
  lottery may be weighted against bulk submitters. So: submitting without a contributor is allowed, review is not guaranteed.
- Qualified (broadened criteria, in force since the August 2026 cycle): PhD holders / postdocs / faculty with >= 2 publications at
  major ACL events (ACL, CL, COLING, CoNLL, EACL, EMNLP, HLT, IJCNLP/AACL, LREC, NAACL, TACL, *SEM), Findings, or major ML venues
  (AAAI, COLM, CVPR, ECCV, FAccT, ICCV, ICLR, ICML, IJCAI, JAIR, JMLR, NeurIPS, TMLR, TPAMI); doctoral students and industry
  researchers with a Master's: >= 2 such publications and >= 3 publications in total.
- Non-author designated contributor: allowed; must vouch that the paper is "ready for consideration for acceptance at a top-tier
  conference" and be willing to do the service; needs a complete OpenReview profile with a verifiable record.
- Manual application for equivalent experience exists but is slow ("send as early as possible").
- Options for this paper, in order: (a) PI qualifies -> PI is the contributor; (b) a qualified colleague vouches as non-author
  contributor; (c) a qualified co-author with a real intellectual contribution (ACL authorship rules); (d) submit into the lottery.

## 3. Responsible NLP checklist answers (fill in the OpenReview form; section pointers refer to paper/main.pdf v2)
| item | answer | where / justification |
| --- | --- | --- |
| A1 limitations | Yes | Section 5 (Limitations) |
| A2 risks | Yes | Ethics statement; Discussion (deployment readout, audit misuse); Limitations (no frontier model, no human baseline) |
| B1 cite artifacts | Yes | Section 2 (SNAP QC FY2024 file, FNS FY2026 parameters, PolicyEngine-US 2.24.5), Appendix F (models and versions) |
| B2 licences | Yes | Appendix F: Qwen3 family and Ministral-3 Apache-2.0; PolicyEngine-US AGPL-3.0; SNAP QC and FNS documents U.S. federal public domain; our release licence in its README (PI to choose: code MIT or Apache-2.0, data CC BY 4.0) |
| B3 intended use | Yes | Appendix F and Ethics: QC file used for household structures only, not redistributed; models used for evaluation; release for audit methodology, not deployment |
| B4 PII / offensive content | Yes | Ethics statement: QC file is de-identified; names are placeholders; items are generated text |
| B5 documentation | Yes | Section 2 and Appendix B (domains: SNAP income tests and ABAWD; English; household-size strata); supplementary README |
| B6 statistics | Yes | Section 2 (6,376 items; 1,554-item subsample: 60 / 74 / 150 cue-paired groups; 29 / 27 / 40 households per task); no train/dev/test split (evaluation only) |
| C1 parameters / compute | Yes | Appendix F (8.2B / 14.8B / 32.8B 4-bit / 8B; one NVIDIA L40; about 20 GPU-hours in total) |
| C2 setup / hyperparameters | Yes | Section 2 Readouts and Appendix F (sampling settings; no search; vendor defaults) |
| C3 descriptive statistics | Yes | Sections 3, Appendix C-D (clustered bootstrap CIs, two seeds, flip counts, noise floor) |
| C4 packages | Yes | Appendix F (vLLM 0.30.0, transformers 5.14.1, PyTorch 2.13.0, PolicyEngine-US 2.24.5); lock files in the supplementary software |
| D1-D5 human subjects | N/A | no annotators or participants |
| E1 AI assistants | Yes | see section 4 below; text goes in the E1 field (anonymous review version has no Acknowledgements) and, at camera-ready, in Acknowledgements |

## 4. E1 statement (DRAFT for the PI to edit; ACL policy: content-creating uses must be disclosed, proofreading is exempt)
"An AI assistant (Claude, Anthropic) was used throughout this project under the first author's direction: to draft and revise
the manuscript text from the author's results notes and tables, to write and refactor the analysis and evaluation code, to run
and score the model experiments on the author's hardware, to generate the tables in the appendix from the result files, and to
produce simulated reviews used to revise the draft. All experimental designs, decisions, interpretations and claims are the
author's; the author verified every reported number against the result files. No generative tool is an author."
Note: the repo's PI-only authorship policy (NORTH_STAR) is about authorship credit and git authorship; it is consistent with
this disclosure. ACL treats undisclosed content-creating use as inappropriate use, so E1 must be answered "Yes" with text.

## 5. OpenReview form fields (draft)
- Title: Where Deservingness Leaks: Direct and Reasoning Readouts of LLM Welfare Determinations
- Paper type: short. Track (NAACL list): "Ethics, Bias, and Fairness" (first choice) or "Computational Social Science, Cultural
  Analytics, and NLP for Social Good"; secondary "Resources, Benchmarks, and Evaluation".
- Keywords: decision audit; deservingness; welfare eligibility; rules-as-code; first-token vs generated readout; chain-of-thought;
  SNAP; fairness evaluation.
- Short abstract (about 190 words, for the form; the PDF keeps the full one):
  "Language models are entering welfare eligibility work. We test whether legally irrelevant deservingness cues (job-search effort,
  controllability of job loss) move their determinations on a SNAP FY2026 rules-as-code testbed with computed, independently
  cross-checked gold labels. The answer depends on the readout. With direct first-token answers, four open models are at chance on
  the income tests and wrongly deny 24-63% of eligible near-threshold households before any cue; cues then move verdicts, mostly in
  task- and model-specific directions, with one exception that holds in all four models: a blameless job loss raises the
  eligibility verdict. A hardship sentence with no deservingness content moves verdicts as much. Asked to compute step by step, the
  same models are at ceiling and paired cue contrasts flip 0-3 of 60-74 pairs with no sign that survives a second seed; every zero
  is bounded. A same-prompt ladder shows that asking for computation, not the thinking switch, removes most of the effect; one cell
  passes a pre-stated leak criterion, and a second model's same-sized asymmetry disappears at the next seed. Audits of LLM benefit
  decisions must use the deployment readout, pair cues, fix a leak criterion before looking, and report effects only where the
  model is competent. We release the testbed."
- Supplementary: software = llm-welfare-rules-anon-software.zip; data = llm-welfare-rules-anon-data.zip (built by
  src/release/make_release.sh; both pass the identifier check). No external links (no Dropbox-type trackers allowed).
- Preprint option: no anonymity period; choose the binding "no non-anonymous preprint" option only if the PI will not post to arXiv
  before 2026-12-18.
- Concurrent submissions: none (Paper 2 is not submitted).
- Previous ARR submissions of this work: none.

## 6. Still open (PI)
1. Service contributor (section 2) and OpenReview profile with ORCID.
2. E1 wording (section 4) and the release licence (B2).
3. Citation for "federal guidance warns that such tools may introduce bias or errors" (Introduction) or soften the sentence.
4. Frontier-model replicate (src/run/run_rules_api.py ready; not run).
5. Commit both repos; the hub history is the pre-registration record.
