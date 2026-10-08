# Consequence analysis (src/eval/consequence.py), 2026-10-08

Table: elig_narrative.md (JSON: elig_narrative.json). Caseload = the 40 pilot bases at the four income margins, income
eligibility, narrative style (the item set both readouts cover); equal base weights primary (size-stratified by
construction), HWGT weights secondary. Rates per 100k cases of that near-threshold synthetic caseload.

What it shows (seed-0 results):
- First-token readout: the controllability contrast changes 7k-16k verdicts per 100k in 14B / 32B and 12k in 8B, always in
  the direction blameless job loss -> YES, fired -> NO. Wrongful denials per 100k are 4k-8k higher under the "fired" cue.
- Thinking readout: 0 verdicts changed and 0 wrongful denials in 14B and 32B; 8B has a small effort-direction residue
  (4k per 100k, CI includes 0).
- Decision-level flips are concentrated: 14B 5 flips in 2 bases, 32B 12 in 3 bases, 8B 9 in 4 bases (of 37), spread over all
  four margins. The probability-level contrast (docs/paper1/tables.md T2) is broad; the verdict-level effect is a few
  households whose P(YES) sits near 0.5. Hence the bootstrap lower bounds at 0: resamples without those bases show no flips.
- HWGT weighting is unstable with 40 bases (one heavy base drives +35.6 pp in 14B); report it only as robustness.

Reading for the paper: an audit that reads first-token probabilities reports a socially patterned eligibility gap and
extra wrongful denials; the same models, asked to reason, produce none. The gap is an artifact of the readout, and it
concentrates on near-tie households, which is where real caseloads also sit.
