# Analysis plan: study A4 — onset, continuity and closeness of natural mentors (Add Health public-use)

Status: v1, 2026-11-13. To be frozen (`PLAN_FREEZE_A4.md`) before anyone runs the script. **Human-run only**: Add Health's Conditions of
Use prohibit AI processing of Add Health data. This plan and `scripts/addhealth_offline/run_addhealth_a4_continuity.py` were written
from the public Wave I, III and IV codebooks and the *Guidelines for Analyzing Add Health Data* only. Scope approved by the PI on
2026-11-13 (D-044).

## Why, and a design constraint found in the codebook

Study A3 found no meaningful bachelor's-attainment difference between mentors who became important before 14 and at 14–17. The next
question is whether **how long a relationship lasted**, or **how close it is**, matters more than when it began.

The Wave III items do not allow duration to be separated from onset for most respondents:
- `H3MN8` asks "for how many years was [has] {he/she} been important in your life?"
- For the roughly 93% whose mentor is **still important** (`H3MN7` = 1), years important ≈ age at Wave III − onset age, so duration is
  fixed by onset and age.
- Duration carries independent information only for relationships that have **ended**: the mentor is no longer important (`H3MN7` = 0)
  or has died (`H3MN3` = 0).

The plan therefore studies **continuity**: whether the relationship ended before age 18 or lasted to 18 or beyond.

## Sample

- Waves I, III and IV public-use respondents with GSWGT134 > 0.
- A mentor at Wave III (`H3MN1` = 1) whose onset age (`H3MN6`) is 0–17, so the mentorship began before typical college entry.
- Bachelor's degree observed at Wave IV (`H4ED2`, as in A3).

## Variables

| Role | Construction |
|---|---|
| Ended | `H3MN3` = 0 (died) or `H3MN7` = 0 (no longer important). `H3MN7` is asked only if the mentor is living; codes 6, 8, 9 → missing. |
| Age the relationship ended | onset (`H3MN6`) + years important (`H3MN8`, 0–54; 96, 98, 99 → missing), for ended relationships. |
| **Exposure (primary)** | `ended_before_18` = 1 if ended and end age < 18; 0 if not ended, or ended at 18 or later. |
| Onset | `onset_lt14` = 1 if onset < 14; 0 if 14–17 |
| Mentor type | `H3MN2`: teacher/counselor 11; kin 1–10; community/other 12–21 (indicators; kin is the reference) |
| Closeness (secondary) | `H3MN11` (0 not at all … 4 very close; asked only if the mentor is living): `close` = 1 if 3–4 |
| Covariates | As A3: sex, age at Wave I, Hispanic, race indicators, parent education, log household income with a missing indicator |
| Weight, cluster | GSWGT134; CLUSTER2 |
| Age at Wave III | `IYEAR3` − birth year (`H1GI1Y`); used only for the descriptive duration check |

## Estimands

**Primary (Q-A4a).** The BA difference between relationships that ended before 18 and those that continued to 18 or beyond.
- **Model:** a weighted linear probability model, adjusted for onset < 14, mentor type and covariates, with SEs clustered on CLUSTER2
  and df = clusters − 1.
- **Tests:** a difference test (two-sided, α = .05) and an equivalence test within ±5 percentage points, the A3 margin.

**Secondary.**
- **Q-A4b:** the onset < 14 vs 14–17 contrast adjusted for continuity and type, compared with A3's unadjusted contrast.
- **Q-A4c:** among living mentors, the BA difference for "quite/very close" vs less close, adjusted as in the primary model.
  - Closeness is reported *at* Wave III (ages 18–26), around and after college entry, so it may reflect, not precede, educational
    paths.
  - It is interpreted descriptively.

**Descriptive.**
- The share of mentors still important.
- Among those, the correlation between years important and age at Wave III minus onset, to check the constraint above.
- The distribution of end ages for ended relationships.

## Power

The share of ended relationships is about 7% in the codebook's (restricted-use) frequencies; ended-before-18 is smaller. A rough
calculation assumes about 2,700 public-use respondents with onset < 18, about 190 ended (an upper bound for ended before 18), a BA rate
of about .30 and a design effect of 1.5. On that basis the minimum detectable difference is about **12 percentage points**, well
above the ±5 margin. **Q-A4a is expected to be imprecise**, and equivalence is very unlikely to be shown. The study is reported mainly
as estimation and as a check on what Add Health can and cannot separate.

## Disclosure and sharing

- **Suppression:** any estimate with a group × outcome cell below 10 is suppressed, as in A3.
- **Sharing:** the PI shares only interpreted results, the direction and the significance and equivalence labels (D-037). The labels
  follow the A3 rules: *equivalent* if TOST p < .05, otherwise *equivalence not established*, plus significant or not at α = .05.
