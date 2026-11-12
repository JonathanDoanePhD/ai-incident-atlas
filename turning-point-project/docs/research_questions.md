# Research questions

Status: draft v0.1 (2026-11-12). Refined from the project brief, the literature review
(`literature_review.md`) and the dataset audits (`dataset_audit.md`, `dataset_audit_early_childhood.md`).
Decisions and their reasons are logged in `research_decision_log.md`.

## Guiding question

When, how and for whom are supportive adult relationships and other developmental experiences
associated with meaningful positive change in young people's educational, psychological and
socioeconomic trajectories?

## Four concepts we keep separate

| Concept | Question it answers | Evidence that can address it |
|---|---|---|
| A. Developmental sensitivity | Is a stage especially *responsive* to a given input? | Randomised or quasi-experimental variation in the *age at exposure* (e.g. age-at-move designs, trials that randomise or stratify by age). Observational age-by-exposure interactions are at best suggestive. |
| B. Decision significance | Does a transition or decision have unusually large downstream consequences? | Longitudinal data around institutional transitions (e.g. course-taking at grade 9), with designs that handle selection into choices. |
| C. Intervention opportunity | Is intervening at a stage practical, reachable and cost-effective? | Programme delivery data, costs, take-up, trial effect sizes by age; not answerable from survey associations. |
| D. Observed trajectory change | Did a person's measured trajectory bend? | Dense repeated measures of the same construct; growth/change-point models. Describes change, does not explain it. |

A finding about one of these is not a finding about the others. For example, a larger
age-14 than age-17 association between adult support and attainment (an observational version
of A) says nothing about whether age 14 is the cheapest or most feasible time to intervene (C).

## Hypotheses (candidate, not preregistered)

H1–H7 from the brief are retained as a *hypothesis space*. Most cannot be tested with any single
public-use dataset (see the feasibility column). Only the narrowed confirmatory hypotheses in
`preregistration_draft.md` are candidates for preregistration.

| ID | Hypothesis | Feasibility with public data (summary; details in the audits) |
|---|---|---|
| H1 | Ages 8–11 especially consequential | Needs a cohort that starts before adolescence and reaches adult attainment with comparable support measures. See `dataset_audit_early_childhood.md`. |
| H2 | Ages 12–15 especially consequential (identity, belonging, agency) | Partially, via between-person age variation at baseline in adolescent cohorts, and retrospective mentor-onset age. Confounded with cohort/grade. |
| H3 | Ages 16–18 especially consequential | As H2. |
| H4 | Ages 18–24 especially consequential | Partially (NLSY97 and Add Health follow into adulthood), but exposure measures of adult support in this range are sparse. |
| H5 | No universal optimal age (individualised timing) | Testable only as heterogeneity: interactions with baseline circumstances; cannot be confirmed by a null age interaction (absence of evidence). Equivalence tests with a pre-set smallest effect size of interest are needed. |
| H6 | Cumulative support (duration/consistency) matters more than onset age | Testable with life-course model comparison (accumulation vs. critical/sensitive period) where the same support measure is repeated. |
| H7 | Transitions matter regardless of age | Grade-based cohorts (HSLS:09: grade 9 baseline; ELS:2002: grade 10) allow transition-anchored, but not age-anchored, comparisons. |

## Primary question for paper 1 (after the feasibility audit)

> Among U.S. adolescents in the NLSY97, does the association between reporting a very supportive
> parent in 1997 and highest grade completed by around age 40 differ with age at report (12–16),
> after adjustment for pre-exposure family and structural characteristics?

This narrows "supportive adults" to **parents** (D-009, needs PI sign-off), because no usable
adolescent cohort repeats a nonparental-mentor measure across ages in a way this project may analyse
(Add Health is excluded by its AI-use policy, D-008). Full plan: `statistical_analysis_plan.md`.

### Feasibility summary by hypothesis (from the audits)

| Hypothesis | Best available design | Strength |
|---|---|---|
| H1 vs H2 (8–11 vs 12–15) | PSID-CDS 2002/2007 identical "how close" items (mother, favourite teachers, other adults) → TAS/PSID attainment; FFCWS ages 9 vs 15 as replication | Weak–moderate: small overlap subsample; one measure per window |
| H2 vs H3 (12–15 vs 16–18) | NLSY97 round-1 support × age 12–16 | Moderate for associations; age confounded with cohort and co-residence |
| H4 (18–24) | Not credibly testable for adult support with audited public data | — |
| H5 (individualised timing) | Heterogeneity analyses in NLSY97 (exploratory, underpowered) | Weak |
| H6 (accumulation) | NLSY79 CYA HOME items repeated biennially (ages 6–14); NLSY97 1997–2000 repeated items | Moderate, with highly correlated exposures (`smith2015`) |
| H7 (transitions, grade 9) | HSLS:09 grade 9 vs 11; ELS:2002 grade 10 vs 12 | Weak–moderate: different teachers/universes across grades |

## Secondary and exploratory questions

1. Does any age pattern differ by baseline economic hardship, household structure or prior
   achievement? (Exploratory; heterogeneity analyses are underpowered by design.)
2. Is cumulative support (number of waves with support) a better description than timing
   (life-course structured approach)?
3. Which adolescent factors *predict* attainment out of sample (Study A), and how well calibrated
   are predictions across groups? Prediction is for understanding, not for screening individuals.
4. Do measured trajectories of engagement or expectations show population-level slope changes
   around school transitions (Study C)?

## What would count as an answer

- A credible *null* (age-invariant association, with a confidence interval excluding
  differences larger than a pre-stated smallest effect size of interest) is a substantive result
  and supports H5/H6 over H1–H4.
- A non-null age interaction would be reported as an association whose causal interpretation
  is limited by the threats in `causal_framework.md`, with sensitivity analyses (E-values,
  negative-control outcomes where available).
