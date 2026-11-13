# Analysis plan: study P3 — praise at ages 6–9 vs 10–14 within families (NLSY79 Children and Young Adults siblings)

Status: v1, 2026-11-13. To be frozen (`PLAN_FREEZE_P3.md`) before the analysis script is run and before the negative-control variable is
extracted. Scope and the ±3-point margin were approved by the PI on 2026-11-13 (D-044).

## Why

Paper 2 compared mothers' praise at child ages 6–9 and 10–14 *between* families. A family that praises more may also differ in many
other ways: stable warmth, values, resources, neighborhoods. Comparing **siblings within the same family** removes everything that is
constant within a family, including stable maternal warmth. This is the main confounder the project could not address so far.

**Not blind.** This plan is written with knowledge of Paper 2's results on the same data:
- adjusted βC ≈ 0.0;
- βD ≈ +1.5 points per SD;
- Δ ≈ −1.6 points;
- unadjusted Δ ≈ +1.0 points.

The within-family estimates have not been computed.

## Question

Within families, is a child's maternal praise at ages 6–9 more or less strongly associated with that child's bachelor's attainment than
praise at ages 10–14?

## Data and sample (as Paper 2)

**Sample.**
- Children born 1979–1995 with at least one praise report in each window and BA observed at the last Young Adult interview at age ≥ 25.
- Child-level covariates must be complete.
- Families (mothers, `MPUBID`) with two or more such children contribute to the within-family estimates. Single children are absorbed
  by the family fixed effect.
- Structure-only counts at planning (no outcome values used): 4,513 children in 1,819 families.

**Variables.**
- **Exposures:** `zC`, `zD`, the window praise scores of Paper 2 (normal scores of praise frequency, averaged within window).
  - They are standardized over Paper 2's full praise analytic sample (6,190 children), so "per SD" means the same as in Paper 2.
- **Outcome:** BA or higher, 0/1, as in Paper 2.
- **Child-level covariates** (vary within families):
  - sex;
  - birth order (2nd; 3rd or later);
  - birth-year group (1984–87, 1988–91, 1992–95);
  - mother's age at the child's birth, which within a family tracks the child's birth year;
  - share of the child's ages 0–14 in poverty;
  - mean log(1 + family income) over ages 0–14.
- Family-level covariates (race/ethnicity, mother's education, AFQT) are absorbed by the fixed effect.

## Model and estimands

**Primary model.** A linear probability model with mother fixed effects, estimated by the within transformation (demeaning by
family):

  `BA_ij = α_j + βC·zC_ij + βD·zD_ij + γ'X_ij + ε_ij`

Standard errors are clustered by family, with df = number of contributing families − 1. The model is unweighted, as Paper 2's primary
analysis was; child weights are not designed for within-family comparisons.

**Primary contrast.** Δ = βC − βD (6–9 minus 10–14), in percentage points of BA attainment per SD of praise.
- **Difference test:** two-sided, α = .05.
- **Equivalence test:** two one-sided tests within **±3 percentage points per SD** (90% CI), as in Studies 2–3. The PI approved this
  margin.

**Labels.** As in the earlier plans:
- *equivalent* if the TOST p < .05;
- *non-equivalent* if the 95% CI lies wholly outside the margin;
- *different, undetermined* if the 95% CI excludes 0 but none of the above holds;
- *inconclusive* otherwise.

**Power, before analysis.** This is computed from the exposures and covariates only, assuming outcome variance 0.29 × 0.71 with
0–40% of it between families. The SE of Δ is 1.5–2.0 points and the minimum detectable Δ at 80% power is **4.3–5.6 points**,
larger than the margin. Equivalence can be shown only if the estimate is near zero. The analysis can detect large timing
differences, not small ones.

## Secondary analyses (prespecified)

| ID | Analysis | Purpose |
|---|---|---|
| B1 | The same sample **without** family fixed effects, with Paper 2's full covariates and errors clustered by mother | Isolates what the fixed effect changes |
| C1 | Closeness ("extremely close", Paper 2's secondary exposure), same fixed-effects model, among children with closeness reported in both windows | Replication with a second construct |
| NC | **Negative-control outcome:** low birth weight (≤ 5.5 lb; `PST0010`, C0328700, 1 yes / 0 no, negatives → missing), same fixed-effects model with praise as exposure | Birth weight precedes both windows. Within-family associations would indicate that praise responds to child traits present from birth. Reported: βC, βD, and the joint Wald test |
| S1 | Primary model without the income and poverty covariates, which partly overlap the windows | Over-adjustment check |
| S2 | Estimates rescaled per **within-family** SD of each window score | Effect per realistic within-family difference |

## Interpretation rules

- The fixed effect removes stable family characteristics only. Child-specific traits that elicit praise and predict attainment remain
  confounders; NC probes them. Sibling-specific circumstances (birth order, family income at different ages) are partly adjusted.
- Within-family estimates are identified mainly by families whose siblings differ in BA: 484 families and 1,250 children at
  planning, a structure-only count.
- If B1 and the primary estimates differ, the plan does not claim which is "right". The difference is reported as how much of the
  between-family pattern is explained by stable family characteristics.
- **No causal claims.**

## Deviations

Any departure from this plan is recorded in the results document and the decision log, with a reason.
