# Supportive relationships at different ages and later educational attainment: four observational analyses in three U.S. cohorts

**Jonathan Doane, Ph.D.** · Working paper v3, 13 November 2026 · Revised after an independent methodological review · Not peer reviewed

> **Changes from v2.** v3 corrects overstated conclusions, describes the analysis plans accurately (frozen locally, not externally
> preregistered), reports estimates from re-runs with a corrected random-number seed, separates the constructs studied, reframes
> the equivalence tests and the accumulation analysis, and fixes bibliographic errors. Details: `docs/independent_review_response.md`.

## Abstract

**Background.** Youth programs often appeal to developmental windows, ages when supportive adults are thought to matter most.
Evidence that the long-run association of support with outcomes differs by age is scarce.
**Methods.** We analyzed three national U.S. cohorts. Each analysis followed a written plan committed with file hashes to a public
repository before its data were opened. These are locally frozen plans, not external preregistrations, and three of the four
were written after the first study's results were known. (1) NLSY97: adolescents' reports of a very supportive mother or father, asked
identically at ages 12–16, and highest grade completed around age 40. (2) HSLS:09: ratings of the current math teacher in grade 9 and
grade 11 (usually different teachers), and bachelor's-degree attainment by 2021. (3) NLSY79 Children and Young Adults: mothers' reports of
praise at child ages 6–9 and 10–14, and bachelor's attainment. (4) NLSY97, exploratory: four annual support reports, 1997–2000.
All analyses vary **age or grade at measurement**, not the age at which relationships began, and none concerns mentoring.
**Results.** Reported support was modestly associated with later attainment. A very supportive mother at age 14 was associated with
{{P1m_t14}} years of schooling ({{P1m_t14_ci}}), and similarly for fathers. In early adolescence, 1 SD more maternal praise was associated with
{{P2_b1014}} percentage points in bachelor's attainment. Contrasts across ages or grades were imprecise and not statistically
significant: age 16 vs 12, mothers {{P1m_d}} years ({{P1m_d_ci}}) and fathers {{P1f_d}} ({{P1f_d_ci}}); grade 11 vs 9, {{B2_d}} points
({{B2_d_ci}}); ages 6–9 vs 10–14, {{P2_d}} points ({{P2_d_ci}}). Equivalence tests met their prespecified margins for fathers and for
grade 9 vs 11, but those margins were as large as the associations themselves. In the exploratory analysis, more years of reported
support went with more schooling ({{AC_slope}} grades per year, {{AC_slope_ci}}). That pattern was described equally well by
"supportive in all four years" and by "any loss of support".
**Conclusions.** In these data, support measured earlier in childhood or adolescence was not more strongly associated with later
attainment than support measured later, and point estimates mostly favored later measurement. The analyses do not show that
developmental timing is irrelevant. Nonlinear and moderate timing differences cannot be excluded, ages of relationship onset were not
observed, and the cumulative-support pattern may reflect stable family characteristics rather than accumulating exposure.

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

| Study | Construct | Informant | Adult | Ages at measurement | Onset observed | Duration observed |
|---|---|---|---|---|---|---|
| 1 NLSY97 | "Very supportive" global rating | Youth | Resident mother / father | 12–16 (one report) | No | No |
| 2 HSLS:09 | Perceived math-teacher fairness and teaching | Student | That term's math teacher (usually different in each grade) | Fall grade 9; spring grade 11 | No | No |
| 3 NLSY79 Children and Young Adults | Praise frequency (behavior) | Mother | Mother | 6–9 and 10–14 (biennial) | No | No |
| 4 NLSY97 1997–2000 | Repeated "very supportive" ratings | Youth | Mother | 12–17 (four annual reports) | No | Repeated ratings only |

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
with E-values [@vanderweele2017]. Reporting follows STROBE where applicable [@vonelm2007]; a formal STROBE checklist has not yet been completed.

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

## 4. Discussion

Across four observational analyses, reported support from parents, and from math teachers in grade 11, was modestly associated with later
educational attainment. We found no evidence that support measured earlier carried more weight than support measured later, and point
estimates mostly favored later measurement. This is weak evidence against a strong early-window hypothesis for these constructs. It is not
evidence that timing does not matter:

1. The prespecified contrasts were imprecise, and the equivalence margins were as large as the associations compared.
2. Linear contrasts can miss nonlinear age patterns.
3. We observed age at measurement, not age at relationship onset or relationship duration.
4. Later measurements are closer to educational decisions, so larger later associations may reflect proximity rather than sensitivity.
5. The adults were parents and teachers, not mentors.

The repeated-report analysis shows that consistently reported support goes with more schooling. It cannot separate accumulation, stability,
loss of support, and stable family characteristics. All results are observational: more capable or easier-going young people may both elicit
and report more support.

### 4.1 Implications for youth mentoring (tentative)

These analyses cannot show when mentoring should begin. Program evidence from the literature, which is between-study and partly
non-randomized, suggests that effects do not depend strongly on participants' age [@dubois2011], that longer matches go with larger
benefits [@grossman2002; @rhodes2005], and that matches with older adolescents end sooner [@grossman2002]. A mentoring program could
reasonably prioritize relationship quality and continuity across transitions while treating the timing question as open. Answering it will
require designs that vary when relationships begin, ideally randomized.

### 4.2 Limitations

All four analyses are observational, use single-informant measures, and vary age at measurement within single cohorts, where age is entangled
with birth year, household composition and distance to the outcome. Outcomes were measured at different ages across studies. Attrition was
handled under a missing-at-random assumption. One planned sensitivity analysis (NLS custom longitudinal weights) and some planned exploratory
analyses were not run. Survey estimates have not been reproduced in R or Stata, and no second analyst has replicated the work. Plans were frozen
locally rather than registered externally.

## 5. Conclusion

In three U.S. cohorts, adult support reported at different ages was modestly associated with later education. Support measured earlier was not
more strongly associated with outcomes than support measured later. These results do not establish that developmental timing is irrelevant, and
they do not show that support has cumulative causal effects. They argue against assuming a narrow early window for parental and teacher support,
and for studies that measure when relationships begin, how long they last, and how good they are.

## Data, code and disclosure

All data are public (BLS: NLSY97, NLSY79; NCES: HSLS:09). Code, frozen plans with file hashes, variable mappings, full results and the audit are
in the project repository; no respondent-level data are redistributed. The author hopes to found a youth mentoring organization, which creates an
interest in particular findings. Analysis code and drafting were assisted by an AI system; the author is responsible for the content.

## References

{{REFERENCES}}
