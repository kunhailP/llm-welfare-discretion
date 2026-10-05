# Paper outline v0 (2026-10-05) — central claim still undecided

Working title: Separating Material Need from Deservingness in LLM-Based Measurement

1. Introduction (1p): LLMs as measurement tools in social science / welfare contexts; FairFund shows allocation gaps but cannot tell judgment from mis-measurement; question: with need fixed and computable, do LLM need verdicts track facts? 3 contributions (fixed after the branch below).
2. Background (0.5p): NICER/CARIN need vs deservingness; LLM annotation validity; prompt/label sensitivity.
3. Measurement framework (1p): need claim = facts -> gap -> verdict, deservingness cues separate; metrics: directional error, spurious group gap, threshold curve; sequence-level label scoring (report the first-token pitfall).
4. Data (1.5p): (1) controlled templates for mechanism; (2) SNAP QC FY2024 real households + official-rule gold; (3) GoFundMe natural probe; human review + agreement.
5. Exp 1, where it breaks (1.5p): question form x context x fact-presentation ladder.
6. Exp 2, does it change conclusions (1p): spurious group gaps on SNAP households.
7. Exp 3, mitigation (0.5p): structured restatement, yes/no, extract-then-compute.
8. Discussion, Limitations, Ethics (1p).

## Branch decided by the scale diagnostic (Qwen3-14B, Qwen3-32B-AWQ, then others)

| Outcome | Central claim | Venue form |
| --- | --- | --- |
| Unemployed-specific failure recurs in other models | Some LLMs condition factual need verdicts on unemployment as a social category, changing measurement conclusions | Long, CSS track |
| Causes differ by model (context / order / label) | LLM need-measurement errors come from question form, not comprehension; always toward "need"; structured facts remove them | Evaluation-method contribution; short paper may fit better |

Pending user decision: SNAP gold = gross test / net test / both.
