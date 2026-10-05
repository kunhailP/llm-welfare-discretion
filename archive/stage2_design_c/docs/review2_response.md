# External review 2 (pasted by user, 2026-10-05): response against the results we now have

The review was written before the rules pilot ran. Since then: thinking off -> income tasks at chance;
thinking on (14B, 32B) -> rule-computable verdicts ~100% and cue effects 0. So we are in the review's
row 3 ("no effect anywhere") for rule-computable decisions, and the review's row 2 framing
("it leaks only where discretion arises") is exactly Design C (docs/11).

| # | review point | verdict | action |
| --- | --- | --- | --- |
| 1 | Fix the cue text, vary only legal relevance | Adopt; already true in Design C (same cue, standard open vs open_need vs enum) | keep as the core contrast |
| 2 | Pre- vs post-P.L. 119-21 packet as a natural experiment | Partly. It tests rule-following vs prior law, not deservingness, so it is a second question (depth-first rule). Cheap and partly observed already (14B/32B trap errors; 5/26 cite "under 18") | small diagnostic section / appendix, not the core |
| 3 | Incomplete facts (hours missing -> correct answer "request verification"); does a low-effort cue make the model fill the gap as 0 hours? | **Adopt, high priority.** It is the second discretion point doc 11 lacked, and it is where the null risk is lowest | add to Design C v2 with a 3-way answer (YES / NO / REQUEST_INFO) |
| 4a | Noise baseline from meaning-preserving edits | Adopt. Note: first-token runs are deterministic, but **thinking runs sample (T=0.6)**, so they also need a seed baseline | name swap, sentence order, 2 seeds on the thinking subset |
| 4b | YES/NO polarity flip | Adopt (32B gross YES rate 0.97 in the rules pilot shows a YES prior) | "grant?" vs "deny?" question |
| 4c | Pre-registered H1/H2 + exploratory, hierarchical model or FDR | Adopt | write before the main run |
| 4d | Rerun every number with provenance | Already true for the new runners (meta.json has versions, sampling, rendered prompt); v1 numbers are not used | none |
| 5 | Larger / reasoning models without paid APIs | Adopt gpt-oss-20b (reasoning, second family; downloading). Llama-3.3-70B-AWQ = 39.8 GB on 48 GB: first-token only, short context, test fit | add both if they load |
| 6 | v1/v2 measurement pitfalls as a methods contribution | Partly. As its own contribution it dilutes; as one section it directly supports the regime axis (direct-answer verdicts are prior-driven) | one section, not a separate claim |
| 7 | Policy units; payment error rate vs CAPER | Adopt the caution: wrongful denials are not in the payment error rate; check FNS definitions before writing anything that maps to the FY2028 cost share | verify before use |
| 8 | Agency framing of job loss (structural / agentless passive / self as agent) | Conditional. **"She quit" is NOT legally irrelevant**: SNAP has a voluntary-quit sanction (7 CFR 273.7(j)). Use agency variants that keep the legal facts fixed (the plant closed / she was let go / her manager fired her). Only if the controllability effect shows up in the discretion pilot | cue-variant extension, conditional |

## Mechanism angles the review lists, mapped to our setup
- Where it leaks (extract-then-compute): reasoning already removes it for computation; in discretion there is
  nothing to compute, so the mechanism question becomes whether the cue is cited (next point).
- Does the reasoning hide the cue: in the rules pilot the cue is cited (effort_low 38-49% of elig traces) but
  the verdict does not move. In discretion: effect present + not cited = unfaithful; effect present + cited
  as a reason = open reliance on a legally irrelevant factor. Both are reportable.
