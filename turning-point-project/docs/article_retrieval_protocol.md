# Protocol: closed-access articles still needed

Status: 2026-11-13. These works have no legal free full text that this environment can reach. Articles are not data, and no
publisher term found prohibits AI reading of a copy you are entitled to. So once you have a legal copy (library, interlibrary loan,
author-shared PDF), send it here as you did with DuBois et al. (2011), and Claude extracts the items below into
`fulltext_age_moderation.md/.csv` and updates the review and working paper. PDFs are never committed (D-022).

## How to get a copy (in order)

1. Your institution's library (journal subscription) or interlibrary loan.
2. ResearchGate or the author's own website (only copies the author posted).
3. Email the corresponding author (template below). Most authors share their own papers for research.

Do not use unauthorized mirrors.

## Articles and what to extract

| Priority | Article | DOI | What to extract |
|---|---|---|---|
| High | Fruiht & Wray-Lake (2013). The Role of Mentor Type and Timing in Predicting Educational Attainment. *Journal of Youth and Adolescence* | 10.1007/s10964-012-9817-0 | The only study of *when* a natural mentor became important (Add Health). Extract attainment differences by timing (before / during / after high school) and by mentor type, with sample sizes, controls and standard errors. |
| High | Christensen et al. (2020). Non-Specific versus Targeted Approaches to Youth Mentoring: A Follow-up Meta-analysis. *Journal of Youth and Adolescence* | 10.1007/s10964-020-01233-x | Meta-analysis of mentoring and academic outcomes. Extract whether age or school level was tested as a moderator, how coded, and results. |
| Medium | Schwartz et al. (2013). Youth Initiated Mentoring: Investigating a New Approach to Working with Vulnerable Adolescents. *American Journal of Community Psychology* | 10.1007/s10464-013-9585-3 | Youth-initiated mentoring evaluation. Extract participant ages and any age or duration findings. |
| Medium | Rhodes et al. (2006). A model for the influence of mentoring relationships on youth development. *Journal of Community Psychology* | 10.1002/jcop.20124 | Model of youth mentoring. Extract developmental-stage propositions (theory, not results). |
| Medium | Roorda et al. (2011). The Influence of Affective Teacher–Student Relationships on Students’ School Engagement and Achievement: A Meta-Analytic Approach. *Review of Educational Research* | 10.3102/0034654311421793 | Teacher-student relationship meta-analysis. Extract the grade-level/age moderator results (primary vs secondary; coefficients). |
| Low | Allen et al. (2018). What Schools Need to Know About Fostering School Belonging: a Meta-analysis. *Educational Psychology Review* | 10.1007/s10648-016-9389-8 | School belonging meta-analysis. Extract whether age or school level moderated associations. |
| Low | Heller et al. (2017). Thinking, Fast and Slow? Some Field Experiments to Reduce Crime and Dropout in Chicago. *The Quarterly Journal of Economics* | 10.1093/qje/qjw033 | Becoming a Man. Confirm participant grades (7-10?) from the full text. |
| Low | Miranda‐Chan et al. (2016). The Functions and Longitudinal Outcomes of Adolescents’ Naturally Occurring Mentorships. *American Journal of Community Psychology* | 10.1002/ajcp.12031 | Confirm the data source used. |
| Low | Zhu et al. (2021). A Structured Approach to Evaluating Life-Course Hypotheses: Moving Beyond Analyses of Exposed Versus Unexposed in the -Omics Context. *American Journal of Epidemiology* | 10.1093/aje/kwaa246 | Confirm the cohort used. |

**Received 2026-11-13 (PI-supplied) and extracted:** Schwartz 2013, Rhodes 2006, Roorda 2011 (accepted manuscript),
Heller (NBER WP 21178, 2015 version), Miranda-Chan 2016 (data source confirmed: Add Health public-use Waves I, III, IV). See
`fulltext_age_moderation.md`. Still outstanding: Fruiht & Wray-Lake 2013, Christensen 2020, Allen 2018, Zhu 2021.

Already checked from free versions: Yeager et al. (2019) delivered the intervention to 12,490 ninth-graders in 65 U.S. public schools
(PubMed Central PMC6786290).

## Extraction form

For each article, `article_extraction_template.csv` records: access route, whether age/stage was tested, how age was coded, the
result with its statistic and location (table/section), a verbatim quote of up to 40 words, any duration or timing finding, and
the takeaway. Same columns as `fulltext_age_moderation.csv`.

## Email template (request a copy from the author)

```text
Subject: Request for a copy of your article

Dear Dr. [Author],

I am an independent researcher studying when supportive adult relationships matter most for young people's educational
trajectories. Your article "[Title]" ([Journal], [Year]) is central to that question, but I do not have institutional
access. Would you be willing to share a copy for my personal research use?

I am particularly interested in [e.g., the results by the timing of the mentoring relationship].

Thank you for your work and for considering this request.

Best regards,
Jonathan Doane, Ph.D.
[affiliation, if any]
```
