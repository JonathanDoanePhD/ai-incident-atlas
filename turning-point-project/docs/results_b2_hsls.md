# Results: study B2 (grade 9 vs grade 11, HSLS:09)

**Perceived math-teacher support at the start of high school and in grade 11, and bachelor's-degree
attainment by June 2021**

Status: first complete run of the frozen plan (`docs/sap_hsls09_grade9.md`; freeze record
`docs/PLAN_FREEZE_B2.md`, written before the data were downloaded). Run 2026-11-12; 20 imputations;
standard BRR variance with 200 replicates. These are **adjusted associations from observational data**, not causal effects.

## Summary

- **Grade 9 (fall 2009):** 1 SD higher perceived math-teacher support was associated with
  **-0.2 percentage points** in the probability of a bachelor's degree
  (95% CI −1.3 to +0.9). That is essentially zero
  after adjusting for the grade-9 math score, socioeconomic status, family structure, sex, race/ethnicity and school locale.
- **Grade 11 (spring 2012):** **+1.1 points** (−0.2 to +2.4).
- **Difference (grade 11 − grade 9):** **+1.3 points**
  (−0.4 to +3.1); p = 0.14.
  **Equivalence within ±3 points: established** (90% CI −0.2 to +2.8).
- **Direction is consistent:** grade 11 ≥ grade 9 in every specification. In two sensitivity analyses
  (positively worded items only, complete cases) the difference reaches p < .05.
- **Exploratory:** a grade-9 student's agreement that "there is a teacher or other adult in school I can
  talk to about problems" was associated with **+2.0 points** per SD
  (+0.8 to +3.3). This item has no grade-11 counterpart, so it
  cannot test timing. It does hint that a *relational* measure carries more information than ratings of a
  math teacher's teaching.

**Interpretation, within the plan's rules.** For this measure of teacher support, the data do not
support a freshman-year window. Grade-9 ratings predicted bachelor's attainment no better than grade-11
ratings, and if anything slightly worse. Together with paper 1, two different cohorts, adults and
measures now point the same way: no sign that support measured earlier in adolescence carries more
long-run weight.

Important caveats: the grade-9 items were asked a few weeks into high school, and the two grades refer to
different teachers. Adjusting for the grade-9 math score and family background removes much of the raw association
(model with only sex and race/ethnicity: grade 9 +1.0, grade 11 +2.7 points).
The items measure perceived teaching more than a close relationship.

## Sample

| Step | n |
|---|---|
| Student records | 23,503 |
| Responded in grade 9 and grade 11 (longitudinal weight > 0) | 18,623 |
| Answered grade-9 math-teacher items | 16,617 |
| Answered math-teacher items in both grades (analyzed) | 14,259 |
| Degree outcome observed (postsecondary records) | 10,592 |
| Degree outcome imputed | 3,667 |

Weighted share with a bachelor's degree or higher (observed): 45.4%.
Scale reliability (Cronbach's α, 3 items): grade 9 0.73, grade 11 0.74.
Correlation between grade-9 and grade-11 scores: 0.15 (different teachers).

## Estimates (percentage points per SD of support, 95% CI)

| Analysis | Grade 9 | Grade 11 | Difference (11 − 9) |
|---|---|---|---|
| Primary (MI, m = 20) | −0.2 (−1.3, +0.9) | +1.1 (−0.2, +2.4) | +1.3 (−0.4, +3.1) |
| S1 positively worded items only | −0.3 (−1.5, +0.8) | +1.5 (+0.3, +2.8) | +1.9 (+0.1, +3.6) |
| S2 complete cases (n = 8865) | −0.4 (−1.7, +0.9) | +1.7 (+0.2, +3.3) | +2.1 (+0.0, +4.2) |
| S4 sex and race/ethnicity only | +1.0 (−0.2, +2.2) | +2.7 (+1.1, +4.3) | +1.7 (−0.4, +3.7) |
| E1 both grades in one model (exploratory) | −0.3 (−1.5, +0.8) | +1.2 (−0.2, +2.5) | +1.5 (−0.5, +3.5) |

S3 (logistic, log-odds per SD; first 5 imputations): grade 9 −0.019, grade 11 +0.051, difference +0.070 (95% CI −0.031 to +0.170).

E2 (exploratory; high = top tercile; difference in BA probability vs low in both grades, points):
high in grade 9 only −1.6 (−5.4, +2.1), high in grade 11 only +1.9 (−1.4, +5.2), high in both +0.6 (−2.5, +3.6).

## Verification and deviations

- Extract counts match the codebook for the checked items; replicate structure (exactly 50% zero
  replicate-to-full weight ratios) identifies standard BRR without a Fay factor, determined before any outcome model.
- Plan hash unchanged (`docs/PLAN_FREEZE_B2.md`).
- Deviation: the logistic sensitivity analysis (S3) used the first 5 of 20 imputations to limit runtime.
- Each replicate re-standardizes the support scores with its own weights (full replication of the standardization step).
- The replicate-weight SE for grade-9 support is close to a robust non-survey SE (design effect ≈ 0.93 in complete cases), plausible for a predictor that varies mostly within schools.

## Limitations

Observational; one item set about one subject's teacher; different teachers in different grades; grade-11
sample limited to students taking math in spring 2012; outcome from postsecondary administrative records
(missing for about a quarter of the analytic sample, imputed under missing-at-random).
