# Source design v0.1 (ChatGPT draft, received 2026-10-05)

The user's v0.1 design (Korean prose + JSON spec `welfare_naacl_research_spec_v01.json`)
was pasted into the session. The JSON was TRUNCATED mid-way (ends inside
`operationalization.unsupported_claims`), so the original file is NOT in this hub.

- [ ] Copy the full `welfare_naacl_research_spec_v01.json` into `docs/` (original lives in the ChatGPT sandbox).

Key fixed points of v0.1 (kept unless a decision in `docs/decisions.md` overrides):
- Working title: Separating Material Need from Deservingness in Language Model Evaluation
- Core 2x2 per base: resource state (shortfall 600/1000 vs sufficient 1200/1000) x job-search activity (8 vs 1 applications)
- 4 independent queries per profile: direct / definition / extraction(JSON) / deservingness 0-100 (separate conversation)
- Formats: numeric totals, itemized, number-free textual (40 bases each)
- Pilot 50 bases x 4 = 200 (dev forever); main 120 new bases x 4 x 2 paraphrases = 960
- Controls: resource change, neutral detail (480), activity removed (240), 10% duplicate runs, optional incomplete-info probe
- Primary estimand: P(SHORTFALL | low activity) - P(SHORTFALL | high activity); truth = 0; cluster bootstrap by base_id (2000)
- Models: Qwen3-8B, Qwen3-14B, Ministral-3-8B (BF16), Qwen3-32B-AWQ; temp 0; Qwen thinking off
- Two independent human item reviewers, blind to model outputs
- Deadline stated: ARR Oct 12 AoE (= KST Oct 13 20:59) -- to be verified (lit agent)
