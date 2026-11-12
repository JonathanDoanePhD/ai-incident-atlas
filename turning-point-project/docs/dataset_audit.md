# Adolescent dataset feasibility audit

Audit date: 2026-11-12. Datasets: NLSY97, Add Health (public-use), ELS:2002, HSLS:09.
Companion files: `dataset_comparison.csv` (one row per dataset), `variable_dictionary_adolescent.csv` (93 candidate variables with source URLs), `../config/datasets.yaml` (machine-readable registry).

Flagship question: does the association between supportive adult relationships (parent support, teacher connectedness, natural mentors, counselor contact) and later educational attainment vary across adolescence by age, developmental stage, or institutional transition such as entry to 9th grade?

## How this audit was done

- Every variable name, wording, scale, sample size and date in the companion files was read from a document fetched during the audit. Each row records its source URL.
- **NLSY97:** I read the nlsinfo.org topical-guide, sample, missing-data and weights pages. I also read the full NLSY97 codebook (`nlsy97_all_1997-2023.cdb`), pulled from the official cohort zip with an HTTP range request. Only the codebook was extracted, not the data.
- **Add Health:** I read the addhealth.cpc.unc.edu pages (About, Data, Public-use, FAQ, Conditions of use) and the official Wave I–IV in-home codebook PDFs. These PDFs describe the restricted full-sample files.
  - The Codebook Explorer (data.cpc.unc.edu) and the UNC Dataverse both failed TLS verification from this machine. ICPSR returned HTTP 403.
  - So no public-use Add Health file or public-use codebook was opened.
- **HSLS:09 and ELS:2002:** I read the NCES survey pages and the public-use online-codebook extracts. These came from the NCES DataLab zip files, which are the codebooks for the public-use files.
- **Downloads:** I checked the data download URLs with `curl -sI` only. No data files were downloaded. Scratch material is in `/tmp/claude-0/-home-user-ai-incident-atlas/70bcfa90-e481-55a4-89a2-3d817a0f3a49/scratchpad/datasets/`.
- **External use:** any figure below that goes into a funder report, grant application or public text should be checked again against the primary source before publication.

## Summary comparison

| | NLSY97 | Add Health (public-use) | HSLS:09 | ELS:2002 |
|---|---|---|---|---|
| Baseline | 8,984 youths, born 1980–84; age 12–16 at end of 1996 | Grades 7–12 in 1994–95; public-use N = 6,504 (restricted 20,745) | Fall 2009 9th graders; 23,503 records, 21,444 base-year respondents (computed), 944 schools | Spring 2002 10th graders; 16,197 records, 750 schools |
| Waves | Annual 1997–2011, then biennial to 2023–24 (round 21) | 1994–95, 1996, 2001–02, 2008, 2016–18, 2022–25 | 2009, 2012, 2013, 2016; transcripts; PEAR records to June 2021 | 2002, 2004, 2006, 2012; transcripts |
| Latest age | 38–44 | 39–51 (Wave VI) | About 25 (2021 records) | About 26 (2012) |
| Repeated adult support | **Parents: same item, many rounds, overlapping ages.** Teachers: round 1 only | Adults, teachers and parents "care" at Waves I and II (1 year apart). Mentor reported looking back at Wave III | Math/science teacher items in 9th and 11th grade (flagged in the codebook as repeats). General school-adult item in 9th only | Counselor/teacher/coach college-information and "favorite teacher's desire" items in 10th and 12th. Teacher-relations scale in 10th only |
| Attainment outcome | `CVC_HIGHEST_DEGREE_EVER` (cumulative to about age 40) | `H3ED1`, `H4ED2` | `X6HIGHDEG` (June 2021), `X4ATPRLVLA` | `F3ATTAINMENT` (2012) |
| Public download | Direct zip, HTTP 200 | None verified (Dataverse TLS failed, ICPSR 403) | Direct zip, HTTP 200 | Direct zip, HTTP 200 |
| Design variables | `VSTRAT`, `VPSU`, `SAMPLING_WEIGHT_CC`, `SAMPLING_PANEL_WEIGHT` | Public-use names not verified | Strata and PSU suppressed; 200 BRR replicate weights | `STRAT_ID`, `PSU`, 200 BRR replicate weights |
| AI-use restriction | None found | **LLM/AI use forbidden for public and restricted data** | None found | None found |

## Dataset notes

### NLSY97

**Sample and waves**
- 8,984 round-1 respondents, born 1980–84.
- The 6,748 cross-sectional cases are joined by a 2,236-case oversample of Black and Hispanic youth.
- 6,569 respondents (about 73%) were interviewed in round 21 (2023–24). The retention rate is 73.1%.

**Age at baseline**
- `CV_AGE_12/31/96` runs from 12 to 16, with roughly 1,700–1,870 youths at each age.
- So in 1997, five single-year birth cohorts were measured at the same time.
- The sample-introduction page gives ages 12–18 at the first interview, but the cohort index page says 12–17. Use `CV_AGE_INT_DATE` for exact ages.

**Supportive adults**

1. Parent supportiveness:
   - Mother item `YSAQ-032`: "When you think about how she acts toward you, in general, would you say she is very supportive, somewhat supportive, or not very supportive?" Father item: `YSAQ-053`.
   - Asked in 1997–2000. Continued as parent-figure loops (`YSAQ-032.01`–`.04`) in 2002–03, and as `YSAQ-032_1`/`_2` in 2006, 2008 and 2011.
   - Who answered changed by round:
     - 1997 and 2000: everyone living with that parent.
     - 1998–99: only youths aged 14 or under at the end of 1996.
     - 2002: under 14 at the end of 1996.
     - From 2006: anyone with a living biological or adoptive mother who has been in contact since round 1.
   - Child Trends built scales `FP_YMSUPP` and `FP_YFSUPP` for rounds 1–3 (0–32, higher means more supportive).
2. Nonparental adults:
   - `YSAQ-351A`, "who would you first turn to" with an emotional problem, was asked in 1997–2017. One option is "A teacher or school counselor", but only 65 of 5,395 youths chose it in 1997.
   - `YDOM-900B` (2003 and 2005) asks who the youth would turn to first for school or job advice. One option is "Your professor or teacher".
3. Teachers: `YSCH-36400` ("The teachers are good") and `YSCH-36500` ("The teachers are interested in the students") were asked in round 1 only.
4. "Mentoring" appears only as participation in a school-to-work program (`YSCH-33700`, option b, 1997–2008).
   - I found no item asking about a nonparental adult who made a difference.
   - The belief that NLSY97 has such a mentoring or adult-support question is **not supported** by the codebook.

**Expectations and control**
- `YEXP-1500` (percent chance of a high school diploma by age 20) and `YEXP-2000` (percent chance of a four-year degree by age 30) were asked in round 1, but only of youths aged 15 or older (born 1980–81).
- In 2001 `YEXP-2000` went to a split-ballot group only.
- The topical-guide table lists the degree item for round 4, but I found no round-4 instance in the codebook.
- Optimism and pessimism items (`YSAQ-356`, `YSAQ-357`) were asked in round 1 of youths aged 14 or under only.
- I found no general mastery or locus-of-control scale.

**Outcomes**
- `CVC_HIGHEST_DEGREE_EVER`, `CVC_HGC_EVER`, `CVC_HS_DIPLOMA`, `CVC_GED`, `CV_ENROLLSTAT`.
- `YINC-1700` (wages; top 2% top-coded).
- `CVC_WKSWK_YR_ET.xx` (weeks worked per year).

**Family and income**
- `CV_YTH_REL_HH_CURRENT` (1997–2003).
- `CV_INCOME_GROSS_YR` (1997–2003), then `CV_INCOME_FAMILY` (2004–2023).
- `CV_HH_POV_RATIO` (every round).

**Missing codes (verified):** −1 refused, −2 don't know, −3 invalid skip, −4 valid skip, −5 non-interview.

**Design and access**
- Design variables: `VSTRAT` and `VPSU`.
- Weights: `SAMPLING_WEIGHT_CC`, `SAMPLING_PANEL_WEIGHT`, `MORTADJ_SAMPWEIGHT`, plus the NLS custom-weights program.
- Data are free through NLS Investigator; an account is optional for browsing.
- Direct zip: `https://nlsinfo.org/cohort-data/nlsy97_all_1997-2023.zip` (HEAD 200, 475 MB).
- Geocode files are restricted and require an application through ResearchDataGov.

### Add Health (public-use)

**Sample and waves**
- Public-use N by wave: I 6,504; II 4,834; III 4,882; IV 5,114; V 4,196; VI 3,937.
- The public-use sample is about one third of the Core and High-Education Black samples.
- Wave dates: 1994–95, Apr–Aug 1996, 2001–02, 2008, 2016–18, 2022–25.
- Wave I 12th graders were not followed at Wave II.

**Supportive adults**
- Wave I protective factors: `H1PR1` "How much do you feel that adults care about you?", `H1PR2` (teachers care), `H1PR3` (parents care). All on a 1–5 scale.
- The same items repeat at Wave II as `H2PR1`–`H2PR3`.
- Also at Wave I: parent closeness and caring (`H1WP9`, `H1WP10`, `H1WP13`, `H1WP14`); mother warmth (`H1PF1`); school connectedness (`H1ED19`–`H1ED24`); trouble getting along with teachers (`H1ED15`).

**Wave III mentoring (Section 13), verified wording**
- `H3MN1`: "Other than your parents or step-parents, has an adult made an important positive difference in your life at any time since you were 14 years old?" In the full sample, 11,434 said yes and 3,708 said no.
- `H3MN2` asks how the person is related. "Teacher/guidance counselor" is the most common single category (n = 2,223, against 1,970 for "friend").
- `H3MN6`: "How old were you when {he/she} first became important in your life?" Answers range 0–25, and 342 people answered age 0. So the "since age 14" stem does not limit when the relationship began.
- `H3MN7`–`H3MN11` cover whether the person is still important, duration, contact and closeness. `H3MN13A`–`D` are the open-ended "how did they help" answers.
- A separate coded file (`mentor3`: `MENTORA1`–`A8` mentor behaviors, `MENTORB1`–`B8` domains) is listed as a "Standard" restricted file. Whether it is in the public-use release is not verified.

**Public-use availability and design variables**
- Add Health says the public-use files "contain all the data from the In-home Interviews, just a smaller sampling". So the H3MN items should be public, but I could not open a public file to confirm.
- The FAQ says the open-ended mentor text may not be quoted.

**Outcomes**
- `H3ED1` (highest grade completed), `H3ED2`/`H3ED3` (GED and diploma), `H4ED2` (highest level of education), `H4EC2` (personal earnings).
- Parent-reported 1994 income: `PA55`.

**Missing codes (observed):** 6/96 refused, 7/97 legitimate skip, 8/98 don't know, 9/99 not applicable, "!" missing.

**Access and policy**
- Restricted design variables: `PSUSCID` (cluster) and `REGION` (strata).
- Restricted weights: `GSWGT3` and `GSWGT3_2` (Wave III).
- I could not verify the public-use design variable names.

> **Blocking constraint.** The Add Health Conditions of Use page includes an AI and LLM Use Policy that applies to **both public-use and restricted-use data**. It says LLMs and other AI tools, naming "Claude AI", "may not be used to manage, process, or analyze data distributed by Add Health". Using them with documentation, codebooks and study-level metadata is allowed. This project's Claude-assisted analysis workflow therefore **cannot** be used on Add Health individual-level data. Any Add Health analysis must be done entirely by human analysts outside this tooling, or dropped.

### HSLS:09

**Sample and waves**
- 944 schools.
- 23,503 student records. 2,059 had base-year unit non-response, which gives 21,444 respondents (computed).
- NCES says over 24,000 students were sampled and over 21,000 responded.
- Waves: base year fall 2009; first follow-up spring 2012 (mostly 11th grade); 2013 Update; HS transcripts 2013–14; second follow-up 2016; postsecondary transcripts and student records 2017–18; PEAR administrative records to June 2021.
- The design is grade-based. In the public file, dates of birth are bottom-coded at 1992 and top-coded at 1996.

**Supportive adults**
- `S1TALKPROB` (9th grade): "There are always teachers or other adults in your school that you can talk to if you have a problem" (strongly agree to strongly disagree). It is an input to `X1SCHOOLBEL`.
- 9th-grade math teacher items `S1MTCHVALUES` … `S1MTCHEASY`, and science equivalents `S1STCH*`.
- 11th-grade `S2MTCHTREAT`, `S2MTCHINTRST`, `S2MTCHEASY`, `S2MTCHTHINK`, `S2MTCHGIVEUP`, and science equivalents.
  - The codebook marks `S2MTCHINTRST` as "a repeat of the BY variable `S1MTCHINTRST`".
  - These items were asked only of students taking math in spring 2012, and they refer to a different teacher than in 9th grade.
- Counselor and teacher contact:
  - 9th grade: `S1CNSLTLKCLG`, `S1TCHTALKCLG`, `S1TCHTALKPRB`, `S1CNSLTLKPRB`, `S1PLANCNSL`, `S1PLANTCHR`.
  - 11th grade: `S2TALKHSCNSL`, `S2REVIEWPLAN`.
  - 2013 Update: `S3CNSLCLG`.
- Parent conversations: `S1MOMTALKCLG` and related items (9th grade).
- A counselor questionnaire is also available.

**Expectations and self-efficacy**
- `X1STUEDEXPCT` and `X2STUEDEXPCT`; parent expectations `X1PAREDEXPCT` and `X2PAREDEXPCT`.
- Domain-specific self-efficacy and identity: `X1MTHEFF`/`X2MTHEFF`, `X1MTHID`/`X2MTHID`.
- No general control scale was found.

**Outcomes**
- High school: `X3HSCOMPSTAT`, `X4HSCOMPSTAT`.
- Postsecondary: `X4ATPRLVLA` (February 2016), `X6EVRATNDCLG`, `X6HIGHDEG` (June 2021).
- Work and income: `X4WORKING16FB`, `X4INCOMECAT`.

**Family:** `X1PARPATTERN`, `X1FAMINCOME`, `X1POVERTY185`, `X1SES`.

**Missing codes (verified):** −1 don't know, −3 carry-through, −4 not administered, −5 suppressed, −6 component not applicable, −7 legitimate skip, −8 unit non-response, −9 missing.

**Design and access**
- `STRAT_ID` and `PSU` are suppressed on the public file. Use 200 BRR replicate weights, for example `W1STUDENT001`–`200` and `W4W1STU001`–`200`.
- Direct public CSV zip (HEAD 200, 348 MB): `https://nces.ed.gov/datalab/files/zip/OnlineCodebook/HSLS_2009-16_PETS_Pear_v1_0_CSV_Datasets.zip`

### ELS:2002

**Sample and waves**
- 750 schools and 16,197 student records. NCES describes "over 15,000 students".
- Waves: 2002 (10th grade), 2004 (12th grade, with the sample "freshened" to represent seniors), 2006, 2012.
- High school transcripts (2005) are restricted-use per NCES. Transcript GPA composites such as `F1RGPP2` are in the public file.

**Supportive adults**
- `BYTSTREL` teacher–student relations scale: base year only, inputs `BYS20A` and `BYS20E`–`H`, α = .73.
- `BYS20F` "Teachers are interested in students"; `BYS27H` "I go to school because my teachers expect me to succeed".
- Repeated at 10th and 12th grade:
  - `BYS59A`–`C` and `F1S48A`–`C`: went to a counselor, teacher or coach for college-entrance information.
  - `BYS66E`–`G` and `F1S44E`–`G`: what the counselor, favorite teacher or coach thinks the student should do after high school. Response option 7 differs between waves, and the 12th-grade items were skipped in the abbreviated questionnaire.
- `BYS71D`: school-arranged mentoring.

**Expectations and control:** `BYSTEXP`, `F1STEXP`, `F2STEXP`; `BYCONEXP` (control expectation, α = .84); `BYMATHSE`/`F1MATHSE`; `BYACTCTL`.

**Outcomes:** `F3HSSTAT`, `F3EVRATT`, `F3ATTAINMENT`, `F3EMPSTAT`, `F3ERN2011` (top-coded and coarsened in the public file).

**Family:** `BYFCOMP`, `BYINCOME`, `BYSES1`.

**Missing codes (verified, defined in the codebook):** −1 to −9.

**Design and access**
- `STRAT_ID` and `PSU` are present in the public file. Weights: `BYSTUWT`, `F1PNLWT`, `F3BYPNLWT`, plus 200 BRR replicates each.
- Direct public CSV zip (HEAD 200, 17.8 MB): `https://nces.ed.gov/datalab/files/zip/OnlineCodebook/ELS_2002-12_PETS_v1_0_Student_CSV_Datasets.zip`
- BRR replicate zip (HEAD 200, 134 MB): `https://nces.ed.gov/datalab/files/zip/OnlineCodebook/ELS_2002-12_PETS_v1_0_Student_BRR_CSV_Datasets.zip`

## Key feasibility judgment: can we see the association change across adolescence?

The deciding question is whether supportive-adult measures are repeated at comparable ages or grades, so that "when" can be separated from "who".

### NLSY97: age-graded, between and within person

**Strengths**
- In 1997, youths aged 12–16 reported parent supportiveness with identical wording, at the same calendar time.
- The 1998–99 rounds re-asked the younger cohorts, and 2000 re-asked everyone living with a parent.
- This is an accelerated longitudinal (cohort-sequential) design. Each age from about 12 to about 19 is observed in several birth cohorts. Within-person change can be separated from between-person age differences, for example with a time-varying-effect or multilevel model of support × age predicting later attainment.
- The outcome window is long (attainment to age 38–44), and the data are a free direct download.

**Threats**

1. Age and cohort are confounded within a round. Across rounds, age and period are confounded. The five-year cohort span keeps cohort differences small, but they are not zero.
2. The support item depends on co-residence ("lives with mother/mother figure"). At older adolescent ages, the youths still living with a parent are a selected group, and that selection is linked to attainment, for example through college enrollment. From 2006 the universe changes to "contact with biological or adoptive mother". Inverse-probability weighting for being in the item's universe, or restricting to ages 12–17, is needed.
3. Being closer in time to the outcome inflates later-age associations. Models need to adjust for prior attainment or grade at measurement.
4. Repeated support covers parents only. Nonparental adults appear only as a rare first-choice category, so the teacher and mentor parts of the question cannot be tested this way.
5. In 2001 the item was given to a split-ballot group only (`TXGROUP`), so 2001 should be excluded or handled explicitly.

### Add Health: retrospective mentor onset, plus a one-year repeat of "adults/teachers care"

**Strengths**
- Rich constructs, including teachers care, adults care, school connectedness, and natural mentor type and onset age.

**Threats**
- `H3MN6` (age the mentor became important) is recalled at Wave III (2001–02), about 7 years after Wave I. The exact age range at Wave III was not verified. Recall error and telescoping are likely.
- Survivorship: only mentors still remembered as important are reported, and current attainment may shape what is recalled (reverse causation). Onset age also varies with relationship type, for example family versus teacher.
- The Wave I to II repeat is one year apart, with between-person variation in grade.
- The public-use N is about 6,500, and the design variables are unverified.

**Decisive:** the AI-use prohibition rules out this project's tooling.

### HSLS:09: a grade-based institutional transition (9th versus 11th grade)

**Strengths**
- The only dataset that starts at the 9th-grade transition.
- It has the best coverage of school-based adults: teachers, counselors and a general "adult in school" item.
- It links to administrative attainment records through 2021.

**Threats**
1. The 9th-grade survey was given in the fall, only weeks into high school, so it captures early-transition perceptions rather than a full year of the relationship.
2. The 11th-grade teacher items exist only for students taking math or science and describe a different teacher. Comparing 9th- and 11th-grade coefficients mixes timing with teacher and course selection.
3. The general "adult to talk to" item and school belonging were asked in 9th grade only.
4. Age is not a design dimension, so the design tests grade or institutional stage, not age.
5. Strata and PSU are suppressed, so replicate weights are required.

**Fit:** HSLS:09 is the right dataset for the freshman-year hypothesis about school-based adults, but not for an age-graded question.

### ELS:2002: grade-based, 10th versus 12th grade

**Strengths**
- Counselor, teacher and coach college-information items and "favorite teacher's desire" items repeat at 10th and 12th grade.
- Attainment is measured in 2012.

**Weaknesses**
- It misses 9th grade, and the repeated items are informational or expectational rather than relational.
- It works best as a replication cohort for an HSLS design, measured one cohort earlier.

### Ranked recommendation

**1. Paper 1: NLSY97, accelerated longitudinal design for parent support**
- Question: does the association between parent supportiveness and attainment vary by age from 12 to 17?
- Data: 1997–2000 `YSAQ-032`/`YSAQ-053` (or `FP_YMSUPP`/`FP_YFSUPP` for 1997–99).
- Outcome: `CVC_HIGHEST_DEGREE_EVER` (BA or higher), with `CVC_HS_DIPLOMA` timing as a secondary outcome.
- Method: a support × age interaction, estimated within person where possible, on person-round data with design-based variance (`VSTRAT`, `VPSU`, `SAMPLING_WEIGHT_CC`, or custom weights).
- Controls: birth cohort, a model of co-residence selection, and attainment or grade at measurement.
- Why first: it is the only dataset that measures support with identical wording at overlapping ages, with a long outcome window and open access.

**2. Paper 1b or 2: HSLS:09, the 9th-grade transition and school-based adults**
- Data: `S1TALKPROB`, `X1SCHOOLBEL`, the teacher items `S1MTCH*`/`S1STCH*` versus `S2MTCH*`/`S2STCH*`, and counselor contact.
- Outcome: `X6HIGHDEG` and `X4ATPRLVLA`.
- Method: BRR weights. Treat the 9th-versus-11th contrast as stage-specific, not causal, and use the repeated teacher items, with selection into course-taking modeled, for the formal timing test.

**3. ELS:2002**
- Out-of-cohort replication of the HSLS 10th/12th-grade school-adult contrasts. Attainment to 2012.

**4. Add Health (public-use)**
- Do not use with this project's AI-assisted workflow, because of the data-use policy.
- If humans run it entirely outside this tooling, the Wave III mentor-onset-age analysis is a useful descriptive complement. Treat the recall and survivorship biases as primary threats.

The choice of dataset and design is the research team's decision. This ranking reflects measurement feasibility only.

## What remains unverified

1. **Add Health public-use files.** Variable presence (including `H3MN1`–`H3MN13` and the coded `mentor3` file), public-use weight and cluster names (believed to be `GSWGT1`/`CLUSTER2`; recalled, not verified), and the Dataverse/ICPSR download terms.
   - Reason: ICPSR 21600 returned 403. dataverse.unc.edu and data.cpc.unc.edu (Codebook Explorer) failed TLS verification through the proxy.
   - The codebooks read describe the restricted full-sample files.
2. **Add Health birth years and exact age range at Wave I.** Not stated on the pages fetched.
3. **NLSY97 round-4 college expectation.** The topical-guide table lists "four-year college degree by 30" for round 4, but the codebook has no round-4 `YEXP-2000`. Possibly a different question name; needs a manual Investigator check.
4. **NLSY97 rounds for the MHI-5 and household/neighborhood environment items.** Pages not read.
5. **NLS, NCES and DataLab terms.** I found no AI/LLM-use policy for NLS or NCES public data, but did not search exhaustively. The DataLab online-codebook terms text was not captured; the app checks a terms-agreement flag.
6. **ELS:2002 and HSLS:09 well-being outcomes, and ELS birth-year distribution.** Not itemized.
7. **HSLS:09 age distribution at baseline.** Public dates of birth are coarsened (1992 or earlier and 1996 or later are recoded). Not tabulated.
8. **Category codes not transcribed.** Several Add Health response codes (show-card scales for `H1WP9`, `H1PF*`, `H1ED19`–`24`) and several HSLS/ELS variables are recorded with "label only" status in the variable dictionary.
9. **Restricted-use costs and fees.** Add Health contracts and NCES licenses: not captured.
