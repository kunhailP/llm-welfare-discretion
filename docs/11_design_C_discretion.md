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
