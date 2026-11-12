# Unverified references and items to check

Checked 2026-11-12. Nothing on this list is cited as evidence in `literature_review.md` or included in `references.bib`. Each item says why it could not be verified or why it is only partly checked.

## Works that could not be verified in Crossref

| Intended work (as remembered; not confirmed) | Why it is listed here | Suggested next step |
|---|---|---|
| Steinberg, L. (2014). *Age of Opportunity: Lessons from the New Science of Adolescence* (trade book) | Crossref has no DOI for the book. The search returned only a 2018 book review (10.2989/17280583.2018.1480166), which is a different work and was excluded. | Verify through a library catalog or ISBN. Use Steinberg (2005), which is verified, for the sensitive-period argument. |
| Allensworth, E. M., & Easton, J. Q. (2005). The on-track indicator as a predictor of high school graduation (Consortium on Chicago School Research report) | Gray literature. Not in Crossref. | Get it from the UChicago Consortium website and cite it as a report. It is predictive only. |
| Allensworth & Easton (2007), "What matters for staying on-track…" (Consortium report) | Gray literature. Not searched in Crossref. | Same as above. |
| McLanahan, S., & Sandefur, G. (1994). *Growing Up with a Single Parent* (book) | Not checked: a book with probably no Crossref DOI. | Verify by ISBN. McLanahan et al. (2013), which is verified, covers the causal debate. |
| Sampson, R. J., & Laub, J. H. (1993). *Crime in the Making* (book) | Not checked: a book. | Verify by ISBN. Laub & Sampson (1993) and Sampson & Laub (2005) are verified. |
| Erikson, E. H. (1968). *Identity: Youth and Crisis* (book) | Not checked: a book. | Verify by ISBN. |
| Werner & Smith Kauai monographs (e.g., *Overcoming the Odds*, 1992) | Not checked. | Werner (1993), which is verified, is used instead. |
| Benson's developmental assets books or chapters | Not checked. | Scales et al. (2000) is verified, but only at metadata level. |
| Lerner et al., PYD handbook chapters | Not checked. | Lerner et al. (2005) is verified. |
| Rubin (1976), "Inference and missing data," *Biometrika* | Not searched. | Verify if MAR/MNAR definitions are needed. |
| Additional Check & Connect RCTs (e.g., Sinclair et al., 2005) | Not searched. Only Sinclair et al. (1998) was verified. | Search Crossref and the What Works Clearinghouse. |
| Big Brothers Big Sisters full impact reports (P/PV, 1995; 2007) | Gray literature. | Cite the verified journal versions: Grossman & Tierney (1998) and Herrera et al. (2011). |

## Works that are verified but were not read in full (follow-up needed)

These works are in `references.bib`, but the content needed for the project's key questions was **not** available in the abstracts read:

- **DuBois, Portillo, Rhodes, Silverthorn & Valentine (2011)** [`dubois2011`]. Only a partial abstract was available. The overall effect size and the **results for age as a moderator** must be taken from the full text. No numbers are attributed to this work.
- **Raposa et al. (2019)** [`raposa2019`]. The abstract does not mention age moderation. Check in the full text whether age was tested.
- **Chetty & Hendren (2018)** [`chetty2018`]. The abstract was read from the NBER working paper w23001, not the QJE version. Confirm that the figure of about 4% per year of exposure matches the published article.
- **Yeager et al. (2019)** [`yeager2019`]. The statement that the sample was ninth graders is **recalled**. Verify it against the full text.
- **Heller et al. (2017)** [`heller2017`]. The grade range of BAM participants is **recalled**. Verify it.
- **Miranda-Chan et al. (2016)** [`mirandachan2016`]. Add Health as the data source is **recalled**. The abstract says only "nationally representative." Verify it.
- **Zhu et al. (2021)** [`zhu2021`]. The empirical cohort name is not given in the abstract. Verify it.
- **Metadata-only items** (no abstract retrieved): `elder1994`, `clausen1991`, `scales2000`, `roorda2017`, `goodenow1993`, `allen2018`, `wentzel1998`, `bandura1977`, `bandura1982`, `marcia1966`, `rubin1987`, `benshlomo2002`. The literature review cites these only for the concepts they are known for.

## Metadata problems found in Crossref records

- `elder1994`: Crossref stores the author as given = "Glen H. Elder", family = "Jr.". This was normalized in the BibTeX.
- `cunha2010`: The Crossref record has no authors. Authors were taken from the PubMed record (PMID 20563300). Full given names still need checking.
- `benshlomo2002`: Crossref lists only Y. Ben-Shlomo. D. Kuh was added as second author from the Semantic Scholar record.
- Online and print years differ for several works: `heller2017` (online 2016), `allen2018` (online 2016), `yeager2018` (online 2017), `white2011` (online 2010), `fruiht2013` (online 2012), `mishra2009` (online 2008), `zhu2021` (online 2020), `vandam2021` (online 2020). The BibTeX uses the print year. The log records both years.
- Several DOIs remembered at the start were wrong and were replaced with the DOIs Crossref returned, after checking authors and venue: `laub1993`, `thomas2008`, `werner1993`, `herrera2011`, `rhodes2006`, `dubois2005`, `erickson2009`, `hurd2010`, `fruiht2013`, `amato2005`, `benner2009`. This is why the verification step matters.
- PubMed searches by DOI returned unrelated records for `clausen1991` and `scales2000`. Those abstracts were thrown out, and both works are treated as metadata-only.
