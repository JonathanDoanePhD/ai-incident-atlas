# Dataset audit: cohorts that start before adolescence

Audit date: 2026-11-12. Scope: longitudinal datasets that begin before age 8 and follow children toward adulthood, judged on whether they could test the Turning Point hypotheses:

- **H1 (foundational, ages 8–11):** adult support in middle childhood matters most for later educational attainment.
- **H2 (identity, ages 12–15):** adult support in early adolescence matters most.
- **H6 (cumulative):** total support across both periods matters most.

The adolescent-start cohorts (NLSY97, Add Health, ELS:2002, HSLS:09) are covered in a separate audit.

Companion files:

- `dataset_comparison_early_childhood.csv`: one row per dataset.
- `variable_dictionary_early_childhood.csv`: candidate variables, each with a source URL and a verification status.

## How facts were verified

Every fact marked *verified* was read from documentation fetched during this audit. The source URLs are in the CSVs. Access conditions on this machine:

| Source | Status here | Workaround used |
|---|---|---|
| nlsinfo.org (NLSY79 CYA) | reachable | Read the topical guide, the codebook supplement (Appendix A, the HOME-SF items), and the sample, weight and access pages |
| psidonline.isr.umich.edu | HTTP 403 | Used the PSID mirror `psidtest.isr.umich.edu`: user guides for CDS-I, II and III and TAS-2023, the 2002 and 2007 child codebooks, the CDS-I and CDS-II questionnaires, the TAS-2023 codebook, and the curated PSID variables PDF |
| ffcws.princeton.edu, ICPSR, openICPSR | HTTP 403 | Used DataCite metadata for ICPSR 31622 (`api.datacite.org/dois/10.3886/icpsr31622`) and the official FFCWS metadata explorer (`metadata.ffcws.princeton.edu`, full variable-metadata CSV, which is documentation and not respondent data) |
| nces.ed.gov (ECLS-K, ECLS-K:2011) | reachable | Read the K–8 user manual part 1, the K–5 user manual (NCES 2019-051) and the K–5 file record layout |
| nichd.nih.gov (SECCYD) | reachable | Read the overview page and the Phase I–IV instrument charts; the ICPSR series 233 pages were blocked |
| cls.ucl.ac.uk (MCS, Next Steps) | reachable | Read the overview and data-access pages only |

No respondent-level data were downloaded. These public URLs were HEAD-checked: NLS Investigator (200), the PSID mirror (200), the PSID SIMBA data center (403), the ECLS data products page (200), the FFCWS metadata download (200), FFCWS documentation (403), ICPSR series 233 (403), and the UK Data Service (200).

Anything not confirmed in fetched documentation is marked "unverified — needs manual check". Beliefs from memory are kept in the `recalled_unverified` column of the variable dictionary and are flagged where they appear below.

## Bottom line

| Dataset | Comparable support at ~8–11 and ~12–15? | Educational attainment at age 22–25 or later? | Can it test H1 vs H2? |
|---|---|---|---|
| **PSID-CDS/TAS** | **Yes, for one subcohort.** Children report closeness to mother, father, favorite teachers and other adults with identical wording and a 4-point scale in 2002 (ages 8+) and 2007 (ages 10+). | **Yes.** TAS covers ages 18–28 and the core PSID records years of education after that. Every original CDS child was born 1984–1997, so all are 26 or older by 2023. | **Best U.S. option**, but the within-person contrast is limited to children aged about 8–10 in 2002 (born about 1992–94), so the subsample is small. |
| **FFCWS** | **Yes, item-identical.** "How close do you feel to your mom/dad?" and "share ideas" items appear at ages 9, 15 and 22. | **Partly.** There is attainment at about 22, plus restricted National Student Clearinghouse degree data. Many cohort members have not yet finished a BA at 22. | **Credible, with caveats:** one measurement per window, and age 15 is at the edge of the 12–15 window. The sample is urban and oversamples non-marital births. |
| **NLSY79 CYA** | **Partly.** The same mother-report items appear in HOME Part C (6–9) and Part D (10–14) every two years from 1988 to 2014. Children self-report only at 10–14. | **Yes.** Highest grade and highest degree are tracked to 2020, when young adults were 12–50. | **Usable for H6 and for maternal-report timing contrasts.** The instrument boundary falls at age 10, not 12. Birth year is confounded with maternal age at birth. |
| SECCYD | Partly. Teacher STRS covers grades 2–6, and a child-reported parent measure appears at grade 6 and age 15. | **Not verified.** The documented phases end at age 15. | No, unless an adult follow-up is confirmed. |
| ECLS-K (1998–99) | No verified repeated support scale. | **No:** the study ends in 8th grade. | No. |
| ECLS-K:2011 | Teacher STRS only from kindergarten to 3rd grade (about ages 5–9). | **No:** the study ends in 5th grade. | No. |

**Recommendation.** Use **PSID-CDS/TAS** as the primary test of timing (H1 vs H2) and **FFCWS** as a replication with item-identical measures. Use **NLSY79 CYA** for cumulative-exposure (H6) models built on repeated mother reports, and as a third check on timing in which the age boundary shifts to 10. None of the three gives a clean, fully balanced design. Section 7 sets out what each can and cannot support. A person on the research team should make the final call on which dataset to use after the manual checks listed in section 8.

## 1. NLSY79 Children and Young Adults (NLSCYA)

**Verified facts** (nlsinfo.org)

- **Population.** All biological children of the female NLSY79 respondents, who were aged 14–21 on 31 December 1978. With weights, the children "may be considered a representative sample of children who have been born to this national sample of women".
- **Births.** Born 1970–2014. 11,551 children had been identified as born to NLSY79 mothers by 2020.
- **Sample by year.**
  - 1986: 5,255 children born to 2,922 interviewed mothers. Of the 5,842 eligible women, more than 2,900 mothers and 4,971 children were interviewed, and assessments were collected for 4,786 children.
  - 1994: 6,109 children under 15 and 980 young adults.
  - 2020: 4,354 young adults, aged 12–50.
- **Waves.**
  - Child assessments every two years, 1986–2014.
  - 2016: mother-reported assessments only. 2018: some mother-reported health and schooling questions.
  - Young Adult interviews from 1994. Children aged 15 and older moved to the Young Adult survey; from 2016 the cutoff became 12.
  - From 2010, young adults over 30 are interviewed only every other round.
- **Supportive adults.**
  - *HOME-SF.* A short form of the HOME inventory combining mother report and interviewer observation, with age-specific parts: A (0–2), B (3–5), C (6–9) and, from 1988, D (10–14). It produces a total score and two subscores, cognitive stimulation and emotional support (`EMOTCyyyy`, `EMOTDyyyy`, `EMOTZyyyy`, `EMOTPyyyy`).
  - *Scoring.* Raw scores contain different items at different ages. Standard scores are normed "on a single year of age basis" within each round.
  - *Items repeated across Parts C and D.* Several mother-report items appear with identical wording in both parts (Appendix A): "How close does child feel toward you?" (`HOME-C21A`/`MS-HOME-C21A`; `HOME-D20A`/`MS-HOME-D20A`), closeness to the biological father, and "How many times in the past week have you praised child…" or "…shown child physical affection?" (`C24D`/`C24F`; `D23D`/`D23F`). The physical-affection items are "not included in score".
  - *Closeness sequence.* The child–parent closeness sequence was added to the HOME in 1994.
  - *Child self-report, ages 10–14.* The Child Self-Administered Supplement (CSAS, 1994–2014) asks about closeness to each parent, whether parents talk over decisions, listen, and share ideas, and about parental monitoring.
  - *Teachers.* Children aged 10 and older (1988–2014) rate items such as "Most of the teachers are willing to help with personal problems."
  - *Young adults.* Asked about closeness to mother and father: younger young adults in 2000, all young adults from 2002.
- **Self-concept.** The SPPC (Harter) gives global self-worth (`SPPCGyyyy`) and scholastic competence (`SPPCSyyyy`) scores. It was asked of children 8 and older in 1986–1992, ages 8–14 in 1994, ages 12–14 in 1996–2014, and young adults aged 12–13 from 2016.
- **School engagement.** From 1996 the survey includes school items drawn from NELS:88 (parent involvement, teacher style). These were asked of children 6 and older in 1996–98 and children 8 and older in 2000–2014.
- **Family environment.** Mother-linked NLSY79 data: father presence (`DADHMyyyy`), contact with an absent father, household composition, and maternal education and income.
- **Outcomes.**
  - `HGC_DLI` (Y36759.00): highest grade completed as of the last interview.
  - `HSTDEGREEDLI` (Y12121.00): highest academic degree as of the last interview.
  - `HGCyyyy` (2004–2020) and `HSTDEGREEyyyy` (2012–2020): round-specific versions.
  - Flags and receipt dates for each degree type.
- **Design and weights.** Child weights are `CSAMWTyy`/`CSAMWTyyyy`, with revised `_REV` versions for 1986–2000. Young adult weights are `YAyyWEIGHT`. The weights adjust for the Black and Hispanic oversamples and for attrition. The military and economically disadvantaged non-Black/non-Hispanic oversamples were dropped.
- **Access.**
  - Public data are free through NLS Investigator; an account is needed only to save datasets.
  - Restricted geocode data for the young adults require the Standard Application Process on ResearchDataGov and are open to U.S. researchers only.
  - Zip code and census tract files exist only for NLSY79 and NLSY97, not for the young adults.

**Limitations for Turning Point**

1. **The age boundary does not match the hypotheses.** Both the HOME parts and the CSAS split at age 10. The 8–11 vs 12–15 contrast can only be built from items that repeat across Parts C and D (the mother-reported closeness, praise and affection items), not from the total or subscale scores.
2. **Who answers changes with age.** At ages 8–9 only mothers report on the relationship. Children's own reports start at 10. Self-report and proxy report are not interchangeable.
3. **Birth year is confounded with maternal age.** Children born early in the panel had young mothers, and children born late had older mothers. Any birth-cohort comparison is confounded with maternal age at birth.
4. **Attrition and changing eligibility rules.** The 2000 young adult oversample was partly unfielded, and young adults aged 21 and older were not fielded in 1998.

## 2. PSID Child Development Supplement and Transition into Adulthood Supplement

**Verified facts** (PSID mirror PDFs)

- **Population and births.** CDS-1997 drew children born 1984–1997 who were aged 0–12 in 1997, up to two per PSID family. PSID is a national household panel; the 1997 sample included an immigrant refresher.
- **CDS-I (1997).** 2,394 families (88%) and 3,563 children. The response-rate section says "2,380 child households and 3,563 children".
- **CDS-II (2002–03).** 2,907 children from 2,019 families (91%), aged 5–18 according to the CDS-II guide. The TAS-2023 guide says 5–17.
- **CDS-III (2007–08).** 1,506 children (90%), aged 10–19 according to the CDS-III guide. The TAS-2023 guide says 10–17.
- **TAS.**
  - Began in 2005 with 745 participants aged 18–20.
  - The original TAS ran every two years from 2005 to 2015 and followed only the original CDS cohort.
  - From 2017 a steady-state design covers all PSID members aged 18–28.
  - TAS-2023: 2,434 interviews from 2,793 eligible (87% response). 13.4% of these respondents came from the original CDS sample.
- **Supportive adults.**
  - *Parental warmth, caregiver report.* CDS-I used six items (G37a–f): hugged or shown physical affection, told the child you love them, spent time on the child's favorite activities, joked or played, talked about the child's interests, told the child you appreciated something. Response options run from "not in the past month" to "every day". CDS-II and CDS-III use E13a–g: G37b, c, e and f were kept, G37a and G37d were dropped, and E13e–g were added.
  - *Closeness, child report.* In CDS-II (ages 8+) and CDS-III (ages 10+), children answered H5, "How close do you feel towards…" their mother (`Q23H5A`/`Q33H5A`), father (`Q23H5B`/`Q33H5B`), stepparents, friends, siblings, **favorite teachers** (`Q23H5G`/`Q33H5G`) and **other adults outside school** (`Q23H5H`/`Q33H5H`). The scale is 1 not very close, 2 fairly close, 3 quite close, 4 extremely close.
  - *Who the close adults are.* H6 asks which other adults the child meant, including **Mentor** (`Q23H6J`/`Q33H6J`) and coach or activity leader.
  - *Talking with parents.* H4 asks how often the child talks with their mother or father about school, plans and friends.
  - *Retrospective report.* TAS-2023 H53–H55 ask about emotional closeness, affection and parenting effort from parent figures before age 18, as part of the ACE neglect subscale (e.g., `TA232054`).
- **Self-concept.** Eccles ability self-concepts in math and reading (E1–E20) were asked in CDS-I and CDS-II. Self-esteem was also measured.
- **Family environment.** HOME-SF, plus the full PSID family economic and composition record.
- **Outcomes.**
  - TAS: G5 "highest grade or year of school … completed" (`TA230990` in 2023) and the constructed Enrollment Status (`TA232392`, ten statuses including "Not enrolled, 4-yr college graduate").
  - Core PSID: "YEARS COMPLETED EDUCATION" in the individual file (`ER34020` 2009, `ER34119` 2011, `ER34230` 2013, `ER34349` 2015, `ER34548` 2017).
- **Access.**
  - Registration is required to download CDS and TAS data. The CDS-TAS Data Center provides "easy and free access".
  - Restricted data require approval of a research and data-protection plan by an IRB. Eligibility is doctoral-level faculty, with others considered case by case.

**Why PSID is the strongest candidate for H1 vs H2.** The child-reported closeness items, including closeness to teachers and other adults, use identical wording and an identical scale in 2002 and 2007. A child aged 8–10 in 2002 was 13–15 in 2007, so the same child reports once in each window. Attainment at 25 and older is available from TAS and the core PSID for the whole original cohort.

**Limitations**

1. Only two self-report waves, five years apart. The within-person timing contrast is limited to birth years of about 1992–94. The exact N is unverified and needs a Data Center extract. It will be a small share of the 2,907 children in CDS-II.
2. Children aged 11–12 in 2002 fall into the 12–15 window by age at the first measure. Children aged 10–17 in 2007 overlap both windows. Age at measurement must be modeled continuously, not by wave.
3. The CDS-I (1997) child interview did not include the closeness items. Its child interview content was limited to Eccles self-concept and self-esteem, according to the CDS-II guide.
4. Caregiver-reported warmth is only partly comparable across waves because items were dropped and added.

## 3. Future of Families and Child Wellbeing Study (formerly Fragile Families)

**Verified facts** (DataCite record for ICPSR 31622 and the FFCWS metadata explorer)

- **Population.** A stratified multistage sample of 4,898 children born 1998–2000 in large U.S. cities (population over 200,000), with births to unmarried mothers oversampled 3:1. National weights apply to 16 randomly selected cities; city weights apply to all 20.
- **Waves and response.**
  - Interviews at birth and at ages 1, 3, 5, 9, 15 and 22. Children were interviewed directly from age 9.
  - Year 9 (2007–10): 3,515 mothers.
  - Year 15 (2014–17): 3,580 primary caregivers and 3,444 teens.
  - Year 22 (2020–24): 2,990 young adults (61% of baseline) and 2,744 primary caregivers.
  - There were teacher surveys at Year 5 (the kindergarten study) and Year 9.
- **Supportive adults, all child-reported (metadata CSV).**
  - "How close do you feel to your mom?": `k5a2e` (age 9), `k6c17` (age 15) and, as "…your biological mother", `k7e5` (age 22).
  - "How well do you and your mom share ideas or talk about things that really matter?": `k5a2f`, `k6c18`, `k7e6`. The father items are parallel.
  - Year 15 adds "Other than your parents or guardians, is there currently an adult in your life who you share ideas with…" (`k6c40`, yes/no, with the relationship in `k6c41`) and "The teachers in this school really care about students" (`k6b4a`).
  - Year 22 asks about parent-like figures, including teachers (`k7e19_13`, `k7e23`).
- **Outcomes.**
  - `k7b1`: highest grade or degree completed.
  - `ck7edu`: constructed attainment (less than high school / high school or equivalent / some college or technical / college or graduate).
  - Restricted National Student Clearinghouse fields (`rs7nsc_*`).
- **Access.** The metadata site states that variables marked "(RES)" or with source "restricted" require a restricted-use contract data license. Other access terms could not be checked because the FFCWS website returned 403.

**Limitations.**

1. There is a single wave in each window (ages 9 and 15). Effects of a particular age cannot be separated from effects of a particular wave.
2. Attainment at 22 is right-censored for bachelor's degrees.
3. The sample is urban and oversamples non-marital births. It is valuable for equity questions but is not national.
4. In the metadata, the label for response value 4 is blank for some Year 9 and Year 15 items. It is presumably "not very close" and needs checking in the codebook.
5. The response codes run in the opposite direction from PSID's (FFCWS 1 = extremely close; PSID 4 = extremely close). They must be harmonized before any pooling.

## 4. NICHD Study of Early Child Care and Youth Development (SECCYD)

**Verified facts** (nichd.nih.gov)

- **Recruitment and size.** Enrolled in 1991 at one month of age, at 10 U.S. sites. The sample was 1,364 in Phase I (1991–94, ages 0–3), 1,226 in Phase II (1995–99, to 1st grade), 1,061 in Phase III (2000–04, grades 2–6) and 1,009 in Phase IV (2005–07, grades 7–9 and age 15). Funding ended in 2009.
- **Supportive adults.** The Phase III and IV instrument charts list:
  - the Student-Teacher Relationship Scale (STRS), completed by teachers in the grade 2–6 columns;
  - the Child-Parent Relationship Scale short form, completed by mother and father (Phase III and at age 15);
  - "Getting Along with My Parent" (parental warmth, support and hostility), completed by the child in grade 6 and at age 15;
  - the HOME inventory and the Network of Relationships Inventory.
- **Access.** Data are archived at ICPSR series 233. ICPSR was blocked from this machine, so access terms are unverified.

**Limitation.** No adult educational attainment appears in the NICHD-documented phases. The grade columns were read from the layout of PDF charts and should be confirmed in the ICPSR codebooks. *Recalled, unverified:* an adult follow-up around age 26 may exist. If so, SECCYD would become a strong candidate, because it measures teacher relationships with a validated instrument across grades 2–6 together with parent-relationship measures at 11–12 and 15. Its sample size, though, is about a fifth of the national studies.

## 5. ECLS-K (1998–99) and ECLS-K:2011

**Verified facts** (nces.ed.gov)

- **ECLS-K (1998–99).**
  - 21,260 kindergartners in the base year; 21,409 children responded in at least one round.
  - Rounds: fall and spring of K (1998–99), 1st grade (fall data for a 30% subsample), spring 3rd grade (2002), spring 5th grade (2004) and spring 8th grade (2007).
  - In 8th grade, children completed the SDQ (adapted from Marsh's SDQ II) and NELS:88 Self-Concept (based on the Rosenberg scale) and Locus of Control scales.
  - Restricted data are released only as cross-sectional files by grade, under an NCES license.
- **ECLS-K:2011.**
  - 18,174 children from kindergarten in 2010–11 through 5th grade in 2016.
  - Teachers completed the STRS (Pianta), which is copyright-protected, from kindergarten through 3rd grade. The composites are closeness `X2/X4/X4K/X6/X7CLSNSS` and conflict `…CNFLCT`.

**Implications.** Neither study has any outcome after 8th grade (ECLS-K) or 5th grade (ECLS-K:2011), so **neither can test associations with adult educational attainment**. ECLS-K:2011's STRS series covers roughly ages 5–9, which falls short of most of the 8–11 window. These studies are useful only for:

- checking whether the measurement models for teacher–child relationships hold in middle childhood;
- intermediate outcomes such as 8th-grade achievement and self-concept, which are mediators rather than the target outcome.

Neither has a linked adult follow-up in the documentation reviewed.

## 6. International alternatives (brief)

- **Millennium Cohort Study (UK).**
  - About 19,000 children born September 2000 – January 2002.
  - Sweeps at 9 months and ages 3, 5, 7, **11, 14**, 17 and **23**; an age-27 sweep is planned for 2028.
  - Free access, mostly through the UK Data Service.
  - It has the right age structure for H1 vs H2 (11 vs 14) and outcomes in early adulthood, but the item-level support measures were not verified here. UK qualifications need mapping to U.S. attainment.
- **Next Steps / LSYPE (England).**
  - Born 1989–90; started at age 13–14 in 2004 with 15,770 participants; followed to ages 25 and 32.
  - Free access through the UK Data Service.
  - Like the U.S. adolescent-start cohorts, **it cannot measure the 8–11 window.**

## 7. Methodological issues for any timing analysis

### Measurement invariance across ages

Timing hypotheses compare how strongly support at time *t1* and at time *t2* relates to the outcome. That comparison is meaningless if "support" means a different construct, or is measured with different error, at the two ages. In the audited datasets, comparability breaks in three ways:

1. **Different instruments at different ages.** Examples: the NLSY79 HOME Part C vs Part D items; ECLS-K:2011 STRS in early grades vs nothing later; PSID caregiver warmth G37 vs E13. Prefer items with identical wording, and treat age-specific scale totals as non-comparable.
2. **A change of informant.** Examples: NLSY79 mother report at 8–9 vs child report from 10; FFCWS parent report before 9 vs child report from 9. Keep informants constant across the windows being compared (child self-report in PSID 2002/2007 and FFCWS 9/15), or model informant explicitly.
3. **The same item meaning different things at different ages.** "Closeness to mother" may carry different meaning at 9 than at 15. With identical multi-item sets (PSID H5, FFCWS closeness and share-ideas items, NLSY79 CSAS items), test longitudinal invariance — configural, then metric, then scalar — using ordinal CFA. Where only one or two items exist, invariance cannot be tested formally. Report this as a limitation and run sensitivity analyses, for example using within-age standardized scores vs raw scores.

### Age, period and cohort confounding

- **Within a single-cohort study (FFCWS, SECCYD):** age at measurement and calendar period are perfectly collinear. A difference between the age-9 and age-15 effects could reflect period, such as 2007–10 vs 2014–17 (the recession, the spread of smartphones), or the wave itself, such as mode or attrition.
- **In multi-cohort designs (PSID-CDS, NLSY79 CYA):** age and period are partly separable because birth years vary at each wave. A 9-year-old and a 14-year-old measured in the same 2002 wave differ in birth cohort. Within PSID, birth cohort 1984–97 at fixed waves gives some leverage. Within NLSY79 CYA, birth year is also confounded with maternal age at birth.
- **Practical steps:**
  - adjust for birth year and maternal age at birth;
  - include wave fixed effects where several cohorts are observed at the same age;
  - pre-specify that the age-at-exposure contrast is estimated *within wave* where possible;
  - interpret any cross-dataset replication (PSID vs FFCWS) in light of their different historical periods.

### Life-course "structured approach" as the analytic frame

The life-course epidemiology structured approach fits these data well. These citations were subsequently verified against Crossref in `literature_review.md` / `references.bib`: Mishra et al. (2009, *International Journal of Epidemiology*; key `mishra2009`) on binary exposures; Smith et al. (2015, *Epidemiology*; `smith2015`) on model selection; and Smith et al. (2016, *International Journal of Epidemiology*; `smith2016`) extending the approach to continuous exposures.

Code adult support as a binary indicator ("high support", above a pre-registered cut-off) or as a continuous score at each window: E1 = about 8–11, E2 = about 12–15. Then compare nested models against a fully saturated model of E1, E2 and E1×E2. Each hypothesis maps to a model:

| Model | Specification | Hypothesis |
|---|---|---|
| Critical period, early | Only E1 affects attainment | H1 |
| Critical period, adolescent | Only E2 affects attainment | H2 |
| Sensitive period | Both affect attainment, with unequal weights (for example, E1 > E2) | H1 or H2 in weaker form |
| Accumulation | Effect ∝ E1 + E2 (equal weights) | H6 |
| Change or mobility | Effect of moving up or down between windows | — |

Model comparison uses F-tests or likelihood-ratio tests against the saturated model, or least angle regression for selecting among competing hypotheses.

Requirements and cautions:

- At least one measure per window per person. PSID meets this for about the 1992–94 births; FFCWS meets it at 9 and 15; NLSY79 CYA meets it for mother reports with the boundary at 10.
- Comparable measures across windows (above).
- E1 and E2 are typically correlated, which makes the hypotheses harder to tell apart. Report how strongly E1 and E2 are correlated, and consider multiple imputation for missing windows.
- Confounders measured before each exposure window: family income, household structure, parental education, prior achievement. Under time-varying confounding (prior achievement affects later support), use marginal structural models or g-methods, not adjustment for mediators.

## 8. Items that need manual checking

1. **PSID.**
   - The N of children with valid H5 responses in both 2002 and 2007, by age in 2002. Needs a Data Center extract.
   - Data Center variable names for the caregiver warmth items (G37, E13).
   - TAS education variable names for waves other than 2023.
   - Core PSID education variable names after 2017.
2. **FFCWS.**
   - Value labels for code 4 on `k5a2e`, `k6c17`, `k5a2f`, `k6c18` and `k5e1b`, and for codes 13 and above on `k7b1`.
   - Public-use registration and data use terms (ffcws.princeton.edu returned 403).
   - Whether the Year 9 teacher survey included a relationship scale (none was found in the metadata search).
3. **NLSY79 CYA.**
   - NLS Investigator reference numbers for the CSAS child-report items (closeness, decisions, share ideas, teacher help) and for young adult closeness to parents.
   - The response scale for the teacher items.
4. **SECCYD.**
   - Exact grades for the STRS, the Child-Parent Relationship Scale and "Getting Along with My Parent", from the ICPSR codebooks.
   - Whether an adult follow-up with educational attainment exists *(recalled, unverified)*.
   - ICPSR access terms.
5. **ECLS-K (1998–99).** Item-level parent–child relationship and teacher–child relationship measures; none were verified.
6. **MCS.** Item-level parent and teacher support measures at ages 11 and 14, and education variables at age 23.
7. ~~Life-course methods citations~~ — resolved: verified in `references.bib` (`mishra2009`, `smith2015`, `smith2016`).

Any statistics taken from this audit for funder reports, grant applications or public communications must be checked against the primary documentation before publication.
