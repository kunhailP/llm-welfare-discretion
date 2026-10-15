# Design and analysis provenance

This repository contains the paper's items, outputs and methods. Earlier unrelated pilot designs are retained in Git history; the full decision log (`docs/decisions.md`), the results notes (`docs/results/`) and the literature notes (`lit/`) stay in the repository and are not part of the release.

## Dated records

- `design/design_B_rules.md`: original task design; retained as a historical document, not a description of every final analysis.
- `protocols/decision_records.md`: edited excerpts for the replication rule and follow-up controls (wording neutralised; dates, rules and numbers unchanged; the rows as originally written are in Git history). The original log rows include later status updates. The manuscript explicitly describes the initial replication criterion and trap exclusion as post hoc.
- `paper1/computed_burden.md`: initial computation-supply plan, dated addenda, interim observations and final observations. Some additions were made after early runs; the dates and ordering remain in the file. Before submission the status notes written while runs were pending were removed and a few phrases reworded; the design, rules, amendments and reads are as recorded, and the earlier versions are in Git history.
- `paper1/confirmation_study.md`: confirmation plan, final sample specification, execution status and reported outcomes.

These are project records, not independently timestamped registry registrations. The manuscript calls the later plans pre-registered because they were recorded before their specified runs; it does not apply that description to the initial exploratory criterion. Pre-run records have been left unchanged during submission cleanup, including assumptions or wording that the final results qualify.

## Source and result integrity

Submission cleanup does not change the rule implementation, experimental prompts, generated items, raw model outputs or model revisions. It corrects the manuscript and documentation to match them. In particular, the seed-12 household count and the plain-prefix manipulation should be read from the shipped inputs and generator, rather than inferred from shorthand in the historical notes.

The initial gold cross-check covers income computations under the documented PolicyEngine settings. ABAWD, positive medical/dependent-care/child-support deductions and asset boundaries rely on the hand-computed tests. Neither the cross-check nor the synthetic cases validate a production benefits system.
