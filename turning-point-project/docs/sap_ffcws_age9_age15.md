# Analysis plan: study R2 (Future of Families replication: age 9 vs age 15)

**Is youth-reported closeness to mother at age 9 or at age 15 more strongly associated with postsecondary education by age 22?
Future of Families and Child Wellbeing Study (FFCWS, formerly Fragile Families).**

Status: v1, 2026-11-13. Frozen (`PLAN_FREEZE_R2.md`) before anyone opens FFCWS respondent data. Variable names and codes were
taken from the official FFCWS metadata file. **Run by a human by default:** FFCWS public data are distributed through ICPSR, whose
LLM policy (approved 2024-12-11) allows public-use data with no-retention institutional AI systems only "with permission from
ICPSR" ("Please contact ICPSR prior to use"). If ICPSR gives written permission and the PI's Claude deployment qualifies, Claude may
run it. Otherwise follow `docs/human_run_checklist.md`.

## Variables (FFCWS metadata)

| Role | Name | Coding |
|---|---|---|
| Closeness to mom, age 9 | `k5a2e` | 1 extremely, 2 quite, 3 fairly, 4 (not very) close; negatives → missing. Exposure = 1 if extremely close |
| Closeness to mom, age 15 | `k6c17` | same coding |
| Education at 22 (outcome) | `ck7edu` | 1 less than HS, 2 HS or equivalent, 3 some college/technical, 4 college or graduate, 5 other. **Primary: any postsecondary (3–4) = 1; 1–2 = 0; 5 and negatives → missing.** Secondary: 4 = 1 |
| Child sex | `cm1bsex` | 1 boy, 2 girl |
| Mother race/ethnicity | `cm1ethrace` | categories as coded |
| Mother education (baseline) | `cm1edu` | 1–4 |
| Poverty ratio (baseline) | `cm1inpov` | log(1 + x) |
| Parents' relationship at birth | `cm1relf` | 1 married, 2 cohabiting, other |
| Mother age at birth | `cm1age` | years |
| Weight | `k7natwt` | age-22 national weight |

## Model

Linear probability model with both ages: `PS = a + b9·close9 + b15·close15 + covariates`, weighted by `k7natwt`, robust
standard errors. Primary contrast Δ = b9 − b15: tested for difference and equivalence (±3 points). The sample oversamples births
to unmarried parents in large U.S. cities, and the outcome at 22 is early for degree completion. Hence "any postsecondary" is primary.

## Sensitivity

S1 unweighted. S2 outcome = college or graduate (`ck7edu` = 4). S3 each age alone. S4 closeness 1–4 (reversed, z-scored).
