# Analysis plan: study R1 (PSID child supplement replication of paper 2)

**Is youth-reported closeness to mother, favorite teachers and other adults at ages 8–11 or at 12–15 more strongly associated with
bachelor's attainment? PSID Child Development Supplement (CDS) 2002 and 2007, with education from the PSID main interview.**

Status: v1, 2026-11-13. Frozen (`PLAN_FREEZE_R1.md`) before anyone opens PSID respondent data. **Human-run only**: PSID's
Conditions of Use state that "the use of Artificial Intelligence (AI) programs and Large Language Models (LLMs) in conjunction
with PSID data is strictly prohibited" (decision D-021). This plan and the script were written from PSID documentation only
(CDS codebooks, CDS-II/III user guides, the curated-variables codebook). Follow `docs/human_run_checklist.md`.

## Why

Paper 2 compared mothers' reports of warmth at 6–9 and 10–14 (NLSY79 Children and Young Adults). PSID adds **the child's own
report**, the **12-year boundary** of the original hypothesis, and **nonparental adults** (favorite teachers, other adults).

## Exposures (identical wording in 2002 and 2007; 1 not very, 2 fairly, 3 quite, 4 extremely close; 0/8/9 → missing)

| Adult | 2002 | 2007 |
|---|---|---|
| Mother (primary) | `Q23H5A` | `Q33H5A` |
| Favorite teachers (secondary) | `Q23H5G` | `Q33H5G` |
| Other adults outside school (secondary) | `Q23H5H` | `Q33H5H` |

Coded 1 = "extremely close" (as in paper 2's closeness measure). Early window: the 2002 report when the child was 8–11; adolescent
window: the 2007 report when the child was 12–15. Children with a report in both windows are analyzed (mainly those aged
8–10 in 2002).

## Outcome

Highest **years completed education** from the PSID main interview individual file (e.g. `ER34548` for 2017; add later waves'
"YEARS COMPLETED EDUCATION" variables in the Data Center). BA = 1 if the maximum across waves at which the person was ≥ 25 is
≥ 16; 0 if < 16; missing if never observed at ≥ 25. Codes 98/99 and 0 (inapplicable) → missing.

## Covariates

Sex and year of birth (individual file; confirm names in the Data Center), total family income 1998 (`ER16462`, log(1 + max(x, 0))),
race of household head (`ER15928`: 1 White, 2 Black, other).

## Model

Linear probability model, both windows together: `BA = a + bE·early + bA·adolescent + covariates`. Weight `CH07PRWT` (CDS-III
child weight); standard errors clustered on the 1968 family (`ER30001`). Primary contrast Δ = bE − bA for mother closeness; tested
for difference and equivalence (±3 percentage points). Teachers and other adults: same model, Holm-adjusted across the three adults.

## Sensitivity

S1 unweighted. S2 closeness as a 1–4 score (z-scored within year). S3 each window alone.

## Caveats

Small overlap sample (only children aged about 8–10 in 2002 have both windows). The 2002 and 2007 "favorite teachers" are different
people. Associations, not causal effects.
