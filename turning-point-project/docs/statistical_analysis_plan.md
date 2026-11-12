# Statistical analysis plan: paper 1

**Working title:** When does adult support matter most? Parental support across adolescence and
educational attainment in the NLSY97.

Status: draft v0.3 (2026-11-12). **Not yet preregistered.** The NLSY97 public release was downloaded
only to read its codebook; respondent-level data have not been opened. All variable identifiers below were
verified in that codebook (`config/mappings/nlsy97.yaml` lists reference numbers and CSV columns). The design choices below are flagged in `research_decision_log.md` (D-008 to D-012)
and were signed off by the PI on 2026-11-12.

## 1. Why this design

The audits (`dataset_audit.md`, `dataset_audit_early_childhood.md`) found:

- **NLSY97** asks one identically worded question about each parent's supportiveness
  (`YSAQ-032` for mother, `YSAQ-053` for father) of every co-resident youth in round 1 (1997),
  when respondents were 12–16 years old as of 31 Dec 1996 (`CV_AGE_12/31/96`). Educational
  attainment is followed to round 21 (2023–24, ages ~39–44). Strata and PSU (`VSTRAT`, `VPSU`)
  are public. NLSY97 has **no repeated measure of nonparental mentors**, so the exposure is
  narrowed to parental support.
- **Add Health**, the only adolescent study with a natural-mentor item and onset age, is
  **excluded**: its Conditions of Use forbid processing its data, public-use included, with
  LLM/AI tools including Claude (verified 2026-11-12 at
  https://addhealth.cpc.unc.edu/conditions-of-use/). Fruiht & Wray-Lake (2013) already
  analysed that item.
- **HSLS:09** supports a grade-anchored companion analysis (grade 9 vs 11; §11).
- **PSID-CDS/TAS** can compare ages ~8–11 with ~12–15 using identical "how close" items, but
  only for a small overlapping subsample. This is planned as paper 2, not paper 1.

The design trades breadth (all supportive adults) for comparability: the same question, asked
the same way, in the same calendar year, to youths of different ages.

## 2. Questions and hypotheses

**Primary (confirmatory) question Q1.** Does the association between reporting a *very
supportive* mother in 1997 and highest grade completed by the latest round differ with age at
report (12–16)?

- H1a (difference): the age-12 vs age-16 contrast in the association, Δ = θ(16) − θ(12), ≠ 0.
- H1b (equivalence): |Δ| < SESOI (§7).
  Both are tested; the four possible verdicts are pre-specified in §7, and *inconclusive* is an
  allowed, reportable outcome.

**Secondary (confirmatory, Holm-adjusted with Q1).** Q2: the same for father support
(`YSAQ-053`), among youths living with a father figure.

**Secondary (descriptive).** θ(a) at each age 12–16 with 95% CIs, for mother and father support.

**Exploratory (labelled as such).** Outcome = BA or higher (`CVC_HIGHEST_DEGREE_EVER` ≥ 4);
heterogeneity by baseline poverty (`CV_HH_POV_RATIO` < 100 vs ≥ 100) and household structure;
the multi-item scales `FP_YMSUPP`/`FP_YFSUPP`; repeated support items in 1997–2000 analysed with
the life-course structured approach (`mishra2009`, `smith2015`); earnings and employment outcomes.

## 3. Population, sample and analytic sample

- NLSY97 cross-sectional and supplemental samples, N = 8,984 at round 1.
- Analytic sample for Q1: round-1 respondents in the `YSAQ-032` universe (living with a
  mother or mother figure) with a valid answer. The flow from 8,984 → analytic n will be reported
  (STROBE item 13). Outcome-missing cases are retained via multiple imputation.
- Selection into the item universe (co-residence) differs by age; see §8, S3.

## 4. Variables

| Role | Analytic name | NLSY97 question (reference no.) | Coding |
|---|---|---|---|
| Exposure | `mother_vs` | `YSAQ-032` (R03257.00), 1997 | 1 if "very supportive"; 0 if "somewhat" or "not very". Universe: lives with mother/mother figure (codebook: 8,607 valid; 77% "very") |
| Exposure (Q2) | `father_vs` | `YSAQ-053` (R03275.00), 1997 | as above. Universe: lives with father/father figure (6,436 valid; 68% "very") |
| Moderator | `age` | `CV_AGE_12/31/96` (R11940.00) | integer 12–16, centred at 14 |
| Outcome | `hgc` | `CVC_HGC_EVER` (Z90838.00) | highest grade completed, 0–20; code 95 ("ungraded", n = 18) → missing. **Observed only if the last interview (`CVC_RND`, Z90851.00) was round 14 (2010) or later**, when every respondent was at least 25; otherwise treated as missing and imputed (codebook: 8,297 respondents last interviewed in rounds 14–21) |
| Outcome (exploratory) | `ba_plus` | `CVC_HIGHEST_DEGREE_EVER` (Z90839.00) | 1 if ≥ 4 (BA/BS or higher); same observation rule |
| Confounder | `pov` | `CV_HH_POV_RATIO` (R12049.00), 1997 | household income-to-poverty ratio; log(1 + ratio) |
| Confounder | `hh_struct` | `CV_YTH_REL_HH_CURRENT` (R12053.00), 1997 | categories as coded; context, not deficit |
| Confounder | `sex` | `KEY!SEX` (R05363.00) | 1 male, 2 female |
| Confounder | `race_eth` | `KEY!RACE_ETHNICITY` (R14826.00) | 4 categories as coded; proxy for structural exposure to discrimination; aggregate reporting only |
| Confounder | `parent_ed` | `CV_HGC_RES_MOM` (R13027.00), `CV_HGC_RES_DAD` (R13026.00) | highest grade of residential mother and father; maximum of the two, missing-indicator for absent parent |
| Confounder | `urban` | `CV_URBAN-RURAL` (R12175.00), 1997 | as coded |
| Design | `strata`, `psu` | `VSTRAT` (R14897.00), `VPSU` (R14898.00) | |
| Weight | `w` | `SAMPLING_WEIGHT_CC` 1997 (R12361.01) | round-1 weight (two implied decimals). Target population: U.S. youths aged 12–16 in 1997. Attrition handled by multiple imputation, not by re-weighting; a custom longitudinal weight from the NLS weighting program is sensitivity S6b |

Missing-value codes −1 to −5 are recoded to NaN with reasons kept (`preprocessing.recode_missing`).
Valid skips (−4) mark out-of-universe cases and are never imputed.

**Excluded from the primary adjustment set (post-exposure or ambiguous):** ASVAB scores (taken in
1997–98, possibly after the support report), later expectations and engagement, grade in 1997
(partly a consequence of earlier school experiences; used in sensitivity S4).

**Prior achievement is weakly measured at baseline**, which is the main unresolved confounding
problem (reverse causation: easier, higher-achieving adolescents may elicit more parental
support). This is addressed only by sensitivity analyses (§8).

## 5. Model

Survey-weighted linear regression (`turning_point.modeling.fit_age_moderation`):

    hgc = β0 + β1·mother_vs + β2·(age−14) + β3·mother_vs·(age−14) + γ'L + ε

- θ(a) = β1 + β3(a − 14); Δ = θ(16) − θ(12) = 4β3.
- Variance by Taylor linearisation with `VSTRAT`/`VPSU`, df = #PSU − #strata (D-002; to be
  cross-checked against R `survey` before publication).
- Age enters linearly because it takes five integer values; the categorical-age model (each age
  its own θ) is sensitivity S1. Age main effects absorb cohort differences in mean attainment.

## 6. Missing data

Multiple imputation by chained equations, m = 40, imputing the outcome and covariates (not
exposures outside their universe), including the exposure × age product as a variable, with
auxiliary variables (later-round enrollment status, 1997 grade, ASVAB) used only in the imputation
model. Estimates pooled by Rubin's rules (`rubin_pool`, Barnard–Rubin df). Complete-case analysis
is sensitivity S2. Fractions of missing information are reported.

## 7. Inference, SESOI and multiplicity

- **Effect sizes**: θ(a) in years of schooling and in SD units of `hgc` (weighted SD), with 95% CIs.
- **SESOI**: |Δ| = 0.20 SD of `hgc`. Rationale: below this, a difference in association across
  adolescence would not plausibly change programme timing decisions, and it is comparable to
  small-to-modest meta-analytic mentoring effects (`dubois2011`, `raposa2019`). Signed off by the PI 2026-11-12 (D-011).
- **Power**: using codebook counts (mother item n = 8,607, 77% "very supportive"; father item n = 6,436,
  68%) and DEFF 1.5–2.5, the minimum detectable age-16 vs age-12 difference is ≈ 0.22–0.29 SD for mother support
  and ≈ 0.23–0.30 SD for father support (`scripts/power_age_interaction.py`;
  planning assumptions, not data). Q1 is therefore **unlikely to detect a difference near the
  SESOI and may be unable to establish equivalence**. Results will be interpreted with this in mind,
  emphasising interval estimates.
- **Decision rules** (two-sided α = 0.05 for H1a; TOST at α = 0.05, i.e. 90% CI, for H1b):
  equivalent / non-equivalent / different-from-zero-but-undetermined / inconclusive
  (`equivalence_test`).
- **Multiplicity**: Holm across {Q1, Q2} for H1a. Exploratory analyses use BH-FDR within families
  and are labelled exploratory regardless of p-values.

## 8. Sensitivity analyses (pre-specified)

| ID | Analysis | Threat addressed |
|---|---|---|
| S1 | Categorical age (12…16); report all θ(a) | linearity of age moderation |
| S2 | Complete-case analysis | MI model misspecification |
| S3 | Inverse-probability weighting for being in the item universe (co-residence) by age, using pre-exposure covariates | selection into the exposure universe at older ages |
| S4 | Adjust additionally for grade in 1997 | age–grade confounding |
| S5 | Ordinal exposure (3 levels) and the `FP_YMSUPP` scale | exposure coding |
| S6 | Unweighted, design-ignorant model | influence of weights |
| S6b | NLS custom longitudinal weight for respondents interviewed in round 1 and round ≥ 14, complete cases | attrition handling |
| S7 | E-values for θ(14) and for Δ (via `rr_from_smd`) | unmeasured confounding (e.g. youth temperament) |
| S8 | Add ASVAB as an (imperfect) prior-achievement proxy | reverse causation / selection on ability |

## 9. Interpretation rules (pre-committed)

- θ(a) is an **adjusted association**, not a causal effect. Δ ≠ 0 would mean the association
  differs by age at report; it would not show that support is more *effective* at that age
  (concept A vs D in `research_questions.md`), because who reports high support, and why, can
  itself change with age (see the methods simulator on the website).
- A null or equivalent result is reported with equal prominence.
- No result will be described as identifying a "critical period".

## 10. Reporting

STROBE checklist for cohort studies; flow diagram; weighted descriptive table by age; all
preregistered analyses reported; code and the exact Investigator tagset published; microdata not
redistributed.

## 11. Companion analysis (HSLS:09; secondary paper, exploratory until separately registered)

Grade-anchored version (H7, "freshman year"): association of school-adult support in fall of grade 9
(`S1TALKPROB`; math-teacher items `S1MTCH*`) versus the repeated spring-of-grade-11 items
(`S2MTCH*`, flagged as repeats in the codebook) with highest degree (`X6HIGHDEG`). Variance by the
200 BRR replicate weights (`fit_glm_replicate`; strata/PSU are suppressed in the public file).
Threats: grade-11 items cover only students taking math that term and refer to a different teacher;
grade-9 items were collected weeks into the transition. Comparison is of *grades*, not ages.

## 12. Status of pre-registration items

1. ~~Data terms~~: PI confirmed NLS (BLS) and NCES terms permit AI-assisted processing (D-012).
2. ~~Human-subjects determination~~: PI reports it is not a barrier (D-015).
3. ~~Variable verification~~: done against the round-21 codebook (2026-11-12).
4. ~~SESOI~~: signed off (D-011).
5. **Open:** read full texts of key mentoring meta-analyses for age-moderation results (the review is abstract-level). This informs the introduction, not the analysis.
6. **Open:** register on OSF, then open the data.
