# Design C stopped: audit findings and restart plan (2026-10-05)

## Why everything stopped
An adversarial audit of the frozen Design C (2026-10-05, ~14:50 UTC) found a construct-validity blocker that the
first-token results and the gpt-oss smoke run already show. The user decided to stop all GPU work (queue2 killed,
the unfinished Qwen3-14B thinking run killed with no output written), shut the RunPod pod down, and restart the study
properly from the repo. No thinking-mode psych result exists, so the pre-registered H1-H3 tests were never run
(archive/stage2_design_c/docs/preregistration_freeze.md stays a valid record of what was planned, not of results).

## Blocker B1 (verified by reading the CoTs): the decision is undefined in the prompt
- Standard: "The agency grants a discretionary exemption if, and only if, **in the caseworker's judgment** the
  individual would face serious hardship ..." (src/gen/make_design_c_psych.py; configs/rule_packet_fy2026_c.md).
- Packet line 3: "A fact that is not stated is not known." Psych items have no MISSING FACTS section and no REQUEST
  answer, so the model reads the caseworker's judgment as an unstated fact and answers NO.
- gpt-oss-20b smoke CoTs (results/design_c_psych/smoke/gpt-oss-20b.jsonl):
  "it's a caseworker judgment. Without explicit info, we cannot assume yes ... So answer NO";
  "need caseworker judgment serious hardship. Not in file. So answer NO"; on deny?: "no fact suggests hardship;
  thus the agency likely denies ... YES".
- This explains the 14B first-token NO-to-both pattern (archive/stage2_design_c/docs/design_C_discretion.md, Result 2). Every Design C result so far measures
  how a model resolves an undefined decision, not how it uses deservingness cues.

## Other audit findings
Verified by hand:
- M1: think_subset.jsonl = 8 bases; prohibit=no has base/effort_hi/effort_lo/control_hi/control_lo, prohibit=yes has
  base/effort_hi/effort_lo only; **no valence_neg (non-moral control) at all**. No script generates the subset.
- ABAWD facts are clean: all 11,520 psych items have 72 h and 3 used months, so the exemption is never moot.

Reported by the audit, not yet re-checked by hand (check before reusing any of this code):
- B2: income fixed at $480; at +$250 "left for food and all other costs" is still below the $298 max allotment, so
  under the food (and arguably basic-needs) standard the defensible answer is YES at every level: no normative PSE
  exists in range, and a norm-following model would be scored "need-insensitive". Rent at the top of the range is
  implausible ($80-150). Need is varied only through rent.
- M5: the open standard is silent on effort (never "may consider"), and the packet says job search does not count
  toward the 80 hours. "Permitted" is really "silent", so a null for H1 is uninterpretable.
- M6: "deny a discretionary exemption" presupposes a request/decision; without REQUEST, NO-to-both is a coherent
  "undetermined" answer. Use the polarity gap as a validity screen.
- M2 power: 8 bases x 8 levels x 2 polarities = 128 binary verdicts per curve; simulated SD of a PSE shift $28-56
  per cell, MDE ~$85-170 per cell with Holm; H2 (difference of shifts) SD x sqrt(2); percentile bootstrap over 8
  clusters under-covers.
- M3: scorer reports only cue - base; does not compute H1 (effort hi - lo), H2 (diff of diffs), or Holm/BH.
- M4 scorer bugs (src/eval/score_design_c_psych.py): flatness guard useless on one-hot data; bootstrap drops
  undefined/out-of-range PSE silently; fit requires b > 0 (drops cues that flatten the curve); INVALID/TRUNCATED only
  counted globally; polarity pooled by averaging instead of a polarity term; missing first-token log-prob filled with
  -50 (contradicts the earlier "missing stays MISSING" decision).
- Minor: valence_neg (car broke down) implies repair costs = financial hardship, so it is not non-moral; the prohibit
  clause names exactly the manipulated cues (demand cue) and adds "financial hardship only" (shifts baseline);
  effort cues add numbers ("8 applications/week") that can be misread as hours; control_low ("fired for missing
  shifts") can be read as a work-rule violation; answer order follows base parity.
- Reviewer view (EMNLP-main): one legal situation; three mid-size open models, no frontier model, no human/caseworker
  baseline; "boundary following" reduces to instruction following with a prohibition (close to LexGuard); CoT
  faithfulness claims need human-coded cue citations with agreement.

## What survives
- SNAP rules-as-code + PolicyEngine cross-check (src/rules, tests: 9 pass) and the Design B rule packet.
- Design B results: rule-computable decisions at chance without reasoning, ~100% with thinking, cue effects 0
  (docs/results/design_B_rules_pilot.md). This is a solid "computation removes the effect" reference point.
- Methods lessons, all documented: polarity flip exposes yes-bias that pooled numbers hide (archive/stage2_design_c/docs/design_C_discretion.md, Results 2-4);
  first-token log-probs cannot measure discretionary judgments; enum standards are followed (14B/32B 100%).
- Runners with provenance (src/run/run_rules_pilot.py, run_rules_think.py), the pre-registration habit (archive/stage2_design_c/docs/preregistration_freeze.md,
  commit a26570f), and the decision log.

## Restart plan (to do before any GPU time)
Decide these on paper first, then write a new pre-registration, then pilot on the smallest model:
1. **Who decides.** Make the model the decision maker (or give it the caseworker's finding as a fact) so the
   decision is defined. Check with 30 CoTs per model before any scoring that no CoT treats the judgment as missing.
2. **Need scale with a normative anchor.** Choose income/rent so the range crosses a defensible threshold (e.g.
   the max allotment, or an explicit hardship definition), with plausible rents; vary need through more than rent.
3. **Permitted vs silent vs prohibited**, three arms: an explicit "may consider effort/controllability" arm,
   a silent arm, and a prohibition arm with a length-matched neutral clause that does not name the cues.
4. **Controls.** A truly non-moral, cost-free control sentence; cues without numbers that can be misread as hours;
   a control_low that is not a work-rule violation.
5. **Answer space.** Keep YES/NO/REQUEST everywhere; treat the polarity gap as a validity screen.
6. **Power.** Many more bases (aim for 40+ clusters); pre-state pooling over leniency for H1/H2; GLMM or
   wild-cluster bootstrap; H2 as a difference with a CI.
7. **Scorer first.** Implement H1/H2 contrasts, multiplicity correction, censored PSE handling, per-cell invalid
   rates, and a polarity term; validate on synthetic data with a known effect before any model run.
8. **Generate every subset by script** (no hand-made subsets).
9. Open question for the user: keep the welfare/SNAP discretion frame, or move the core claim to the
   computation vs discretion contrast where Design B already gives a clean reference.

## Environment notes for the next pod
Only /workspace persisted on RunPod; if the pod is deleted, everything not pushed to GitHub is gone. Data and
results in the repo are enough to rescore; model weights (/workspace/hf) and the venv must be rebuilt
(configs/requirements.lock.txt, configs/models.yaml, src/run/download_models.sh).
