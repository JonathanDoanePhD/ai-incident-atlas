# Analysis plan: study B2 (grade 9 vs grade 11)

**Does the association between perceived math-teacher support and bachelor's-degree attainment differ
between the start of high school (fall of grade 9) and grade 11? HSLS:09.**

Status: v1, 2026-11-12. Written and frozen (see `PLAN_FREEZE_B2.md`) **before HSLS:09 respondent-level
data were downloaded or opened**. Every variable below was read in the official public-use codebook
(`HSLS_2009-16_PETS_Pear_v1_0_CodeBook_RecordFileLayout.zip`, NCES DataLab). This is a personal
research project; the plan is not registered with a public registry.

## 1. Question and what it can and cannot show

This study tests the "freshman year" idea in the one public dataset that repeats the same
adult-support items in grade 9 and later in high school. It compares **grades, not ages**.
The grade-9 items were asked in **fall 2009**, a few weeks or months into high school. The grade-11
items were asked in **spring 2012** and refer to that term's math teacher, usually a different person.
The items describe a math teacher's fairness and teaching ("makes math interesting / easy to
understand"). They are closer to perceived teaching support than to a close mentoring relationship,
and we will describe them that way.

- **Q-B2 (primary):** Is θ11 − θ9 different from zero, and is it within ±3 percentage points?
  θg is the adjusted difference in the probability of a bachelor's degree or higher by June 2021 per
  1 SD higher perceived math-teacher support in grade g.
- A larger θ9 than θ11 would be *consistent with* (not proof of) a freshman-year window for teacher support.
  A larger θ11 would point the other way. Equivalence would suggest that, for this measure, grade 9 is
  not special.

## 2. Sample

Students who responded in the base year (fall 2009, grade 9) and the first follow-up (spring 2012),
and who answered the math-teacher items in **both** rounds, i.e. took math in both terms
(items' universe excludes −7 "legitimate skip"). Weight `W2W1STU` > 0. Flow will be reported.

## 3. Variables (all verified in the codebook)

| Role | Name | Coding |
|---|---|---|
| Exposure, grade 9 | `S1MTCHTREAT`, `S1MTCHINTRST`, `S1MTCHEASY` | 1 strongly agree … 4 strongly disagree. Recode so higher = more supportive: INTRST and EASY reversed (5 − x); TREAT ("treats some kids better than others") kept as is. Scale = mean of answered items (≥ 2 of 3). Standardised (weighted, analytic sample) |
| Exposure, grade 11 | `S2MTCHTREAT`, `S2MTCHINTRST`, `S2MTCHEASY` | Codebook marks each as a repeat of the S1 item. Same coding |
| Outcome | `X6HIGHDEG` | 1 if bachelor's (3), master's (5) or doctoral (7); 0 if 0, 1, 2, 8, 9, 10; −8/−9 missing → imputed |
| Covariates (grade 9) | `X1SEX`, `X1RACE` (8 categories → White, Black, Hispanic (4,5), Asian, other), `X1SES`, `X1PARPATTERN` (two bio/adoptive parents vs other; missing imputed), `X1TXMTSCOR` (grade-9 math theta score), `X1LOCALE` | Missing codes −9, −8 → missing |
| Imputation auxiliaries only | `X2TXMTSCOR`, `X4EVRATNDCLG`, `S1TALKPROB` | |
| Weight | `W2W1STU` with replicates `W2W1STU001`–`W2W1STU200` | BRR. The Fay coefficient will be taken from the NCES documentation if found; otherwise inferred from the replicate-weight structure (ratio of replicate to full weights) **before** any outcome model is fitted |

## 4. Model

For each grade g separately, survey-weighted linear probability model:
`BA = α + θg·z(support_g) + covariates`. Both models are fitted on the same students with the same
weights, in the full sample and in each replicate. The difference θ11 − θ9 is computed within each
replicate, so its variance reflects the correlation between the two estimates. Outcome and covariate
missingness: chained-equations imputation with predictive mean matching, m = 20, pooled by Rubin's rules.
Inference: t on 200 − 1 = 199 df (one per replicate minus one).

**SESOI:** |θ11 − θ9| < 0.03 (3 percentage points per SD), tested by two one-sided tests at α = .05. Chosen
before seeing data as the smallest difference that would plausibly change when a school or programme
invests in teacher–student support. Verdicts as in paper 1 (equivalent / non-equivalent /
different-but-undetermined / inconclusive).

## 5. Sensitivity and exploratory analyses

- S1: two positively worded items only (INTRST, EASY), excluding TREAT.
- S2: complete cases.
- S3: logistic model (log-odds scale).
- S4: no covariates except sex and race/ethnicity.
- Exploratory E1: both grades in one model (mutually adjusted). E2: four-pattern life-course
  comparison of high support (top tercile) in grade 9 and grade 11 (accumulation vs grade-specific).
  E3: grade-9 "there is a teacher or other adult in school I can talk to about problems"
  (`S1TALKPROB`), association only (no grade-11 counterpart).

## 6. Interpretation rules

Associations, not causal effects. Different teachers and terms across grades mean a difference in θ could
reflect measurement timing (fall vs spring), course level, or which students take math in grade 11, as
well as any true grade-specific importance. Results are reported whatever their direction.
