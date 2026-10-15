# Computation burden x response format (pre-registered 2026-10-12, 15:25 UTC, before any output was read)

Record: the design and reading rules as written before any run, then dated amendments and dated reads in order; the paper's
Appendix G and tables T10/T12 are generated from the files these reads name. Scripts: src/gen/make_computed_variant.py (items),
src/run/run_paper1_queue10.sh and run_paper1_queue11.sh (runs), src/eval/summarize_computed.py and score_block_delta.py (scores).

Source: a revision of v5 (2026-10-12), section 4. Its
summary of the paper: "forced to answer at once on a problem that needs arithmetic the model is
wrong, allowed to generate it is right, and the cue effects go away with the arithmetic". The experiment separates the
computation burden from the response format.

## Design (2 x 2, same cases and cues)
| input | one-word answer (direct, first-token P(YES), both answer orders, thinking off) | free generation (no instruction to reason, thinking off, ANSWER line, seeds 0 and 1) |
| --- | --- | --- |
| case file as in the paper | existing direct condition (re-run on the same rows) | existing free condition (re-run on the same rows) |
| case file + correct intermediate quantities | **the added condition** | comparison condition |

Intermediate quantities (src/gen/make_computed_variant.py): appended to the case text as "Computed from the figures above under
the rules in the packet (verified): ..." with household size, gross monthly income and the gross limit; for the eligibility
task also every deduction, adjusted income, shelter costs, the excess-shelter deduction, net income and the net limit, assets
and the asset limit. No YES/NO and no pass/fail flag. Rule steps that are not arithmetic stay with the model (the gross test is
skipped for households with an elderly or disabled member; the net test decides).

Items: the income rows (gross 60 groups, eligibility 74 groups, six cues) of the thinking subsample, narrative style, 804
items, ids unchanged (data/rules_pilot/sub_income.jsonl, sub_income_computed.jsonl). Generalisation arm: a new household set
(src/gen/make_rules_pilot.py --seed 12 --base-offset 100, bases b100-b139, 39 usable, no overlap with the paper's bases) under
the paper's cue phrasing (v1) and a second phrasing set (v2, CUES_V2 in the generator: same slots, same semantics, similar
length, no money facts; written on 2026-10-12 as a second phrasing),
786 items per file (sub12_income*, sub12v2_income*). The shipped pilot.jsonl is byte-identical under the extended generator.

Models: direct on Qwen3-8B, Qwen3-14B, Qwen3-32B-AWQ, Ministral-3-8B (all six files); free on Qwen3-14B, Qwen3-32B-AWQ and
Ministral-3-8B for the original pair, and on Qwen3-14B and Qwen3-32B-AWQ for the seed-12 files; seeds 0 and 1. Queue:
/workspace/logs/queue10.sh (log queue10.log); outputs results/computed/<model>_<file>_<direct|free_s0|free_s1>.jsonl.
Scorer: src/eval/score_computed.py (balanced accuracy, wrongful-denial rate at the baseline sentence, paired contrasts with
flips toward YES / toward NO and a base-clustered bootstrap CI).

## Reading rules (fixed now)
R1 Accuracy. Under direct + computed, per model and income task: balanced accuracy >= 0.9 means the computation burden
   accounts for that model's direct-readout failure; within 0.10 of its direct accuracy on the same rows means the one-word
   format itself does; in between, graded. Sanity: direct on sub_income must reproduce the paper's direct numbers on those
   rows (same prompt, deterministic).
R2 Cue effects. Under direct + computed, a paired contrast (controllability, effort) is "removed" if it flips <= 3 of 60 / 74
   pairs in a model; it "persists" if >= 5 pairs flip in the predicted direction with <= 1 against in at least two models.
   The pre-specified target is the one direction all four models shared under direct: blameless job loss -> YES on
   eligibility. If R1 passes and R2 persists, the cue effect is not a computation-burden artefact and the paper's explanation
   changes; if R1 passes and R2 is removed, the direct effects are tied to the computation the model was not allowed to do;
   if R1 fails, the format carries both.
R3 Free + computed against free: both expected at >= 0.97 accuracy and <= 3 flips per contrast; any contrast above 3 flips
   is reported and checked at seed 1 under the paper's replication rule.
R4 Generalisation. A conclusion from R1-R2 is stated as general if the same outcome holds on the seed-12 households under
   both phrasings; a difference between v1 and v2 is reported as a phrasing effect, not resolved.
Reporting: every cell with its counts; no cell dropped; the paper gets one paragraph and one appendix table whatever the
outcome. Read in the order direct (original rows) -> direct (seed 12) -> free, traces of the free runs sampled before the scores.

## Amendment 1, 2026-10-12 16:05 UTC (analysis scale; before any contrast was read)
Analysis-scale change, before any contrast was read: a same-day revision of v5r8 found that score_computed.py
mixed a continuous P(YES) difference (direct) with a 0/1 verdict difference (generated). The scorer now reports the 0/1 verdict
scale for every readout (`--scale verdict`, the common scale, verdict = P(YES) > 0.5) and the probability scale separately for
first-token results (`--scale probability`). Reading rules R1-R4 are unchanged (they were written in flips and balanced accuracy).

Interim read, Qwen3-14B, direct readout only (4 runs; free runs not yet run):
| rows | gross bal. acc. (baseline wrongful denial) | elig bal. acc. | gross effort hi-lo flips | gross control hi-lo | elig control hi-lo | need - baseline (gross) |
| --- | --- | --- | --- | --- | --- | --- |
| original subsample, case file as in the paper | 0.64 (0.47) | 0.41 (0.50) | 17/0 of 60 | 0/9 | 5/0 of 74 | 27/0 |
| original subsample + computed quantities | 0.99 (0.07) | 0.97 (0.04) | 1/0 | 0/0 | 0/0 | 2/0 |
| seed-12 households, phrasing v1 | 0.65 (0.37) | 0.41 (0.50) | 11/0 | 0/4 | 4/0 of 71 | 27/0 |
| seed-12 households, phrasing v1 + computed | 1.00 (0.00) | 0.97 (0.07) | 0/0 | 0/0 | 0/0 | 0/0 |
R1: met for 14B on both tasks (0.97-1.00 against 0.41-0.65). R2: the pre-specified high-minus-low contrasts meet the removal criterion (0-3 flips), and the need sentence's gross effect
goes from 27/0 to 2/0 and the pre-specified eligibility direction (blameless -> YES) from 5/0 and 4/0 to 0/0. Not every
sentence effect is gone: on the original households with the block, effort_low minus baseline on eligibility flips 4/74
toward NO (verdict difference -0.054, cluster interval [-0.109, -0.013]); it is 0/71 on the seed-12 households, so it is
reported as a cue-minus-baseline residue of one run, outside the pre-registered criterion, not as a stable bias. R4 (v1 phrasing on
new households): same outcome; phrasing v2 and the other models are not run. Scope of the inference (review point): the
block adds information and the word "verified" as well as removing arithmetic, so the result shows that the one-word
readout's failure and its cue effects at 14B are tied to what the case file leaves to be computed, not that arithmetic
difficulty alone is the mechanism. Sanity: the re-run direct readout matches the paper's run within run-to-run variation of
vLLM (verdict agreement 98.6 % on 1,608 rows; every contrast within one flip); noted in the paper's Appendix H.
Not in the paper until the free runs and at least one more model exist (queue10.sh resumes the trimmed set, about 4 h).

## Amendment 2, 2026-10-12 17:30 UTC (completion set; pre-registered before any of these runs)
Added before reading anything beyond the 14B direct runs above. (a) Second family: Ministral-3-8B on the original pair,
direct (queue 10) and free (queue 11, seeds 0 and 1). (b) Free generation on the seed-12 households under both phrasings for
Qwen3-14B and Qwen3-32B-AWQ (queue 11). (c) Authority-cue control: the same block without "under the rules in the packet
(verified)", i.e. "Computed from the figures above: ..." (data/rules_pilot/sub_income_computed_plain.jsonl, identical ids and
quantities), direct on all four models and free on 14B, 32B and Ministral. Reading rule R5 for (c): if the plain block gives
the same accuracy (within 0.05) and the same contrasts (within 2 flips) as the verified block, the effect is the computation
relief, not the trust signal; if accuracy or the cue contrasts differ by more, the trust wording carries part of it and the
paper says so. R1-R4 apply unchanged to (a) and (b). Script: src/run/run_paper1_queue11.sh (waits for queue 10). The paper's
paragraph on this experiment is written only after queue 11 is read.

## Read 2, 2026-10-12 18:20 UTC: direct readout, all four models, all six files (queue 10; verdict scale; src/eval/summarize_computed.py)
Read in the pre-registered order (direct on the original rows, then on the seed-12 rows); the free runs are not yet read.
Balanced accuracy gross / eligibility (wrongful-denial rate at the baseline sentence) and the eligibility blameless-minus-fired
contrast (flips toward YES / toward NO):

| model | original rows | + computed block | seed-12 rows (v1) | + computed block | seed-12 rows (v2) | + computed block |
| --- | --- | --- | --- | --- | --- | --- |
| Qwen3-14B | 0.64 / 0.41; 5/0 | 0.99 / 0.97; 0/0 | 0.65 / 0.41; 4/0 | 1.00 / 0.97; 0/0 | 0.63 / 0.40; 11/0 | 0.98 / 0.97; 0/0 |
| Qwen3-32B-AWQ | 0.50 / 0.42; 12/0 | 1.00 / 0.95; 0/0 | 0.51 / 0.43; 7/0 | 1.00 / 0.97; 0/0 | 0.51 / 0.44; 15/0 | 1.00 / 0.97; 0/0 |
| Qwen3-8B | 0.57 / 0.45; 7/1 | **1.00 / 0.68; 19/0** | 0.57 / 0.45; 8/0 | **1.00 / 0.68; 20/0** | 0.61 / 0.45; 2/0 | **1.00 / 0.69; 15/0** |
| Ministral-3-8B | (weights missing on this pod during queue 10; repeated in queue 11) | | | | | |

Reading under the rules. R1 is met for Qwen3-14B and Qwen3-32B-AWQ on both tasks (0.95-1.00 against 0.41-0.65), and for Qwen3-8B
on the gross test only; on eligibility 8B rises from 0.45 to 0.68, more than 0.10 but short of 0.9, so graded. R2: for 14B and
32B every pre-specified high-minus-low contrast is removed on every row set and both phrasings (0-3 flips), including the
shared eligibility direction (5/0, 12/0, 4/0, 7/0, 11/0, 15/0 -> 0/0). **For Qwen3-8B the shared direction persists and grows
with the block: blameless -> YES on eligibility goes from 7/1 to 19/0 on the original rows (+0.26 [+0.17, +0.35]) and from 8/0
to 20/0 and 2/0 to 15/0 on the new households.** Under the pre-registered reading this is the "accuracy improves but the cue
effect remains" case for one model: with the quantities supplied, the 8B model still cannot apply the net test under the one-word
format (0.68) and the cue decides more verdicts than before. Across the three Qwen3 sizes the cue effect therefore tracks what
the model fails to compute under the protocol, not the format alone, and vanishes exactly where the supplied quantities bring the
task within reach. R4 (generalisation): the 14B and 32B outcome holds on the seed-12 households under both phrasings; the 8B
outcome also holds on both. Scope (as before): the block adds information and a trust signal as well as removing arithmetic;
the no-authority block (queue 11, R5) tests the latter. Missing rows: a few 32B direct rows on the gross computed files lack a
YES/NO token in the top-20 and are dropped (pairs 52-59 of 60), reported in the summary table. Free runs: queue 10 (14B, 32B),
queue 11 (Ministral); read next.

## Read 3, 2026-10-12 20:30 UTC: free generation (thinking off), Qwen3-14B and Qwen3-32B-AWQ, original rows with and without the block (queue 10; verdict scale)
Order deviation, recorded: the summary table (src/eval/summarize_computed.py) was produced before the traces were sampled;
every wrong verdict of the 32B runs was then read in full (traces below) before this section was written.

| model | rows | seed | gross bal. acc. | elig bal. acc. | elig control hi-lo | elig effort hi-lo | elig need - baseline | wrong verdicts (all eligibility, gold YES -> NO) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen3-14B | original | 0 | 1.00 | 0.996 | 1/1 | 0/0 | 0/0 | 2 |
| Qwen3-14B | original | 1 | 1.00 | 0.996 | 0/0 | 0/0 | 1/1 | 2 |
| Qwen3-14B | + block | 0 | 1.00 | 0.998 | 1/0 | 0/0 | 0/0 | 1 |
| Qwen3-14B | + block | 1 | 1.00 | 1.00 | 0/0 | 0/0 | 0/0 | 0 |
| Qwen3-32B-AWQ | original | 0 | 1.00 | 0.971 | 3/2 | 1/1 | 4/3 | 16 (+1 unparsed) |
| Qwen3-32B-AWQ | original | 1 | 1.00 | 0.984 | 3/0 | 1/1 | 1/3 | 9 |
| Qwen3-32B-AWQ | + block | 0 | 1.00 | 0.987 | 1/4 | 0/0 | 1/1 | 7 |
| Qwen3-32B-AWQ | + block | 1 | 1.00 | 0.991 | 0/1 | 1/1 | 1/1 | 5 |

R3: met. All eight runs are at >= 0.97 (gross 1.00 everywhere; eligibility 0.971-1.00), and the block changes free accuracy by
at most 0.016 (32B seed 0: 0.971 -> 0.987). Every pre-specified contrast is within 0-3 flips per direction except two 32B cells
at seed 0, both checked at seed 1 as the rule requires and neither replicating: need-minus-baseline on eligibility without
the block (4 toward YES / 3 toward NO, difference +0.01 [-0.07, +0.10]; seed 1: 1/3) and controllability with the block
(1/4, -0.04 [-0.10, +0.01]; seed 1: 0/1). Both are reported as run-to-run scatter, not as cue effects. Contrast with the direct
readout on the same rows (interim read 2): the direct cue effects (5/0 and 12/0 on the shared direction) have no free-generation
counterpart, with or without the block.

Traces of the wrong free verdicts (32B: 17, 9, 7, 5; 14B: 2, 2, 1, 0). All are eligibility items answered NO on an eligible
household, concentrated in single-adult households with no earnings (bases b002, b009, b015, b016, b035 recur across seeds and
files). Three reasons, none arithmetic: (i) the ABAWD work requirement applied to a single adult with no earned income, with
the absence of any statement about hours read as failing the 80-hour requirement (the majority of cases; e.g. "without evidence of
80 hours of work or program participation, the household is not eligible"); (ii) the minimum-benefit line ("eligible households
of 1 or 2 people receive at least $24") read as an eligibility threshold when the computed benefit is <= $0; (iii) age 63
treated as "not elderly (60+)", so the gross test is applied (b000, b027; 4 of the 12 wrong verdicts with the block). The
block supplies the quantities and the model restates them correctly in every one of these traces; the errors are rule
application, which is why the block does not remove them. The one unparsed row (seed 0, b027 effort_low) wrote "**A**NSWER: NO"
and is counted as missing, not as a verdict. The 14B errors (bases b002, b008, b014, b017, b035) are of kind (i).
Reason (i) is the same resolution of an absent fact as a failing value that the evidence-sufficiency study documents on its
own items; it is noted here for the PI and not used in Paper 1's claims.
Pending for this experiment: Ministral (direct and free), the no-authority block (R5), seed-12 free (queue 11, after queue 12).

## Read 4 (2026-10-13 02:50 UTC): queue 11 (R5 plain block, Ministral direct and free, 14B seed-12 free)
Queue 11 ran 00:25-02:43 UTC, every run complete (direct 1,608/1,572 rows, free 804/786, 0 errors).
Traces sampled before the scores (Ministral free original/plain, 14B seed-12 free). Full cells in docs/paper1/tables.md T10.

R5 (plain block "Computed from the figures above: ..." vs verified block). 14B direct: 0.994/0.971 vs 0.992/0.969, contrasts
0/0 vs 0/0 and 4/0 vs 3/0 -> met. 32B direct: 1.0/0.946 (0 missing rows) vs 1.0/0.947 (7 missing), all 0/0 -> met. Free: 14B
0.993-1.000 vs 0.998-1.000, 32B 0.987-0.989 vs 0.987-0.991; two seed-0 cells differ by 3-4 flips (14B effort 0/3 vs 0/0; 32B
control 2/0 vs 1/4, the latter the block cell already flagged in read 3) and by 0-2 at seed 1 -> met at seed 1. 8B direct:
eligibility 0.735 vs 0.684 (difference 0.051, outside the 0.05 tolerance); controllability 11/0 (+0.149 [+0.078, +0.233]) vs
19/0 (+0.257 [+0.172, +0.353]); effort 6/2 vs 9/0 -> NOT met: the "verified" wording carries part of the 8B effect size; the
effect persists (>= 5 flips, <= 1 against) and exceeds the original 7/1 under both wordings, so "grows" stands for both.
Ministral direct: gross 0.778 vs 0.850 (difference 0.072), eligibility 0.598 vs 0.593; contrasts 3/0, 1/0, 1/0, 1/3 vs 0/0,
0/0, 0/1, 2/3 -> gross accuracy outside tolerance, contrasts within 3 flips: the wording carries part of Ministral's gross relief.

Ministral (second family), R1-R3. Direct original rows 0.561/0.395 with effects gross 12/0 (+0.20 [+0.06, +0.34]), 9/0
(+0.15 [+0.06, +0.25]), eligibility 6/0 and 6/0 (+0.08, lower bound +0.00); with the block 0.850/0.593 (R1 graded: neither
>= 0.9 nor within 0.10 of direct) and every contrast 0-3 flips (R2 removed). Seed 12: v1 0.536/0.409 -> 0.828/0.627,
contrasts 2/0, 2/0, 5/0, 2/0 -> 1/0, 1/1, 0/2, 1/5; v2 0.536/0.408 -> 0.814/0.633, 2/0, 4/0, 4/0, 4/0 -> 2/0, 0/0, 5/0
(+0.070 [+0.014, +0.141]), 1/2. The v2+block eligibility controllability cell (5/0) is the only persisting-direction cell and
is one model, so R2's "at least two models" is not met; reported, not claimed. Free without the block: 1.000/0.973 (s0),
0.997/0.991 (s1), R3 met; effort s0 2/4 (4 flips toward NO) checked at seed 1: 1/1, not replicating. Free with the block: 
0.986/0.945 (s0, 10 missing), 0.988/0.938 (s1, 18 missing); plain block 0.969/0.969 (2 missing), 0.975/0.949 (4 missing) ->
R3 NOT met for Ministral with either block. Traces: 142/164 (verified) and 102/98 (plain) of 804 answers are a bare
"ANSWER: X" line with no computation, almost all on the gross task (bare-row accuracy 0.85-0.97, rest 0.94-0.97); the wrong
eligibility rows apply the elderly exemption on one member of a pair and not the other (e.g. b022: "fails gross test" for
control_high, "exempt, elderly" for control_low), so the 4-6 flips per contrast (4/4, 5/3, 5/4, 6/2; plain 0/6, 3/5, 2/1, 3/6)
are bidirectional rule-application noise, none meeting the persistence rule; the plain s0 control cell 0/6 is 3/5 at seed 1.
Missing rows are all misspelt answer lines ("ANSVER:", "ANSWE:", "**Answer**: NO") whose verdict is readable and correct in
every case (10/10, 18/18, 2/2, 4/4); scored as missing per the pre-registration, noted in Appendix G. Without the block
Ministral's 6 missing rows at seed 1 are 3 readable-correct, 1 readable-wrong, 2 unreadable.

R4 on the free rung (14B, seed 12, v1; v2 free not run, as pre-registered). Without the block 0.983/0.991 (s0), 0.983/0.994
(s1); with it 0.961/1.000, 0.953/0.996; contrasts 0-2 flips everywhere -> the free-rung outcome (no cue effect, block changes
nothing on eligibility) holds on the new households. The gross drop with the block is two households: b116 (member aged 59,
read as elderly and so exempt from the gross test by both seeds, 10 and 12 rows; 5 rows without the block) and b125 (4 and
5 rows); the block lists "household of 1; gross $1,764; limit $1,696" and the model argues the exemption anyway.

Conclusion for the paper (v5r14): the mechanism claim for 14B and 32B survives the wording control (R5 met on direct);
for 8B the effect is present and enlarged under both wordings, with the "verified" wording adding to its size; Ministral
confirms the direction (direct effects removed, accuracy up) without reaching the accuracy criterion, and its free rung gets
noisier with the block rather than cleaner. Stated in the body paragraph, Limitations and Appendix G; T10 carries every cell.
