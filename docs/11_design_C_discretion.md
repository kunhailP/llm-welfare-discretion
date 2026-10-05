# Design C: deservingness enters through discretion, not computation (draft, 2026-10-05)

## Why
- Rules pilot, thinking off: cue effects exist, but on near-chance verdicts (docs/10 section 2).
- Thinking on, Qwen3-14B: income verdicts 100% correct and cue effects exactly 0 (docs/10 section 5).
- So for rule-computable determinations, the interference story does not survive reasoning at 14B.
- Political science (street-level bureaucracy, Lipsky; deservingness heuristics, van Oorschot's CARIN): human
  deservingness acts where the rule leaves judgment. Welfare law has such points: ABAWD discretionary
  exemptions, good cause, hardship.

## Core question (one problem, in depth)
When the rule hands an LLM discretion over a welfare decision, do legally irrelevant deservingness cues
(effort, controllability) move the decision, how much are they worth in dollars of need, and does an explicit
legal instruction to ignore them remove the effect, with and without reasoning?

## Design (pilot: data/discretion_pilot, src/gen/make_discretion_pilot.py)
One legal situation: a non-exempt ABAWD adult, 72 h in March 2026, 3 countable months used, so rules alone say no.
Question: grant a discretionary exemption?
| factor | levels |
| --- | --- |
| standard (rule-boundness) | enum_no (gold NO), enum_yes (gold YES), open (caseworker judgment on serious hardship), open_need (open + "only financial hardship; reason for job loss, job-search effort, other circumstances must NOT be considered") |
| need | money left after rent + utilities: +$200 / +$50 / -$100 / -$250 |
| cue | none, effort hi/lo, controllability hi/lo, valence_neg (non-moral) |
| base | 40 (name x age x utilities), the cluster unit |
| inference | first-token both orders (4 models); thinking (14B, 32B, 20 bases) |

## Measures (src/eval/score_discretion.py)
- Competence: enum accuracy, and cue effects there (should be 0).
- Need sensitivity: slope of P(grant) on need ($100 steps).
- Cue effect (cue - none, hi - lo), cluster bootstrap over bases.
- **Dollar equivalent**: cue effect / need slope, i.e. how many dollars of monthly shortfall a cue is worth.
- Prohibition effect: cue effect in open_need vs open (does a legal instruction remove it?).
- Reasoning: the same contrasts in thinking mode; whether the reasoning cites the cue.

## What would make this the paper
- The 2x2 core: computation (rule-bound vs discretionary) x inference regime (direct vs reasoning), with dollar
  equivalents, a scale curve, and the prohibition test.
- Expected pattern to test (not assumed): rule-bound -> no cue effect under reasoning; discretionary -> cue effect
  that survives reasoning and is cited in the reasoning (CoT faithfulness), and is only partly removed by the prohibition.

## Known gaps before scaling
- Single legal situation; add a second discretion point (good cause for missing work hours) to show generality.
- The prohibition text is ours; anchor wording in real guidance (7 CFR 273.24 discretionary exemptions; state manuals).
- No human baseline (user decision); the human side is cited from the deservingness literature.

## Result 1: v1 discretion pilot, Qwen3-14B first-token (2026-10-05)
results/discretion_pilot/score_qwen3-14b.json (probability) and score_logit_qwen3-14b.json (log-odds; src/eval/score_discretion_logit.py).
- Decisions: enum_no 1.00 / enum_yes 1.00 correct. **Open standards: P(grant) = 0.00 in every cell**, even when rent exceeds income by $250. No decision ever flips, so in probability space every effect is 0.
- Log-odds (YES - NO, mean of orders) still move. Mean at cue=none: open -15.4, open_need -15.9 (enum_no -22.5, enum_yes +14.6).
  | contrast (dlogit [95% CI]) | enum_no | enum_yes | open | open_need |
  | --- | --- | --- | --- | --- |
  | need slope per $100 less left | 0.07 | -0.03 | 0.31 | 0.34 |
  | effort hi - lo | +0.12 | +0.55 | **+1.87 [1.78, 1.95] (~$607)** | **+1.71 (~$498)** |
  | control hi - lo | -0.20 | -0.10 | -0.28 | +0.32 |
  | valence_neg - none | 0.00 | 0.00 | +2.01 | +1.51 |
- Reading, with caveats:
  - Under discretion the effort contrast is 3-15x its size under enumerated rules, and the prohibition
    ("job-search effort must NOT be considered") cuts it by only ~9%. That is the Design C pattern.
  - But all of it is deep in the tail (P(grant) ~ 1e-7). A shift from -16 to -14 log-odds changes no decision.
    Tail log-odds also move in the rule-bound enum conditions, so tail sensitivity is partly generic.
  - cue - none contrasts are confounded: the `none` sentence (long residence, same landlord) signals stability,
    and the non-moral valence_neg moves the odds as much as effort_high. Only hi - lo contrasts are clean.
  - Controllability goes the "wrong" way under open (-0.28) and flips sign under open_need: no stable effect.
- Consequence: the open standard as worded is a floor for 14B (direct answers). Decision-level evidence must come
  from thinking runs (v2 queued) or from a standard whose baseline sits near the decision boundary.

## Result 2: psychometric set, Qwen3-14B first-token (2026-10-05)
results/design_c_psych/score_ft_qwen3-14b.json. The polarity flip exposes a response prior:
- P(YES) for "does the agency GRANT?" is 0.00-0.01 (serious, basic) and 0.16-0.32 (food); P(YES) for "does the
  agency DENY?" is 0.01-0.06. **The model says NO to both opposite questions**, so pooled P(grant) ~ 0.49 is an
  artifact (pos ~ 0, neg ~ 1). Polarity gap in P(grant): -0.58 to -0.95.
- Need moves P(YES|grant) only under the most lenient wording (food: 0.16 at +$250 -> 0.31 at -$600); no curve
  crosses 0.5, so no PSE is defined.
- Reading: with direct answers, 14B does not make the discretionary judgment at all; it answers NO to whatever is
  asked. The v1 "always deny" floor (Result 1) was this prior, not a judgment. Discretion has to be measured with
  generated answers (thinking ladder, queued). This is also a methods point for the paper: without the polarity
  flip, the pooled first-token numbers would have looked like a well-calibrated 50/50 judge.

## Result 3: psychometric set, Qwen3-32B-AWQ first-token + cue effects in both models (2026-10-05)
results/design_c_psych/firsttoken/qwen3-32b-awq.jsonl (0 missing). Numbers below: P(YES) per question, mean over bases, cues, orders.
- 32B, unlike 14B, gives polarity-consistent answers: food standard P(YES|grant?) 0.69-0.78 vs P(YES|deny?) 0.09-0.13;
  serious 0.29-0.40 vs 0.21-0.25. **The standard's wording moves the verdict (food > basic > serious).**
- **Need does not.** P(YES|grant?) is flat from +$250 left over to -$600 shortfall and drops slightly (~0.07) at the
  surplus->shortfall step (e.g. food/no: 0.78 at +$50, 0.69 at -$50). No curve crosses 0.5 in the right direction, so no PSE.
- **Cue effects are an acquiescence artifact.** Mean log-odds(grant), cue minus base, split by polarity:
  14B prohibit=no: grant? +0.55..+2.52 for every cue (incl. effort_low and the non-moral valence_neg);
  deny? -0.09..-0.81. Every added sentence raises P(YES) to whichever question is asked; it does not move the
  grant/deny decision. 32B shows the same sign pattern, smaller (|effect| <= 0.8). Pooled over polarity these
  look like cue effects; split, they are a yes-bias shift. The prohibition clause does not remove it.
- Reading: first-token answers on discretion respond to the standard's surface wording and to added text, not to
  need or to cue meaning. This is a methods result for the paper (polarity flip + PSE are needed to see it) and
  confirms that H1-H3 must be tested on generated (thinking) verdicts, as pre-registered (docs/13).

## Result 4: remaining first-token runs (psych 8B / Ministral; v2 all 4 models) (2026-10-05)
Scores: results/design_c_v2/firsttoken/score_<model>.json (0 missing rows in every run).
Psych set:
- Qwen3-8B: answers NO to "deny?" almost always (P(YES) 0.01-0.30). On "grant?" under basic/serious there is a small
  slope in the right direction (P(YES) 0.07-0.17 at surplus -> 0.16-0.32 at shortfall); never crosses 0.5. Cue effects
  are the same yes-bias as 14B/32B (valence_neg +1.5 / +3.7 logits on grant?, -0.7 / -1.2 on deny?).
- Ministral-3-8B: flat in need (all cells within 0.05). Its cue effects keep the same sign in both polarities, i.e. a
  real but small grant shift: effort_high - effort_low ~ +0.3 to +0.5 logits, but the non-moral valence_neg is as large
  or larger (+0.2..+0.8).
v2 set (cue = none rates):
- Enum standards (gold): 14B and 32B 100% in both polarities; Ministral 89-100%; 8B fails the neg polarity of enum_no
  (says NO to "deny?" when gold is deny). **When the rule lists the facts, 14B/32B follow it; when the standard is open,
  the same models do not respond to need** (open/open_need slope <= 0.03 per $100, sign negative for 14B/32B).
- Hours task: 14B correct at 72h, polarity-inconsistent at 88h (grant? 0.98 correct; deny? 0.18 correct); 32B grants at
  72h (acc 0.13 / 0.05; 72 < 80 required hours), correct at 88h; 8B and Ministral deny at 88h. Missing hours (gold REQUEST):
  REQUEST is ~0 for 8B/14B, 0.07 Ministral, 0.40 (grant?) / 0.16 (deny?) for 32B. H3 cannot be tested first-token.
- Cue contrasts (polarity-pooled) are all |d| <= 0.09 in P(grant); none is interpretable on these floors.
Reading: across 4 models and both sets, first-token is reliable only for the enum (explicit-list) standards. The
enum-vs-open contrast is itself relevant to the paper (explicit rule followed; open standard falls back to a default),
but every H1-H3 test goes to the thinking runs as pre-registered.
