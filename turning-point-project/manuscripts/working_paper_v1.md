
# When does adult support matter most? Parental support across adolescence and educational attainment in the NLSY97

**Jonathan Doane, Ph.D.** · Working paper v1, 12 November 2026 · Not peer reviewed

## Abstract

**Background.** Interventions for young people are often justified by appeals to developmental
windows, periods when supportive relationships are thought to matter most. Direct evidence on
whether the long-run payoff of adult support differs across adolescence is scarce.
**Methods.** Using the National Longitudinal Survey of Youth 1997 (NLSY97), we analysed adolescents'
1997 reports of how supportive their resident mother (n = 8,607) and father (n = 6,436) were. All
received the same question in the same year, at ages 12–16. We related these reports to highest
grade completed, measured at ages 25–44. Survey-weighted linear models with design-based variance
(117 design degrees of freedom) and 40 multiple imputations estimated the adjusted association at each
age, and the difference between ages 16 and 12. That difference was tested for both difference and
equivalence (bound ±0.20 SD). The analysis plan was frozen before respondent-level data were opened.
**Results.** Reporting a *very supportive* parent was associated with about half a year more completed
schooling: 0.47 years (95% CI 0.31–0.63) for mothers and 0.47 (0.29–0.64) for fathers, at age 14.
The association did not differ clearly by age at report. For mothers, the age-16 minus age-12
difference was +0.26 years (−0.21 to 0.74), and the equivalence test was inconclusive. For fathers it
was −0.18 years (−0.64 to 0.27), statistically equivalent to no meaningful difference. Associations
were modest relative to plausible unmeasured confounding (E-value 1.56) and fell by a fifth to a quarter
after adjustment for a cognitive test score.
**Conclusions.** Within ages 12–16, these data provide no evidence that parental support is more
consequential at younger ages. They are more consistent with an association that is stable across
early and middle adolescence, or that accumulates over time, than with a narrow developmental window.

## 1. Introduction

The idea of a *turning point*, an experience that redirects a life trajectory, is central to
life-course research (Elder, 1998; Rutter, 1996). Rutter's review stressed that turning-point effects
are heterogeneous and usually depend on particular qualities of experience affecting subgroups, not on
age alone (Rutter, 1996). A parallel literature describes adolescence as a period of heightened
plasticity and opportunity for intervention (Dahl et al., 2018). Yet a review of sensitive periods in adolescent
development concluded that concrete evidence for them is mostly lacking (Fuhrmann et al., 2015).

Some of the strongest evidence on the timing of environmental exposure comes from housing mobility.
In the Moving to Opportunity experiment, moving to a lower-poverty neighbourhood before age 13 improved
college attendance and earnings, while moving as an adolescent did not (Chetty et al., 2016). Quasi-experimental
estimates suggest gains accumulate roughly linearly with each childhood year of exposure (Chetty & Hendren, 2018).
Models of skill formation likewise emphasise that early skills raise the returns to later investment
(Cunha & Heckman, 2007), while noting that later investment can substitute for earlier investment, particularly for
noncognitive skills (Cunha et al., 2010).

For supportive relationships specifically, the evidence on timing is thinner. Meta-analyses of youth
mentoring programmes find small-to-modest average benefits (DuBois et al., 2002; Raposa et al., 2019). Relationships
lasting a year or more show the most benefit, and early termination is associated with declines
(Grossman & Rhodes, 2002). Teacher–student relationship quality is associated with engagement and achievement,
more strongly in higher grades overall (Roorda et al., 2011). The transition to high school is a documented point
of disruption (Benner & Graham, 2009), and ninth-grade outcomes add to the prediction of dropout (Neild et al., 2008). The one
study we found that examined when a natural mentor became important used retrospective reports in Add
Health. It found that mentors who became important after high school were associated with the most
attainment (Fruiht & Wray-Lake, 2013).

No study we identified compared the long-run association of the *same* measure of adult support across
ages within a single cohort. We address that gap for parental support, asking: **does the association
between adolescents' reports of a very supportive parent and later educational attainment differ by the
age at which the report was made?**

We distinguish four questions that are often conflated: whether a stage is especially responsive to an
input (developmental sensitivity); whether a transition has unusually large consequences (decision
significance); whether intervening is especially practical at a stage (intervention opportunity); and
whether an individual's trajectory visibly changes (observed trajectory change). Our design speaks only
to an observational version of the first.

## 2. Methods

### 2.1 Data

The NLSY97 is a nationally representative panel of 8,984 U.S. youths born 1980–84, first interviewed in
1997 and followed through round 21 (2023–24). The public release provides sampling strata and primary
sampling units (117 strata with 2 PSUs each). Variables were extracted from the public all-variables file.
Identifiers were verified in the official codebook, and the extract's univariate counts matched the
codebook exactly.

### 2.2 Measures

*Exposure.* In round 1 (1997), youths living with a mother or mother figure were asked: "When you think
about how she acts toward you, in general, would you say she is very supportive, somewhat supportive, or
not very supportive?" The equivalent question was asked about fathers. We coded *very supportive* = 1.
Seventy-seven percent of youths reported a very supportive mother and 68% a very supportive father
(unweighted codebook counts).

*Age.* Age on 31 December 1996 (12–16), centred at 14.

*Outcome.* Highest grade completed (0–20). Because the NLSY97 cumulative variable records attainment as of
each respondent's last interview, attainment was treated as observed only for respondents last interviewed
in 2010 or later, when all were at least 25. Others were imputed.

*Covariates (measured 1997).* Household income-to-poverty ratio (log), household parental structure,
highest grade completed by residential parents, sex, race/ethnicity (as a proxy for exposure to structural
disadvantage), and urban residence. Household structure is treated as context. We make no assumption that
any household form is deficient.

### 2.3 Analysis

The model was survey-weighted linear regression of highest grade completed on support, age, their
product, and covariates, with round-1 sampling weights. Variance was estimated by Taylor linearisation
using strata and PSUs, with t reference distributions on 117 degrees of freedom. Respondents outside each
item's universe were retained with zero weight (domain estimation). Missing covariate and outcome values
were multiply imputed by chained equations with predictive mean matching (m = 40), using auxiliary
variables (White et al., 2011), and pooled by Rubin's rules (Rubin, 1987).

The estimand θ(a) is the adjusted mean difference in years of schooling between youths reporting and not
reporting a very supportive parent at age a. The primary contrast is Δ = θ(16) − θ(12). We tested
H0: Δ = 0 (two-sided, α = .05, Holm-adjusted across mother and father) and, by two one-sided tests,
equivalence within ±0.20 SD of the outcome. Unmeasured confounding was summarised with E-values
(VanderWeele & Ding, 2017). Reporting follows STROBE where applicable (von Elm et al., 2007).

The analysis plan, including the equivalence bound, sensitivity analyses and interpretation rules, was
frozen in a timestamped repository commit, with file hashes, before respondent-level data were opened. It
was not registered with a public registry. Standard errors were independently reproduced by a
paired-PSU jackknife; the linearised and jackknife SEs agreed to three decimals.

## 3. Results

### 3.1 Sample

Of 8,984 round-1 respondents, 8,610 lived with a mother figure and 8,607 answered the mother item. 6,443
lived with a father figure and 6,436 answered the father item. Attainment was observed at a 2010+
interview for 7,838 (mother sample) and 5,816 (father sample). The fraction of missing information for Δ
was 0.08 (mother) and 0.11 (father). The weighted SD of highest grade completed was 3.1 years.

### 3.2 Association by age

**Table 1.** Adjusted difference in highest grade completed (years) for youths reporting a very supportive
parent, by age at report (95% CI).

| Age | Mother | Father |
|---|---|---|
| 12 | 0.34 (0.07, 0.61) | 0.56 (0.28, 0.84) |
| 13 | 0.40 (0.21, 0.59) | 0.51 (0.31, 0.72) |
| 14 | 0.47 (0.31, 0.63) | 0.47 (0.29, 0.64) |
| 15 | 0.54 (0.32, 0.75) | 0.42 (0.21, 0.64) |
| 16 | 0.60 (0.30, 0.91) | 0.38 (0.08, 0.67) |
| **Δ = 16 − 12** | **+0.26 (−0.21, 0.74)** | **−0.18 (−0.64, 0.27)** |
| Δ in SD units (90% CI) | +0.08 (−0.04, 0.21) | −0.06 (−0.18, 0.07) |
| Holm-adjusted p (Δ = 0) | .54 | .54 |
| Equivalence (±0.20 SD) | Inconclusive | Equivalent |

For both parents, a very supportive report was associated with roughly half a year more schooling at every
age. Neither difference across age was statistically distinguishable from zero. For fathers, the 90% CI
excluded differences larger than 0.20 SD. For mothers, the upper limit (0.21 SD) only just exceeded the bound.

### 3.3 Sensitivity analyses

Results were similar in complete-case analyses, with inverse-probability weights for living with the parent,
with adjustment for grade in 1997, with an ordinal or multi-item version of the exposure, and without
weights. For mothers, Δ was positive in every specification (+0.04 to +0.34, on each specification's own
scale). For fathers its sign varied. Estimating each age separately produced a non-monotone pattern for
both parents (mother: 0.33, 0.31, 0.71, 0.29, 0.65 years at ages 12–16), not a trend. Adding the
ASVAB math–verbal percentile reduced θ(14) from 0.47 to 0.35 (mother) and 0.39 (father).

### 3.4 Unmeasured confounding

The E-value for θ(14) was 1.56 (1.41 for the confidence limit). An unmeasured factor associated with both
reported support and schooling at a risk ratio of about 1.6, beyond the measured covariates, could fully
account for the association.

### 3.5 Exploratory analyses

Exploratory estimates by baseline poverty status and for bachelor's-degree attainment had wide intervals
and showed no consistent pattern. We do not interpret them.

## 4. Discussion

Across ages 12 to 16, adolescents' reports of a very supportive parent were associated with about half
a year more completed schooling decades later, and this association did not depend clearly on the age at
which support was reported. If anything, maternal support reported at older ages was slightly more
strongly associated with attainment, the opposite of an early-adolescent window, but this was not
statistically reliable. For fathers, the data rule out age differences larger than about a fifth of a
standard deviation.

These findings fit poorly with a strong version of the hypothesis that early adolescence, including the
transition into high school, is a uniquely consequential window for supportive relationships. They fit
better with accounts in which support matters across adolescence, or matters through accumulation over
time (Chetty & Hendren, 2018; Grossman & Rhodes, 2002). They align with the caution that sensitive periods in adolescence
are more often asserted than demonstrated (Fuhrmann et al., 2015).

### 4.1 Limitations

First, the associations are observational. More academically capable or temperamentally easier
adolescents may both elicit and report more support, and the attenuation after adjusting for a test score
is consistent with this. Second, support was a single self-report at one time. Third, in a single cohort,
age at report is entangled with birth year and with selection into living with a parent. Fourth,
attrition was handled under a missing-at-random assumption. Fifth, the study concerns parents, not
mentors or teachers. Sixth, a 1980s birth cohort may not represent young people today. Finally, the
plan was frozen privately rather than registered publicly, and one planned sensitivity analysis (custom
longitudinal weights) was not run.

### 4.2 Implications for youth mentoring

These results cannot show that mentoring works or when to deliver it. They say that, in national data, the
long-run association of a supportive parent with schooling is about the same whether that support was
reported at 12 or at 16. For programme design, this weakens the case for concentrating support at a single
early-adolescent age. It is consistent with the mentoring evidence that relationship duration and quality
matter (Grossman & Rhodes, 2002; DuBois et al., 2002). Tests of timing for nonparental support will need designs that vary
the age at which relationships begin.

### 4.3 Next steps

(1) Extend to ages 8–15 with identical relationship items in the PSID Child Development Supplement.
(2) Examine school-based adult support at grade 9 versus grade 11 in the High School Longitudinal Study
of 2009. (3) Use repeated NLSY97 support items (1997–2000) to compare accumulation and sensitive-period
models (Mishra et al., 2009; Smith et al., 2015).

## Data and code availability

NLSY97 public data are available from the U.S. Bureau of Labor Statistics. Code, the frozen plan, variable
mappings and full results (`docs/results_paper1.md`) are in the project repository. No respondent-level
data are redistributed.

## Disclosure

The author hopes to found a youth mentoring organisation, which creates an interest in particular findings.
The analysis plan was fixed before the data were examined to limit that influence. Analysis code and drafting
were assisted by an AI system; the author is responsible for the content.

## References

Benner, A. D., & Graham, S. (2009). The Transition to High School as a Developmental Process Among Multiethnic Urban Youth. *Child Development*, *80*(2), 356–376. https://doi.org/10.1111/j.1467-8624.2009.01265.x

Chetty, R., & Hendren, N. (2018). The Impacts of Neighborhoods on Intergenerational Mobility I: Childhood Exposure Effects. *The Quarterly Journal of Economics*, *133*(3), 1107–1162. https://doi.org/10.1093/qje/qjy007

Chetty, R., Hendren, N., & Katz, L. F. (2016). The Effects of Exposure to Better Neighborhoods on Children: New Evidence from the Moving to Opportunity Experiment. *American Economic Review*, *106*(4), 855–902. https://doi.org/10.1257/aer.20150572

Cunha, F., & Heckman, J. (2007). The Technology of Skill Formation. *American Economic Review*, *97*(2), 31–47. https://doi.org/10.1257/aer.97.2.31

Cunha, F., Heckman, J. J., & Schennach, S. M. (2010). Estimating the Technology of Cognitive and Noncognitive Skill Formation. *Econometrica*, *78*(3), 883–931. https://doi.org/10.3982/ecta6551

Dahl, R. E., Allen, N. B., Wilbrecht, L., & Suleiman, A. B. (2018). Importance of investing in adolescence from a developmental science perspective. *Nature*, *554*(7693), 441–450. https://doi.org/10.1038/nature25770

DuBois, D. L., Holloway, B. E., Valentine, J. C., & Cooper, H. (2002). Effectiveness of Mentoring Programs for Youth: A Meta‐Analytic Review. *American Journal of Community Psychology*, *30*(2), 157–197. https://doi.org/10.1023/a:1014628810714

Elder, G. H. (1998). The Life Course as Developmental Theory. *Child Development*, *69*(1), 1–12. https://doi.org/10.1111/j.1467-8624.1998.tb06128.x

Fruiht, V. M., & Wray-Lake, L. (2013). The Role of Mentor Type and Timing in Predicting Educational Attainment. *Journal of Youth and Adolescence*, *42*(9), 1459–1472. https://doi.org/10.1007/s10964-012-9817-0

Fuhrmann, D., Knoll, L. J., & Blakemore, S. J. (2015). Adolescence as a Sensitive Period of Brain Development. *Trends in Cognitive Sciences*, *19*(10), 558–566. https://doi.org/10.1016/j.tics.2015.07.008

Grossman, J. B., & Rhodes, J. E. (2002). The Test of Time: Predictors and Effects of Duration in Youth Mentoring Relationships. *American Journal of Community Psychology*, *30*(2), 199–219. https://doi.org/10.1023/a:1014680827552

Mishra, G., Nitsch, D., Black, S., De Stavola, B., Kuh, D., & Hardy, R. (2009). A structured approach to modelling the effects of binary exposure variables over the life course. *International Journal of Epidemiology*, *38*(2), 528–537. https://doi.org/10.1093/ije/dyn229

Neild, R. C., Stoner-Eby, S., & Furstenberg, F. (2008). Connecting Entrance and Departure: The Transition to Ninth Grade and High School Dropout. *Education and Urban Society*, *40*(5), 543–569. https://doi.org/10.1177/0013124508316438

Raposa, E. B., Rhodes, J., Stams, G. J. J. M., Card, N., Burton, S., Schwartz, S., Sykes, L. A. Y., Kanchewa, S., Kupersmidt, J., & Hussain, S. (2019). The Effects of Youth Mentoring Programs: A Meta-analysis of Outcome Studies. *Journal of Youth and Adolescence*, *48*(3), 423–443. https://doi.org/10.1007/s10964-019-00982-8

Roorda, D. L., Koomen, H. M. Y., Spilt, J. L., & Oort, F. J. (2011). The Influence of Affective Teacher–Student Relationships on Students’ School Engagement and Achievement: A Meta-Analytic Approach. *Review of Educational Research*, *81*(4), 493–529. https://doi.org/10.3102/0034654311421793

Rubin, D. B. (1987). *Multiple Imputation for Nonresponse in Surveys*. Wiley. https://doi.org/10.1002/9780470316696

Rutter, M. (1996). Transitions and Turning Points in Developmental Psychopathology: As applied to the Age Span between Childhood and Mid-adulthood. *International Journal of Behavioral Development*, *19*(3), 603–626. https://doi.org/10.1177/016502549601900309

Smith, A. D. A. C., Heron, J., Mishra, G., Gilthorpe, M. S., Ben-Shlomo, Y., & Tilling, K. (2015). Model Selection of the Effect of Binary Exposures over the Life Course. *Epidemiology*, *26*(5), 719–726. https://doi.org/10.1097/ede.0000000000000348

VanderWeele, T. J., & Ding, P. (2017). Sensitivity Analysis in Observational Research: Introducing the E-Value. *Annals of Internal Medicine*, *167*(4), 268–274. https://doi.org/10.7326/m16-2607

von Elm, E., Altman, D. G., Egger, M., Pocock, S. J., Gøtzsche, P. C., & Vandenbroucke, J. P. (2007). The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) statement: guidelines for reporting observational studies. *The Lancet*, *370*(9596), 1453–1457. https://doi.org/10.1016/s0140-6736(07)61602-x

White, I. R., Royston, P., & Wood, A. M. (2011). Multiple imputation using chained equations: Issues and guidance for practice. *Statistics in Medicine*, *30*(4), 377–399. https://doi.org/10.1002/sim.4067
