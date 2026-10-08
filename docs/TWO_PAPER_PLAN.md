# Two-paper plan (2026-10-08)

Status: drafted by the assistant on the PI's instruction (NAACL preliminary paper first, ACL follow-up second).
Nothing here is decided until the PI logs it in docs/decisions.md. This supersedes the single-paper framing in
docs/RESTART_PLAN.md ("decide the next design before any GPU time"), which now applies to Paper 2 only.

## The split in one table

| | Paper 1: preliminary (NAACL 2027) | Paper 2: follow-up (ACL 2027) |
| --- | --- | --- |
| Venue / cycle | ARR October 2026 (deadline 2026-10-12 23:59 AoE = KST 10-13 20:59), commit to NAACL 2026-12-23 | ARR January 2027 (date TBA), commit to ACL |
| Form | Short (4p) recommended; long only if a second seed and the off-mode ladder are run in time | Long (8p) |
| Question | Where, in rule-computable welfare determinations, do deservingness cues move LLM verdicts, and does the readout (direct vs reasoning) change the answer? | When the record is incomplete, do deservingness cues decide whether an LLM caseworker requests verification, grants, or denies? And does it use the same cue where the law makes it material? |
| Claim type | Reference point + measurement method (positive about the method, null about leakage under reasoning) | Positive, defined claim with rule gold (REQUEST), directional errors, CoT citation, consequence analysis |
| Data | In hand: Design B first-token (4 models, 6,376 items) + thinking (3 models, 1,554 items); Design C first-token (4 models) as methods evidence | New: Design D in the separate repo llm-welfare-evidence (PI's evidence-pilot patch, 2026-10-08): 24-base development set now, ladders and 40+ bases for the main study |
| GPU needed before submission | None required. Optional (pod rebuild ~2 h + runs ~6 h): second thinking seed; `--thinking off` same-prompt ladder; Ministral thinking run is not possible (no thinking mode) | Full: pilot in October, main runs in November |
| Track | Computational social science (primary); evaluation methods (secondary) | Computational social science; ethics/fairness secondary |

## What Paper 1 establishes for Paper 2 (and must therefore contain)
1. The testbed: SNAP FY2026 rules-as-code with the PolicyEngine-US cross-check and the QC-sampled household structures.
   Paper 2 cites it instead of re-describing it.
2. The computation reference point: with reasoning, rule-computable verdicts are at ceiling and paired cue contrasts are 0
   (T2 in docs/paper1/tables.md). Paper 2's claim "the effect lives where facts are incomplete, not where they are computable"
   needs this baseline.
3. The measurement lessons: direct first-token verdicts on aggregated facts follow a prior, any added sentence moves them
   (T3), the polarity flip exposes a yes-bias that pooled numbers hide, and first-token readouts cannot measure a
   discretionary judgment. Paper 2 uses generated verdicts as the primary readout because of this.
4. The protocol: both answer orders, base-clustered bootstrap, pre-registration, read-the-CoT-before-scoring rule.

## What Paper 1 must NOT claim (so Paper 2 stays novel)
- No claim about discretion, missing facts, or REQUEST behaviour as a finding. Design C first-token results appear only as
  evidence that the readout fails, in a methods paragraph or appendix.
- No "reasoning removes bias" claim; the wording is "under this protocol, verdicts do not move" (review of 370c219).
- No consequence/allocation numbers (saved for Paper 2, where the effect, if any, is defined).

## Known reviewer objections to Paper 1 and the answers to write
| objection | answer |
| --- | --- |
| Null result | The null is on the protocol where the model is competent; the non-null is on the protocol used by first-token audits. The paper is about which readout an audit should use. Cite Posner & Saran (formalism) and Soffer et al. (stable inside criteria) as predictions it confirms with gold-scored, multi-step rules |
| Small open models only | Stated as a limitation; the scale curve (8B, 14B, 32B) is reported. The follow-up adds frontier models |
| "Prompt sensitivity is known" | The contribution is the gold-scored, legally indexed version: the controllability contrast is the single consistent first-token signal (+0.04 to +0.09 on eligibility in all four models, clustered CIs exclude 0), and it vanishes under reasoning |
| Child-15 trap is adversarial | Reported as its own analysis; checklist-vs-age conflict named as such |
| One legal situation, one program | Limitation; Paper 2 adds the evidentiary dimension, not a second program |
| Maryland uses Claude | No Claude in Paper 1. Disclose if added in Paper 2 |

## Timeline
| when | Paper 1 | Paper 2 |
| --- | --- | --- |
| Oct 8-12 | Write from docs/paper1/outline.md and tables.md; Limitations + Responsible NLP checklist; anonymised release repo; register all authors as reviewers | Evidence repo: smoke + competence run on Qwen3-8B as the runbook says (docs/RUNPOD_EVIDENCE_PILOT.md there) |
| Oct 13-31 | Rest | Paired development run; build the cue-surface and evidence ladders (depth_roadmap.md there); pilot; freeze; OSF pre-registration |
| Nov | Respond to nothing (reviews in Dec) | Main runs: open models, then frontier if the pilot passes the pre-registered gate |
| Dec | Meta-reviews 12-18, NAACL commitment 12-23 | CoT coding (300 traces), consequence analysis, writing |
| Jan | Notification 2027-02-10 | ARR January submission |

## Repo split (2026-10-08)
Paper 1 stays in this repo (hub). Paper 2 lives in llm-welfare-evidence (local: /root/llm-welfare-evidence), assembled from the
PI's evidence-pilot patch plus the hub files it imports. This repo's docs are not retargeted to Design D.

## Open points for the PI
1. Confirm the Oct 12 cycle for Paper 1 (docs/NORTH_STAR.md records that it was skipped on 2026-10-05; this plan reverses that).
2. Short vs long for Paper 1. Short fits the content in hand; long needs the optional runs above.
3. Whether Paper 1 should include the Design C first-token methods results at all (recommended: one paragraph, appendix table).
