# External sources used by this paper

| Local path | Source | Use and redistribution |
| --- | --- | --- |
| `snap_params/snap-fy26-incomeEligibilityStandards.pdf` | USDA FNS FY2026 cost-of-living adjustments, https://www.fns.usda.gov/snap/fy-2026-cola | Federal income limits; included as a U.S. federal work |
| `snap_params/snap-fy26maximumAllotments-deductions.pdf` | Same FNS source | Allotments and deductions; included as a U.S. federal work |
| `candidates/snap_qc_fy2024/qc_pub_fy2024.csv` | SNAP Quality Control public-use data, FY2024, https://snapqcdata.net/datafiles | De-identified household structures and sampling weights; download separately |

For full item regeneration, download the FY2024 CSV archive, extract `qc_pub_fy2024.csv` into the path above, and run `src/gen/make_rules_pilot.py` as documented in `docs/REPRODUCING.md`. The source archive and CSV are not included in the current tree or anonymous release. Generated test items and the parameter PDFs are included, so table reproduction does not need the QC download.

The experiment used the FY2024 release recorded as revised on 2026-08-18. Earlier repository history included the source ZIP; it was removed from the current tree to match the paper's distribution statement.
