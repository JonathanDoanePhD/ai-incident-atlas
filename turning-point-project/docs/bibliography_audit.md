# Bibliography audit

Independent audit for the Turning Point Project, carried out 2026-11-13 at the request of an external methodological reviewer. The aim was to find errors, not to confirm earlier work. No existing project file was edited. The per-work results are in `bibliography_audit.csv` (88 rows).

**Before external use.** Any statistic or citation from this audit or from the project files must still be checked against the primary source before it goes into a funder report, grant application or public communication.

## What was checked and how

| Task | Method | Sources |
|---|---|---|
| 1. Metadata | Fresh Crossref query for all 88 DOIs, one at a time (generic User-Agent, 0.3 s between calls). Compared title, first-author surname, author count, year (published-print, else issued), journal, volume, issue and pages with `references.bib` and `evidence_matrix.csv`. Capitalization and punctuation differences are reported as minor. A second independent check used Europe PMC `journalInfo` and title, available for 54 works. | Crossref; Europe PMC |
| 2. Study design | Each `study_type` was compared with the abstract, the title and the matrix's own `design_or_method` and `limitations` columns, and with the full text where one was available. | As in task 3 |
| 3. Findings | Each `key_finding` was compared with a freshly downloaded abstract: Europe PMC (54), Crossref (most of the rest), the saved project abstracts, and OpenAlex for three works. Saved full texts were used where available. | Europe PMC, Crossref, OpenAlex, saved texts |
| 4. Quotations | Every quoted string of 25 characters or more in `fulltext_age_moderation.md`, and every `quote` cell in the `.csv`, was searched in the saved texts. Whitespace, hyphenation, ligatures and dashes were normalized, and fuzzy matching was used for anything not found. The PI's PDFs were re-extracted with `pdftotext` without `-layout`, because the layout extracts break across columns. | `scratchpad/fulltext/*.txt`, `userpdfs/*.txt`, re-extracted PDFs |
| 5. Evidence level | Each work was classified from what actually exists on disk and what the project files report. | All of the above |
| 6. Manuscript | All 30 `[@...]` brackets (35 key uses, 27 distinct keys) in `manuscripts/working_paper_v2.src.md` were checked for existence in the bib and for support of their sentence. | bib; abstracts; full texts |

## Summary counts

| Item | Count |
|---|---|
| Bib entries / matrix rows | 88 / 88 (same keys); every entry has a DOI, so `no_doi` = 0 |
| Crossref match: yes / minor / no | 58 / 27 / 3 |
| ...of the 58 "yes", the bib copies a **defective Crossref field** | 3 (`kuh2003`, `hernan2016`, `smith2016`) |
| ...of the 3 "no", the bib is probably right and Crossref is wrong | 3 (`elder1994`, `cunha2010`, `benshlomo2002`) |
| Year, journal or DOI mismatches between bib, matrix and Crossref | 0 (bib and matrix agree on all 88). One cross-source year conflict: `smith2021` (Crossref 2021, PubMed 2022) |
| Study-type labels questioned | 14 (6 substantive, 3 unsupported by anything read, 5 minor or internal inconsistency) |
| Finding verdicts: supported / partially supported / overstated / unsupported / cannot check | 71 / 2 / 0 / 0 / 15 |
| Matrix fields that imply more reading than the recorded evidence level | 6 (`heller2017`, `yeager2019`, `cunha2010`, `mirandachan2016`, `kuh2003`, `zhu2021`) |
| Stale matrix fields that contradict later full-text reading | 6 (`dubois2011`, `raposa2019`, `vandam2018`, `vandam2021`, `roorda2017`, and bib notes for `dubois2011`/`grossman2002`) |
| Evidence level: full_text_verified / abstract_only / metadata_only | 13 / 64 / 11 |
| ...full text: open access / PI-supplied copy / trial report substitute | 8 / 3 / 2 |
| Matrix `evidence_level_read` understates full-text reading | 8 rows (`dubois2002`, `raposa2019`, `vandam2018`, `vandam2021`, `dubois2005`, `raposa2018`, `hill2009`, `roorda2017`) |
| Quoted strings checked (md 51, csv 13) | 64: 58 exact, 3 exact after whitespace normalization, 3 exact apart from an interrupting page header, **0 not found** |
| Manuscript keys missing from bib | 0 of 27 |
| Manuscript citation brackets: supported / partially / not supported by cited work / cannot check | 26 / 2 / 1 / 1 |

## Most serious problems

1. **Manuscript cites the wrong document for the trial age result.** "impacts did not differ reliably between elementary and secondary students [@herrera2011]": this result comes from the 2007 P/PV report (Table F.2), not from the 2011 *Child Development* article. The article was read only at abstract level, its abstract gives no age-subgroup result, and the report is not in the bib. The sentence also ends with a stray ",." typo.
2. **Two bib titles copy Crossref artifacts and will print wrongly.** `kuh2003` is titled "Life course epidemiology: Figure 1", and `hernan2016` "... Not Available: Table 1." Europe PMC/PubMed give "Life course epidemiology" and "Using Big Data to Emulate a Target Trial When a Randomized Trial Is Not Available". The matrix has the same errors.
3. **`smith2016` is incomplete.** It has no volume or issue, and its pages are "dyw164". Europe PMC gives *Int J Epidemiol* 45(4):1271–1279.
4. **RCT labels on non-randomized analyses.** `grossman2002` and `bayer2015` are labelled "RCT", but the exposure analysed (match length, relationship closeness) was not randomized. The matrix's own design column says "secondary analysis". These labels flow into the review's "causal" framing.
5. **"Longitudinal" labels on cross-sectional studies.** `rhodes2005` is called longitudinal, but its authors say "The cross-sectional nature of these data..." because quality items were asked only at follow-up. `lerner2005` uses Wave 1 only, and `chetty2022` is a ZIP-level ecological cross-section. `cunha2010` is labelled "quasi-experimental" but is a structural model fitted to observational data.
6. **Evidence-level bookkeeping is inconsistent across files.** Eight works whose open full texts were read are still recorded as abstract or metadata level in the matrix and bib. `references.bib` says `dubois2011` and `grossman2002` were "read at abstract level", while the matrix says full_text. `fulltext_age_moderation.csv` labels PI-supplied copies and companion reports as `open_full_text`. The literature review still says "No full texts were read" (lines 8 and 263) and "Not read" for DuBois 2011 (line 71).
7. **Stale limitations contradict findings in the same row.** `dubois2011` says "Only partial abstract available; no quantitative claims made here." next to a full-text key finding. `raposa2019`, `vandam2018` and `vandam2021` still say age moderation must be checked in full text, although it was. `roorda2017` is "Not summarized", yet the manuscript cites it for a specific result.
8. **Teacher-relationship age gradient is overstated in the manuscript and review.** "more strongly in higher grades [@roorda2011]" leaves out the same abstract's caveat that negative-relationship effects were stronger in primary school. The 2017 full text found only one of five paths stronger in secondary school. The review (line 135) adds "It supports a stronger role for positive teacher relationships in adolescence", which the 2011 abstract does not separate out.
9. **Causal claims rest on abstract-only reading.** The review calls `oyserman2006` "randomized" and "causal evidence" (lines 163 and 218), but the abstract does not mention random assignment. It also concludes from `heller2017` that a relationship-delivered program "appears to work through *cognitive* mechanisms, not through the relationship itself" (line 80), although the authors call their mechanism data "not ideal" and their support "suggestive".
10. **Smaller factual slips.**
    - `grossman2002` gives N = 1,138 as the analytic N. That is the number randomized; 959 completed follow-up. Its "2-year vs ~1.25-year expected length" restates a hypothetical illustration as an estimate.
    - `amato2005` (matrix and review line 188) says the abstract is "descriptive only", but it reports findings.
    - The saved scratch file `litreview/abstracts.json` holds unrelated papers' abstracts under `clausen1991` (a colon-cancer review) and `scales2000` (a 2026 EEG study). The project correctly treated both works as metadata-only, but the provenance file is contaminated.

## 1. Metadata mismatches

### Substantive: bib reproduces or diverges from a defective record

| Key | Field | references.bib / matrix | Crossref | Other source | Action |
|---|---|---|---|---|---|
| kuh2003 | title | "Life course epidemiology: Figure 1" | same (artifact) | Europe PMC: "Life course epidemiology." | Fix title in bib and matrix |
| hernan2016 | title | "...Is Not Available: Table 1." | same (artifact) | Europe PMC: no ": Table 1" | Fix title in bib and matrix |
| smith2016 | volume/issue/pages | none / none / "dyw164" | same (online-first record) | Europe PMC: 45 / 4 / 1271–1279 | Add volume, number, pages |
| smith2021 | year/volume | 2021 / none | published-print 2021; online 2022 | PubMed/Europe PMC: 2022, series vol. 53 | Decide year; add `volume = {53}` |
| elder1994 | first author | "Elder, Jr., Glen H." | family "Jr.", given "Glen H. Elder" | — | Bib correct; Crossref defective (already noted) |
| cunha2010 | authors | Cunha, Heckman, Schennach (3) | no authors (0) | Europe PMC: Cunha F, Heckman J, Schennach S | Bib correct; fill in given names |
| benshlomo2002 | author count | Ben-Shlomo, Kuh (2) | Ben-Shlomo only (1) | no Europe PMC record | Probably correct; confirm on OUP page |

### Minor: formatting only (bib matches Crossref)

| Keys | Issue |
|---|---|
| schwartz2013, vandam2018, hurd2010, timpe2015, fruiht2018, hagler2018, mirandachan2016, raposa2018 | Issue written `1--2` / `3--4` vs Crossref `1-2` / `3-4` (BibTeX en dash; equivalent) |
| dubois2002, vandam2018, timpe2015, fruiht2018, hagler2018, mirandachan2016 | Non-ASCII U+2010 hyphen in title or author ("Meta‐Analytic", "Long‐Term", "Miranda‐Chan", "Wray‐Lake") |
| laub1993 | ALL-CAPS title with footnote asterisk ("...STUDY OF CRIME*") |
| bayer2015 | ALL-CAPS title |
| heller2017, chetty2018 | Title ends with footnote asterisk |
| masten2001, eccles1993, wentzel1998, hill2009, bandura1977, bandura1982, marcia1966, oyserman2006, mello2008, hamaker2015 (and hernan2016) | Trailing period in title |
| rubin1987 | `publisher = {Wiley}` vs Crossref container "Wiley Series in Probability and Statistics" |
| yeager2019, chetty2022 | Matrix author list truncated with "..." (bib complete: 25 and 22 authors) |

Year conventions are consistent. The bib follows Crossref published-print, so `vandam2021` (online 2020), `heller2017`, `allen2018`, `yeager2018`, `white2011`, `mishra2009` and `zhu2021` (all online the year before) are cited by print year in both files. That is acceptable, but readers who find the online-first version may see a different year.

## 2. Study-type concerns

| Key | Recorded | Concern | Suggested label |
|---|---|---|---|
| grossman2002 | RCT | Match length not randomized; regression on length dummies plus 2SLS. The matrix design column itself says "Secondary analysis of RCT". | Secondary analysis of RCT (non-experimental) |
| bayer2015 | RCT | Mediation analysis of the BBBS SBM RCT. Closeness "is not randomly assigned" (abstract); uses 2SLS. | Secondary analysis of RCT (non-experimental, IV) |
| rhodes2005 | observational longitudinal | Measure development. Quality items asked only at the 18-month follow-up. Authors: "The cross-sectional nature of these data...". | Cross-sectional measure development (RCT sample) |
| lerner2005 | observational longitudinal | "Using data from Wave 1" (abstract). The matrix's own design and limitations columns say cross-sectional. | Cross-sectional |
| chetty2022 | observational longitudinal | ZIP-code-level associations of friendship-network measures with mobility. | Cross-sectional ecological |
| cunha2010 | quasi-experimental | Structural estimation of production functions with nonlinear factor models; no quasi-experimental variation claimed. | Structural econometric (observational) |
| goodenow1993 | observational longitudinal | Metadata only; design "Scale development". Nothing read supports "longitudinal". | Scale development (verify) |
| scales2000 | observational longitudinal | Metadata only; design "Survey analysis". Unsupported. | Verify (commonly described as a cross-sectional survey) |
| wentzel1998 | observational longitudinal | Metadata only; design "Survey". Unsupported. | Verify |
| clausen1991 | theory | Design column says "Longitudinal analysis", which is internally inconsistent. | Verify; probably observational longitudinal |
| oyserman2006 | RCT | The abstract reports experimental (n = 141) vs control (n = 123) groups but does not state random assignment. | Confirm randomization in full text |
| marcia1966 | theory | Design column says "Measure development". | Measure development (minor) |
| gabarddurnam2020 | methods | Matrix describes a conceptual review. | Review (minor) |
| raposa2018 | observational longitudinal | Retrospective Wave III mentor reports against earlier SES; closer to retrospective cross-sectional. | Minor |

## 3. Finding-support verdicts that are not "supported"

The full list for all 88 works is in the CSV.

| Key | Verdict | Note |
|---|---|---|
| grossman2002 | Partially supported | Duration and age findings verified in full text. But "N = 1,138" is the number randomized; 959 (85%) were followed up and used in models. "(2-year vs ~1.25-year expected length)" is the authors' illustration: "if the match of a younger adolescent lasted for two years, then the match of a similar, but older, adolescent would last for a year and a quarter". |
| amato2005 | Partially supported | The matrix says "abstract is descriptive only" and "Abstract gives no findings". The abstract does report findings: children of two continuously married parents are less likely to have a range of problems; causality cannot be shown; marriage promotion would raise average well-being only modestly. |
| kuh2003 | Cannot check | The abstract is one sentence. The key finding adds definitions "per full text - verify" that were not read. |
| cunha2007 | Cannot check | No abstract retrievable (Crossref, OpenAlex). The project's Semantic Scholar abstract was not saved. |
| gabarddurnam2020 | Cannot check | No abstract retrievable (Crossref, Europe PMC, OpenAlex). |
| roorda2017 | Cannot check (matrix) | Matrix says "Not summarized", but the full text was read and its md finding verifies (quotes exact). The row is stale. |
| elder1994, clausen1991, scales2000, goodenow1993, allen2018, wentzel1998, bandura1977, bandura1982, marcia1966, rubin1987, benshlomo2002 | Cannot check | Metadata only. No finding is stated except recalled concepts, which are flagged "verify". |

**Fields that imply more reading than the recorded evidence level** (the key findings themselves match the abstracts):

- `heller2017`: "grades 7-10 per full text; verify"
- `yeager2019`: "US 9th graders (per full text; verify)"
- `cunha2010`: "US child panel data (per full text; verify)"
- `mirandachan2016`: "Add Health per authors; verify"
- `zhu2021`: "ALSPAC-type ... verify cohort"
- `kuh2003`: as above

These details may be right, but none of them is in the abstract that was read.

**Stale fields that contradict later full-text reading:**

- `dubois2011`, limitations: "Only partial abstract available; no quantitative claims made here."
- `raposa2019`, limitations: "whether age was tested must be checked in full text"
- `vandam2018` and `vandam2021`, limitations: "age moderation not reported in abstract"
- `roorda2017`: "Not summarized"
- `references.bib` notes for `dubois2011` and `grossman2002`: "read at abstract level"

**Upgraded by the auditor.** `chetty2018` was summarized from the NBER working-paper abstract. The auditor confirmed the same claims (linear exposure effects, about 4% per year, more than 7 million families) in the QJE abstract via OpenAlex.

**Full-text claims in `fulltext_age_moderation.md` that were spot-checked and matched the saved texts:**

- DuBois 2002, Table II: developmental level k = 41, Q_b 0.53/0.06, d .17/.13 (fixed) and .17/.15 (random).
- Raposa 2019, Table 3: age k = 63, B1 = 0.02, t1 = 1.67, F(1, 643) = 2.78, "+" = p < .10.
- van Dam 2018: F = 0.309, 3.192†, 0.776, 0.878.
- van Dam 2021: F(1, 167) = 0.827; g = 0.44/0.18; time F = 2.946.
- Herrera 2007, Table F.2: all seven values listed, with the "YES+" for social studies.
- Tierney & Grossman report, Table 8: 11.4 months.
- Grossman & Rhodes 2002: N, ages, Table I declines, 2SLS pattern, 65%, "year and a quarter".
- Rhodes 2005: 347; ages 9.4–15.9, mean 12.10; median-split MANOVA Wilks λ = .99; 13–19 vs 1–6 months.
- DuBois 2011: 73 evaluations; age groups; "each of the four age groups"; "less than 6 months"; the single-parent caveat.

**Minor issues in the md:**

- In Herrera Table F.2, "*" means p < .10 and "**" means p < .05. The md table copies the stars without the legend.
- The md says "mentoring effects did not depend on age group" (line 375). DuBois 2011 reports no significant association and favorable effects within each group, but gives no per-group estimates or k in the main text. "Was not significantly associated with age group" is more exact.
- Lines 160, 73 and 348–354 still list `grossman2002` and `dubois2011` as unread, contradicting the addendum.

## 4. Evidence level per work

| Level | n | Works |
|---|---|---|
| full_text_verified: open access | 8 | dubois2002, raposa2019, vandam2018, vandam2021, dubois2005, raposa2018, roorda2017, hill2009 |
| full_text_verified: PI-supplied copy | 3 | dubois2011, grossman2002, rhodes2005 |
| full_text_verified: trial report substitute (cited article read at abstract level only) | 2 | herrera2011 (Herrera et al. 2007 P/PV report), grossman1998 (Tierney & Grossman 1995/2000 P/PV report) |
| abstract_only | 64 | All others with an abstract. For cunha2007 and gabarddurnam2020 the project's Semantic Scholar abstract could not be re-retrieved. kuh2003 has a one-sentence abstract. |
| metadata_only | 11 | elder1994, clausen1991, scales2000, goodenow1993, allen2018, wentzel1998, bandura1977, bandura1982, marcia1966, rubin1987, benshlomo2002 |

### Claims needing full text that rest on abstract or metadata only, or that the cited work does not support

| File:line | Work | Issue |
|---|---|---|
| literature_review.md:8, :263 | all | "No full texts were read"; "75 of 87 works ... 12 at metadata level". Now stale: 13 works have full-text or substitute reading, there are 88 works, and 11 are metadata only. |
| literature_review.md:71, :91, :179, :245 | dubois2011, raposa2019 | Still says age moderation "must be pulled from the full text" or is unknown. Answered by the addendum, but the main text was not updated. |
| literature_review.md:80 | heller2017 | "an adolescent program delivered through relationships appears to work through *cognitive* mechanisms, not through the relationship itself". Overstated: the authors say "Our data on mechanisms are not ideal" and find only "suggestive support". BAM is a group cognitive-behavioral program. |
| literature_review.md:135, :219 | roorda2011 | "It supports a stronger role for positive teacher relationships in adolescence". The abstract says "Overall, stronger effects ... in the higher grades" without separating positive relationships; the roorda2017 full text found only positive→engagement stronger in secondary. |
| literature_review.md:163, :218 | oyserman2006 | "randomized ... This is causal evidence". Randomization is not stated in the abstract; it needs full-text confirmation. |
| literature_review.md:172 | chetty2016 | "The MTO finding that adolescent moves can harm **shows** that a disruptive transition ... can cancel out gains". The authors say "perhaps because of disruption effects". "Is consistent with" fits better. |
| literature_review.md:174 | cunha2010 | "Substitutability between investment periods". The abstract's elasticity is "between investments in one period and stocks of skills in that period". Imprecise paraphrase. |
| literature_review.md:188 | amato2005 | "Its abstract is descriptive only". Incorrect (see section 3). |
| literature_review.md:200 | kuh2003 | Attributes critical-period, accumulation and chains-of-risk content to a work read only through a one-sentence abstract. Already labelled "glossary", but the content is not verified. |
| literature_review.md:111–119, :226; manuscript:48 | fruiht2013 | The comparative claim "after high school predicts the most attainment" rests on the abstract only; the full text is not accessible. It is labelled in the review, but not in the manuscript. |
| manuscript:56 | herrera2011 | Claim comes from the 2007 report, not the cited article (see section 6). |
| fulltext_age_moderation.csv | dubois2011, rhodes2005, grossman2002, herrera2011, grossman1998 | `access = open_full_text` is wrong. The first three are PI-supplied copies; the last two are companion reports, not the cited articles. |

## 5. Quote checks

Normalization covered whitespace, end-of-line hyphenation, ligatures and dash and quote characters. 13 of the 51 md strings are quoted section or table titles, such as "Coding Studies and Potential Moderators"; all of them matched. The string at md line 44 ("developmental level") was a short label, not a quote, and was excluded.

| File | Key | Quote (truncated) | Result |
|---|---|---|---|
| md | dubois2002 | As shown in Table II, the demographic characteristics of youth and their families that wer… | exact |
| md | dubois2002 | developmental level approaching significance (p < .06) as a moderator of effect size under… | exact (normalized) |
| md | dubois2002 | larger estimates of effect size at earlier stages of development were evident only when fa… | exact |
| md | dubois2002 | Mentor–Youth Relationships | exact |
| md | dubois2002 | neither reported average frequency of contact between mentors and youth nor length of rela… | exact |
| md | raposa2019 | Between-study moderators of the effectiveness of mentoring programs | exact |
| md | raposa2019 | There were no differences in study effect sizes as a function of youth age or youth race/e… | exact |
| md | raposa2019 | Moderators of the Effectiveness of Youth Mentoring | exact |
| md | raposa2019 | it is somewhat surprising that there were not different effects of mentoring based on yout… | exact |
| md | raposa2019 | Further research is warranted to determine whether, despite potentially poorer relationshi… | exact |
| md | raposa2019 | The lack of significant differences in effect sizes based on program length is inconsisten… | exact |
| md | raposa2019 | relationship length may be an important determinant of youth outcomes within a specific re… | match split by page header |
| md | vandam2018 | Coding Studies and Potential Moderators | exact |
| md | vandam2018 | The capacity and willingness of youths to forge close connections with natural mentors may… | exact |
| md | vandam2018 | Last, none of the participant‐ or study characteristics moderated the relation between the… | exact |
| md | vandam2018 | Relationship quality aspects and length of the mentoring relationship did not have a moder… | exact |
| md | vandam2021 | Early or middle adolescence | exact |
| md | vandam2021 | Moderators of the outcomes of youth initiated mentoring programs | exact |
| md | vandam2021 | As the mean age of youth in samples showed restriction of range problems, this variable wa… | exact |
| md | vandam2021 | Limitations, and Future Research Directions | exact |
| md | vandam2021 | Since young children and their parents may feel discomfort with this approach, it will be … | exact |
| md | herrera2011 | None of the impacts are statistically different across groups at a 0.10 level of significa… | exact |
| md | herrera2011 | for only science and starting to skip school | exact |
| md | herrera2011 | Sixty-one percent of participants attended elementary school (fourth or fifth grade); abou… | exact |
| md | herrera2011 | Impacts for Youth with Different Characteristics | exact |
| md | herrera2011 | the impacts on the paired subgroups (i.e., girls and boys, elementary and middle/high scho… | exact |
| md | herrera2011 | Table F.2 on page 111 indicates that middle/high school students may have benefited more f… | exact |
| md | herrera2011 | when one looks for impacts on many variables and among many subgroups, spurious significan… | exact |
| md | herrera2011 | Youth who are able to sustain longer matches may have personal characteristics (e.g., stro… | exact |
| md | grossman1998 | The Sample Youth and the Volunteers | exact |
| md | grossman1998 | Sixty-nine percent of youth came to the program between the ages of 11 and 13. | exact |
| md | grossman1998 | The tables contain information for the sample as a whole and for six subgroups: boys, girl… | exact |
| md | grossman1998 | Several study agencies do not match 15- to 17-year-old youth. | exact |
| md | grossman1998 | the average length of match for treatments who had been matched was almost 12 months | exact |
| md | dubois2005 | since you were 14 years old | exact |
| md | dubois2005 | Respondents ranged in age from 18 to 26 years at Wave III (mean = 21.4; SD = 1.6). | exact |
| md | dubois2005 | All analyses include statistical control for demographic variables of gender, age, and rac… | exact |
| md | dubois2005 | Mentoring relationships ranged in duration from 1 to 26 years (mean = 9.1; SD= 7.1). | exact |
| md | raposa2018 | we excluded respondents who reported that their mentor became important before the Wave I … | exact (normalized) |
| md | raposa2018 | Participants in the analytic sample were between age 18 and 28 with a mean age of 21.8 yea… | exact |
| md | roorda2017 | Only the direct association between positive relationships and engagement was stronger in … | exact |
| md | roorda2017 | teacher–student relationships appear to be no less important for older students than for y… | exact |
| md | hill2009 | Studies were also eliminated if they combined middle-school-age students with other age gr… | exact |
| md | dubois2011 | extended to programs with a relatively brief duration (i.e., less than 6 months). | exact |
| md | rhodes2005 | Neither age nor gender of the youth showed a consistent relationship with the scales | exact |
| md | dubois2011 | Age group (<8 years old, 8–10 years old, 11–14 years old, 15–18 years old) | exact |
| md | dubois2011 | participation in a mentoring program had a favorable effect on youth within each of the fo… | exact |
| md | dubois2011 | From a developmental standpoint, benefits of participation in mentoring programs are appar… | exact |
| md | grossman2002 | Adolescents in relationships that lasted a year or longer reported the largest number of i… | exact |
| md | grossman2002 | matches involving 13–16 year olds were 65% more likely to break up in each period than mat… | match split by page header |
| md | grossman2002 | if the match of a younger adolescent lasted for two years, then the match of a similar, bu… | exact |
| csv | dubois2002 | larger estimates of effect size at earlier stages of development were evident only when fa… | exact |
| csv | raposa2019 | There were no differences in study effect sizes as a function of youth age or youth race/e… | exact |
| csv | vandam2018 | Last, none of the participant‐ or study characteristics moderated the relation between the… | exact |
| csv | vandam2021 | As the mean age of youth in samples showed restriction of range problems, this variable wa… | exact |
| csv | herrera2011 | the impacts on the paired subgroups (i.e., girls and boys, elementary and middle/high scho… | exact |
| csv | grossman1998 | The tables contain information for the sample as a whole and for six subgroups: boys, girl… | exact |
| csv | dubois2005 | All analyses include statistical control for demographic variables of gender, age, and rac… | exact |
| csv | raposa2018 | we excluded respondents who reported that their mentor became important before the Wave I … | exact (normalized) |
| csv | roorda2017 | teacher–student relationships appear to be no less important for older students than for y… | exact |
| csv | hill2009 | Studies were also eliminated if they combined middle-school-age students with other age gr… | exact |
| csv | dubois2011 | benefits of participation in mentoring programs are apparent from early childhood to adole… | exact |
| csv | rhodes2005 | Neither age nor gender of the youth showed a consistent relationship with the scales | exact |
| csv | grossman2002 | matches involving 13-16 year olds were 65% more likely to break up in each period than mat… | match split by page header |

**Differences found:**

- dubois2002 footnote 7: the source reads "( p < .06)"; the md writes "(p < .06)". The md states this normalization.
- raposa2018 (md and csv): the source reads "( N = 4,498)"; spacing only.
- raposa2019 "relationship length may ... be an important determinant": in the source the sentence is broken by the running head "Journal of Youth and Adolescence (2019) 48:423–443". The words are identical.
- grossman2002 "matches involving 13–16 year olds ... 10–12 year olds": broken by a page header after "matches with". The words are identical. The csv uses a hyphen ("13-16") where the source has an en dash.

No quote was not found, and no wording differences were found.

## 6. Manuscript citation checks (`working_paper_v2.src.md`)

All 27 keys exist in `references.bib`.

| Line | Citation | Claim (abridged) | Verdict | Note |
|---|---|---|---|---|
| 31 | elder1998; rutter1996 | Turning points central to life-course research | Supported | Elder supports life-course theory; Rutter discusses turning points |
| 32 | rutter1996 | Effects heterogeneous; depend on qualities of experience more than age | Supported | Paraphrases "particular qualities of experiences ... (rather than universal life phase transitions)" |
| 33 | dahl2018 | Adolescence a period of plasticity and opportunity for intervention | Supported | Abstract: "formational neurobiological development", "windows of opportunity" |
| 34 | fuhrmann2015 | Concrete evidence mostly lacking | Supported | Near-verbatim abstract |
| 38 | chetty2016 | Moving before 13 improved college and earnings; adolescent moves did not | Supported | Abstract: adolescent moves "slightly negative" |
| 39 | chetty2018 | Roughly linear gains per year of exposure | Supported | QJE abstract (OpenAlex) |
| 40 | cunha2007 | Early skills raise returns to later investment | Cannot check | No abstract or full text available to auditor; consistent with project summary |
| 41 | cunha2010 | Later investment can substitute for earlier, particularly for noncognitive skills | Partially supported | Abstract: substitutability between investment and existing skill stocks decreases with stage for cognitive and increases for noncognitive skills. Wording loosely recasts this as early-vs-late investment |
| 44 | dubois2002; raposa2019 | Small-to-modest average benefits | Supported | DuBois "modest or small"; Raposa "medium/moderate" by prevention benchmarks but "modest impact". Consider "small to moderate" |
| 45 | grossman2002 | Most benefit in relationships of a year or longer | Supported | Full text; duration not randomized (2SLS) |
| 46 | roorda2011 | More strongly in higher grades | Partially supported | Leaves out the abstract's caveat (negative relationships stronger in primary school) and conflicts with roorda2017 (only 1 of 5 paths stronger) |
| 46 | benner2009 | Transition to high school a point of disruption | Supported | Abstract |
| 47 | neild2008 | Ninth-grade outcomes predict dropout | Supported | Abstract |
| 48 | fruiht2013 | Strongest association for mentors important after high school | Supported (abstract only) | Full text not read; retrospective timing and likely reverse causation not mentioned in the manuscript |
| 52 | dubois2011 | 73 evaluations; age <8 to 15–18; favorable in every group; "not confined to a particular stage of development" | Supported | PI copy; quote exact (Summary, p. 57) |
| 52 | dubois2002 | d = .17 vs .13, not significant | Supported | Fixed-effects values; random effects .17 vs .15. Say "fixed-effects" |
| 53 | raposa2019 | No significant age association (range about 9–16); "somewhat surprising" | Supported | Full text; marginal p < .10 |
| 55 | vandam2018; vandam2021 | No significant age differences | Supported | van Dam 2018 relationship quality p < .10 (k = 8); van Dam 2021 rests on 11 samples |
| 56 | herrera2011 | Impacts did not differ between elementary and secondary students | **Not supported by the cited work as read** | From the 2007 P/PV report (Table F.2, Ch. IV), not in the bib; the 2011 article (abstract only) reports no age subgroups. Typo ",." |
| 57 | roorda2017 | One association stronger in secondary, other four equal | Supported | "Equal" means not significantly different (χ²(4) = 2.69, p = .61) |
| 59 | grossman2002 | Matches with 13–16 year olds ended sooner; benefits in year-plus matches | Supported | Full text |
| 60 | rhodes2005 | Age unrelated to quality; longer matches higher quality | Supported | Full text; cross-sectional, median-split age |
| 75 | white2011 | MICE with predictive mean matching | Supported | Tutorial on MICE |
| 76 | rubin1987 | Rubin's rules | Supported | Standard attribution (metadata only) |
| 77 | vanderweele2017 | E-values | Supported | Abstract |
| 78 | vonelm2007 | STROBE | Supported | Abstract |
| 143 | mishra2009; smith2015 | Restricted life-course models | Supported | Abstracts |
| 159 | fuhrmann2015 | Adolescent sensitive periods more asserted than demonstrated | Supported | Fair paraphrase of "concrete evidence ... mostly lacking" |
| 160 | grossman2002 | Relationship duration matters | Supported | Duration not randomized |
| 175 | grossman2002 | Older adolescents' relationships tend to end sooner | Supported | Full text (65% higher hazard for ages 13–16) |

Totals: 26 supported (one at abstract level only), 2 partially supported, 1 not supported by the cited work as read, 1 cannot check, across 30 brackets. Line 46 has two brackets.

## Recommended corrections

Exact current text is followed by suggested text. Items marked "verify" need a person to check the source before the change.

### references.bib and evidence_matrix.csv

1. `kuh2003` title: `{{Life course epidemiology: Figure 1}}` → `{{Life course epidemiology}}`. In the matrix, `Life course epidemiology: Figure 1` → `Life course epidemiology`.
2. `hernan2016` title: `{{Using Big Data to Emulate a Target Trial When a Randomized Trial Is Not Available: Table 1.}}` → `{{Using Big Data to Emulate a Target Trial When a Randomized Trial Is Not Available}}`. Make the same change in the matrix.
3. `smith2016`: `pages = {dyw164},` → `volume = {45},` / `number = {4},` / `pages = {1271--1279},` (per Europe PMC; verify on the publisher page).
4. `smith2021`: add `volume = {53},`. Decide between `year = {2021}` (Crossref print) and `2022` (PubMed and series volume year) (verify).
5. `laub1993`: `{{TURNING POINTS IN THE LIFE COURSE: WHY CHANGE MATTERS TO THE STUDY OF CRIME*}}` → `{{Turning Points in the Life Course: Why Change Matters to the Study of Crime}}`.
6. `bayer2015`: `{{USING VOLUNTEER MENTORS TO IMPROVE THE ACADEMIC OUTCOMES OF UNDERSERVED STUDENTS: THE ROLE OF RELATIONSHIPS}}` → `{{Using Volunteer Mentors to Improve the Academic Outcomes of Underserved Students: The Role of Relationships}}`.
7. `heller2017`: `...Dropout in Chicago*}}` → `...Dropout in Chicago}}`. `chetty2018`: `...Childhood Exposure Effects*}}` → `...Childhood Exposure Effects}}`.
8. Remove trailing periods from the 11 titles listed in section 1, and replace U+2010 "‐" with "-" in the 6 Wiley entries.
9. `cunha2010` author: `Cunha, Flavio and Heckman, James J. and Schennach, Susanne M.` is consistent with PubMed. Keep it, but leave the existing note as is.
10. `benshlomo2002`: keep two authors, and confirm Kuh as second author on the OUP article page (verify).
11. Bib notes. `dubois2011` and `grossman2002`: `read at abstract level` → `read in full text (copy supplied by the PI)`. `dubois2002`, `raposa2019`, `vandam2018`, `vandam2021`, `dubois2005`, `raposa2018`, `hill2009`: `read at abstract level` → `read in full text (open access)`. `roorda2017`: `read at metadata_only level` → `read in full text (open access)`.

### evidence_matrix.csv

12. `study_type` changes:
    - grossman2002 `RCT` → `secondary analysis of RCT (non-experimental)`
    - bayer2015 `RCT` → `secondary analysis of RCT (non-experimental, IV)`
    - rhodes2005 `observational longitudinal` → `cross-sectional (measure development)`
    - lerner2005 `observational longitudinal` → `cross-sectional`
    - chetty2022 `observational longitudinal` → `cross-sectional ecological`
    - cunha2010 `quasi-experimental` → `structural econometric (observational)`
    - goodenow1993, scales2000, wentzel1998: mark `observational longitudinal (unverified)` until read
    - clausen1991: make study_type and design consistent (verify)
    - oyserman2006: keep `RCT` only after confirming randomization in the full text (verify)
13. `evidence_level_read`:
    - dubois2002, raposa2019, vandam2018, vandam2021, dubois2005, raposa2018, hill2009: `abstract (...)` → `full_text (open access)`
    - roorda2017: `metadata_only` → `full_text (open access)`
    - herrera2011, grossman1998: `abstract (crossref)` → `abstract (crossref); companion P/PV report read`
14. `dubois2011` limitations: `Only partial abstract available; no quantitative claims made here.` → `Full text (PI copy) read. Age is a between-study moderator test (no significant association); per-age-group estimates not given in main text.`
15. `raposa2019` limitations: `Abstract does not report age as a significant moderator; whether age was tested must be checked in full text.` → `Full text read: mean sample age tested as continuous moderator, not significant (F(1,643)=2.78, p<.10); sample means 9-16; between-study only.`
16. `vandam2018` limitations: `Mostly correlational primary studies; age moderation not reported in abstract.` → `Mostly correlational primary studies; full text: age not a moderator for presence (F(1,163)=0.31), marginal for quality (p<.10, k=8).` `vandam2021`: `Few studies; age moderation not reported in abstract.` → `Few studies (11 samples); full text: age group not a significant moderator (F(1,167)=0.83).`
17. `roorda2017` key_finding: `Not summarized (no abstract retrieved).` → `Only the association between positive relationships and engagement was stronger in secondary than primary school (beta .32 vs .24); the other four paths did not differ (chi2(4)=2.69, p=.61).`
18. `grossman2002` key_finding: `(N = 1,138, ages 10-16)` → `(1,138 randomized, 959 followed up; ages 10-16)`, and `(2-year vs ~1.25-year expected length)` → `(authors' illustration: a match lasting two years for a younger adolescent would last about a year and a quarter for a similar older one)`.
19. `amato2005` key_finding: `(abstract is descriptive only)` → `(abstract: children of continuously married parents have fewer problems; causality not demonstrable; marriage promotion would improve average well-being only modestly)`. Limitations: `Abstract gives no findings.` → `Review; causal claims limited.`
20. Population fields marked "per full text; verify" (heller2017, yeager2019, cunha2010, mirandachan2016, zhu2021, kuh2003): either verify from the full text or remove the unverified detail.

### fulltext_age_moderation.csv and .md

21. In the csv `access` column: `dubois2011`, `rhodes2005`, `grossman2002` `open_full_text` → `pi_supplied_copy`; `herrera2011`, `grossman1998` `open_full_text` → `companion_report_not_cited_article`.
22. md line 375: `mentoring effects did not depend on age group` → `mentoring effects were not significantly associated with age group (per-group estimates not reported in the main text)`. Update lines 73, 160 and 348–354, which still list `dubois2011` and `grossman2002` as unread. Add the star legend to the Herrera Table F.2 reproduction (* p < .10, ** p < .05).

### manuscripts/working_paper_v2.src.md

23. Line 56: `Within one
school-based mentoring trial, impacts did not differ reliably between elementary and secondary students [@herrera2011], as reported in the publicly released trial report,.` → `Within one school-based mentoring trial, impacts did not differ reliably between elementary and middle/high school students, according to the publicly released trial report [@herrera2007report].` Add a bib entry for Herrera, C., Grossman, J. B., Kauh, T. J., Feldman, A. F., & McMaken, J., with Jucovy, L. Z. (2007), *Making a Difference in Schools: The Big Brothers Big Sisters School-Based Mentoring Impact Study*, Public/Private Ventures (ERIC ED503245). Mark it as gray literature (verify).
24. Lines 45–46: `Teacher–student relationship quality is associated with engagement and achievement, more strongly
in higher grades [@roorda2011].` → `Teacher–student relationship quality is associated with engagement and achievement [@roorda2011]; in an updated meta-analysis, only the link between positive relationships and engagement was stronger in secondary than in primary school [@roorda2017].` Then trim the duplicate sentence at line 56–57 or keep it as the full-text detail.
25. Lines 40–41: `while later investment can substitute for earlier investment,
particularly for noncognitive skills [@cunha2010]` → `while the substitutability of investment for existing skills falls at later stages for cognitive skills but rises for noncognitive skills, so later remediation is relatively more feasible for noncognitive skills [@cunha2010]`.
26. Line 52: `(d = .17 vs .13)` → `(fixed-effects d = .17 vs .13; Q_b = 0.53)`.
27. Line 48: `found the strongest association for mentors who became important after high school [@fruiht2013].` → `found the strongest association for mentors who became important after high school, although timing was reported retrospectively and post-high-school mentors partly reflect continued education [@fruiht2013].`
28. Line 52: `In DuBois et al. [@dubois2002]` renders as "DuBois et al. (DuBois et al., 2002)". Use `[-@dubois2002]` or the in-text form `@dubois2002`. The same applies to `Raposa et al. [@raposa2019]` on line 53.

### docs/literature_review.md

29. Line 8: `No full texts were read.` → `The main text was written from abstracts; full texts read later are reported in the addendum and in fulltext_age_moderation.md.` Line 263: `75 of 87 works were read at abstract level, and 12 at metadata level only. **No full texts were read.**` → `Of 88 works, 13 were later read in full text or through a companion trial report, 64 at abstract level and 11 at metadata level only.`
30. Line 71 (DuBois 2011 row): `Not read` → `Full text (PI copy); see addendum`.
31. Line 80: `This matters for the project: an adolescent program delivered through relationships appears to work through *cognitive* mechanisms, not through the relationship itself.` → `The authors' mechanism data are "not ideal"; they find only suggestive support for a cognitive mechanism and no positive evidence for a generic mentoring effect.`
32. Line 135: `It supports a stronger role for positive teacher relationships in adolescence, but` → `It suggests stronger associations in higher grades overall (but not for negative relationships), and`.
33. Line 163: `**This is causal evidence that identity-focused support can work in the year before the high-school transition.**` → `**If random assignment is confirmed in the full text, this is causal evidence that identity-focused support can work in the year before the high-school transition.**` Make the matching change in line 218: `All three are **causal**.` → `Two are randomized (Yeager et al.; Sinclair et al.); Oyserman et al.'s design needs full-text confirmation.`
34. Line 172: `shows that a *disruptive transition* in adolescence can cancel out gains` → `is consistent with the authors' suggestion that a *disruptive transition* in adolescence can cancel out gains`.
35. Line 188: `Its abstract is descriptive only.` → `Its abstract reports that children of continuously married parents have fewer problems, while noting that causality cannot be demonstrated.`

### Scratch provenance (not a project file)

36. `scratchpad/litreview/abstracts.json`: the entries for `clausen1991` (PMID 34414429) and `scales2000` (PMID 43009667) belong to unrelated papers. Delete them or mark them invalid so they are not reused.

## Limits of this audit

- Full texts were available only for the 13 works listed in section 4, so all other findings were checked against abstracts only.
- No abstract could be retrieved for `cunha2007`, `gabarddurnam2020`, or the 11 metadata-only works, so they are marked "cannot check".
- The two P/PV reports and the PI-supplied PDFs were checked as they exist locally. Their authorization and provenance were not re-examined.
- Europe PMC was used as a second metadata source where it had a record (54 of 88). For the rest, Crossref was the only source.
- No participant data or personal information is involved. All names in this file are those of published authors.
