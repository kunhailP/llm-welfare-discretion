# North star — read before every design decision

## Standing policies (current; set by the PI, 2026-10-05)
- **Target and bar:** ACL 2027 via the January 2027 ARR cycle, judged at EMNLP-main quality, aiming at ~4.5 overall
  (the PI treats ~4.2 as borderline). "EMNLP" names the quality bar, not a change of venue.
- **Two questions for every step:** novelty (what prior work does not show) and venue fit (which track, which
  reviewer would call it a clear NLP contribution). If a step serves neither, drop it.
- **Depth first:** the first paper opens ONE unexplored problem and digs it deeply; it is the foundation for
  follow-ups. Extra contributions (e.g. legally grounded concept erasure, probing) go to a follow-up roadmap.
- **Learn from reference works, never copy them** (Zhao / FrECI / FrECO: design approach only).
- **No human-participant baseline** (too costly for this paper).
- **No paid API models** until the design is strong enough to place high at EMNLP/NAACL; open models only until then.
- **Look at results one by one**, carefully; read model reasoning before scoring; pre-register before reading.
- **Git:** commits authored by the PI only, no AI co-author trailers; never store access tokens anywhere.
- **Tracks:** primary computational social science; secondary evaluation methods, analysis, fairness. Do not force
  the agentic-communication theme track.

The sections below are kept for the record (NAACL-cycle and stage-1 framing).


> **Retarget (2026-10-05):** the Oct-12 ARR cycle (NAACL 2027) is skipped. Target: Jan-2027 ARR cycle
> (ACL 2027; exact date TBA), bar ~4.5 overall. Core question: in real welfare administration, do strong
> LLMs pull need judgments toward deservingness cues, and does that change measurement/allocation
> conclusions? See decisions.md. The NAACL facts below are kept for the record.

Every design choice is checked against two questions:

1. **Novelty:** what does this show that prior work (FairFund-Bench, Value Entanglement, prompt/label
   sensitivity work, LLM-annotation validity work, Zhao/FrECI) does not?
2. **Venue fit:** would a NAACL reviewer accept it as a clear, substantive NLP contribution
   (methodological, empirical, evaluation-method, or resource)?

If a step serves neither, drop it.

## NAACL 2027 facts (CFP, checked 2026-10-05)

| Item | Value |
| --- | --- |
| ARR submission (long 8p / short 4p) | 2026-10-12, 23:59 AoE (KST 10-13 20:59) |
| All authors registered as reviewers | 2026-10-12 (same day; new reciprocal reviewing policy) |
| Meta-reviews | 2026-12-18 |
| NAACL commitment | 2026-12-23 (choose NAACL or COLING; cannot change after) |
| Notification | 2027-02-10 |
| Conference | 2027-06-01 to 06-05, San Francisco |
| Required | Limitations section, Responsible NLP checklist, ACL ethics policy, double-blind |

## Track fit

| Track | Fit |
| --- | --- |
| Computational social science / NLP for social good | primary |
| Resources, benchmarks and evaluation (evaluation methodology) | secondary |
| Interpretability and analysis (stage decomposition) | secondary |
| Ethics, bias, fairness (spurious group gaps) | secondary |
| Theme track: language as a medium for agentic communication | NOT a fit; CFP says merely using agents is insufficient. Do not force it |

## Where the novelty must come from (as of the oracle-ladder diagnostic)

- "Unemployed context overrides stated facts" in general: NOT supported (yes/no wording ~perfect in Qwen3-8B and Ministral-3-8B).
- Live candidate: failure appears only with need-laden answer vocabulary (SHORTFALL/SUFFICIENT) in the unemployed context.
- "Prompts are sensitive" is not new. The claim must show the sensitivity is
  (a) directional, (b) socially patterned (unemployed, not employed or no context), and
  (c) consequential (spurious group differences in downstream measurement).
- Long vs short paper: decide after sequence-level scoring. A single sharp finding fits a 4-page short paper.
