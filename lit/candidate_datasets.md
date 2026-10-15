# Candidate external datasets: ecological validity, human baselines, rule-grounded gold

Compiled 2026-10-05 for the NAACL 2027 (ARR, deadline 2026-10-12) submission.
Weaknesses addressed: **(a)** naturally occurring text, **(b)** human baselines, **(c)** real policy rules.

Verification legend:
- **V** = page/API/file opened by us this session.
- **P** = partially verified (some pages blocked; the gaps are stated).
- **U** = unverified claim (search snippet only).

Local samples go in `data/external/candidates/<name>/`. We only downloaded files with a clear open license (CC0, CC BY-NC, US public domain). For anything with an unclear license we read the documentation only.

---

## Ranked top 5 (overall)

| # | Candidate | Fixes | License | 5-day effort | Why |
|---|---|---|---|---|---|
| 1 | **USDA SNAP Quality Control public-use microdata, FY2024** | (c), partly (a) | US federal public-use data (public domain; no license text on site) | 1.5–2 d | 44,891 real, de-identified households. Each has gross/net income, rent, shelter deduction, assets, employment status per person, and FNS's own **pass/fail flags for the gross, net and asset tests** (`FSGRTEST`, `FSNETEST`, `FSASTEST`). We can render real households into text, take gold from the agency, and add deservingness cues as controlled perturbations. This is the strongest single answer to "templates are unrealistic" plus "no real rules". Downloaded and inspected. |
| 2 | **USDA FNS SNAP eligibility page (FY2027 parameters) + PolicyEngine-US rules-as-code** | (c) | FNS page: US gov work. PolicyEngine-US: **AGPL-3.0** (code only; we only run it) | 1 d | The official gross test (130% FPL) and net test (100% FPL), deductions and asset limits for Oct 2026–Sep 2027, plus an open engine that recomputes `meets_snap_gross_income_test` / `meets_snap_net_income_test` / `is_snap_eligible`. We installed it and ran it. This turns SHORTFALL/SUFFICIENT into "eligible under SNAP rule X", a label reviewers cannot call arbitrary. |
| 3 | **"All in this together?" COVID deservingness vignettes (Harvard Dataverse LPHMB7)** | (b) | **CC0 1.0** | 1 d | 2,295 Canadian respondents × 4 vignettes = 9,180 human allocations (study 1). Factors include **vignette income ($30k–$120k)** and **employment status (employed / reduced / unemployed / unemployed due to pandemic)**. Study 2 adds 0–10 deservingness ratings. This is a direct human analogue of our "unemployed context" manipulation: do humans also let employment status override income? Our raw means suggest they do (see entry). Downloaded and inspected. |
| 4 | **MDCC GoFundMe corpus (Xu, Li, Zhou, CIKM 2023; Zenodo 8287320)** | (a) | **CC BY-NC 4.0** ("solely for academic research") | 1.5 d | 14,961 real campaign narratives. 1,344 are "Financial Emergency" and 2,526 "Emergency". About 998 contain both a $ amount and rent/bills/income/job-loss language. Each has goal and raised amounts. Clear license and a peer-reviewed release; the best licensed source of natural need narratives with extractable amounts. Downloaded and inspected. |
| 5 | **Knotz, Gandenberger, Fossati & Bonoli (2022) NICER/CARIN replication (OSF 37me5)** | (b), theory anchor | **No license set on OSF** (`node_license: null`) | 1 d once permission is granted | The canonical source of our framework. 3 experiments: US Qualtrics N=360, US MTurk N=334, Germany N=400, 8 vignettes each, outcome 0–100% salary replacement. Variables include `vig_need`, `vig_effort`, `vig_control`, `vig_attitude`, `vig_recip`, `vig_ident`. **Email the authors for permission** before using the microdata. Their published coefficients can be cited regardless. **Caveat:** in this experiment need = number of dependents, not a resource–cost gap. |

Honourable mentions:
- **Hsieh & Kline 2025** (CC0): income × effort crossed numerically, with real transfers.
- **Random Acts of Pizza**: classic NLP need narratives with outcomes, but no license and usernames included.
- **NY OTDA fair-hearing decision archive**: real SNAP/public-assistance adjudications, reproduction allowed with attribution, but we could not fetch a sample PDF.

Suggested 5-day package: #1 + #2 give the "real households, real rules" study. #3 (plus Hsieh–Kline) gives the human baseline. #4 gives the ecological probe (about 200 MDCC narratives, with facts extracted by 2 annotators and judged against #2). Cite #5 for theory and request its data.

---

## A. Naturally occurring need narratives

### A1. MDCC: Multimodal Dynamic Dataset for Donation-based Crowdfunding Campaigns  [V]
- **URLs opened:** https://zenodo.org/api/records/8287320 (record), https://github.com/Jiayang-L1/mdcc (README)
- **Maintainer / venue:** Xovee Xu, Jiayang Li, Fan Zhou. CIKM 2023, pp. 5417–5421, doi:10.1145/3583780.3615124
- **Size / format:**
  - 14,961 campaigns: `raw_data.csv` 75 MB, JSON/pickle variants.
  - Photos (9.5 GB) not needed.
  - 18 columns: `campaign_id, category, goal, launch_date, country, city, raw_description, clean_description, cover_photo, num_photo_main_body, raised, donation_time, donation_amount, comment_time, comment_cor_time, comment_text, update_time, update_text`.
- **License (exact):** Zenodo `cc-by-nc-4.0`. README: "Creative Commons Attribution Non Commercial 4.0 International. This dataset is intended solely for academic research and should not be utilized to develop services or algorithms that promote unfair or unethical practices." (The GitHub repo's license field shows "Other/NOASSERTION"; the data license is the Zenodo one.)
- **Access:** direct download. **Sample saved:** `data/external/candidates/mdcc_gofundme/raw_data.csv`
- **Our inspection:**
  - Categories: Memorial 4,632; Medical 3,580; Animals 2,879; Emergency 2,526; Financial Emergency 1,344.
  - 98% from the US. Median description length 167 words.
  - 15.5% contain a `$` amount; 30.7% mention rent/bills/income/unemployment/eviction; 998 contain both.
- **Use:**
  - (a) Sample about 200 Emergency / Financial Emergency narratives. Two annotators extract monthly income, essential costs and amounts, then label need from the gap (or SNAP gross/net test where household size is given) and label deservingness cues (job loss/effort, blame, reciprocity, identity).
  - Then test whether LLM need labels track the extracted gap or the cues, using the same SHORTFALL/SUFFICIENT vs yes/no vs structured-facts conditions.
  - `raised/goal` is a weak, noisy proxy for donor judgment.
- **Effort:** 1.5 d (filter + annotation guide + 2×200 annotations + run).
- **Risks:**
  - Real names of beneficiaries, sometimes children, plus medical details. Pseudonymize in the paper and don't quote verbatim narratives without paraphrase.
  - NC license is fine for academic use.
  - Data was scraped from GoFundMe; ToS risk sits with the releasers, but mention it.
  - IRB: secondary analysis of public data. Check whether your institution needs an exemption determination.

### A2. Random Acts of Pizza (RAOP)  [V docs only; data not downloaded]
- **URL opened:** https://cs.stanford.edu/~althoff/raop-dataset/
- **Maintainer / venue:** Althoff, Danescu-Niculescu-Mizil, Jurafsky, ICWSM 2014 (Stanford)
- **Size / format:**
  - 5,671 requests from r/Random_Acts_Of_Pizza (Dec 2010–Sep 2013), JSON.
  - Fields: `request_text`, `request_text_edit_aware`, `request_title`, outcome (`requester_received_pizza`), `giver_username_if_known`, requester account/karma/activity stats, timestamps, up/downvotes, `in_test_set`.
  - The release includes the paper's narrative lexicons (desire, family, job, money, student).
- **License (exact):** none stated. The page says only "Please cite this paper and send us a note if you use this resource in your work." The license is **unclear**, so per instructions we did not download.
- **Access:** direct tarball.
- **Use:** (a) a classic NLP need-narrative corpus with built-in deservingness cues (the job/money/student narratives) and a real human outcome (received pizza). Financial facts are sparse ("$3 until payday"), so this is suited to cue-sensitivity analysis rather than gap-based need gold.
- **Effort:** 1 d.
- **Risks:**
  - No license.
  - Contains Reddit usernames (requester and giver); strip them.
  - Reddit content terms; Reddit's Data API terms could not be opened from our environment (U).
  - Recommend emailing the authors for written permission.

### A3. Kiva: Kaggle "Data Science for Good: Kiva Crowdfunding"  [V]
- **URLs opened:**
  - Kaggle API metadata: https://www.kaggle.com/api/v1/datasets/view/kiva/data-science-for-good-kiva-crowdfunding
  - https://rdrr.io/github/m-clark/noiris/man/kiva.html
  - Kiva developer page: https://www.kiva.org/build/data-snapshots
- **Maintainer:** Kiva (uploader Chris Crawford), 2018, version 5.
- **Size / format:** 233 MB of CSVs. `kiva_loans.csv` has `id, funded_amount, loan_amount, activity, sector, use, country, region, currency, partner_id, term_in_months, lender_count, borrower_genders, repayment_interval, ...`
- **License (exact):** Kaggle metadata `licenseName: "CC0: Public Domain"`.
  - Full loan *descriptions* are only in Kiva's own snapshots (`http://s3.kiva.org/snapshots/kiva_ds_{json,csv}.zip`).
  - The snapshot page states no license; it links to Kiva developer Terms of Service, which we did not open (U). The page says snapshots are "generated intermittently".
  - Kiva GraphQL returned 403 to us.
- **Use:** weak fit. These are productive microloans ("to buy stock for her shop"), not consumption need, and are mostly outside the US. Only `use` (one sentence) is CC0.
- **Effort:** 1 d. **Risks:** borrower names, photos and terms in the full snapshot. **Not recommended.**

### A4. Reddit financial-hardship corpora  [P]
- **pf-dataset** (https://github.com/rayniery/pf-dataset, opened): 546 r/personalfinance posts labelled for financial distress. No license (GitHub license: none). Too small; license unclear.
- **Dreaddit** (Turcan & McKeown 2019, includes r/assistance in its financial domain): official zip at http://www.cs.columbia.edu/~eturcan/data/dreaddit.zip responds 200. We found no license; not downloaded. HF mirrors carry no license tags. (U for content counts; from search snippet: 355 labeled segments in the financial domain.)
- **Ma & Rajtmajer, "Private Seeds, Public LLMs"** (arXiv 2604.07486, abstract opened): the snippet claims a financial-hardship Reddit dataset (8,948/1,000/1,000). The abstract page does not mention a release. **U.**
- No r/povertyfinance or r/Assistance dataset with an explicit research license was found.
- **Not recommended** within 5 days.

### A5. FairFund-Bench (already in repo)
Already cloned at commit 74b75f3 (`data/external/fairfund-bench`). Not re-verified here.

### A6. Administrative and court decisions on benefits
- **NY OTDA Fair Hearing Decision Archive**  [P]
  - **Opened:** search page via Wayback, https://web.archive.org/web/2025/https://otda.ny.gov/hearings/search/; disclaimer via Wayback, https://web.archive.org/web/2025/https://otda.ny.gov/disclaimer.asp
  - Live otda.ny.gov resets connections from our host.
  - "search all of the Fair Hearing decisions issued by the Office of Administrative Hearings since November 1, 2010 ... edited to remove all identifying information." It is full-text search over redacted PDFs (e.g., `otda.ny.gov/fair hearing images/2026-1/Redacted_9056022P.pdf`); we **could not open a decision PDF**.
  - **Terms (exact, disclaimer):** "Unless otherwise noted ... OTDA grants users permission to reproduce materials published by OTDA on this Website so long as OTDA is noted as the source, and the date the Web page was accessed, along with the date of publication of the material cited, is noted. ... the contents may not be modified in any way."
  - **Use:** (a)+(c). Real SNAP/public-assistance adjudications with stated income and shelter amounts and a legal outcome under the rules; the best "real text + real rule" source if accessible.
  - **Effort:** 2–3 d (scraping PDFs, extraction).
  - **Risks:** the access block; "may not be modified" (quote, don't edit; derived annotations are probably fine but confirm); redacted but sensitive.
  - **Recommend as future work or appendix only.**
- **UK Upper Tribunal (AAC) decisions**  [V]
  - **Opened:** https://www.gov.uk/administrative-appeals-tribunal-decisions?tribunal_decision_categories[]=universal-credit (85 UC decisions listed; OGL v3.0). From 7 Apr 2025 only "wider public interest" decisions appear there; all decisions are on Find Case Law.
  - **Find Case Law terms** (opened https://caselaw.nationalarchives.gov.uk/what-you-can-do-freely): the Open Justice Licence "does not permit computational analysis". Programmatic bulk searching or extraction needs a separate (free) licence via a 29-question application.
  - UT decisions are about points of law and rarely contain clean need facts. **Not recommended in 5 days.**
- **Dutch Rechtspraak open data**  [P]
  - The open-data page loads, and the API (`data.rechtspraak.nl/uitspraken/zoeken`) responds with feed rights "Copyright 2026 Rechtspraak."
  - We did not confirm reuse terms. The text is Dutch. Not recommended.
- **US SSA ALJ decisions:** not searched in depth. ALJ decisions are not published as a corpus as far as we found (U). Disability cases also turn on medical, not income, facts. Skip.

---

## B. Human judgment data (baselines)

### B1. Knotz et al. 2022, "A Recast Framework for Welfare Deservingness Perceptions" (OSF 37me5)  [V]
- **URLs opened:**
  - OSF API https://api.osf.io/v2/nodes/37me5/ and file tree
  - Paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC8378786/ (CC BY 4.0)
  - Do-file `DesRecast_US_Qualtrics_Analysis.do` (read only, not saved)
- **Venue:** Social Indicators Research 159(3), 2022.
- **Files:**
  - `DesRecast_US_Qualtrics.dta` (108 KB), `DesRecast_US_AMT.dta` (79 KB), `DesRecast_GER_Qualtrics.dta` (115 KB)
  - 3 Stata do-files
  - `SIR_vignettes.xlsx` (19 KB)
- **Variables (from the do-file):**
  - `vig_deserv` (outcome, 0–100 % of former salary)
  - `vig_control`, `vig_attitude`, `vig_recip`, `vig_ident`, `vig_need`, `vig_effort`
  - `vig_real`, `vig_easy`, `r_id`, `r_age(_cat)`, `r_gender`, `r_educ`, `r_race`, `r_inc`, `r_cheat`
  - 8 vignettes per respondent.
- **Operationalization (paper):**
  - Need = "financially responsible for [himself / partner / partner and child / partner and three children]".
  - Effort = job search from "not looking" to "5–6 applications per week".
  - Control = laid off vs. resigned.
  - Reciprocity = 1/2/4/8 years of contributions.
  - Identity = country of birth.
  - N: 360 (US Qualtrics), 334 (US MTurk), 400 (DE).
- **License:** OSF `node_license: null`, so **no license**. The paper says "Our replication data and code files are publicly available", but public is not the same as licensed. We did not download the data.
- **Use:**
  - (b) Present the exact vignettes to the LLM, compare its 0–100 ratings and its effect sizes (need vs effort vs control ...) with human coefficients.
  - Also test whether the LLM's *need* coefficient is distorted by effort/control, as in our finding.
  - **Caveat for the paper:** need here is dependents, not a resource–cost gap. Our gap-based need is a deliberate refinement and should be stated as such.
- **Effort:** 1 d. **Risks:** license (email Knotz for permission); no PII.

### B2. "All in this together?" COVID-19 government-aid deservingness (Harvard Dataverse doi:10.7910/DVN/LPHMB7)  [V]
- **Opened:** Dataverse API metadata, README.md; downloaded `study1.tab`. Venue per README: Frontiers in Political Science 2021 (preregistered).
- **License:** **CC0 1.0** (Dataverse license field).
- **Size:**
  - study1: 9,180 rows, 2,295 respondents × 4 vignettes.
  - study2 and study2_alt: about 1.5 MB each.
- **Fields:**
  - `vignette_allocation` (CAD 0–4000)
  - `vignette_income` ($30k/$60k/$90k/$120k)
  - `vignette_employment` (Employed full-time / Employed, reduced income / Unemployed / Unemployed due to pandemic)
  - `vignette_children`, `vignette_health`, `vignette_marital`, `vignette_citizen`, `vignette_ethnicity`, `vignette_gender`
  - Respondent covariates.
  - Study 2 adds `vignette_deservingness` (0–10), `vignette_similarity`, and a GST vs COVID framing condition.
- **Our quick look (study 1, raw means, not causal estimates):**
  - Allocation by employment: employed full-time 1,149; reduced income 1,727; unemployed 1,637; unemployed (pandemic) 1,863.
  - Allocation by income: $30k 1,703 down to $120k 1,462.
  - Employment status moves allocations far more than a 4× income difference does. This is a human parallel to our LLM "unemployed context" effect and frames it as "LLM vs human" rather than "LLM is wrong".
- **Use:** (b) Re-render the vignettes, have LLMs allocate and rate (study 2), and compare the marginal effects of income vs employment.
- **Effort:** 1 d. **Risks:** none (CC0, anonymized). Saved: `data/external/candidates/covid_deservingness_LPHMB7/`

### B3. Hsieh & Kline 2025, "Deservingness Heuristics Drive Redistributive Choices, But Weights on Recipient Effort Vary" (doi:10.7910/DVN/AOT2JW)  [V]
- **License:** CC0 1.0.
- **Files:** `Codebook.md`, 4 small tabs (MTurk N≈105/112, students N≈55/57), `Replication Code.qmd`. All saved in `candidates/hsieh_kline_AOT2JW/`.
- **Design (codebook):**
  - Participants transfer real earnings to recipients whose income = wage rate × number of tables completed (effort).
  - "Observable" condition: income and effort both visible (`yo_l_xx`, `yo_h_xx`).
  - "Unobservable" condition: income only (`no_xx`).
- **Use:** (b) The cleanest numeric need × effort decomposition. LLMs can play the same allocation, comparing the slope on income (need) with the slope on effort.
- **Effort:** 0.5 d. **Risks:** small N; a lab task, not welfare.

### B4. Other CC0 Harvard Dataverse deservingness replication sets  [V metadata only]
Opened via the Dataverse API. All CC0 1.0:
- **TIXGF8:** Jensen & Petersen 2017, AJPS, "Deservingness Heuristic and Politics of Health Care". Studies 1–4 with codebooks; Study 2 is a 2×2 control/need-type vignette, 7-pt aid support. Terms field: "CC0 license with the following additional/modified terms" (the text is empty). Saved `readme.txt`.
- **AZTWDW:** DeSante 2013, "Working Twice as Hard ..." Race × work-ethic applicant allocation; N=1000. Codebook and data saved. We did not fully inspect the variables. Note that `applicants.csv` turned out to hold WIC/SNAP yearly figures, not applicants, so we deleted it.
- **6U9FHM:** Sawler, JOP, gender and welfare claimant deservingness.
- **0RIQH7:** Bitton & Treger 2026, "When Effort Is Not Enough".
- **6ECD1D:** Myers, Zhirkov & Lunz Trujillo, conjoint of who is "on welfare". 27 MB zip, not downloaded.
- **UN2SMP:** Ellis, "Race, Deservingness, and Social Spending Attitudes".
- **3U3XNH:** Baumberg Geiger, disability-claimant deservingness pre-analysis plan plus pilot data.

Search result to discard: the search engine attributed **doi:10.7910/DVN/FHU7ET** to Aarøe & Petersen 2014, but the API shows it is Trump, "When Is It Fair to Tax the Rich?". **Aarøe & Petersen 2014 replication data: not located (U).**

### B5. ESS Round 8 (2016) Welfare Attitudes module  [V]
- **Opened:**
  - Source questionnaire: https://stessrelpubprodwe.blob.core.windows.net/data/round8/fieldwork/source/ESS8_source_questionnaires.pdf (text extracted)
  - Licence: https://www.europeansocialsurvey.org/contact/disclaimer
- **License (exact):** "ESS data is licensed under CC BY-NC-SA 4.0" and documentation under CC BY-SA 4.0. "The data are available without restrictions, for not-for-profit purposes." ESS asks users to link to the portal, not re-host.
- **Relevant items:**
  - E-block conditionality vignettes (split ballot): "Imagine someone who is unemployed and looking for work ... What should happen to this person's unemployment benefit if… they turn down a job because it pays a lot less / needs a lower level of education / they refuse ...", with variants for a person in their 50s, aged 20–25, and a single parent with a 3-year-old. Responses: lose all / half / small part / keep all.
  - Also "social benefits make people lazy?" (E13ff), government responsibility for the unemployed, and basic income (E36).
- **Use:** (b) a population-scale, cross-national human distribution for effort/reciprocity conditionality. We can elicit LLM responses to the same items and compare with country distributions. It does not cross need with cues, so it is complementary only.
- **Effort:** 0.5–1 d (portal download, ~40k respondents). **Risks:** NC-SA (fine for research); don't redistribute.

### B6. Not located / not verified
- Kootstra 2016 (ESR) vignette data: no repository found (U).
- Buss 2019 (JESP), Laenen, van Oorschot: no public microdata found in this pass (U).

---

## C. Real programme rules (rule-based gold)

### C1. USDA FNS SNAP eligibility (FY2027 parameters)  [V]
- **Opened:** https://www.fns.usda.gov/snap/recipient/eligibility (curl; WebFetch was 403). Page updated 1 Oct 2026; "information on this page is for Oct. 1, 2026, through Sept. 30, 2027". It notes OBBBA-2025 changes still being incorporated.
- **Rules (48 states + DC):**
  - Gross ≤ 130% FPL: 1 person $1,729; 2: $2,345; 3: $2,960; 4: $3,575; +$616 per extra member.
  - Net ≤ 100% FPL: $1,330 / $1,804 / $2,277 / $2,750; +$474 per extra member.
  - Resources: $3,000, or $4,750 with an elderly or disabled member.
  - Deductions: 20% of earned income; standard $217 (1–3 persons); dependent care; medical over $35 (elderly/disabled); child support (some states); homeless shelter $205.66; excess shelter above 50% of adjusted income, capped at $769.
  - Max allotment (1 person) $306; benefit = max − 0.3 × net.
  - BBCE: states may raise limits.
- **Statute:** 7 CFR 273.9(d), opened via the eCFR API: "Deductions shall be allowed only for the following household expenses: (1) Standard deduction ...".
- **License:** US federal government work (17 U.S.C. §105), public domain.
- **Note:** the FNS worked example has an internal inconsistency ($1,171 adjusted income in one row, $1,165 in the next). Don't copy it as gold.
- **Use:** (c) Define SHORTFALL/SUFFICIENT as failing or passing the SNAP net-income test (or gross test) for a stated household. Gold is computable and citable.

### C2. PolicyEngine-US (rules-as-code)  [V, executed]
- **Opened:** https://github.com/PolicyEngine/policyengine-us, GitHub API (license `AGPL-3.0`, pushed 2026-10-05), PyPI (v2.24.5). Variables directory `policyengine_us/variables/gov/usda/snap/eligibility/` contains `meets_snap_gross_income_test`, `meets_snap_net_income_test`, `meets_snap_asset_test`, `is_snap_eligible`, `work_requirements/`, `student/`.
- **Our test** (scratch venv, single adult, TX, 2026):
  - $1,500/mo earnings with $900 rent: eligible, `snap` = $1,488/yr.
  - $3,000/mo: fails both tests.
  - **$800/mo: passes both income tests but `is_snap_eligible` = False**, presumably via default non-financial conditions (work requirements). Set hours/ABAWD inputs explicitly or use the income tests only.
- **License:** AGPL-3.0 for the code. Running it to compute labels creates no distribution obligation. Cite the version.
- **Also:** PolicyEngine-UK (AGPL-3.0) models Universal Credit (`is_uc_eligible`, `uc_maximum_amount`, `work_allowance`, `standard_allowance`, ...). OpenFisca-core is AGPL-3.0.
- **Effort:** 1 d to wrap as a gold-label function for our profiles and SNAP QC households.

### C3. UK Universal Credit (GOV.UK)  [V]
- **Opened:**
  - https://www.gov.uk/universal-credit/what-youll-get: standard allowance single <25 £338.58, single ≥25 £424.90, couple <25 £528.34, couple with either ≥25 £666.97; tariff income £4.35 per £250 between £6,000 and £16,000.
  - https://www.gov.uk/universal-credit/how-your-earnings-affect-your-payments: 55p taper per £1; work allowance £427/month (with housing support).
- **License:** "All content is available under the Open Government Licence v3.0".
- **Use:** (c) a second jurisdiction for robustness (a UK version of the vignettes), with PolicyEngine-UK as the engine.

### C4. USDA SNAP Quality Control public-use file, FY2024  [V, downloaded]
- **Opened:** https://snapqcdata.net/ and https://snapqcdata.net/datafiles (FY1996–FY2024; FY2024 revised and posted 2026-08-18). Contact FNAStudies@usda.gov.
- **File:** `qcfy2024_csv.zip` (5.4 MB) unpacks to `qc_pub_fy2024.csv` (92 MB): **44,891 households × 1,177 columns**. Saved in `candidates/snap_qc_fy2024/`.
- **Key fields:**
  - Gross and net income: `FSGRINC`, `FSNETINC`, `RAWGROSS`, `RAWNET`, plus `TPOV` (income as % of poverty).
  - Shelter: `RENT`, `SHELDED`, `UTIL`, `SHELCAP`.
  - Deductions: `FSERNDED`, `FSSTDDED`, `FSDEPDED`, `FSMEDDED`, `FSTOTDED`.
  - Assets: `FSASSET`, `LIQRESOR`.
  - Benefit: `FSBEN`, `RAWBEN`, `BENMAX`.
  - **Test flags:** `FSGRTEST`, `FSNETEST`, `FSASTEST`, `CAT_ELIG`.
  - Per person (1–16): `AGE`, `SEX`, `EMPSTA`/`EMPSTB` (employment), `WRKREG` (work registration), `ABWDST` (ABAWD status), `WAGES`, `SOCSEC`, `FSUNEMP` (unemployment income).
  - Error fields: `STATUS` (1 correct 27,055; 2 over-issuance 10,734; 3 under-issuance 7,102), `AMTERR`, `ELEMENT*`/`NATURE*` error codes.
- **License:** none printed on the site. It is a US federal public-use file (de-identified, public domain).
- **Use:**
  - (c)+(a-lite) Sample real households, render them as short first-person or caseworker narratives with real amounts, and use `FSNETEST`/`FSGRTEST` (or PolicyEngine recomputation) as gold.
  - Add effort/control/reciprocity cues as minimal pairs. Employment, work-registration and ABAWD fields allow a realistic cue distribution.
  - Bonus: QC error cases (`STATUS` 2/3) let us compare LLM errors with real caseworker errors.
  - Caveat: almost all households are participants, so near the threshold most pass. Stratify by `TPOV` and create "sufficient" contrasts by income scaling, documented as such.
- **Effort:** 1.5–2 d. **Risks:** essentially none for privacy (public de-identified); keep the weights caveat.

---

## D. NLP financial-reasoning sanity baselines  [V license only]
- **FinQA** (EMNLP 2021): https://github.com/czyssrs/FinQA, MIT.
- **ConvFinQA** (EMNLP 2022): https://github.com/czyssrs/ConvFinQA, MIT.
- **TAT-QA:** https://github.com/NExTplusplus/TAT-QA, MIT; 16,552 questions over 2,757 hybrid contexts.
- **Relevance: low.** They use corporate filings. Use at most as a numeracy sanity check: "the model can subtract".
- **SARA** (StAtutory Reasoning Assessment, JHU): https://nlp.jhu.edu/law/sara/, opened. Tax-law statutes plus cases with Prolog-computed gold; the closest NLP precedent for "rule-computed gold over natural-language cases". The page shows no license, and the GitHub repo `SgfdDttt/sara` has no license (U). **Cite as related work** rather than use.
- **HoosierHelp** (arXiv 2608.09946, opened): 240 samples, social-service navigation agents over 3,971 Indiana resources. Data release and license not stated. Related work only.

---

## Downloaded samples (all clear licenses)
```
data/external/candidates/
  covid_deservingness_LPHMB7/   README.md, study1.tab            (CC0)
  hsieh_kline_AOT2JW/           Codebook.md, 4 .tab, .qmd         (CC0)
  jensen_petersen_TIXGF8/       readme.txt, codebook_study2.pdf   (CC0)
  desante_AZTWDW/               codebook .smcl, data (.dta-format .tab)  (CC0)
  mdcc_gofundme/                raw_data.csv (75 MB)              (CC BY-NC 4.0)
  snap_qc_fy2024/               qcfy2024_csv.zip + csv (92 MB)    (US public-use)
```
Not downloaded because the license is unclear: OSF 37me5 data (Knotz et al.), RAOP, Dreaddit, Kiva snapshots, NY OTDA PDFs (also blocked).

## Open actions
1. Email C. Knotz for permission to use the OSF 37me5 microdata. Ask whether a CC-BY license can be added to the OSF node.
2. (Optional) Email T. Althoff for RAOP permission.
3. Pin PolicyEngine-US 2.24.5 in `configs/requirements.lock.txt` if adopted. Decide on the gross test, net test, or both as the gold definition and log it in `docs/decisions.md`.
