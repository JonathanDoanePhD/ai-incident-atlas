# Analysis plan addendum: accumulation vs timing in the NLSY97 (exploratory)

Status: v1, 2026-11-12. Frozen (`PLAN_FREEZE_P1E.md`) before the 1998–2000 support items were extracted.
Paper 1's frozen plan (SAP §2) listed this as an exploratory analysis; this addendum fixes its details.

## Question

Among youths who were 12–14 at the end of 1996, is highest grade completed better described by **how many**
of the four annual reports (1997–2000) describe a very supportive mother (accumulation, H6) or by **when**
(critical/sensitive periods)?

## Data

`YSAQ-032` in rounds 1–4 (reference numbers R03257.00, R21667.00, R34846.00, R48821.00; identical wording
1997–1999; 2000 inserts "[mother (figure)]"). In 1998–1999 the item was asked only of youths aged ≤ 14 at the end of
1996 who lived with a mother figure, so the sample is restricted to those ages and to youths with a valid
answer in all four rounds (complete exposure histories). Outcome, covariates, weights, design and outcome
observation rule: as in paper 1.

## Models (survey-weighted linear, design-based variance; complete cases on covariates and outcome)

- Accumulation: `hgc ~ count + age + covariates`, where count = number of rounds (0–4) with "very supportive".
- Sensitive periods: `hgc ~ count + E1998 + E1999 + E2000 + age + covariates`. Accumulation holds iff the
  three deviation coefficients are 0. Design-adjusted Wald F test (3 df) is the **primary exploratory test**.
- Critical period r: `hgc ~ E_r + age + covariates`, for each round r. Compared descriptively by AIC with the others
  (unweighted quasi-likelihood; `compare_lifecourse_models`).
- Report: the per-round coefficients from the sensitive-period model and the accumulation slope, with 95% CIs.

## Caveats (pre-stated)

Exposures across adjacent years are highly correlated, which limits power to separate the models (`smith2015`).
Complete-history restriction selects stable households. Exploratory: no confirmatory claims.
