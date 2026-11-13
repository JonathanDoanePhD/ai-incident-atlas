# Full-text extraction: age and duration as moderators of mentoring effects

Prepared 2026-11-12 for the Turning Point Project. This file supplements `literature_review.md`, which was written from abstracts only.

## How this was done

- **Sources.** Only legally open full texts were used. They were found through Europe PMC, PubMed Central, Unpaywall (queried with the generic address `research@example.org`), OpenAlex, Semantic Scholar's open-access field, institutional repositories (UvA-DARE, DukeSpace) and public Public/Private Ventures (P/PV) reports. No pirated sources were used. Where a copy's legal status could not be confirmed, it was not used.
- **Quotes.** Quotes are verbatim and 40 words or fewer. The only changes are to PDF artifacts: words broken by end-of-line hyphens were rejoined, ligatures such as "ﬁ" were written as "fi", and stray spaces were removed (for example, "( p < .06)" became "(p < .06)").
- **Locations.** Each quote names its section or table. Page numbers are given only where the retrieved copy shows the journal or report pagination.
- **Numbers.** Every number below was copied from a table or sentence in the retrieved full text. Nothing was recalled from memory.
- **Scratch copies.** The plain-text versions used for extraction are in `/tmp/claude-0/-home-user-ai-incident-atlas/70bcfa90-e481-55a4-89a2-3d817a0f3a49/scratchpad/fulltext/`.
- **Companion reports.** For grossman1998 and herrera2011, the journal articles are closed. The P/PV technical reports on the same trials are public, so those were read. They are labelled as companion reports and are **not** the cited articles. Their numbers can differ from the articles because they use different analytic samples and follow-up definitions.

**Verification note.** These figures came from a careful reading, but anything that goes into a funder report, grant application or public communication must still be checked against the primary source before publication.

## Access summary

| Key | Access | Route |
|---|---|---|
| dubois2002 | Open full text | DukeSpace repository (hdl.handle.net/10161/14943) |
| dubois2011 | **Not accessible** | Closed per Unpaywall, OpenAlex and Semantic Scholar. A copy hosted by an unrelated nonprofit's website was found, but its authorization could not be verified, so it was not used. |
| raposa2019 | Open full text | UvA-DARE repository, final published version |
| christensen2020 | **Not accessible** | Closed. The only PDF found was on an unverified mirror, which was not used. |
| vandam2018 | Open full text | Europe PMC / PMC (PMC6174947) |
| vandam2021 | Open full text | UvA-DARE repository, final published version |
| grossman2002 | **Not accessible here** | Unpaywall lists a free-to-read ("bronze") copy on the Wiley site, but that page is behind a bot challenge that this environment may not bypass. A person using a browser can probably read it at the publisher. Unverified third-party copies were not used. |
| herrera2011 | Article closed; **companion report read** | Herrera et al. (2007), P/PV report *Making a Difference in Schools* (ERIC record ED503245; copy at files.givewell.org) |
| grossman1998 | Article closed; **companion report read** | Tierney & Grossman with Resch, P/PV *Making a Difference* (1995 study, 2000 re-issue), via the UNT web archive of ppv.org |
| dubois2005 | Open full text | PubMed Central (PMC1449212) |
| fruiht2013 | **Not accessible** | Closed. No author-posted copy was found. **No timing-category effect sizes could be extracted.** |
| schwartz2013 | **Not accessible** | An author-lab URL (rhodeslab.org) is listed by Semantic Scholar but returned HTTP 401 |
| rhodes2006 | **Not accessible** | Closed |
| raposa2018 | Open full text | PubMed Central (PMC5837955) |
| roorda2017 (other meta-analysis in bib) | Open full text | UvA-DARE repository, final published version |
| hill2009 (other meta-analysis in bib) | Open full text | Europe PMC / PMC (PMC2782391) |
| roorda2011, allen2018 (other meta-analyses in bib) | **Not accessible** | Closed |

---

## dubois2002: DuBois, Holloway, Valentine and Cooper (2002), meta-analysis of 55 evaluations

**Access.** Open full text at DukeSpace: http://hdl.handle.net/10161/14943. The copy is typeset with the journal's pagination (AJCP 30(2), pp. 157–197).

**What was tested.** Youth "developmental level" was a categorical moderator with two levels: late childhood/early adolescence, and middle/late adolescence. The text does not give the age cut-offs. It says the coding sheet is "available from the first author". Duration was tested two ways, both coded continuously and shown as two bands: expected length of relationship (<12 vs ≥12 months) and actual average length of relationship (<1 vs ≥1 year). Youth-characteristic moderators were tested with statistical control for methodological factors and for the two best-practice indices (Table II, notes c and g).

**Numbers (Table II, pp. 174–176)**

| Moderator | k | Fixed effects Q_b | d (fixed) | Random effects Q_b | d (random) |
|---|---|---|---|---|---|
| Developmental level | 41 | 0.53 | | 0.06 | |
| – Late childhood/early adolescence | 20 | | .17 (±.06) | | .17 (±.11) |
| – Middle/late adolescence | 21 | | .13 (±.09) | | .15 (±.12) |
| Length of relationship expected | 51 | 1.66 | | 0.35 | |
| – <12 months | 34 | | .16 | | .18 |
| – ≥12 months | 17 | | .14 | | .16 |
| Average length of relationship (actual) | 12 | 0.05 | | 0.05 | |
| – <1 year | 6 | | .23 | | .23 |
| – ≥1 year | 6 | | .14 | | .14 |

**Verbatim quotes**

- Results, "Characteristics of Youth" (p. 182): "As shown in Table II, the demographic characteristics of youth and their families that were examined (i.e., gender, race/ethnicity, developmental level, single-parent home, socioeconomic status) were not significant moderators of effect size."
- Footnote 7 (pp. 181–182): "developmental level approaching significance (p < .06) as a moderator of effect size under the assumption of fixed effects when removing control for the best practice indices (ds of .21 and .10 for late childhood/early adolescence and middle/late adolescence, respectively)"
- Footnote 7, continued: "larger estimates of effect size at earlier stages of development were evident only when failing to control for associated variation in relevant features of the programs involved."
- Results, "Mentor–Youth Relationships" (p. 183): "neither reported average frequency of contact between mentors and youth nor length of relationship was a significant moderator of effect size."

**Takeaway.** Age, coded as two developmental bands, did not significantly moderate effects. Without controls for program practices there was a near-significant tilt toward younger youth (d = .21 vs .10), but it disappeared once best practices were controlled, because programs for younger youth used more of them. Duration was not a significant moderator either, but only 12 samples reported actual relationship length.

---

## dubois2011: DuBois, Portillo, Rhodes, Silverthorn and Valentine (2011)

**Access.** Not accessible. No verifiably authorized open copy was found. Unpaywall, OpenAlex and Semantic Scholar all report it as closed, the SAGE page returned HTTP 403, and a copy on an unrelated organization's website was not used because its authorization could not be confirmed. **Nothing about its age moderation is reported here.** The project should get the full text through a library before stating any age result from this work.

---

## raposa2019: Raposa et al. (2019), meta-analysis of 70 outcome studies

**Access.** Open full text, final published version, at UvA-DARE: https://pure.uva.nl/ws/files/52287310/Raposa2019_Article_TheEffectsOfYouthMentoringProg.pdf

**What was tested.** Mentee age was coded from the study samples (sex, age, grade and race/ethnicity were recorded). It was entered as a continuous between-study moderator in a three-level meta-regression. Table 1 gives sample age as minimum 9, maximum 16, mean 12. Program length in months (minimum 2, maximum 60, mean 11), meeting length, meeting frequency and timing of assessment were also tested.

**Numbers (Table 3, "Between-study moderators of the effectiveness of mentoring programs")**

- **Mentee age:** k = 63, #ES = 645, B0/g = 0.21, B1 = 0.02, t1 = 1.67, F(1, 643) = 2.78, flagged p < .10 (not significant at .05). The coefficient is positive, which would mean slightly larger effects at higher sample mean age, but it is non-significant.
- **Program length in months:** k = 30, #ES = 331, B1 = 0.00, t1 = 0.15, F(1, 329) = 0.02.
- **Meeting length in hours:** k = 31, #ES = 348, B1 = −0.01, t1 = −1.98, F(1, 346) = 3.92, p < .05. Longer expected meetings went with smaller effects.
- **Timing of assessment** (post-test vs follow-up): F(1, 703) = 2.48, p = .12. Only 11 studies had follow-ups.

**Verbatim quotes**

- Results, "Youth characteristics": "There were no differences in study effect sizes as a function of youth age or youth race/ethnicity"
- Discussion, "Moderators of the Effectiveness of Youth Mentoring": "it is somewhat surprising that there were not different effects of mentoring based on youth age. Past research tends to show that older youth have less close and enduring mentoring relationships"
- Same section: "Further research is warranted to determine whether, despite potentially poorer relationship processes, mentoring relationships can still be equally influential for older youth."
- Same section, on duration: "The lack of significant differences in effect sizes based on program length is inconsistent with previous research and theory indicating the importance of longer relationships"
- Same section: "relationship length may be an important determinant of youth outcomes within a specific relationship or program, it may be less important in distinguishing overall levels of mentoring effectiveness across programs."

**Takeaway.** Age was tested and was not a significant moderator (marginal, p < .10, with a slightly positive slope). The age range is narrow: sample means ran from 9 to 16, averaging 12. Program length did not predict effect size across programs, and the authors separate this from length mattering within a program.

---

## christensen2020: Christensen et al. (2020)

**Access.** Not accessible. It is closed per Unpaywall, OpenAlex and Semantic Scholar. A PDF on an unverified mirror was not used. **Nothing about age moderation is reported here.**

---

## vandam2018: van Dam et al. (2018), natural mentoring, multilevel meta-analysis

**Access.** Open full text at Europe PMC / PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC6174947/ (also available from the Wiley open-access page).

**What was tested.** Studies had to have a sample mean age between 13 and 24 (inclusion criteria). Sample "mean age" was coded and tested as a continuous moderator in two separate meta-analyses: one on the *presence* of a natural mentor and one on the *quality* of the relationship. Length of relationship in years was also coded as a continuous variable.

**Numbers**

- **Table 4, presence of a natural mentor:**
  - Age: k = 22, #ES = 165, B0 (mean r) = .106, B1 = −.003, t1 = −0.556, F(1, 163) = 0.309, not significant.
  - Length of relationship: k = 8, #ES = 78, B1 = .007, t1 = 0.881, F(1, 76) = 0.776, not significant.
- **Table 6, quality of the natural mentoring relationship:**
  - Age: k = 8, #ES = 56, B0 = .204, B1 = −.031, t1 = −1.787, F(1, 54) = 3.192, flagged † (p < .10).
  - Length of relationship: k = 2, #ES = 9, B1 = −.010, F(1, 7) = 0.878, not significant.

**Verbatim quotes**

- Method, "Coding Studies and Potential Moderators": "The capacity and willingness of youths to forge close connections with natural mentors may vary as a function of their age."
- Results (Table 4 text): "Last, none of the participant‐ or study characteristics moderated the relation between the presence of a natural mentor and youth outcomes."
- Results (Table 6 text): "Relationship quality aspects and length of the mentoring relationship did not have a moderating effect."

**Takeaway.** Mean sample age (ages 13–24 only) did not moderate the association between having a natural mentor and outcomes. For relationship *quality*, the trend was marginal (p < .10, k = 8) toward weaker associations in older samples. Relationship length did not moderate either association, but few studies reported it (k = 8 and k = 2). These are correlational, between-study associations.

---

## vandam2021: van Dam et al. (2021), youth-initiated mentoring (YIM) meta-analysis

**Access.** Open full text, final published version, at UvA-DARE: https://pure.uva.nl/ws/files/67375316/Dam2021_Article_YouthInitiatedMentoringAMeta_a.pdf

**What was tested.** The Method says age was planned as a three-level dummy-coded moderator (young, middle and late adolescents) because of range restriction. Table 3, however, reports two levels: "Early or middle adolescence" and "Late adolescence". Program duration was not tested as a moderator. Timing of assessment (post-test vs follow-up) was tested.

**Numbers (Table 3, "Moderators of the outcomes of youth initiated mentoring programs")**

- **Age group:** F(1, 167) = 0.827, not significant.
  - Early or middle adolescence: k = 5, #ES = 103, g = 0.44, t0 = 2.097, p < .05.
  - Late adolescence: k = 6, #ES = 66, g = 0.18, t0 = 0.946, B1 = −0.26, t1 = −0.909.
- **Time of measurement:**
  - Post-test: k = 8, g = 0.36.
  - Follow-up: k = 6, g = 0.23, B1 = −0.13.
  - F(1, 167) = 2.946, p < .10.

**Verbatim quotes**

- Method, analysis: "As the mean age of youth in samples showed restriction of range problems, this variable was treated as a discrete moderator (i.e., young, middle, or late adolescents) and consequently transformed into dummy variables."
- Discussion, "Limitations, and Future Research Directions": "Since young children and their parents may feel discomfort with this approach, it will be important to determine the age at which YIM can be safely and effectively implemented."

**Takeaway.** The pooled effect was numerically larger in early/middle-adolescent samples (g = 0.44) than in late-adolescent samples (g = 0.18), but the difference was not significant. It rests on 11 samples, so it should not be read as evidence of an age gradient. YIM has not been studied in children.

---

## grossman2002: Grossman and Rhodes (2002), "The test of time"

**Access.** Not accessible from this environment. Unpaywall lists a free-to-read (bronze) copy at https://onlinelibrary.wiley.com/doi/pdfdirect/10.1023/A%3A1014680827552, but automated access is blocked by a bot challenge, which was not bypassed. Unverified third-party copies were not used. **No age or duration numbers were extracted.** The literature review's claims about this paper (older adolescents' matches ending early; effects rising with duration) still rest on the abstract. A team member can probably open the publisher copy in a browser and check them.

---

## herrera2011: Herrera et al. (2011), BBBS school-based mentoring trial

**Access.** The *Child Development* article is closed. The companion P/PV report was read instead: Herrera, Grossman, Kauh, Feldman and McMaken with Jucovy (2007), *Making a Difference in Schools: The Big Brothers Big Sisters School-Based Mentoring Impact Study* (ERIC record ED503245). The copy used is at https://files.givewell.org/files/unitedstates/BBBS/220_publication.pdf. The ppv.org original could not be retrieved, so this is a third-party copy of a report P/PV distributed free of charge. **This is not the cited 2011 article.**

**What was tested.** Impacts in a subgroup intent-to-treat analysis, comparing elementary school students with middle/high school students. Duration was examined as match-length groups (0–3, >3–6 and >6–9 months), compared with non-mentored peers. Match length was not randomized.

**Numbers**

- **Sample (Chapter II, "Age and Grade"):** 61% in grades 4–5, about a third in grades 6–8, 6% in grade 9; mean age about 11.
- **Table F.2, year-one impacts "by Age"** (elementary n = 330; middle/high n = 202):

| Outcome | Elementary | Middle/high | Difference significant? |
|---|---|---|---|
| Overall academic performance | 0.11* | 0.09 | No |
| Social studies | 0.00 | 0.19** | YES+ (p < .10) |
| Quality of classwork | 0.09 | 0.15** | No |
| Assignments completed | 0.10 | 0.21** | No |
| Serious school misconduct | −0.41** | −0.20 | No |
| Start to skip school | −0.26 | −0.43* | No |
| Scholastic efficacy | 0.06* | 0.07 | No |

Only social studies differed between groups, and only at p < .10.

- **Table F.5, year two:**
  - Elementary (n = 310): college expectations 0.09; starting to skip −0.24.
  - Middle school (n = 183): college expectations 0.07; starting to skip −0.30.
  - "None of the impacts are statistically different across groups at a 0.10 level of significance."
- **Table 14, match length vs non-mentored peers** (0–3 months n = 139; >3–6 months n = 269; >6–9 months n = 157):
  - Overall academic performance: 0.04, 0.09, 0.16**.
  - Table note: the groups differed from each other "for only science and starting to skip school".

**Verbatim quotes**

- Chapter II, "Age and Grade": "Sixty-one percent of participants attended elementary school (fourth or fifth grade); about a third were in middle school (sixth through eighth grade); and 6 percent were ninth graders"
- Chapter IV, "Impacts for Youth with Different Characteristics": "the impacts on the paired subgroups (i.e., girls and boys, elementary and middle/high school students, minority youth and non-minority youth, those students performing relatively well academically and those struggling academically) did not significantly differ from each other."
- Appendix F: "Table F.2 on page 111 indicates that middle/high school students may have benefited more from SBM than did elementary school students, though both benefited."
- Appendix F, on caution: "when one looks for impacts on many variables and among many subgroups, spurious significant findings will appear randomly."
- Chapter IV, on match length: "Youth who are able to sustain longer matches may have personal characteristics (e.g., strong social skills) that lead to both longer matches and improved performance and behavior at school."

**Takeaway.** In this within-trial comparison, which avoids the cross-program confounding of meta-analyses, impacts did not differ reliably between elementary and middle/high school students. The few numerical differences leaned slightly toward older students, and the authors call subgroup differences possibly spurious. Longer matches went with larger gains, but the authors warn this may reflect selection.

---

## grossman1998: Grossman and Tierney (1998), BBBS community-based mentoring trial

**Access.** The *Evaluation Review* article is closed. The companion P/PV report was read instead: Tierney and Grossman with Resch, *Making a Difference: An Impact Study of Big Brothers Big Sisters*. This is the 1995 study, re-issued in September 2000, retrieved from the UNT Libraries web archive of ppv.org: https://webarchive.library.unt.edu/web/20130213215151/http://www.ppv.org/ppv/publications/assets/111_publication.pdf. **This is not the cited 1998 article.**

**What was tested.** In this report, subgroup impacts are given by gender and race (six subgroups) only. A search of the full report found **no impact estimates by age**. Age was among the baseline characteristics controlled in regressions. Duration is described, but its link to impacts is not analyzed here.

**Numbers**

- Age-eligible range 10–16 (footnote 8).
- Baseline age distribution (Table 3): 10.4% age 10, 24.4% age 11, 23.9% age 12, 20.7% age 13, 14.1% age 14, 5.4% age 15, 1.2% age 16.
- Average total exposure among ever-matched treatment youth: 11.4 months (Table 8).

**Verbatim quotes**

- "The Sample Youth and the Volunteers": "Sixty-nine percent of youth came to the program between the ages of 11 and 13."
- Same section: "The tables contain information for the sample as a whole and for six subgroups: boys, girls, minority boys, minority girls, white boys and white girls."
- Footnote 8: "Several study agencies do not match 15- to 17-year-old youth."
- "Length of Matches": "the average length of match for treatments who had been matched was almost 12 months"

**Takeaway.** The trial covered ages 10–16, mostly 11–13, and the public report does not test age moderation. It cannot show whether impacts differ by age. The duration–effect analysis on this sample is Grossman and Rhodes (2002), which could not be accessed.

---

## dubois2005: DuBois and Silverthorn (2005), natural mentoring in Add Health

**Access.** Open full text at PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC1449212/

**What was tested.** Age was **not** tested as a moderator. It was a control covariate in every model. Mentoring covered any mentor "since you were 14 years old", and outcomes were measured at ages 18–26. Relationship duration is described but was not tested as a moderator.

**Verbatim quotes**

- Methods, "Covariates": "Respondents ranged in age from 18 to 26 years at Wave III (mean = 21.4; SD = 1.6)."
- Table notes: "All analyses include statistical control for demographic variables of gender, age, and race/ethnicity."
- Results: "Mentoring relationships ranged in duration from 1 to 26 years (mean = 9.1; SD= 7.1)."

**Takeaway.** This study does not address whether the payoff of mentoring differs by age or stage. The relationships were long (9.1 years on average), and the authors present longevity as a plausible mechanism without testing it.

---

## fruiht2013: Fruiht and Wray-Lake (2013), mentor type and timing

**Access.** Not accessible. It is closed per Unpaywall, OpenAlex and Semantic Scholar, and no author repository copy was found. **The effect sizes by timing category (before, during or after high school) could not be extracted.** The literature review's account rests on the abstract only and should stay labelled that way.

---

## schwartz2013: Schwartz et al. (2013)

**Access.** Not accessible. The author-lab URL (http://www.rhodeslab.org/files/Schwartzetal.pdf) listed by Semantic Scholar returned HTTP 401, and no other open copy was found.

---

## rhodes2006: Rhodes (2006), conceptual model

**Access.** Not accessible (closed). This is a conceptual paper, not an effect-size study.

---

## raposa2018: Raposa, Erickson, Hagler and Rhodes (2018), economic disadvantage and natural mentors

**Access.** Open full text at PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC5837955/

**What was tested.** Age was **not** tested as a moderator of mentoring effects. The study examines access to mentors and the features of the relationships, not their effects. The sample was restricted to mentors who became important after Wave I.

**Verbatim quotes**

- Method: "we excluded respondents who reported that their mentor became important before the Wave I data collection (N = 4,498). This allowed us to focus on mentors acquired during adolescence"
- Method: "Participants in the analytic sample were between age 18 and 28 with a mean age of 21.8 years at the Wave III follow-up."

**Takeaway.** This study does not bear on age moderation of mentoring effects. Its timing restriction (mentors acquired after Wave I) is a design choice, not a test.

---

## Other meta-analyses in the bib that touch on age

### roorda2017: Roorda et al. (2017), affective teacher–student relationships

**Access.** Open full text, final published version, at UvA-DARE: https://pure.uva.nl/ws/files/21283991/Affective_Teacher_Student_Relationships_and_Students_Engagement_and_Achievement.pdf

**What was tested.** School level was coded as primary (preschool to elementary, 105 studies) vs secondary (middle, junior high and high school, 74 studies), and tested with a multigroup meta-analytic structural equation model.

**Numbers**

- **Positive relationships → engagement:** β = .32 in secondary vs .24 in primary. Constraining them equal worsened fit: χ²(1) = 6.16, p < .05.
- **The other four direct effects** can be treated as equal across levels: χ²(4) = 2.69, p = .61.
- **Indirect effect, positive relationships → achievement:** .06 (primary) vs .08 (secondary) (Table 4).

**Verbatim quotes**

- Abstract: "Only the direct association between positive relationships and engagement was stronger in secondary school than in primary school."
- Discussion: "teacher–student relationships appear to be no less important for older students than for younger students."

**Takeaway.** In this 2017 update, most teacher–student relationship associations are the same in primary and secondary school, and only one path is stronger in secondary school. This is more limited than the age-graded pattern the review currently cites from Roorda et al. (2011), which is closed and was read at abstract level. The findings are correlational and between-study.

### hill2009: Hill and Tyson (2009), parental involvement in middle school

**Access.** Open full text at PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC2782391/

**What was tested.** Age was **not** tested. The design excluded studies that mixed age groups.

**Verbatim quote**

- Method: "Studies were also eliminated if they combined middle-school-age students with other age groups, as the focus of this meta-analysis was on early adolescence and middle school as a unique developmental stage and context."

### roorda2011 and allen2018

**Access.** Not accessible (closed). Not extracted.

---

## What full texts show about age moderation in mentoring

1. **Where age was tested, no meta-analysis we could read found significant age moderation of mentoring effects.**
   - DuBois et al. (2002): developmental level, k = 41, Q_b = 0.53 (fixed) and 0.06 (random).
   - Raposa et al. (2019): mean age, k = 63, B = 0.02, F(1, 643) = 2.78, p < .10.
   - van Dam et al. (2018): presence of a natural mentor, k = 22, F = 0.309. Relationship quality, k = 8, p < .10.
   - van Dam et al. (2021): k = 11 samples, F(1, 167) = 0.827.

   "Not significant" is not the same as "no difference". These tests have little power, and the confidence intervals are wide.

2. **Directions are inconsistent, and none is significant.**
   - DuBois 2002: larger effects for younger youth, but only *without* controls for program practices (d = .21 vs .10, p < .06), and the gap vanished with controls.
   - Raposa 2019: a slightly positive slope with age.
   - van Dam 2018 (quality) and van Dam 2021: numerically smaller associations or effects for older samples.
   - BBBS school-based trial report: numerically somewhat larger impacts for middle/high school students on a few outcomes, with one difference significant at p < .10.

   Taken together, the full texts give no consistent age gradient.

3. **The age range tested is narrow.**
   - Formal-program meta-analyses mostly cover sample means of about 9–16 (Raposa 2019: mean 12).
   - Natural-mentoring meta-analyses cover means of 13–24 (van Dam 2018).
   - No full text read here compares early childhood with adolescence. Range restriction was explicit enough that van Dam 2021 had to recode age into categories.

4. **Between-study age comparisons are confounded with program type and practice.** DuBois 2002 shows this directly: the apparent advantage for younger youth came from programs for younger youth using more best practices (footnote 7). In meta-regressions, age is a property of the *study sample*, so it moves together with setting, program goals, mentor type and outcome measures. The only within-trial age contrast available (the Herrera et al. 2007 report) avoids that confound. It found no reliable difference between elementary and middle/high school students. It was also not powered for subgroups, and the authors warn of spurious findings.

5. **Duration and timing.**
   - Program or relationship length did not moderate effect sizes *across* studies (DuBois 2002, actual length k = 12; Raposa 2019, k = 30; van Dam 2018, k = 8 and k = 2).
   - Within one trial, longer school-based matches went with larger gains (Herrera 2007, Table 14). The authors flag selection, because match length was not randomized.
   - Raposa 2019 explicitly separates within-program from between-program duration effects.
   - Longer expected meeting times went with *smaller* effects (Raposa 2019).
   - Follow-up assessments showed effects that were similar (Raposa 2019) or marginally smaller (van Dam 2021) than post-test effects.

6. **Gaps that still need full text.**
   - DuBois et al. (2011), the largest program meta-analysis with a developmental framing.
   - Christensen et al. (2020).
   - Grossman and Rhodes (2002), for the age–early-termination claim.
   - Fruiht and Wray-Lake (2013), for the timing-category effect sizes.

   The literature review's statements about these four should stay labelled as abstract-level until the full texts are read through library access.

**Implication for the project.** The full texts do not support a claim that formal mentoring "works better" at one developmental stage. They are also too narrow in age range, and too confounded with program type, to rule such a claim out. That supports the project's choice to test stage differences directly in individual-level data, using prespecified moderation within the same design and measures, rather than inferring them from cross-study comparisons.


## Addendum (2026-11-13): three works read from copies supplied by the PI

### dubois2011 — DuBois, Portillo, Rhodes, Silverthorn & Valentine (2011), *Psychological Science in the Public Interest*

- **Access:** PDF supplied by the PI (not redistributed).
- **Age tested:** yes. Developmental stage was coded as "Age group (<8 years old, 8–10 years old, 11–14 years old, 15–18 years
  old)" (Table 1).
- **Result:** age was not among the moderators associated with differences in effect size (Table 2 lists only those that were).
  The text states that "participation in a mentoring program had a favorable effect on youth within each of the four age groups
  that we considered" (section on generalizability of effectiveness).
- **Authors' summary:** "From a developmental standpoint, benefits of participation in mentoring programs are apparent from
  early childhood to adolescence and thus not confined to a particular stage of development" (Summary, p. 57).
- **Duration:** positive effects also "extended to programs with a relatively brief duration (i.e., less than 6 months)."
- **Other moderators** (individually associated with larger effects): youth with prior problem behavior, more male youth, higher
  individual/environmental risk, mentor background fit, interest-based matching, and youth *not* in single-parent households.
  The single-parent moderator did not hold up independently of the other moderators.
- **Takeaway:** across 73 evaluations, mentoring effects did not depend on age group. This is the strongest program-level
  evidence against a single best age.

### rhodes2005 — Rhodes, Reddy, Roffman & Grossman (2005), *Journal of Primary Prevention*

- **Access:** PDF supplied by the PI (not redistributed). Crossref-verified 2026-11-13.
- **Sample:** 347 Big Brothers Big Sisters youth, ages 9.4–15.9 (mean 12.1).
- **Age:** "Neither age nor gender of the youth showed a consistent relationship with the scales" of relationship quality, and a
  median-split MANOVA found no age differences (Results).
- **Duration:** youth in matches of 13–19 months reported significantly more positive relationship quality on all four scales than
  youth in 1–6 month matches (MANOVA, Tukey post hoc).
- **Takeaway:** within a program, relationship quality tracks duration, not the young person's age. Duration is not randomized.

### grossman2002 — Grossman & Rhodes (2002), *American Journal of Community Psychology*

- **Access:** PDF supplied by the PI (not redistributed).
- **Sample:** 1,138 Big Brothers Big Sisters applicants in the randomized trial, ages 10–16 (mean 12.25), surveyed at baseline and 18 months.
- **Duration:** "Adolescents in relationships that lasted a year or longer reported the largest number of improvements, with
  progressively fewer effects emerging among youth who were in relationships that terminated earlier" (Abstract). Youth in matches
  that ended within the first 3 months showed significant declines in global self-worth and perceived scholastic competence
  (Table I). The pattern largely held in two-stage least squares models that treat match length as endogenous (Table II).
- **Age:** age predicted *duration*, not benefit: "matches involving 13–16 year olds were 65% more likely to break up in each period
  than matches with 10–12 year olds"; "if the match of a younger adolescent lasted for two years, then the match of a similar, but
  older, adolescent would last for a year and a quarter" (Results, predictors of duration).
- **Takeaway:** this is an *intervention-opportunity* finding (concept C), not a developmental-sensitivity finding. Sustaining a
  relationship is harder with older adolescents, and what predicts benefit is sustaining it.

### Updated synthesis

With DuBois et al. (2011) now read in full, the program evidence is consistent: no meta-analysis finds that mentoring
works better at a particular age, and the largest one finds favorable effects from under 8 to 18. Duration and relationship quality
recur as the more important features, with the caveat that longer relationships are partly self-selected. Age enters mainly
through duration: relationships with older adolescents end sooner (`grossman2002`), so programs serving them need to work harder to
sustain matches.
