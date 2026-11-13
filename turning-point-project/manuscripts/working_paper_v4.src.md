# Supportive relationships at different ages and later educational attainment: observational analyses in six U.S. cohorts

**Jonathan Doane, Ph.D.** · Working paper v4, 13 November 2026 · Revised after an independent methodological review · Not peer reviewed

> **Changes from v2.** v3 corrects overstated conclusions, describes the analysis plans accurately (frozen locally, not externally
> preregistered), reports estimates from re-runs with a corrected random-number seed, separates the constructs studied, reframes
> the equivalence tests and the accumulation analysis, and fixes bibliographic errors. Details: `docs/independent_review_response.md`.
> **v3.1 (same day).** Adds three analyses run by the author outside AI tools (Add Health, PSID, Future of Families; reported
> qualitatively), the NLS custom-weight sensitivity analysis, an independent R reproduction of the survey estimates, a STROBE checklist
> with covariate, study-size and participant-flow reporting, and full-text corrections to the literature summary.
> **v4.** Adds Study 8, a within-family (sibling) comparison of praise at 6–9 and 10–14 that removes stable family characteristics, and
> Study 9, an author-run Add Health analysis of whether mentoring relationships continued to age 18. Records the second analyst's
> confirmation of the results.

## Abstract

**Background.** Youth programs often appeal to developmental windows, ages when supportive adults are thought to matter most.
Evidence that the long-run association of support with outcomes differs by age is scarce.
**Methods.** We analyzed six U.S. cohorts. Each analysis followed a written plan committed with file hashes to a public
repository before its data were opened. These are locally frozen plans, not external preregistrations, and all but the first were
written after earlier results were known. (1) NLSY97: adolescents' reports of a very supportive mother or father, asked
identically at ages 12–16, and highest grade completed around age 40. (2) HSLS:09: ratings of the current math teacher in grade 9 and
grade 11 (usually different teachers), and bachelor's-degree attainment by 2021. (3) NLSY79 Children and Young Adults: mothers' reports of
praise at child ages 6–9 and 10–14, and bachelor's attainment. (4) NLSY97, exploratory: four annual support reports, 1997–2000.
These four vary **age or grade at measurement**, not the age at which relationships began, and none concerns mentoring. Three further
analyses were run by the author outside AI tools, as the data providers require, and are reported qualitatively: (5) Add Health, age at
which a natural mentor first became important (before 14 vs 14–17); (6) PSID Child Development Supplement, children's closeness to
mother, favorite teachers and other adults at 8–11 vs 12–15; (7) Future of Families, closeness to mother at 9 vs 15. Two follow-up
studies addressed the main weaknesses of the first round: (8) NLSY79 Children and Young Adults siblings, comparing praise at 6–9 and
10–14 within families to remove stable family characteristics; (9) Add Health, author-run, whether a mentoring relationship begun before
18 continued to age 18 or ended earlier.
**Results.** Reported support was modestly associated with later attainment. A very supportive mother at age 14 was associated with
{{P1m_t14}} years of schooling ({{P1m_t14_ci}}), and similarly for fathers. In early adolescence, 1 SD more maternal praise was associated with
{{P2_b1014}} percentage points in bachelor's attainment. Contrasts across ages or grades were imprecise and not statistically
significant: age 16 vs 12, mothers {{P1m_d}} years ({{P1m_d_ci}}) and fathers {{P1f_d}} ({{P1f_d_ci}}); grade 11 vs 9, {{B2_d}} points
({{B2_d_ci}}); ages 6–9 vs 10–14, {{P2_d}} points ({{P2_d_ci}}). Equivalence tests met their prespecified margins for fathers and for
grade 9 vs 11, but those margins were as large as the associations themselves. In the exploratory analysis, more years of reported
support went with more schooling ({{AC_slope}} grades per year, {{AC_slope_ci}}). That pattern was described equally well by
"supportive in all four years" and by "any loss of support". In the author-run analyses, no timing contrast was statistically
significant. Mentors who first became important at 14–17 were associated with slightly higher bachelor's attainment than mentors
from before 14, and differences larger than 5 percentage points were ruled out. The PSID and Future of Families contrasts were
inconclusive, with point estimates for mothers favoring the earlier window. **Within families (Study 8; {{P3_n}} children in {{P3_fam}}
families), the timing difference for praise was {{P3_d}} points per SD ({{P3_d_ci}}) and equivalent within ±3 points**, while the same
children compared across families showed {{P3B_d}} points ({{P3B_d_ci}}; p = {{P3B_p}}), favoring the later window. Relationships that continued to 18 were
associated with higher attainment than those that ended earlier, but the difference was not significant and inconclusive (Study 9).
**Conclusions.** In these data, no timing contrast showed support or mentoring at earlier ages to be more strongly associated with
later attainment than at later ages, and point estimates did not consistently favor either. For natural mentors, onset before 14 was
not associated with a meaningful advantage over onset at 14–17. Comparing siblings removed the between-family tendency for later praise
to look more important, which therefore reflects stable family characteristics rather than age. The analyses do not show that
developmental timing is irrelevant.
Nonlinear and moderate timing differences cannot be excluded, mentor onset was reported retrospectively, and the cumulative-support
pattern may reflect stable family characteristics rather than accumulating exposure.

## 1. Introduction

The idea of a *turning point*, an experience that redirects a life trajectory, is central to life-course research [@elder1998; @rutter1996].
Rutter stressed that turning-point effects are heterogeneous and depend on the qualities of experience more than on age alone
[@rutter1996]. Adolescence has been described as a period of heightened plasticity and opportunity for intervention [@dahl2018], but a
review of sensitive periods in adolescent development found concrete evidence mostly lacking [@fuhrmann2015].

The clearest evidence on the timing of environmental exposure comes from housing mobility. In the Moving to Opportunity experiment,
moving to a lower-poverty neighborhood before age 13 improved college attendance and earnings, while moving as an adolescent did not
[@chetty2016]. Quasi-experimental estimates suggest roughly linear gains per childhood year of exposure [@chetty2018]. Skill-formation models
emphasize that early skills raise returns to later investment [@cunha2007]. Estimates from one such model suggest that substitutability
between earlier and later investment falls at later stages for cognitive skills but rises for noncognitive skills [@cunha2010].

For supportive relationships the evidence on timing is thinner. Mentoring programs show small-to-modest average benefits
[@dubois2002; @raposa2019]. In one program, benefits were concentrated in relationships lasting a year or longer, although match length
was not randomized [@grossman2002]. Teacher–student relationship quality is associated with engagement and achievement, with larger associations in studies of
higher grades, except that negative relationships mattered more in primary school; the authors caution that secondary-school studies
mostly relied on students reporting both measures [@roorda2011]. In an updated meta-analysis, only the link between positive relationships and engagement was stronger in secondary than in primary school
[@roorda2017]. The transition to high school is a documented point of disruption [@benner2009], and ninth-grade outcomes predict dropout
[@neild2008]. One study of when natural mentors became important compared only young adults who had a mentor. Mentors who became important
during high school were not associated with more attainment than mentors from before high school, and mentors from after high school
were associated with somewhat more. Timing was reported retrospectively, the models adjusted for twelfth-grade grades that followed many
of the earlier mentorships, and post-high-school mentors partly reflect continued education [@fruiht2013].

The program literature tests age only between studies. The largest meta-analysis coded age as under 8, 8–10, 11–14 and 15–18, found
favorable effects in every group and no association of age with effect size, and concluded that benefits are "not confined to a particular
stage of development" [@dubois2011]. Earlier and later meta-analyses also found no significant age moderation
[@dubois2002; @raposa2019; @vandam2018; @vandam2021]. In one school-based mentoring trial, impacts did not differ reliably between elementary
and middle/high school students [@herrera2007report]. Within a program, age predicted how long matches lasted: matches with 13–16-year-olds ended
sooner than with 10–12-year-olds [@grossman2002]. Youth age was unrelated to relationship quality, while longer matches had higher quality
[@rhodes2005]. Between-study age comparisons are confounded with program type, and none compares early childhood with adolescence.

We distinguish four questions that are often conflated: whether a stage is especially responsive to an input (developmental sensitivity);
whether a transition has unusually large consequences; whether intervening is especially practical at a stage; and whether an individual's
trajectory visibly changes. Our designs address only an observational version of the first. They also differ from mentoring research in
two ways that limit what they can show. The adults studied are parents and math teachers, and what varies is the age at which support was
**reported**, not the age at which a relationship **began** or how long it **lasted** (Table 1).

**Table 1.** Constructs analyzed (full comparison: `docs/construct_validity.md`).

| Study | Construct | Informant | Adult | Ages at measurement | Exposure years; outcome | Onset observed | Duration observed |
|---|---|---|---|---|---|---|---|
| 1 NLSY97 | "Very supportive" global rating | Youth | Resident mother / father | 12–16 (one report) | 1997; highest grade at last interview, 2010–2024 (most at ages 39–44) | No | No |
| 2 HSLS:09 | Perceived math-teacher fairness and teaching | Student | That term's math teacher (usually different in each grade) | Fall grade 9; spring grade 11 | 2009, 2012; degree by June 2021 (about age 25) | No | No |
| 3 NLSY79 Children and Young Adults | Praise frequency (behavior) | Mother | Mother | 6–9 and 10–14 (biennial) | 1986–2010; degree at last interview at age ≥ 25, through 2020 | No | No |
| 4 NLSY97 1997–2000 | Repeated "very supportive" ratings | Youth | Mother | 12–17 (four annual reports) | 1997–2000; as Study 1 | No | Repeated ratings only |

## 2. General methods

**Plans.** Each analysis followed a written plan whose files were hashed and committed to the project's public repository before the
respondent-level data were downloaded or opened. Commit times precede data-file creation times. These are locally frozen plans, not
registrations with an external registry. Studies 2–4 were planned after Study 1's results were known.

**Estimation.** We used survey weights and design-based variance where the design allowed: Taylor linearization with strata and PSUs
(Study 1), 200 balanced-repeated-replication weights (Study 2), and clustering by mother (Study 3). Missing outcome and covariate values were
multiply imputed by chained equations with predictive mean matching [@white2011] and pooled by Rubin's rules [@rubin1987]. An audit found that
the imputation random-number generator had not been seeded, so results were re-run with an explicit seed. Re-runs are now byte-identical,
and estimates differ from those in v2 only by Monte Carlo error (Table 2 footnote). Each primary contrast was tested for difference from zero
(two-sided, α = .05) and for equivalence within a prespecified margin by two one-sided tests (90% CI). Unmeasured confounding was summarized
with E-values [@vanderweele2017]. Reporting follows STROBE [@vonelm2007]; the completed checklist is `docs/strobe_checklist.md`.

**Covariates and study size.** Models adjusted for background characteristics measured before or at the first exposure:
- **Study 1 and Study 4:** sex, race/ethnicity, household poverty ratio, urban residence, parental education and household structure.
- **Study 2:** sex, race/ethnicity, socioeconomic status, two-parent household, grade-9 mathematics score and school locale.
- **Study 3:** child sex, race/ethnicity, birth-year group, birth order, mother's age at birth, mother's education and AFQT
  percentile, and family income and poverty in childhood.

Sample sizes were fixed by the cohorts. Before analysis, Study 1's minimum detectable age-16 vs age-12 difference was estimated at
about 0.22–0.30 SD, so it was not powered to detect differences near its 0.20 SD margin. Participant flow is in Appendix A.
Participant characteristics, missing data per variable and unadjusted estimates are in `docs/strobe_tables.md`. Unadjusted associations
were larger than adjusted ones, as expected from confounding by family background. Unadjusted timing contrasts were near zero or slightly
favored the earlier measurement in Studies 1 and 3, so the adjusted tendency toward later measurement in those studies depends partly on
covariate adjustment.

**Reproduction in R.** The confirmatory survey estimates of Studies 1 and 2 (primary and complete-case) were re-estimated independently
in R with the `survey` and `mitools` packages, from the same analysis-ready data. All 30 quantities agreed to within 10⁻¹¹
(`crosscheck/`). Data preparation and imputation were not re-implemented in R; a second analyst independently confirmed the results.

**Analyses run by the author.** Add Health, PSID and the Future of Families study restrict AI processing of their data. For these studies,
plans and analysis scripts were written with AI assistance from public documentation only, frozen with file hashes, and run by the author
on a personal computer outside AI tools. The author's interpretations are reported here; no numerical estimates were shared with AI tools.
- **Study 5 (Add Health, public-use Waves I, III and IV).** Exposure: age at which a nonparental adult who "made an important positive
  difference" first became important, reported at Wave III. Primary contrast: onset before 14 vs 14–17. Outcome: bachelor's degree by
  Wave IV. Margin: ±5 percentage points.
- **Study 6 (PSID Child Development Supplement 2002 and 2007).** Exposure: the child's own report of being extremely close to their
  mother, favorite teachers and other adults, at 8–11 and at 12–15. Outcome: bachelor's degree by age 25 or later. Margin: ±3 points,
  with Holm adjustment across the three adults.
- **Study 7 (Future of Families and Child Wellbeing Study).** Exposure: extremely close to mother at age 9 and at age 15. Outcome: any
  postsecondary education or training by 22. Margin: ±3 points.
- **Study 9 (Add Health, follow-up to Study 5).** Among mentors who became important before 18, whether the relationship ended before
  age 18 (mentor no longer important, or deceased, with onset plus years important under 18) or continued. Outcome: bachelor's degree by
  Wave IV. Margin: ±5 points. The codebook showed that for mentors still important at Wave III, "years important" equals age minus onset,
  so duration cannot be separated from onset. Continuity is the only stability contrast the items allow. Expected minimum detectable
  difference: about 12 points.

**Study 8: within-family design.** Planned after the first round as the main test of family confounding (plan frozen before
analysis; `docs/sap_p3_cya_siblings.md`).
- **Model:** Study 3's praise windows in a linear probability model with mother fixed effects, so each child is compared with their
  own siblings.
- **Covariates:** child-level only (sex, birth order, birth-year group, mother's age at the birth, childhood income and poverty).
- **Variance:** standard errors clustered by family.
- **Margin:** ±3 points per SD, as in Study 3.
- **Negative control:** low birth weight as the outcome, which praise at 6–14 cannot affect.
- **Power:** before analysis, the minimum detectable difference was 4.3–5.6 points.
- **Disclosure:** the plan was written knowing Study 3's between-family results.

**What the equivalence margins mean.** The margins (±0.20 SD in Study 1; ±3 percentage points per SD in Studies 2–3) were set before the data
were seen. They turned out to be as large as or larger than the associations being compared. Equivalence therefore rules out only differences
larger than roughly the whole association. It is not evidence that timing is irrelevant.

## 3. Results

**Table 2.** Primary estimates (95% CI). Positive numbers mean more schooling (Study 1, years) or higher probability of a bachelor's degree
(Studies 2–3, percentage points per SD).

| Study | Earlier measurement | Later measurement | Difference (prespecified contrast) | p | Equivalence (margin; 90% CI) |
|---|---|---|---|---|---|
| 1 NLSY97, mothers | age 12: {{P1m_t12}} | age 16: {{P1m_t16}} | 16 − 12: {{P1m_d}} ({{P1m_d_ci}}) | {{P1m_p}} (Holm {{P1_holm}}) | not shown (±0.20 SD; {{P1m_eq_ci}} SD) |
| 1 NLSY97, fathers | age 12: {{P1f_t12}} | age 16: {{P1f_t16}} | 16 − 12: {{P1f_d}} ({{P1f_d_ci}}) | {{P1f_p}} (Holm {{P1_holm}}) | shown (±0.20 SD; {{P1f_eq_ci}} SD) |
| 2 HSLS:09 | grade 9: {{B2_t9}} | grade 11: {{B2_t11}} | 11 − 9: {{B2_d}} ({{B2_d_ci}}) | {{B2_p}} | shown (±3; {{B2_eq_ci}}) |
| 3 NLSY79 Children and Young Adults, praise | 6–9: {{P2_b69}} | 10–14: {{P2_b1014}} | (6–9) − (10–14): {{P2_d}} ({{P2_d_ci}}) | {{P2_p}} | not shown (±3; {{P2_eq_ci}}) |
| 8 Same cohort, siblings (mother fixed effects) | 6–9: {{P3_b69}} | 10–14: {{P3_b1014}} | (6–9) − (10–14): {{P3_d}} ({{P3_d_ci}}) | {{P3_p}} | shown (±3; {{P3_eq_ci}}) |

Re-runs with the corrected seed changed estimates by at most {{MC_maxdiff}} relative to v2; no test decision changed.

**Study 1 (NLSY97).** Of 8,984 respondents, 8,607 rated a mother figure and 6,436 a father figure. At age 14, a very supportive rating was
associated with {{P1m_t14}} years of schooling for mothers ({{P1m_t14_ci}}) and {{P1f_t14}} for fathers ({{P1f_t14_ci}}), about 0.15 SD. The
prespecified linear contrast between ages 16 and 12 was not statistically significant for either parent. The E-value for the age-14 association
was {{P1m_E}}, and adding a cognitive test score reduced it by a fifth to a quarter, so modest unmeasured confounding could account for it.
Estimates for each age separately were irregular (higher at 14 and 16 than at 13 and 15). A post-hoc audit test of any difference across the five
ages, in complete cases, gave p = {{AUD_A_m}} (mothers) and p = {{AUD_A_f}} (fathers). The linear contrast does not capture such patterns.

**Study 2 (HSLS:09).** Among {{B2_n}} students who rated their math teacher in both grades, the grade-9 rating was not associated with bachelor's
attainment after adjustment ({{B2_t9}} points per SD), and the grade-11 rating was weakly associated ({{B2_t11}}). The difference was within
the ±3-point margin, but the margin is about three times the grade-11 association. Two sensitivity analyses (positively worded items only;
complete cases) found the difference statistically significant at p < .05, in the direction of grade 11. The grade-9 items were asked weeks
into high school and concern a different teacher than the grade-11 items.

**Study 3 (NLSY79 Children and Young Adults).** For {{P2_n}} children of {{P2_mothers}} mothers, praise at 6–9 was not associated with
bachelor's attainment ({{P2_b69}} points per SD), while praise at 10–14 was ({{P2_b1014}}). The difference was imprecise. A post-hoc audit using
exactly one report per window, which equalizes measurement reliability, gave a difference of {{AUD_B_one}} points ({{AUD_B_one_ci}}). That
contradicts a reliability explanation, but it is a post-hoc result.

**Study 4 (NLSY97, exploratory).** Among {{AC_n}} youths with four annual reports and complete covariates, each additional year rated very
supportive went with {{AC_slope}} more grades completed ({{AC_slope_ci}}). A test of equal weights across years did not reject (p = {{AC_wald_p}}),
but non-rejection is not evidence for accumulation. In a post-hoc audit:
- A stricter test, that only the number of supportive years matters, was borderline (p = {{AUD_C_within}}).
- A model with an indicator for "very supportive in all four years" ({{AUD_C_all4}} grades) absorbed the count entirely.
- A model with "any loss of support" fit best on an approximate information criterion.

The analyzed youths were more advantaged than those excluded for incomplete histories, though reweighting for inclusion left the estimates
unchanged. A stable family characteristic measured with error would produce the same pattern as cumulative exposure. **These data do not
demonstrate a cumulative effect of support.**

**Study 8 (siblings).** Among {{P3_n}} children in {{P3_fam}} families with two or more children, praise at 6–9 and at 10–14 had
nearly the same within-family association with bachelor's attainment ({{P3_b69}} and {{P3_b1014}} points per SD; neither significant). The
difference, {{P3_d}} points ({{P3_d_ci}}), was equivalent within ±3 (90% CI {{P3_eq_ci}}; TOST p = {{P3_tost}}).
- **Without the fixed effect, same children:** the difference was {{P3B_d}} points ({{P3B_d_ci}}; p = {{P3B_p}}), favoring the later
  window. With the fixed effect on exactly those children it was {{P3BF_d}} ({{P3BF_d_ci}}).
- **Without income and poverty covariates:** {{P3S1_d}} ({{P3S1_d_ci}}).
- **Closeness:** {{P3C_d}} points ({{P3C_d_ci}}), inconclusive. Closeness at 10–14 was associated with attainment within families
  ({{P3C_b1014}}) and closeness at 6–9 was not ({{P3C_b69}}).
- **Negative control:** praise did not predict low birth weight within families (joint p = {{P3NC_p}}).
- **What drives the estimate:** mainly the {{P3_disc}} families whose siblings differ in bachelor's attainment.

**Studies 5–7 and 9 (run and interpreted by the author; no estimates shown).**
- **Study 5 (Add Health):** bachelor's attainment was slightly higher when a natural mentor first became important at 14–17 than before
  14. The difference was not statistically significant, and equivalence within ±5 percentage points was supported.
- **Study 6 (PSID):** associations were more positive at 8–11 for mothers and favorite teachers, and at 12–15 for other adults. No
  difference was significant after Holm adjustment, and none was shown equivalent within ±3 points. All three are inconclusive.
- **Study 7 (Future of Families):** the association of closeness to mother with postsecondary participation was more positive at age 9
  than at 15. The difference was not significant and equivalence was not shown. It is inconclusive.
- **Study 9 (Add Health):** attainment was higher when a mentoring relationship continued to 18 or later than when it ended before 18.
  The difference was not significant, and equivalence within ±5 points was not shown. It is inconclusive, as expected given its power.

## 4. Discussion

Across these observational analyses, reported support from parents, and from math teachers in grade 11, was modestly associated with later
educational attainment. No timing contrast was statistically significant. In Studies 1–3, point estimates mostly favored later measurement.
In the author's replications with children's own reports (Studies 6–7), estimates for mothers favored the earlier window, so the direction
is not consistent. The one analysis of when a natural mentor became important (Study 5) ruled out an advantage of more than 5 percentage
points for onset before 14 over onset at 14–17. This agrees with the full text of the only earlier study of mentor timing, which found no
difference between mentors from before and during high school [@fruiht2013].

The sibling comparison (Study 8) is the strongest design here, because it removes everything stable within a family. In it, the timing
difference for praise was close to zero and equivalent within the margin. Between families, the same children showed a later-window
advantage, which therefore reflects family characteristics associated with both later praise and college, not the age of the child.
Within families, praise was only weakly associated with attainment at either age. Most of the praise–attainment association lies between
families.

Taken together, this is weak-to-moderate evidence against a strong early-window hypothesis for these constructs. It is not evidence that
timing does not matter:

1. The prespecified contrasts were imprecise, and the equivalence margins were as large as the associations compared.
2. Linear contrasts can miss nonlinear age patterns.
3. Except in Studies 5 and 9, we observed age at measurement, not age at relationship onset or duration. Their onset ages and
   relationship histories were reported retrospectively, in early adulthood, and in Add Health duration cannot be separated from onset.
4. Later measurements are closer to educational decisions, so larger later associations may reflect proximity rather than sensitivity.
5. Apart from Studies 5 and 9's natural mentors, the adults were parents and teachers, not mentors; none of the studies concerns formal
   mentoring programs.
6. The sibling design removes only stable family characteristics. Child traits that develop after birth and elicit praise can still
   confound it, and families with two or more children are not representative of all families.

The repeated-report analysis shows that consistently reported support goes with more schooling. It cannot separate accumulation, stability,
loss of support, and stable family characteristics. All results are observational: more capable or easier-going young people may both elicit
and report more support.

### 4.1 Implications for youth mentoring (tentative)

These analyses cannot show when mentoring should begin. Program evidence from the literature, which is between-study and partly
non-randomized, suggests that effects do not depend strongly on participants' age [@dubois2011], that longer matches go with larger
benefits [@grossman2002; @rhodes2005], and that matches with older adolescents end sooner [@grossman2002]. A mentoring program could
reasonably prioritize relationship quality and continuity across transitions while treating the timing question as open. Our only
continuity analysis (Study 9) pointed the same way but was too imprecise to add evidence. Answering it will
require designs that vary when relationships begin, ideally randomized.

### 4.2 Limitations

All analyses are observational and use single-informant measures. Studies 1–4 and 6–8 vary age at measurement within single cohorts, where age is entangled
with birth year, household composition and distance to the outcome. Outcomes were measured at different ages across studies. Attrition was
handled under a missing-at-random assumption. NLS custom longitudinal weights left Study 1's estimates essentially unchanged; some planned
exploratory analyses were not run. The survey estimates were reproduced in R from the same analysis-ready data, and a second analyst
confirmed the results. Studies 5–7 and 9 are reported only as the author's qualitative interpretations, so readers cannot check their
estimates. Study 8 is unweighted and complete-case on the outcome. Plans were frozen locally rather than registered externally. Each cohort represents a defined U.S. population: youths aged
12–16 in 1997 (Studies 1 and 4), ninth-graders in fall 2009 (Study 2), children born 1979–1995 to a national cohort of women born
1957–1964 (Studies 3 and 8), and, for Studies 5–7 and 9, adolescents in grades 7–12 in 1994–95, PSID families' children, and children born in large
U.S. cities in 1998–2000 (Add Health for both 5 and 9). Results may not generalize to other countries, later cohorts or formal mentoring programs.

## 5. Conclusion

In six U.S. cohorts, adult support reported at different ages was modestly associated with later education. Support measured, or mentoring
begun, earlier was not more strongly associated with outcomes than support measured or mentoring begun later. Comparing siblings, praise
at 6–9 and at 10–14 carried the same weight within ±3 points. These results do not establish that developmental timing is irrelevant, and
they do not show that support has cumulative causal effects. They argue against assuming a narrow early window for parental and teacher support,
and for studies that measure when relationships begin, how long they last, and how good they are.

## Data, code and disclosure

Studies 1–4 and 8 use public data (BLS: NLSY97, NLSY79; NCES: HSLS:09). Studies 5–7 and 9 use Add Health public-use, PSID and Future of
Families data, analyzed by the author outside AI tools under those providers' terms. Code, frozen plans with file hashes, variable mappings,
full results for Studies 1–4 and 8 and the audit are in the project repository; no respondent-level data are redistributed. Funding: no external funding. The author hopes to found a youth mentoring organization, which creates an
interest in particular findings. Analysis code and drafting were assisted by an AI system; the author is responsible for the content.

## Appendix A. Participant flow (Studies 1–4 and 8)

| Study 1 NLSY97 | Mothers | Fathers |
|---|---|---|
| Round-1 respondents | 8,984 | 8,984 |
| In item universe (living with a parent figure of that sex) | 8,610 | 6,443 |
| Valid answer (analyzed) | 8,607 | 6,436 |
| Attainment observed at an interview in 2010 or later (age ≥ 25) | 7,838 | 5,816 |
| Attainment imputed (m = 40) | 769 | 620 |

| Study 2 HSLS:09 | n |
|---|---|
| Student records | 23,503 |
| Responded in grades 9 and 11 (longitudinal weight > 0) | 18,623 |
| Rated math teacher in both grades (analyzed) | 14,259 |
| Degree observed / imputed (m = 20) | 10,592 / 3,667 |

| Study 3 NLSY79 Children and Young Adults | n |
|---|---|
| Children | 11,551 |
| Born 1979–1995 | 9,270 |
| Praise reported in both windows (analyzed) | 6,190 children of 3,138 mothers |
| Outcome observed (age ≥ 25) / imputed (m = 20) | 5,680 / 510 |

| Study 4 NLSY97 accumulation | n |
|---|---|
| Aged 12–14 in 1996 | 5,419 |
| Mother-support item answered in all four rounds, 1997–2000 | 3,870 |
| Complete covariates and observed outcome (analyzed) | 2,566 |

| Study 8 NLSY79 Children and Young Adults siblings | n |
|---|---|
| Praise analytic sample (Study 3) | 6,190 children of 3,138 mothers |
| Outcome observed and child covariates complete, in families with 2+ such children (analyzed) | {{P3_n}} children in {{P3_fam}} families |
| Families whose siblings differ in bachelor's attainment | {{P3_disc}} |

## References

{{REFERENCES}}
