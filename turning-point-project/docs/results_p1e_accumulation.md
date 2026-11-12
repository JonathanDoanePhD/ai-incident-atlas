# Results: accumulation vs timing in the NLSY97 (exploratory addendum)

Plan: `docs/sap_nlsy97_accumulation.md` (frozen before the 1998–2000 items were extracted; `docs/PLAN_FREEZE_P1E.md`).
Exploratory; survey-weighted with design-based variance; complete cases.

## Summary

Among youths aged 12–14 at the end of 1996 with mother-support reports in all four rounds (1997–2000),
**each additional year described as "very supportive" went with +0.22 more grades completed**
(95% CI +0.14 to +0.31). A design-based test that the four years carry equal weight did
**not** reject accumulation (F(3, 115) = 0.83, p = 0.48). Among restricted life-course models,
accumulation had the lowest AIC. The unrestricted (saturated) model fit better, hinting at non-additive patterns, such as
consistent support in every year. Reports in different years correlate only 0.27–0.45, so the rounds carry distinct information.

## Sample

Aged 12–14 in 1996: 5,419; complete four-round exposure history: 3,870;
complete covariates and observed outcome (analysed): 2,566.

## Per-round coefficients (all four rounds in one model; grades completed)

| Round | Estimate (95% CI) |
|---|---|
| E1997 | +0.03 (−0.31, +0.37) |
| E1998 | +0.42 (+0.13, +0.71) |
| E1999 | +0.29 (−0.01, +0.60) |
| E2000 | +0.10 (−0.22, +0.42) |

## Life-course model comparison (unweighted, descriptive)

| Model | ΔAIC |
|---|---|
| saturated | 0.00 |
| accumulation | 8.30 |
| critical_E1998 | 9.73 |
| sensitive_periods | 9.86 |
| critical_E1999 | 18.06 |
| critical_E2000 | 23.85 |
| critical_E1997 | 29.72 |
| null | 32.91 |

## Caveats

Complete-history and complete-case restrictions select more stable households; the 1998–1999 item universe
limits the sample to younger youths; exploratory, so no confirmatory claims.
