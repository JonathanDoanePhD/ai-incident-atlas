# Independent review response and audit

**Project:** The Turning Point Project · **Audit date:** 2026-11-13 · **Auditor:** Claude (AI), at the PI's request, after an external
methodological review recommended major revisions. The audit prioritized finding errors over defending earlier conclusions.
Nothing has been published or deployed as part of this audit.

## 1. Summary

The four completed analyses were checked against their frozen plans, codebooks and code, re-run end to end, and their equivalence
claims recomputed with independent code. The core estimates hold. The audit found:

- **One reproducibility defect.** The multiple-imputation random-number generator was never seeded, so the recorded seed did not
  reproduce results. Now fixed and re-run.
- **Several overstated interpretations.** Equivalence was read as "timing doesn't matter", and accumulation was read as cumulative effects.
- **Construct conflation.** Parents and teachers were discussed as if they were mentors, and age at measurement as if it were age at
  onset or duration.
- **Inaccurate description of the plans.** "Preregistration" was used for locally frozen plans.
- **Bibliographic errors.** A set of these was found and corrected.

No primary test decision changed. **The project is not yet ready for public release.** Four things remain outstanding: replication in
R or Stata, a second human analyst, the unrun custom-weight sensitivity analysis, and the PI's review of the corrected text.

## 2. Files and code inspected

- **Plans and freezes:** `docs/statistical_analysis_plan.md`, `preregistration_draft.md`, `sap_hsls09_grade9.md`,
  `sap_nlsy79cya_childhood.md`, `sap_nlsy97_accumulation.md`, `PLAN_FREEZE*.md` (7), git history.
- **Mappings and dictionaries:** `config/mappings/nlsy97.yaml`, `nlsy97_accumulation_spec.json`, `nlsy79cya_spec.json`,
  `docs/variable_dictionary*.{md,csv}`, and the official codebooks (NLSY97 `.cdb`, NLSY79 CYA `.cdb`, NLSY79 `.cdb`, HSLS:09 codebook).
- **Extraction:** `scripts/extract_nls.py`, the inline NLSY97 and HSLS:09 extraction code (session log), `data/raw/*/*.csv` (git-ignored),
  provenance manifests.
- **Analysis code:** `src/turning_point/modeling.py`, `longitudinal.py`, `preprocessing.py`, `scripts/run_paper1.py`, `run_b2_hsls.py`,
  `run_p2_cya.py`, `run_p1e_accumulation.py`, `crosscheck_variance.py`, `report_paper1.py`.
- **Outputs:** `outputs/*.json` (original versions preserved in `outputs/audit/original_2026-11-12/`).
- **Text:** `manuscripts/working_paper_v2.src.md`, `docs/results_*.md`, `docs/literature_review.md`, `website/index.html`,
  `website/assets/app.js`, `scripts/build_site_data.py`, `README.md`.
- **Bibliography:** `docs/references.bib`, `evidence_matrix.csv`, `fulltext_age_moderation.*`, saved full texts. Audited separately in
  `docs/bibliography_audit.md` and `.csv`.

New audit code: `scripts/audit_checks.py` (post-hoc checks → `outputs/audit/audit_results.json`),
`scripts/build_estimands_table.py` (→ `outputs/primary_estimands.csv`), `scripts/fill_manuscript_numbers.py`.

## 3. Verification results

### 3.1 Plan integrity and timeline

All seven freeze records still match their files (SHA-256). Each freeze commit predates the creation of the data extract it governs:

| Study | Freeze commit (UTC) | Extract created (UTC) |
|---|---|---|
| P1 | 20:39 | 20:41 |
| B2 | 21:18 | 21:21 |
| P2 | 21:46 | 21:47 |
| P1E | 21:50 | 21:51 |

All on 2026-11-12. **However**, the freezes are commits in an investigator-controlled repository, not external registrations. B2, P2 and P1E
were planned after P1's results were known, and P1E's author knew the P1 data (Issue I-06).

### 3.2 Data and coding

Extract counts match codebook frequencies for every item checked:
- **NLSY97:** support items, age, last interview round, sex.
- **HSLS:09:** math-teacher items, talk-to-adult item, degree outcome.
- **NLSY79 CYA:** degree, praise, closeness, race, sex, birth order. All children link to a mother record.

Coding of race (CRACE 1 Hispanic, 2 Black, 3 other), sex, missing-value codes, the degree thresholds and the outcome-observation rules
was confirmed in the codebooks.

### 3.3 Sample selection, missing data, weighting, clustering, standard errors, multiplicity

| | P1 NLSY97 | B2 HSLS:09 | P2 NLSY79 CYA | P1E NLSY97 |
|---|---|---|---|---|
| Sample | Item universe (lives with parent figure) + valid answer: 8,607 mothers / 6,436 fathers | BY + F1 respondents with math-teacher items in both grades: 14,259 | Born 1979–95, praise in both windows: 6,190 children, 3,138 mothers | Age 12–14, four valid reports, complete cases: 2,566 |
| Outcome missing | Imputed (769 / 620) | Imputed (3,667, 26%) | Imputed (510) | Complete cases |
| Imputation | MICE-PMM, m = 40 (plan) | m = 20 (plan) | m = 20 (plan) | none |
| Weights | Round-1 cross-sectional (plan) | W2W1STU (plan) | Unweighted primary (plan); child weight S3 | Round-1 weight |
| Variance | Taylor, 117 strata × 2 PSU, df 117; domain estimation (zero weight outside item universe) | 200 BRR replicates, standard BRR (no Fay; determined from replicate structure), df 199 | Cluster-robust by mother, df 3,137 | Taylor, df 117 |
| Multiplicity | Holm across mother/father (plan) | Single primary | Single primary; Holm across exposures added (not in plan) | Exploratory |
| Independent SE check | Paired-PSU jackknife = Taylor to 3 decimals (one imputation) | **Not done** | **Not done** | **Not done** |

CIs use t with the stated df (Rubin/Barnard–Rubin df after imputation). Confirmed in code.

### 3.4 Reproducibility re-run

1. **First re-run (original code).** Imputation-based estimates were **not reproducible**: differences of up to ~0.01 years (P1) and ~0.2
   points (B2, P2). Exploratory subgroup estimates moved more, for example one poverty contrast went from 0.75 to 0.66. The complete-case
   analyses (P1E, B2 S2, audit checks) reproduced exactly. Diagnosis: statsmodels' `MICEData` takes its own `rng` argument and otherwise uses
   fresh OS entropy, so the scripts' `np.random.seed()` had no effect. Single-threaded linear algebra and a fixed `PYTHONHASHSEED` did not
   help, which confirmed the diagnosis.
2. **Fix.** `MICEData(..., rng=seed)` in `run_paper1.py`, `run_b2_hsls.py` and `run_p2_cya.py`. Two seeded runs are now byte-identical.
3. **Official results** are now the seeded re-runs (`outputs/*.json`). The original outputs are preserved in `outputs/audit/original_2026-11-12/`,
   and the unseeded re-run in `outputs/audit/rerun_2026-11-13/`. No primary test decision changed:

| Contrast | Original (v2) | Seeded re-run (v3) |
|---|---|---|
| P1 mothers Δ (years) | +0.264 (−0.208, 0.737) | +0.275 (−0.198, 0.748) |
| P1 fathers Δ | −0.183 (−0.640, 0.275) | −0.191 (−0.655, 0.273) |
| P1 Holm p | .54 | .50 |
| B2 θ11 − θ9 (prob.) | +0.0131 (−0.0045, 0.0308) | +0.0151 (−0.0021, 0.0323) |
| P2 praise Δ (prob.) | −0.0167 (−0.0390, 0.0056) | −0.0157 (−0.0393, 0.0080) |

### 3.5 Equivalence claims (recomputed with independent code)

TOST p = max of the two one-sided p-values; "within" means the 90% CI lies strictly inside ±margin. All numbers are from the seeded re-run;
the original values are in `outputs/audit/equivalence_recheck_original.csv`.

| Claim | Estimate | SE | df | 95% CI | 90% CI | Margin | p (two-sided) | TOST p | 90% CI within margin | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| P1 fathers, Δ (SD units) | −0.062 | 0.076 | 99.4 | −0.213 to 0.089 | −0.188 to 0.064 | ±0.20 | .42 | .036 | yes | equivalent (linear contrast only) |
| P1 mothers, Δ (SD units) | +0.088 | 0.077 | 106.9 | −0.064 to 0.240 | −0.039 to 0.216 | ±0.20 | .25 | .074 | no | not shown |
| **B2 HSLS:09, θ11 − θ9** | **+0.0151** | **0.0087** | **150.7** | **−0.0021 to 0.0323** | **+0.0007 to 0.0295** | **±0.03** | **.086** | **.045** | **yes (upper limit 0.0295 vs 0.03)** | **equivalent, but fragile** (see below) |
| P2 praise, Δ | −0.0157 | 0.0120 | 474.6 | −0.0393 to 0.0080 | −0.0355 to 0.0042 | ±0.03 | .19 | .117 | no | not shown |
| P2 closeness, Δ | −0.0167 | 0.0123 | 1,294.5 | −0.0409 to 0.0075 | −0.0370 to 0.0036 | ±0.03 | .18 | .140 | no | not shown |

TOST lower/upper p-values for each row: `outputs/audit/equivalence_recheck_seeded.csv` (and `_original.csv` for v2 values). No equivalence
claim is supported by the 95% CI lying within the margins. All claims rest on the 90% CI, as TOST at α = .05 requires.
Exact values are in `outputs/primary_estimands.csv`.

**B2 fragility.** Across three imputation runs of the same model, the B2 TOST p was .030 (original), .030 (unseeded re-run) and .045 (seeded).
The upper 90% limit came within 0.0005 of the margin, and the seeded 90% CI also excludes zero. A precision check with m = 100 is reported
in §3.7. The B2 verdict should be described as borderline.

### 3.6 Post-hoc audit analyses (not in any frozen plan)

| Check | Result |
|---|---|
| **A.** P1: θ equal at all five ages (4-df design Wald, complete cases) | Mothers F = 1.68, p = .16; fathers F = 2.18, p = .076. Irregular pattern (high at 14 and 16, low at 13 and 15) |
| **B.** P2: equalize reliability (one report per window) | Δ = −2.4 points (−4.5 to −0.4), n = 5,375. Two reports per window: −1.7 (−4.9 to 1.5), n = 3,513. Ordering not explained by unequal numbers of reports |
| **C.** P1E: model comparison | Cumulative slope 0.22 (0.14–0.31). Strict accumulation (equal pattern means within count) F(11, 107) = 1.88, p = .0498. "All four years" indicator 0.69 (0.31–1.08), with the count term going to 0.01. "Any loss of support" −0.49 (−0.77 to −0.21). Approximate weighted AIC: loss 4,970.7; saturated 4,971.0; stability 4,971.8; cumulative 4,986.0; best single round (1998) 4,989.4; onset 5,007.0 |
| **C.** P1E: complete-case selection | Analyzed vs excluded (weighted): grade completed 14.7 vs 13.7; very supportive in 1997 78% vs 72%; parent education 13.9 vs 13.3. IPW for inclusion: slope 0.219 (0.129–0.308), unchanged |

### 3.7 Monte Carlo precision of B2 (m = 100)

Post-hoc precision check with m = 100 imputations (same model and seed; `outputs/audit/b2_results_m100_mc_check.json`):

| | Estimate | SE | 95% CI | 90% CI | TOST p |
|---|---|---|---|---|---|
| θ9 | −0.0017 | 0.0058 | −0.0132 to 0.0098 | | |
| θ11 | +0.0122 | 0.0070 | −0.0016 to 0.0260 | | |
| θ11 − θ9 | +0.0139 | 0.0089 | −0.0037 to 0.0315 | −0.0009 to 0.0287 | .037 |

The equivalence verdict holds with m = 100, but remains borderline: the upper 90% limit is 0.0287 against a 0.03 margin. The official result
stays the plan's m = 20 run. Across all four runs the TOST p ranged from .030 to .045.

## 4. Issues identified

| ID | Severity | Issue | Evidence | Correction |
|---|---|---|---|---|
| I-01 | **High** | Imputation RNG not seeded; recorded seed did not reproduce results | §3.4 | Fixed (`rng=seed`); all MI analyses re-run; outputs replaced; originals archived |
| I-02 | **High** | Equivalence read as "timing irrelevant", although margins are as large as the associations: P1 ±0.20 SD vs θ(14) ≈ 0.15 SD; B2 ±3 points vs θ11 ≈ 1.3 points | §3.5 | Text now says equivalence rules out only differences about as large as the whole association |
| I-03 | **High** | Linear 16-vs-12 contrast ignores nonlinear age heterogeneity; "fathers equivalent" stated without qualification | §3.6 A | Qualified; all-ages test reported as post-hoc |
| I-04 | **High** | "Consistent with accumulation" overstated: non-rejection treated as support; stability, loss and stable-trait explanations fit as well; complete-case selection | §3.6 C | Reframed: cumulative effects not demonstrated |
| I-05 | **High** | Construct conflation: parents and teachers vs mentors; age at measurement vs onset vs duration | `docs/construct_validity.md` | Construct table added; text separates constructs; mentoring implications made tentative |
| I-06 | **High** | "Preregistration" language for locally frozen plans; B2, P2, P1E planned after P1 results | §3.1 | All text now says "frozen locally in the project repository; not externally preregistered" |
| I-07 | Medium | B2 equivalence borderline and sensitive to Monte Carlo error; two sensitivity analyses significant toward grade 11 | §3.5, §3.7 | Described as borderline |
| I-08 | Medium | B2 compares ratings of different teachers; items measure teaching more than relationship | construct table | Stated |
| I-09 | Medium | Deviations from plans: S6b (custom weights) not run; BH-FDR for exploratory analyses (P1 SAP §7) not applied; household-structure heterogeneity, earnings and employment (P1 exploratory) not run; STROBE checklist not produced; B2 S3 on 5 of 20 imputations; P1 "missing indicator for absent parent" replaced by imputation; P2 Holm added (not planned) | Plans vs code | Listed in limitations; S6b workflow prepared (`scripts/run_paper1_s6b.py`) **Update 2026-11-13:** S6b run (D-033); it matches S2 complete cases. |
| I-10 | Medium | Earlier bug (item-universe label) and a manual JSON patch (S5b n) | Session history | Bug fixed before results; S5b n now produced by code; verified in re-run |
| I-11 | Medium | Wrong citation for the trial age result (`herrera2011` → 2007 report); outdated and overstated literature claims; wrong study-type labels; junk titles; incomplete metadata | `bibliography_audit.md` | Corrected in bib, matrix, review and manuscript (§5) |
| I-12 | Low | P1 equivalence in SD units treats the SD as fixed | Code | Noted |
| I-13 | Low | AIC comparisons (P2 E1, P1E) unweighted or approximate; not design-based | Code | Labeled descriptive |
| I-14 | Low | Outcomes measured at different ages across studies (≈40, ≈26, ≥25 varying) | Plans | Noted in limitations |
| I-15 | Low | No cross-study multiplicity control for the narrative synthesis (5 primary contrasts and many sensitivity analyses) | — | Synthesis language now descriptive |
| I-16 | Info | No independent replication in R or Stata; BRR not cross-checked; no second analyst | — | Remaining limitation (§7) |

## 5. Corrections made

- **Code:** seeded imputation in three scripts; new audit, estimands and number-filling scripts; manuscript renderer supports reports.
- **Outputs:** official outputs replaced by seeded re-runs; originals and the unseeded re-run archived under `outputs/audit/`.
- **Manuscript:** new `manuscripts/working_paper_v3.md`, with numbers filled from outputs by script. v2 is kept unchanged as a record.
- **Website (not published):** hero, notice, updates, verdict text and accumulation panel rewritten; the preregistration wording removed.
- **Results documents:** each `docs/results_*.md` now opens with an audit note pointing to the corrected interpretation.
- **Bibliography:** junk titles fixed (`kuh2003`, `hernan2016`); `smith2016` volume/issue/pages added (45(4):1271–1279, Europe PMC);
  study-type labels corrected for `grossman2002`, `bayer2015`, `rhodes2005`, `lerner2005`, `chetty2022`, `cunha2010`; evidence levels
  updated for 11 works; `grossman2002` sample (1,138 randomized, 959 followed up) and illustration wording corrected; `herrera2007report`
  added; literature-review lines 8, 71, 80, 135, 163, 172, 188, 218 and 263 corrected.
- **New documents:** `docs/construct_validity.md`, `docs/reproducibility_checklist.md`, `docs/bibliography_audit.{md,csv}`,
  `outputs/primary_estimands.csv`.

## 6. Unresolved numerical inconsistencies

1. **Older outputs and documents.** Monte Carlo differences separate the v2 numbers (original outputs) from the v3 numbers (seeded
   re-runs). `docs/results_*.md` still show the original numbers; each now carries a note naming the authoritative files.
2. **B2 equivalence p.** It varies across imputation runs (.030–.045), near the .05 threshold; see §3.7.
3. **Reliability check vs primary for P2.** The complete-case versions (§3.6 B) use a different sample (n = 5,375) from the imputed primary
   (n = 6,190), so they are not directly comparable.

## 7. Remaining limitations and what independent replication needs

| Need | Why it can't be done here | What is required |
|---|---|---|
| Survey estimates in R `survey` or Stata `svy` | Not installed | Run P1 with `svydesign(ids=~VPSU, strata=~VSTRAT, weights=~w, nest=TRUE)`; B2 with `svrepdesign(type="BRR")` on W2W1STU001–200 |
| Second analyst | Single AI analyst | A human statistician re-implements from the plans and the reproducibility checklist |
| S6b custom-weight sensitivity | Needs NLS online tool | PI downloads weights for `data/processed/nlsy97_s6b_ids.txt`; run `scripts/run_paper1_s6b.py` |
| STROBE checklist | Not yet written | Complete before submission |
| Human-run studies (A3, R1, R2) | Data terms prohibit AI | Human analyst, outside AI tools |
| Closed-access articles | No legal copy | `docs/article_retrieval_protocol.md` |

## 8. Recommended manuscript conclusion

> In three U.S. cohorts, adult support reported at different ages was modestly associated with later education. Support measured earlier
> in childhood or adolescence was not more strongly associated with outcomes than support measured later, and point estimates mostly
> favored later measurement. These results do not establish that developmental timing is irrelevant. The prespecified contrasts were
> imprecise, the equivalence margins were as large as the associations compared, nonlinear age patterns could not be excluded, and the
> analyses observed the age at which support was reported, not when relationships began. They also do not show that support has
> cumulative causal effects: consistent support over four years was associated with more schooling, but cumulative exposure, stability,
> loss of support and stable family characteristics could not be distinguished. The findings argue against assuming a narrow early window
> for parental and teacher support, and for studies that measure when relationships begin, how long they last, and how good they are.

## 9. Proposed next study (not started; to begin only after this audit is accepted)

**Distinguishing duration, stability, quality and timing of supportive relationships.**

- **Question:** among young people with a nonparental mentor or a supportive parent, are relationship *duration*, *stability*
  (continuity vs disruption), *quality*, and *timing* (age at onset, age at measurement) separately associated with educational
  outcomes, once they are measured as distinct variables?
- **Data:**
  1. **Add Health Wave III mentor items** (onset age `H3MN6`, years important `H3MN8`, closeness `H3MN11`, type `H3MN2`). Human-run only.
     This is the only source with onset and duration for natural mentors.
  2. **NLSY97 parent-support items 1997–2003** (stability, gains and losses, with youth fixed effects for time-varying outcomes such as
     enrollment and expectations).
  3. **NLSY79 Children and Young Adults sibling comparisons.** Siblings are measured at different ages in the same survey years, so mother
     fixed effects separate timing from stable family warmth.
- **Design features:**
  - Measurement models that separate stable trait from occasion-specific support (trait–state models).
  - Prespecified contrasts with margins justified by program-relevant effect sizes and smaller than the associations themselves.
  - Target-trial framing for "gaining" or "losing" support.
  - Negative-control outcomes.
  - External registration (OSF) before any outcome is examined.
- **Gate:** begin only after (a) the PI accepts this audit, (b) the R/Stata cross-check of P1 and B2 is done, and (c) the plan is externally registered.
