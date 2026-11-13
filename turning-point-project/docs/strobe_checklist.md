# STROBE checklist — working paper v3

STROBE checklist for cohort studies (von Elm et al., 2007), completed 2026-11-13 for `manuscripts/working_paper_v3.md` together
with its supporting documents.

**Scope.**
- **Studies covered:** the four analyses run with AI assistance (Study 1 NLSY97, Study 2 HSLS:09, Study 3 NLSY79 Children and Young
  Adults, Study 4 NLSY97 accumulation).
- **Studies outside scope:** the author-run analyses (A3 Add Health, R1 PSID, R2 Future of Families) are reported qualitatively only,
  and their STROBE items are the author's to complete from local outputs.

**Status key.**
- **Yes:** reported in the paper.
- **Supp.:** reported in a project document the paper cites.
- **Partly:** incomplete.
- **No:** missing.
- **n/a:** not applicable.

Draft by Claude; **the PI reviews and approves.**

| # | Item | Status | Where | Gap / action |
|---|---|---|---|---|
| 1a | Design named in title or abstract | Yes | Title ("observational analyses"); Abstract | — |
| 1b | Informative, balanced abstract | Yes | Abstract | Revisit after adding author-run results (done in this revision) |
| 2 | Background and rationale | Yes | §1 | — |
| 3 | Objectives and prespecified hypotheses | Yes | §1 (four questions); §2 Plans; SAPs | — |
| 4 | Study design, early in paper | Yes | Abstract Methods; §2 | — |
| 5 | Setting: locations, dates of recruitment, exposure, follow-up, data collection | Partly | Abstract; Table 1; §3 | Paper lacks survey years and outcome-measurement years per study. **Action:** add a Table 1 column with cohort birth years, exposure years and outcome year |
| 6a | Eligibility, sources, selection; follow-up methods | Supp. | Results docs "Sample" sections; SAPs | **Action:** Appendix A flow table (added in this revision) |
| 6b | Matching | n/a | — | — |
| 7 | Define outcomes, exposures, confounders, effect modifiers | Partly | Table 1 (exposures); Table 2 header (outcomes); SAPs | Covariates were not listed in the paper. **Action:** covariate sentence in §2 (added in this revision) |
| 8 | Data sources and measurement; comparability across groups | Supp. | `construct_validity.md`; config mappings; SAPs | — |
| 9 | Efforts to address bias | Yes | §2; §3 sensitivity analyses; §4.2 | — |
| 10 | How study size was arrived at | Partly | SAP §power (Study 1); not in paper | **Action:** one sentence on fixed cohort sizes and Study 1's minimum detectable difference (added in this revision) |
| 11 | Handling of quantitative variables; groupings | Supp. | SAPs (standardization per SD; "very supportive" dichotomy; age windows) | — |
| 12a | Statistical methods, including confounding control | Yes | §2 Estimation | — |
| 12b | Subgroups and interactions | Partly | Results docs (poverty subgroups, exploratory) | Paper omits the exploratory subgroup results. Acceptable: labeled exploratory in `results_paper1.md` |
| 12c | Missing data | Yes | §2 (MI by chained equations, PMM, Rubin's rules) | Add *m* per study (Appendix A) |
| 12d | Loss to follow-up | Yes | §2 (MAR imputation); S2/S3/S6b sensitivity analyses; Study 4 IPW | — |
| 12e | Sensitivity analyses | Yes | §3; results docs | — |
| 13a | Numbers at each stage | Supp. → Yes | Results docs; **Appendix A (added)** | — |
| 13b | Reasons for non-participation at each stage | Partly | Appendix A row labels | Reasons are implied by the stage names, which is acceptable for secondary data |
| 13c | Flow diagram | Partly | Appendix A tables | A table substitutes for a diagram; a diagram is optional |
| 14a | Characteristics of participants (demographic, clinical, social); exposures and confounders | **No** | — | No descriptive table of covariates by study. **Action (Claude can do):** weighted descriptive table per study from the existing analysis files |
| 14b | Number with missing data for each variable | Partly | Outcome-imputed counts only (Appendix A) | Covariate missingness not reported. **Action (Claude can do):** missingness table per study |
| 14c | Follow-up time | Partly | Table 1 / §3 (outcome ages) | Covered by the item 5 action |
| 15 | Outcome events or summary measures over time | Supp. | Results docs (BA share, SD of schooling) | Fold into the 14a table |
| 16a | Unadjusted and adjusted estimates with CIs; confounders adjusted for | Partly | Table 2 (adjusted only) | Unadjusted estimates not reported. **Action (Claude can do):** unadjusted versions of the primary models |
| 16b | Category boundaries for continuous variables | Yes | Table 1; SAPs | — |
| 16c | Relative risk translated to absolute risk | n/a | Linear probability and linear models already report absolute differences | — |
| 17 | Other analyses (subgroups, interactions, sensitivity) | Yes | §3; results docs | — |
| 18 | Key results with reference to objectives | Yes | §4 opening | — |
| 19 | Limitations, including bias direction and magnitude | Yes | §4 list; §4.2 | — |
| 20 | Cautious overall interpretation | Yes | §4; §5 | — |
| 21 | Generalizability | Partly | §4.2 (single cohorts, U.S.) | Could state the target populations explicitly. **Action:** one sentence |
| 22 | Funding and role of funders | **No** | — | **PI to supply** (e.g., "No external funding" if true). The disclosure of the planned mentoring organization is present |

## Summary of open actions

**Done in this revision (2026-11-13):**
- covariate sentence (item 7)
- study-size sentence (item 10)
- Appendix A participant flow (items 6a, 12c, 13a)

**Claude can do next, as descriptive reporting only with no new inference:**
- weighted participant characteristics (item 14a)
- covariate missingness (item 14b)
- unadjusted estimates (item 16a)
- survey-year column (items 5 and 14c)
- generalizability sentence (item 21)

**PI only:**
- funding statement (item 22)
- final approval of this checklist
