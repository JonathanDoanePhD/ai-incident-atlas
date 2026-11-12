# Analysis plan: paper 2 (middle childhood vs early adolescence)

**Is maternal warmth in middle childhood (ages 6–9) or early adolescence (ages 10–14) more strongly
associated with earning a bachelor's degree? NLSY79 Children and Young Adults.**

Status: v1, 2026-11-12. Written and frozen (`PLAN_FREEZE_P2.md`) **before respondent-level data were
opened**. Only the public codebooks of the NLSY79 Children and Young Adults (CYA) and NLSY79 main files were
read. Variable reference numbers are in `config/mappings/nlsy79cya_spec.json`. Personal research project;
not publicly registered. Exploratory in the sense that it was added after paper 1, but all choices below are
fixed before the data are seen.

## 1. Why this design

PSID requires a registration the PI has not yet completed. The CYA is free and public, and its mothers answered
**identically worded HOME items** every two years in two age sections: Part C (child aged 6–9) and Part D
(10–14). Each child therefore has repeated reports in both windows, and adult education is measured
in the young-adult interviews. This is the closest available test of H1 (middle childhood) against H2
(early adolescence) and of H6 (accumulation). Note the window boundary is **10, not 12**.

## 2. Exposures (mother report)

- **Primary — praise.** "How many times (in the past week) have you praised [child] for doing something
  worthwhile?" Parts C and D, 1988–2016. Values capped at 17 (the 1988 top-code), then converted to
  normal scores (rank-based inverse normal) **within survey year × part**, removing level shifts across
  years, modes (self-administered supplement until 2004; integrated interview from 2006) and sections.
  Window score = mean of the child's normal scores in that window; then standardised across children.
- **Secondary — closeness.** "How close does [child] feel toward you?" (1 extremely … 4 not at all close),
  1994–2016. Coded 1 = extremely close. Window score = share of the window's reports that are
  "extremely close"; then standardised.

## 3. Outcome

`HSTDEGREE_DLI` (highest degree as of last young-adult interview): 1 if bachelor's or higher (codes 4–8),
0 if 0–3. Observed only if age at last YA interview (`LASTINTYR` − `CYRB`) ≥ 25; otherwise missing and
imputed. Children who could not have been interviewed at 25 by 2020 (born after 1995) are excluded.

## 4. Sample

Children born 1979–1995 with at least one exposure report in **each** window (Part C and Part D).

## 5. Covariates (pre-exposure or background)

Child sex (`CSEX`), race/ethnicity (`CRACE`: Hispanic, Black, non-Black non-Hispanic), birth year
(indicators for 1979–83, 84–87, 88–91, 92–95), birth order (`BTHORDR`, 1/2/3+), mother's age at birth
(`MAGEBIR`), mother's highest grade (1990, `HGCREV1990`), mother's AFQT percentile (`AFQT-3`, NLSY79 main
file), and from the NLSY79 main file for survey years when the child was 0–14: share of years in poverty
(`POVSTATUS`) and mean log(1 + family income) (`TNFI_TRUNC`). Income and poverty partly overlap the exposure
windows. They are treated as confounders (economic resources affect both parenting and schooling).

## 6. Model and estimands

Linear probability model, both windows together:
`BA = α + βC·zC + βD·zD + covariates`.

- βC, βD: adjusted difference in BA probability per SD of window-specific warmth, holding the other window fixed.
- **Primary contrast:** Δ = βC − βD (positive favours middle childhood).
  - H1 window: βC > 0, βD ≈ 0.
  - H2 window: βD > 0, βC ≈ 0.
  - Accumulation (H6): βC ≈ βD.
- Tests: Δ = 0 (two-sided); equivalence |Δ| < 0.03 (3 points per SD, TOST), as in study B2.
- Variance: cluster-robust by mother (`MPUBID`), since siblings share a mother. The NLSY79 public files
  have no strata/PSU variables.
- **Unweighted** primary analysis: the CYA represents children of a 1979 cohort of women, not a birth
  cohort, and later-born children are over-represented among those reaching adulthood. Sensitivity: weighted by
  the child sampling weight from the survey year of the child's first Part D report.
- Missing covariates and outcome: chained-equations imputation (PMM), m = 20, Rubin's rules.

## 7. Sensitivity and exploratory analyses

- S1 closeness instead of praise (secondary exposure).
- S2 complete cases.
- S3 child sampling weights.
- S4 each window alone (total association, not mutually adjusted).
- S5 drop income and poverty (in case they act as mediators).
- E1 life-course structured approach (`mishra2009`; `smith2015`) on binary exposures (top tercile within window):
  compare critical-C, critical-D, accumulation and saturated models; descriptive model comparison only.

## 8. Interpretation rules

Associations, not causal effects. Mother-reported warmth may reflect the child's behaviour (reverse
causation), and the two windows are correlated. Results are reported in full, whatever their direction.
A null Δ is evidence against a window **for this measure and these ages**, not against all windows.
