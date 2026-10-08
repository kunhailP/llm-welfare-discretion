# paper/ — Paper 1 (NAACL 2027 via ARR Oct 2026), short paper

- main.tex: the draft (anonymous review mode). Numbers come from docs/paper1/tables.md and docs/results/design_B_rules_pilot.md;
  regenerate the tables with `python src/eval/make_paper1_tables.py` before editing numbers by hand.
- rule_packet_fy2026.md: copy of configs/rule_packet_fy2026.md for Appendix A (re-copy if the packet changes).
- references.bib: copy of lit/references.bib; added.bib: citations not in lit/.
- acl.sty, acl_natbib.bst: official ACL style files (github.com/acl-org/acl-style-files, downloaded 2026-10-08). Do not edit.
- archive/main_v0.tex: v0 before the blind reviews (docs/paper1/blind_reviews.md).
- Build: `make` (latexmk). Page limit: 4 pages of content for review; Limitations, Ethics, References and appendices do not count.
