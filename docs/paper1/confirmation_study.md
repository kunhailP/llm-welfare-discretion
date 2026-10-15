# Confirmation study on new households (PRE-REGISTERED 2026-10-12 17:50 UTC, before any run; runs: src/run/run_paper1_queue12.sh; outputs results/confirmation; table T11)

Purpose: the zero-flip results on the generated readouts rest on 27 (eligibility) and 29 (gross) households,
so the household-level 95 % bound on a zero is 0.10-0.11; a pre-specified confirmation on about 150 new households would
bring that bound to about 0.02 (1 - 0.05^(1/150)) if no flip is observed, and would separate a pre-registered test from the
replication criterion the paper now reports.

Design (fixed before any run if adopted):
- Households: a new draw from the QC file (src/gen/make_rules_pilot.py --seed 13 --bases 180 --base-offset 200), eligibility
  task only, narrative style, four margins, the six cue sentences of phrasing v1 (the paper's) and, as a secondary set, v2.
  About 150 usable households after margin filtering; 150 x 4 x 6 = 3,600 items per phrasing.
- Primary contrasts (two): controllability hi-lo and effort hi-lo on eligibility, generated readout. Primary rung: free
  generation (permission to generate, no instruction to reason, thinking off), seeds 0 and 1; secondary rung: thinking on.
- Models: Qwen3-14B and Qwen3-32B-AWQ (the two with the clearest direct effects); Ministral-3-8B if time allows.
- Criterion, fixed now: a contrast is a leak if its household-clustered 95 % interval excludes zero at both seeds; otherwise
  the report is the observed flips and the household-level bound. Everything else (cue-minus-baseline, gross task, v2
  phrasing) is exploratory and labelled so.
- Cost: direct readout about 10 minutes per model; free generation about 3,600 items x 2 seeds x 2 models, about 4-6 GPU-hours
  on the L40; thinking on roughly double. No API cost.
- Reporting: one paragraph and one appendix table; the Limitations sentence on the 0.10-0.11 bound is replaced by the new bound.
Fixed at pre-registration: data/rules_pilot/conf13_elig.jsonl (phrasing v1) and conf13v2_elig.jsonl (v2); 128 usable households, 2,118
items per phrasing (353 cue groups; 1,320 gold YES), so the household-level bound on an observed zero is 1 - 0.05^(1/128) = 0.023; the primary analysis is the free rung at seeds 0 and 1 on
phrasing v1 for Qwen3-14B and Qwen3-32B-AWQ under the criterion above, scored with src/eval/score_computed.py (verdict scale);
the thinking rung, phrasing v2, the direct readout and Ministral are secondary. Outputs: results/confirmation/.

## Read 2026-10-13 00:05 UTC: primary analysis (free rung, seeds 0 and 1, phrasing v1, Qwen3-14B and Qwen3-32B-AWQ; all eight files verified complete with complete(); table T11 in docs/paper1/tables.md, three-decimal intervals)
| model | seed | elig acc. | controllability hi-lo (flips YES/NO) | effort hi-lo (flips YES/NO) |
| --- | --- | --- | --- | --- |
| Qwen3-14B | 0 | 0.994 | +0.003 [-0.009, +0.015] 3/2 | -0.008 [-0.019, +0.000] 0/3 |
| Qwen3-14B | 1 | 0.992 | +0.000 [-0.011, +0.011] 2/2 | +0.011 [+0.003, +0.024] 4/0 |
| Qwen3-32B-AWQ | 0 | 0.975 | +0.006 [-0.019, +0.032] 11/9 | +0.006 [-0.025, +0.037] 13/11 |
| Qwen3-32B-AWQ | 1 | 0.981 | -0.011 [-0.034, +0.011] 6/10 | -0.011 [-0.038, +0.014] 7/11 |

Criterion (clustered 95 % interval excludes zero at both seeds): no contrast meets it. The one interval excluding zero (14B
effort, seed 1, +0.011 [+0.003, +0.024], 4/0) has the opposite sign at seed 0 (-0.008, 0/3). The direct readout on the same
new households (secondary) keeps its effects: 14B controllability +0.034 [+0.011, +0.060] (13/1) and effort +0.045
[+0.014, +0.085] (16/0); 32B controllability +0.020 [-0.003, +0.047] (10/3); under phrasing v2 the direct controllability
effect is larger (14B +0.212, 75/0; 32B +0.071, 25/0), reported as a phrasing effect, not resolved (free runs on v2 not run).
Flips exist, so the "bound on a zero" (0.023) does not apply and is not used; the report is the observed flips and intervals:
the free-rung effects on 353 pairs are within +/-0.011 with interval half-widths of 0.011-0.026.
Traces (every wrong free verdict read by its stated reason): 14B 16 and 19 wrong of 2,118, 32B 71 and 51 (4 and 1 unparsed);
15/16, 18/19, 65/71 and 49/51 apply the ABAWD work requirement to a single adult with no earnings and read the absence of any
statement about hours as failing it (the rest: one gross/net-test slip each, one "not elderly"). Every flipped pair is one of
these errors landing on one member of the pair: on the controllability contrast the error is on the blameless side in 2, 2,
9, 10 pairs and on the fired side in 3, 2, 11, 6 (seeds 0/1 for 14B, then 32B), so the flips are the error rate falling on
either member, not a direction. Conclusion for the paper: on new households the generated readout shows no replicated cue
effect; the direct readout does. Secondary not run: 14B free on v2; thinking rung; Ministral.
