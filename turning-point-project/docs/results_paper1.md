# Results: paper 1

> **Audit note (2026-11-13).** Numbers below are from the original (v2) run. Authoritative numbers are the seeded re-runs in `outputs/*.json` and `outputs/primary_estimands.csv`; interpretation is corrected in `docs/independent_review_response.md` and `manuscripts/working_paper_v3.md`. Equivalence for fathers applies only to the linear age-16 vs age-12 contrast. The ±0.20 SD margin is larger than the age-14 association (≈0.15 SD), and a post-hoc test of any difference across the five ages gave p = .16 (mothers) and .08 (fathers). Statements below that the data "rule out" differences or show "no sign of a developmental window" overstate the evidence.

**When does adult support matter most? Parental support across adolescence and educational attainment in the NLSY97**

Status: first complete run of the frozen analysis plan (`docs/PLAN_FREEZE.md`, frozen at commit 970c8fc
before respondent-level data were opened). Run 2026-11-12; 40 imputations; seed 20261112.
These are **adjusted associations from observational data**, not causal effects.

## Summary

- Youths who described their mother as *very supportive* in 1997 later completed about **0.47 more
  years of schooling** (95% CI 0.31 to 0.63; about 0.15 SD) than otherwise similar peers. The figure for
  fathers was about the same: **0.47 years** (0.29 to 0.64). These are estimates at age 14, adjusted for
  family income, parents' education, household type, sex, race/ethnicity and urban residence.
- **The association did not clearly depend on age at report (12 vs 16).**
  - Mother (Q1, primary): difference 16 vs 12 = **+0.26 years** (−0.21 to 0.74), +0.08 SD;
    Holm-adjusted p = 0.54. Equivalence: **inconclusive**. The 90% CI (−0.04 to 0.21 SD) only just
    crosses the +0.20 SD bound.
  - Father (Q2, secondary): difference = **−0.18 years** (−0.64 to 0.27), −0.06 SD; Holm-adjusted
    p = 0.54. Equivalence: **established**. The 90% CI (−0.18 to 0.07 SD) lies inside ±0.20 SD.
- **The direction differs by parent and is not robust.** For mothers, every sensitivity analysis gives
  a positive difference (+0.04 to +0.34 years), slightly larger at older ages. For fathers the sign
  flips across specifications. Fitting each age separately (S1) gives a zigzag rather than a trend,
  with the highest value at 14 for both parents.
- **Unmeasured confounding could explain the overall association.** The E-value for the age-14
  association is 1.56 (1.41 for the CI limit). An unmeasured factor associated with both support and
  schooling at a risk ratio of about 1.6 could account for it. Adding the ASVAB test score, an imperfect
  proxy for prior achievement, shrinks the association by a fifth to a quarter (mother 0.47 → 0.35;
  father 0.47 → 0.39), as expected if more able adolescents also report more supportive parents.

**Interpretation, within the plan's rules (SAP §9).** For parental support reported between ages 12 and
16, these data give no sign of a developmental window. For fathers they rule out differences larger than
the pre-set bound. For mothers they leave room for a modest *later* advantage, the opposite of an
early-adolescent window. This fits the accumulation and individualized-timing hypotheses (H5/H6)
better than the age-specific window hypotheses (H2/H3). It says nothing about nonparental mentors, about
ages outside 12–16, or about what would happen if support were changed (concepts A and C in
`research_questions.md`).

## Sample (STROBE flow)

| | Mother (Q1) | Father (Q2) |
|---|---|---|
| Round-1 respondents | 8,984 | 8,984 |
| In item universe (living with a parent figure of that sex) | 8,610 | 6,443 |
| Valid answer (analyzed) | 8,607 | 6,436 |
| Attainment observed at a 2010+ interview (age ≥ 25) | 7,838 | 5,816 |
| Attainment imputed | 769 | 620 |
| Fraction of missing information (Δ) | 0.08 | 0.11 |

Weighted share reporting a *very supportive* mother by age 12–16: 78.7, 74.7, 71.7, 82.3, 80.6%;
father: 72.1, 67.2, 64.8, 69.7, 67.2%. Weighted SD of highest grade completed: 3.11 (mother sample),
3.07 (father sample). Design: 117 strata × 2 PSUs, 117 design degrees of freedom.

## Primary estimates (years of schooling, 95% CI)

| Age at report | Mother | Father |
|---|---|---|
| 12 | 0.34 (0.07, 0.61) | 0.56 (0.28, 0.84) |
| 13 | 0.40 (0.21, 0.59) | 0.51 (0.31, 0.72) |
| 14 | 0.47 (0.31, 0.63) | 0.47 (0.29, 0.64) |
| 15 | 0.54 (0.32, 0.75) | 0.42 (0.21, 0.64) |
| 16 | 0.60 (0.30, 0.91) | 0.38 (0.08, 0.67) |
| **Difference 16 − 12** | **0.26 (−0.21, 0.74)** | **−0.18 (−0.64, 0.27)** |

Figures: `outputs/paper1_effect_by_age_mother.html`, `outputs/paper1_effect_by_age_father.html`.

### Mother support: sensitivity analyses

| Analysis | n | Association at 14 | Difference 16 vs 12 |
|---|---|---|---|
| Primary (MI, m = 40) | 8607 | 0.47 (0.31, 0.63) | 0.26 (-0.21, 0.74) |
| S1 each age separately | — | 0.71 (0.35, 1.06) | ages 12–16: 0.33, 0.31, 0.71, 0.29, 0.65 |
| S2 complete cases | 5232 | 0.47 (0.29, 0.65) | 0.21 (-0.39, 0.81) |
| S3 IPW for co-residence (complete cases) | 5232 | 0.47 (0.29, 0.65) | 0.21 (-0.39, 0.81) |
| S4 + grade in 1997 | MI | 0.47 (0.30, 0.64) | 0.24 (-0.21, 0.69) |
| S5a ordinal exposure (per step) | MI | 0.42 (0.27, 0.57) | 0.26 (-0.15, 0.66) |
| S5b multi-item scale (per point, subsample) | 5214 | 0.07 (0.04, 0.09) | 0.04 (-0.04, 0.11) |
| S6 unweighted, no design | MI | 0.40 (0.25, 0.55) | 0.11 (-0.31, 0.53) |
| S8 + ASVAB percentile | MI | 0.35 (0.19, 0.51) | 0.34 (-0.09, 0.78) |

Exploratory (mother): below poverty line Δ = 0.75 (-0.22, 1.72); at/above Δ = 0.16 (-0.36, 0.68); BA-or-higher log-odds at 14 = 0.42 (SE 0.08), Δ = 0.44 (SE 0.24).

### Father support: sensitivity analyses

| Analysis | n | Association at 14 | Difference 16 vs 12 |
|---|---|---|---|
| Primary (MI, m = 40) | 6436 | 0.47 (0.29, 0.64) | -0.18 (-0.64, 0.27) |
| S1 each age separately | — | 0.84 (0.46, 1.23) | ages 12–16: 0.51, 0.39, 0.84, 0.20, 0.37 |
| S2 complete cases | 3955 | 0.46 (0.25, 0.67) | 0.23 (-0.29, 0.74) |
| S3 IPW for co-residence (complete cases) | 3955 | 0.41 (0.20, 0.63) | 0.21 (-0.30, 0.73) |
| S4 + grade in 1997 | MI | 0.45 (0.28, 0.62) | -0.28 (-0.74, 0.18) |
| S5a ordinal exposure (per step) | MI | 0.37 (0.23, 0.52) | -0.24 (-0.59, 0.11) |
| S5b multi-item scale (per point, subsample) | 3953 | 0.04 (0.01, 0.07) | -0.05 (-0.14, 0.04) |
| S6 unweighted, no design | MI | 0.42 (0.27, 0.57) | -0.33 (-0.76, 0.10) |
| S8 + ASVAB percentile | MI | 0.39 (0.24, 0.54) | -0.01 (-0.44, 0.42) |

Exploratory (father): below poverty line Δ = -0.68 (-1.88, 0.52); at/above Δ = -0.15 (-0.65, 0.35); BA-or-higher log-odds at 14 = 0.41 (SE 0.07), Δ = -0.15 (SE 0.20).
The poverty-subgroup and BA-or-higher analyses are **exploratory**. Their intervals are wide and they
are not evidence of differences between groups.

## Verification

- **Extraction:** counts in the 24-column extract match the codebook exactly for the exposure items,
  age, last-interview round and sex. Extract SHA-256 `462bc6f1…1f90` (manifest in `data/processed/`, git-ignored).
- **Variance:** a delete-one-PSU jackknife (`scripts/crosscheck_variance.py`), which shares no variance
  code with the main estimator, reproduces the linearized standard errors to three decimals
  (ratio 1.000 for both θ(14) and Δ).
- **Estimator:** unit tests include agreement with statsmodels' cluster-robust variance and a Monte
  Carlo bias and coverage check (`tests/test_modeling.py`).
- **Plan integrity:** hashes of the four frozen files still match `docs/PLAN_FREEZE.md`.

## Deviations from the plan

| # | Plan | What happened | Effect |
|---|---|---|---|
| 1 | Register the plan (OSF) | PI chose not to use OSF. The plan was frozen by a timestamped branch commit with file hashes. The git tag could not be pushed (proxy refused) | Weaker public verifiability; same content |
| 2 | Cross-check estimates against R `survey` | R not available; the `samplics` package fails on this numpy version. Replaced by an independent JK2 jackknife | Agreement to 3 decimals |
| 3 | S6b custom longitudinal weight | Not run: NLS custom weights come from an online tool not available offline | One planned sensitivity analysis missing |
| 4 | Exploratory: life-course models of 1997–2000 items; earnings and employment | Not run (variables not extracted) | Exploratory only |
| 5 | Implementation details not spelled out in the plan | Subpopulations analyzed by domain estimation (zero weight outside, full design kept). PMM imputation (statsmodels MICE, k = 5); some household-type dummies are constant in a sample and are dropped from models. S3 universe model: age, age², sex, race/ethnicity, urban, poverty (with missing indicators) | None on primary estimates |
| 6 | Bug found during checking | The item-universe flag compared against a misspelled missing-code label, so S3 was initially a no-op and the flow counts were wrong. Fixed and fully re-run before this report. The reported n for S5b counted padding rows; corrected | Primary results unaffected |

## Limitations

Observational data. Support is a single self-report at one time point. Age at report is confounded with
birth cohort (1980–84) and with selection into living with a parent. Prior achievement is weakly
measured at baseline. Attrition is handled by imputation under missing-at-random. Results concern
parental support only.
