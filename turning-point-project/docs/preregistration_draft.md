# Preregistration draft (OSF "Secondary data preregistration" structure)

Status: **DRAFT — not submitted.** To be registered (e.g. on OSF) only after the blocking items
in `statistical_analysis_plan.md` §12 are resolved and the PI approves. All analytic detail is in
the SAP; this document records the commitments a registry asks for.

## Study information

- **Title:** When does adult support matter most? Parental support across adolescence and
  educational attainment in the NLSY97.
- **Research question:** Does the association between adolescents' reports of a very supportive
  parent and later educational attainment differ by age at report (12–16)?
- **Hypotheses:** H1a (Δ = θ(16) − θ(12) ≠ 0) and H1b (|Δ| < 0.20 SD), mother support (Q1);
  same for father support (Q2). No directional prediction is made: the literature
  (`literature_review.md`) offers arguments for larger associations earlier (exposure/accumulation;
  `chetty2018`), later (proximity to decisions; `roorda2011` grade pattern), and no difference.

## Data description

- **Dataset:** NLSY97, U.S. Bureau of Labor Statistics; public-use release through round 21.
- **Access:** free public download (NLS Investigator); no restricted variables used.
- **Prior knowledge of the data:** Neither the PI nor the analysis code has opened NLSY97
  respondent-level data as of this draft. The PI has read the published literature, including NLSY97-based
  studies; any such familiarity will be disclosed here before registration. Codebook metadata
  (question wording, universes, frequencies shown in codebooks) were read during the feasibility
  audit; codebook frequencies are univariate and do not reveal exposure–outcome relationships.
- **Data-access timestamp:** to be recorded at download (SHA-256 via `tpp validate`).

## Variables

As in SAP §4. Exposure coding (very supportive = 1) and outcome (`CVC_HGC_EVER`, latest round)
are fixed here.

## Analysis plan

- Model, variance, df: SAP §5.
- Missing data: SAP §6 (MI, m = 40).
- Inference criteria, SESOI, verdict rules and multiplicity: SAP §7.
- Sensitivity analyses S1–S8: SAP §8. Exploratory analyses: SAP §2 (listed, labelled exploratory).
- Data exclusion: none beyond item universe and valid-skip codes.
- Outliers: none removed; `hgc` is bounded 0–20.

## Commitments

1. All confirmatory results reported regardless of direction or significance.
2. Deviations from this plan reported in a deviations table with reasons.
3. Analysis code public; data obtained by readers from BLS.
4. The PI's motivation (founding a youth mentoring organisation) disclosed as a potential
   conflict of interest.
