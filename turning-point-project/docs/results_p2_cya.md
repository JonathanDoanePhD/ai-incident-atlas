# Results: paper 2 (maternal warmth at ages 6–9 vs 10–14, NLSY79 Children and Young Adults)

> **Audit note (2026-11-13).** Numbers below are from the original (v2) run. Authoritative numbers are the seeded re-runs in `outputs/*.json` and `outputs/primary_estimands.csv`; interpretation is corrected in `docs/independent_review_response.md` and `manuscripts/working_paper_v3.md`. The windows are defined by age at measurement of mother-reported praise, not by when relationships began. A post-hoc check with one report per window (equal reliability) kept the same ordering.

Status: first complete run of the frozen plan (`docs/sap_nlsy79cya_childhood.md`; `docs/PLAN_FREEZE_P2.md`,
frozen before the data were opened). Run 2026-11-12; 20 imputations; cluster-robust variance by mother.
**Adjusted associations from observational data**, not causal effects.

## Summary

- **Ages 6–9 (middle childhood):** 1 SD more maternal praise (mother report, averaged over the child's
  biennial reports in that window) went with **-0.1 points** in the probability of a bachelor's
  degree (95% CI −1.5 to +1.2), holding praise at 10–14 fixed.
- **Ages 10–14 (early adolescence):** **+1.6 points** (+0.3 to +2.9).
- **Difference (6–9 minus 10–14):** **-1.7 points** (−3.9 to +0.6), p = 0.14;
  equivalence within ±3 points **inconclusive** (90% CI −3.5 to +0.2).
- **Same ordering everywhere:** every sensitivity analysis and the secondary exposure (closeness: 6–9
  +0.8, 10–14 +2.4 points) put the 10–14 window at or above 6–9.
- **Life-course comparison (exploratory):** the "early-adolescence only" and "accumulation" models fit about
  equally well (ΔAIC 0.2), and better than "middle childhood only".

**Interpretation.** These data give no support to H1, the idea that middle childhood is the decisive window
for this kind of parental warmth. If anything, warmth reported at 10–14 is more strongly associated with later
degree attainment. This ordering is also what we would expect if associations simply grow with proximity to the
outcome, or if what matters is warmth that persists. The design cannot distinguish these, and the associations are small
(about 1–2 points per SD against a 29% base rate).

## Sample

| Step | n |
|---|---|
| Children in the CYA | 11,551 |
| Born 1979–1995 | 9,270 |
| Praise reported in both windows (analyzed) | 6,190 children of 3,138 mothers |
| Outcome observed (last YA interview at age ≥ 25) | 5,680 |
| Outcome imputed | 510 |
| Closeness reported in both windows | 3,989 |

Mean number of praise reports per child: 1.8 at 6–9, 2.0 at 10–14.
Correlation between window scores: praise 0.55, closeness 0.41.
Unweighted share with a bachelor's degree or higher (observed): 29.2%.

## Estimates (percentage points per SD, 95% CI; both windows in one model)

| Analysis | Ages 6–9 | Ages 10–14 | Difference (6–9 − 10–14) |
|---|---|---|---|
| Primary: praise (MI, m = 20) | −0.1 (−1.5, +1.2) | +1.6 (+0.3, +2.9) | −1.7 (−3.9, +0.6) |
| S1 closeness (secondary exposure) | +0.8 (−0.6, +2.2) | +2.4 (+0.9, +3.9) | −1.6 (−4.0, +0.9) |
| S2 complete cases (n = 5375) | −0.4 (−1.9, +1.0) | +1.8 (+0.4, +3.2) | −2.2 (−4.6, +0.1) |
| S3 child sampling weights | +0.0 (−1.8, +1.8) | +1.9 (+0.1, +3.7) | −1.9 (−4.9, +1.2) |
| S5 without income and poverty | −0.1 (−1.4, +1.3) | +1.5 (+0.2, +2.8) | −1.6 (−3.8, +0.7) |

S4 (each window alone, not mutually adjusted): ages 6–9 +0.7 (SE 0.6); ages 10–14 +1.5 (SE 0.6).

E1 life-course structured approach (exploratory; binary top tercile within window; first imputation; logistic; unweighted):

| Model | ΔAIC | p vs saturated |
|---|---|---|
| critical_D | 0.00 | 0.90 |
| accumulation | 0.21 | 0.81 |
| null | 1.07 | 0.35 |
| sensitive_periods | 1.82 | 0.88 |
| critical_C | 1.97 | 0.34 |
| saturated | 3.80 | — |
| mobility | 4.63 | 0.09 |

Exposure patterns (low/high at 6–9, 10–14): {'00': 3292, '01': 832, '10': 834, '11': 1232}.

## Caveats

Mother-reported praise may partly reflect the child's behavior and achievement (reverse causation). The
windows differ in distance to the outcome. The CYA describes children of a 1979 cohort of young women, and children
born to younger mothers are over-represented among those old enough for adult outcomes. Window boundary is
age 10, not 12. No strata/PSU in public NLSY79 files: inference clusters on mother only.

## Verification

Extract counts match the codebooks (degree, praise and closeness items checked). All children link to a mother
record. Plan hashes unchanged (`docs/PLAN_FREEZE_P2.md`).
