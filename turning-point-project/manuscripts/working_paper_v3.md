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
+0.47 years of schooling (0.31 to 0.63), and similarly for fathers. In early adolescence, 1 SD more maternal praise was associated with
+1.5 percentage points in bachelor's attainment. Contrasts across ages or grades were imprecise and not statistically
significant: age 16 vs 12, mothers +0.28 years (−0.20 to 0.75) and fathers −0.19 (−0.65 to 0.27); grade 11 vs 9, +1.5 points
(−0.2 to +3.2); ages 6–9 vs 10–14, −1.6 points (−3.9 to +0.8). Equivalence tests met their prespecified margins for fathers and for
grade 9 vs 11, but those margins were as large as the associations themselves. In the exploratory analysis, more years of reported
support went with more schooling (0.22 grades per year, 0.14 to 0.31). That pattern was described equally well by
"supportive in all four years" and by "any loss of support".
**Conclusions.** In these data, support measured earlier in childhood or adolescence was not more strongly associated with later
attainment than support measured later, and point estimates mostly favored later measurement. The analyses do not show that
developmental timing is irrelevant. Nonlinear and moderate timing differences cannot be excluded, ages of relationship onset were not
observed, and the cumulative-support pattern may reflect stable family characteristics rather than accumulating exposure.

## 1. Introduction

The idea of a *turning point*, an experience that redirects a life trajectory, is central to life-course research (Elder, 1998; Rutter, 1996).
Rutter stressed that turning-point effects are heterogeneous and depend on the qualities of experience more than on age alone
(Rutter, 1996). Adolescence has been described as a period of heightened plasticity and opportunity for intervention (Dahl et al., 2018), but a
review of sensitive periods in adolescent development found concrete evidence mostly lacking (Fuhrmann et al., 2015).

The clearest evidence on the timing of environmental exposure comes from housing mobility. In the Moving to Opportunity experiment,
moving to a lower-poverty neighborhood before age 13 improved college attendance and earnings, while moving as an adolescent did not
(Chetty et al., 2016). Quasi-experimental estimates suggest roughly linear gains per childhood year of exposure (Chetty & Hendren, 2018). Skill-formation models
emphasize that early skills raise returns to later investment (Cunha & Heckman, 2007). Estimates from one such model suggest that substitutability
between earlier and later investment falls at later stages for cognitive skills but rises for noncognitive skills (Cunha et al., 2010).

For supportive relationships the evidence on timing is thinner. Mentoring programs show small-to-modest average benefits
(DuBois et al., 2002; Raposa et al., 2019). In one program, benefits were concentrated in relationships lasting a year or longer, although match length
was not randomized (Grossman & Rhodes, 2002). Teacher–student relationship quality is associated with engagement and achievement, with larger associations in studies of
higher grades, except that negative relationships mattered more in primary school; the authors caution that secondary-school studies
mostly relied on students reporting both measures (Roorda et al., 2011). In an updated meta-analysis, only the link between positive relationships and engagement was stronger in secondary than in primary school
(Roorda et al., 2017). The transition to high school is a documented point of disruption (Benner & Graham, 2009), and ninth-grade outcomes predict dropout
(Neild et al., 2008). One study of when natural mentors became important compared only young adults who had a mentor. Mentors who became important
during high school were not associated with more attainment than mentors from before high school, and mentors from after high school
were associated with somewhat more. Timing was reported retrospectively, the models adjusted for twelfth-grade grades that followed many
of the earlier mentorships, and post-high-school mentors partly reflect continued education (Fruiht & Wray-Lake, 2013).

The program literature tests age only between studies. The largest meta-analysis coded age as under 8, 8–10, 11–14 and 15–18, found
favorable effects in every group and no association of age with effect size, and concluded that benefits are "not confined to a particular
stage of development" (DuBois et al., 2011). Earlier and later meta-analyses also found no significant age moderation
(DuBois et al., 2002; Raposa et al., 2019; Van Dam et al., 2018; van Dam et al., 2021). In one school-based mentoring trial, impacts did not differ reliably between elementary
and middle/high school students (Herrera et al., 2007). Within a program, age predicted how long matches lasted: matches with 13–16-year-olds ended
sooner than with 10–12-year-olds (Grossman & Rhodes, 2002). Youth age was unrelated to relationship quality, while longer matches had higher quality
(Rhodes et al., 2005). Between-study age comparisons are confounded with program type, and none compares early childhood with adolescence.

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
multiply imputed by chained equations with predictive mean matching (White et al., 2011) and pooled by Rubin's rules (Rubin, 1987). An audit found that
the imputation random-number generator had not been seeded, so results were re-run with an explicit seed. Re-runs are now byte-identical,
and estimates differ from those in v2 only by Monte Carlo error (Table 2 footnote). Each primary contrast was tested for difference from zero
(two-sided, α = .05) and for equivalence within a prespecified margin by two one-sided tests (90% CI). Unmeasured confounding was summarized
with E-values (VanderWeele & Ding, 2017). Reporting follows STROBE where applicable (von Elm et al., 2007); a formal STROBE checklist has not yet been completed.

**What the equivalence margins mean.** The margins (±0.20 SD in Study 1; ±3 percentage points per SD in Studies 2–3) were set before the data
were seen. They turned out to be as large as or larger than the associations being compared. Equivalence therefore rules out only differences
larger than roughly the whole association. It is not evidence that timing is irrelevant.

## 3. Results

**Table 2.** Primary estimates (95% CI). Positive numbers mean more schooling (Study 1, years) or higher probability of a bachelor's degree
(Studies 2–3, percentage points per SD).

| Study | Earlier measurement | Later measurement | Difference (prespecified contrast) | p | Equivalence (margin; 90% CI) |
|---|---|---|---|---|---|
| 1 NLSY97, mothers | age 12: +0.33 | age 16: +0.61 | 16 − 12: +0.28 (−0.20 to 0.75) | .25 (Holm .50) | not shown (±0.20 SD; −0.04 to 0.22 SD) |
| 1 NLSY97, fathers | age 12: +0.57 | age 16: +0.38 | 16 − 12: −0.19 (−0.65 to 0.27) | .42 (Holm .50) | shown (±0.20 SD; −0.19 to 0.06 SD) |
| 2 HSLS:09 | grade 9: −0.2 | grade 11: +1.3 | 11 − 9: +1.5 (−0.2 to +3.2) | .09 | shown (±3; +0.07 to +2.95) |
| 3 NLSY79 Children and Young Adults, praise | 6–9: 0.0 | 10–14: +1.5 | (6–9) − (10–14): −1.6 (−3.9 to +0.8) | .19 | not shown (±3; −3.6 to +0.4) |

Re-runs with the corrected seed changed estimates by at most 0.19 (years or percentage points) relative to v2; no test decision changed.

**Study 1 (NLSY97).** Of 8,984 respondents, 8,607 rated a mother figure and 6,436 a father figure. At age 14, a very supportive rating was
associated with +0.47 years of schooling for mothers (0.31 to 0.63) and +0.47 for fathers (0.30 to 0.65), about 0.15 SD. The
prespecified linear contrast between ages 16 and 12 was not statistically significant for either parent. The E-value for the age-14 association
was 1.56, and adding a cognitive test score reduced it by a fifth to a quarter, so modest unmeasured confounding could account for it.
Estimates for each age separately were irregular (higher at 14 and 16 than at 13 and 15). A post-hoc audit test of any difference across the five
ages, in complete cases, gave p = .16 (mothers) and p = .08 (fathers). The linear contrast does not capture such patterns.

**Study 2 (HSLS:09).** Among 14,259 students who rated their math teacher in both grades, the grade-9 rating was not associated with bachelor's
attainment after adjustment (−0.2 points per SD), and the grade-11 rating was weakly associated (+1.3). The difference was within
the ±3-point margin, but the margin is about three times the grade-11 association. Two sensitivity analyses (positively worded items only;
complete cases) found the difference statistically significant at p < .05, in the direction of grade 11. The grade-9 items were asked weeks
into high school and concern a different teacher than the grade-11 items.

**Study 3 (NLSY79 Children and Young Adults).** For 6,190 children of 3,138 mothers, praise at 6–9 was not associated with
bachelor's attainment (0.0 points per SD), while praise at 10–14 was (+1.5). The difference was imprecise. A post-hoc audit using
exactly one report per window, which equalizes measurement reliability, gave a difference of −2.4 points (−4.5 to −0.3). That
contradicts a reliability explanation, but it is a post-hoc result.

**Study 4 (NLSY97, exploratory).** Among 2,566 youths with four annual reports and complete covariates, each additional year rated very
supportive went with 0.22 more grades completed (0.14 to 0.31). A test of equal weights across years did not reject (p = .48),
but non-rejection is not evidence for accumulation. In a post-hoc audit:
- A stricter test, that only the number of supportive years matters, was borderline (p = .05).
- A model with an indicator for "very supportive in all four years" (+0.69, 95% CI 0.31 to 1.08 grades) absorbed the count entirely.
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
non-randomized, suggests that effects do not depend strongly on participants' age (DuBois et al., 2011), that longer matches go with larger
benefits (Grossman & Rhodes, 2002; Rhodes et al., 2005), and that matches with older adolescents end sooner (Grossman & Rhodes, 2002). A mentoring program could
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

Benner, A. D., & Graham, S. (2009). The Transition to High School as a Developmental Process Among Multiethnic Urban Youth. *Child Development*, *80*(2), 356–376. https://doi.org/10.1111/j.1467-8624.2009.01265.x

Chetty, R., & Hendren, N. (2018). The Impacts of Neighborhoods on Intergenerational Mobility I: Childhood Exposure Effects. *The Quarterly Journal of Economics*, *133*(3), 1107–1162. https://doi.org/10.1093/qje/qjy007

Chetty, R., Hendren, N., & Katz, L. F. (2016). The Effects of Exposure to Better Neighborhoods on Children: New Evidence from the Moving to Opportunity Experiment. *American Economic Review*, *106*(4), 855–902. https://doi.org/10.1257/aer.20150572

Cunha, F., & Heckman, J. (2007). The Technology of Skill Formation. *American Economic Review*, *97*(2), 31–47. https://doi.org/10.1257/aer.97.2.31

Cunha, F., Heckman, J. J., & Schennach, S. M. (2010). Estimating the Technology of Cognitive and Noncognitive Skill Formation. *Econometrica*, *78*(3), 883–931. https://doi.org/10.3982/ecta6551

Dahl, R. E., Allen, N. B., Wilbrecht, L., & Suleiman, A. B. (2018). Importance of investing in adolescence from a developmental science perspective. *Nature*, *554*(7693), 441–450. https://doi.org/10.1038/nature25770

DuBois, D. L., Holloway, B. E., Valentine, J. C., & Cooper, H. (2002). Effectiveness of Mentoring Programs for Youth: A Meta‐Analytic Review. *American Journal of Community Psychology*, *30*(2), 157–197. https://doi.org/10.1023/a:1014628810714

DuBois, D. L., Portillo, N., Rhodes, J. E., Silverthorn, N., & Valentine, J. C. (2011). How Effective Are Mentoring Programs for Youth? A Systematic Assessment of the Evidence. *Psychological Science in the Public Interest*, *12*(2), 57–91. https://doi.org/10.1177/1529100611414806

Elder, G. H. (1998). The Life Course as Developmental Theory. *Child Development*, *69*(1), 1–12. https://doi.org/10.1111/j.1467-8624.1998.tb06128.x

Fruiht, V. M., & Wray-Lake, L. (2013). The Role of Mentor Type and Timing in Predicting Educational Attainment. *Journal of Youth and Adolescence*, *42*(9), 1459–1472. https://doi.org/10.1007/s10964-012-9817-0

Fuhrmann, D., Knoll, L. J., & Blakemore, S. J. (2015). Adolescence as a Sensitive Period of Brain Development. *Trends in Cognitive Sciences*, *19*(10), 558–566. https://doi.org/10.1016/j.tics.2015.07.008

Grossman, J. B., & Rhodes, J. E. (2002). The Test of Time: Predictors and Effects of Duration in Youth Mentoring Relationships. *American Journal of Community Psychology*, *30*(2), 199–219. https://doi.org/10.1023/a:1014680827552

Herrera, C., Grossman, J. B., Kauh, T. J., Feldman, A. F., & McMaken, J. (2007). *Making a Difference in Schools: The Big Brothers Big Sisters School-Based Mentoring Impact Study*. Public/Private Ventures.

Neild, R. C., Stoner-Eby, S., & Furstenberg, F. (2008). Connecting Entrance and Departure: The Transition to Ninth Grade and High School Dropout. *Education and Urban Society*, *40*(5), 543–569. https://doi.org/10.1177/0013124508316438

Raposa, E. B., Rhodes, J., Stams, G. J. J. M., Card, N., Burton, S., Schwartz, S., Sykes, L. A. Y., Kanchewa, S., Kupersmidt, J., & Hussain, S. (2019). The Effects of Youth Mentoring Programs: A Meta-analysis of Outcome Studies. *Journal of Youth and Adolescence*, *48*(3), 423–443. https://doi.org/10.1007/s10964-019-00982-8

Rhodes, J., Reddy, R., Roffman, J., & Grossman, J. B. (2005). Promoting Successful Youth Mentoring Relationships: A Preliminary Screening Questionnaire. *The Journal of Primary Prevention*, *26*(2), 147–167. https://doi.org/10.1007/s10935-005-1849-8

Roorda, D. L., Jak, S., Zee, M., Oort, F. J., & Koomen, H. M. Y. (2017). Affective Teacher–Student Relationships and Students' Engagement and Achievement: A Meta-Analytic Update and Test of the Mediating Role of Engagement. *School Psychology Review*, *46*(3), 239–261. https://doi.org/10.17105/spr-2017-0035.v46-3

Roorda, D. L., Koomen, H. M. Y., Spilt, J. L., & Oort, F. J. (2011). The Influence of Affective Teacher–Student Relationships on Students’ School Engagement and Achievement: A Meta-Analytic Approach. *Review of Educational Research*, *81*(4), 493–529. https://doi.org/10.3102/0034654311421793

Rubin, D. B. (1987). *Multiple Imputation for Nonresponse in Surveys*. Wiley. https://doi.org/10.1002/9780470316696

Rutter, M. (1996). Transitions and Turning Points in Developmental Psychopathology: As applied to the Age Span between Childhood and Mid-adulthood. *International Journal of Behavioral Development*, *19*(3), 603–626. https://doi.org/10.1177/016502549601900309

van Dam, L., Blom, D., Kara, E., Assink, M., Stams, G. J., Schwartz, S., & Rhodes, J. (2021). Youth Initiated Mentoring: A Meta-analytic Study of a Hybrid Approach to Youth Mentoring. *Journal of Youth and Adolescence*, *50*(2), 219–230. https://doi.org/10.1007/s10964-020-01336-5

Van Dam, L., Smit, D., Wildschut, B., Branje, S., Rhodes, J., Assink, M., & Stams, G. (2018). Does Natural Mentoring Matter? A Multilevel Meta‐analysis on the Association Between Natural Mentoring and Youth Outcomes. *American Journal of Community Psychology*, *62*(1--2), 203–220. https://doi.org/10.1002/ajcp.12248

VanderWeele, T. J., & Ding, P. (2017). Sensitivity Analysis in Observational Research: Introducing the E-Value. *Annals of Internal Medicine*, *167*(4), 268–274. https://doi.org/10.7326/m16-2607

von Elm, E., Altman, D. G., Egger, M., Pocock, S. J., Gøtzsche, P. C., & Vandenbroucke, J. P. (2007). The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) statement: guidelines for reporting observational studies. *The Lancet*, *370*(9596), 1453–1457. https://doi.org/10.1016/s0140-6736(07)61602-x

White, I. R., Royston, P., & Wood, A. M. (2011). Multiple imputation using chained equations: Issues and guidance for practice. *Statistics in Medicine*, *30*(4), 377–399. https://doi.org/10.1002/sim.4067
