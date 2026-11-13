# Analysis plan: study A3 (when a natural mentor became important, Add Health public-use)

**Is the age at which a nonparental adult became important associated with bachelor's-degree
attainment by Wave IV?**

Status: v1, 2026-11-13. Frozen (`PLAN_FREEZE_A3.md`) before anyone opens Add Health respondent data.

## Who runs it, and why

Add Health's Conditions of Use prohibit using AI tools, including Claude, to manage, process or analyze Add Health data,
public-use included. They permit AI use with public codebooks and documentation. So:

- This plan and the script `scripts/addhealth_offline/run_addhealth_mentor_timing.py` were written by Claude **from the public
  codebooks and the Add Health *Guidelines for Analyzing Add Health Data* only**.
- A human analyst (the PI or a colleague) downloads the data and runs the script **on their own computer, outside any AI tool**,
  following `docs/addhealth_human_analyst_checklist.md`.
- Neither the data nor the script's output are given to an AI tool unless Add Health confirms in writing that sharing aggregate
  results is allowed.

## Question and hypotheses

Among Add Health public-use respondents interviewed at Waves I, III and IV, compare bachelor's attainment across four groups,
defined by the Wave III mentor items:

- **No mentor:** `H3MN1` = 0.
- **Onset before 14:** `H3MN1` = 1 and `H3MN6` 0–13 (the mentor first became important before age 14).
- **Onset at 14–17.**
- **Onset at 18 or later.**

- **Primary contrast (Q-A3):** onset before 14 vs onset at 14–17. Both groups' mentors began before typical college entry, so this is the
  cleanest test of early vs adolescent timing. It is tested for difference (two-sided, α = .05) and equivalence (±5 percentage
  points, TOST).
- **Secondary:** each onset group vs no mentor. Onset 18+ is reported but **not interpreted as a timing effect**: mentors who first
  become important at 18 or later are often met in college or work, so attainment may cause the mentoring rather than the reverse
  (Fruiht & Wray-Lake, 2013, found the largest association for this group).
- **Exploratory:** mentor type (`H3MN2`: teacher/counselor 11; kin 1–10; community/other 12–21) within each onset group;
  mentor duration (`H3MN8`, years important).

## Variables (verified in the public codebooks)

| Role | Variable | Coding |
|---|---|---|
| Mentor (Wave III) | `H3MN1` | 0 no, 1 yes; 6, 8, 9 → missing |
| Onset age | `H3MN6` | 0–25 years; 96, 98 → missing; 97 legitimate skip (no mentor) |
| Mentor type | `H3MN2` | 1–21 as above; 96–99 → missing |
| Duration | `H3MN8` | years; reserve codes → missing |
| Outcome (Wave IV) | `H4ED2` | 1 if ≥ 7 (bachelor's or higher: 7, 8, 9, 10, 11, 12, 13), 0 if 1–6; 96, 98 → missing |
| Sex | `BIO_SEX` | 1 male, 2 female |
| Age at Wave I | `IYEAR`, `H1GI1Y` | age ≈ interview year − birth year |
| Hispanic | `H1GI4` | 0/1; 6, 8 → missing |
| Race | `H1GI6A`–`H1GI6E` | marked 0/1 (White, Black, American Indian, Asian, other) |
| Parent education | `PA12` | 1–10 → years-of-schooling-like order; 10 never went → lowest; 96 → missing |
| Family income | `PA55` | thousands of dollars; log(1 + x); missing → median + indicator |
| Grades, Wave I | `H1ED11`–`H1ED14` | 1 A … 4 D or lower; 5+ → missing; GPA = 5 − mean (sensitivity only) |
| Cluster | `CLUSTER2` | public-use cluster (Guidelines, Table 3.3); no strata in public use |
| Weight | `GSWGT134` (Waves I, III, IV longitudinal weight) from the public Wave IV weights file; the script stops if it is absent | amended 2026-11-13 before any run (D-030); the frozen version fell back to `GSWGT4_2` |

## Model

Weighted linear probability model with cluster-robust (CLUSTER2) standard errors:
`BA = group indicators (reference: onset 14–17) + sex + age + Hispanic + race + parent education + log income + income-missing`.
Complete cases on all variables except income. Reported: group differences in percentage points with 95% CIs; Q-A3 TOST;
n by group; weighted BA rate by group (cells < 10 suppressed).

## Sensitivity (pre-specified)

S1 unweighted; S2 add Wave I GPA (a pre-mentor proxy only for onsets after Wave I); S3 logistic model (log odds);
S4 onset cut-point at 12 instead of 14 (before 12 vs 12–17).

## Caveats

Onset is recalled at ages 18–26 and refers to the *most influential* mentor; youth whose early mentors faded may not report them.
Wave I covariates may be measured after an early mentor began. Public-use is a subsample (about a third) of the full study.
Associations, not causal effects.
