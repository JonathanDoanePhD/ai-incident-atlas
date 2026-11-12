# The Turning Point Project

**When, how, and for whom do supportive relationships and developmental experiences shape young
people's future trajectories?**

A preregistration-first research programme on the developmental timing of supportive adult
relationships and educational attainment. Principal investigator: Jonathan Doane, Ph.D.
([research portfolio](https://jonathandoanephd.github.io/research-portfolio/)).

> **Status (2026-11-12): first results for paper 1** (`docs/results_paper1.md`). Parental support
> reported at ages 12–16 is associated with about half a year more schooling, with no clear difference by
> age at report. These are observational associations. Survey microdata stay outside git; synthetic data
> appear only in `tests/`.

## What is here

| Area | Contents |
|---|---|
| Literature | `docs/literature_review.md` (abstract-level critical review), `docs/evidence_matrix.csv` (87 works), `docs/references.bib`, `docs/citation_verification_log.jsonl` (Crossref record for every DOI), `docs/references_unverified.md` |
| Data feasibility | `docs/dataset_audit.md` (NLSY97, Add Health, HSLS:09, ELS:2002), `docs/dataset_audit_early_childhood.md` (PSID-CDS/TAS, NLSY79 CYA, FFCWS, ECLS-K, ECLS-K:2011, SECCYD, UK cohorts), comparison CSVs, `docs/variable_dictionary*.{md,csv}` (150 documented variables), `config/datasets.yaml` |
| Design | `docs/research_questions.md`, `docs/conceptual_framework.md`, `docs/causal_framework.md` + `causal_dag.dot`, `docs/statistical_analysis_plan.md`, `docs/preregistration_draft.md`, `docs/ethics_and_limitations.md`, `docs/research_decision_log.md` |
| Code | `src/turning_point/`: ingestion with provenance manifests, validation (ranges, identifiers, microdata-in-git guard), missing-code recoding that keeps reasons, scale scoring/reliability, survey-weighted GLMs (Taylor linearisation and replicate weights), restricted cubic splines, age-moderation models, equivalence tests, Rubin pooling, Holm/BH, E-values, life-course structured-approach model comparison, guarded change-point estimation, grouped CV and subgroup calibration, provenance-stamped Plotly figures, CLI |
| Tests | `tests/`: 38 tests incl. agreement with statsmodels' cluster-robust variance, a Monte Carlo bias/coverage check of the primary estimator, life-course model recovery, and site/citation integrity |
| Website | `website/`: dependency-free static site (GitHub Pages compatible), generated data in `website/data/site.js` |
| Planning | `scripts/power_age_interaction.py` → `outputs/design_power_age_interaction.csv` (assumed inputs, not data) |

## Key decisions so far (details in `docs/research_decision_log.md`)

- **Paper 1** (signed off by the PI 2026-11-12): NLSY97 — does the association between a youth's report of a very
  supportive parent at ages 12–16 (1997) and highest grade completed (~age 40) differ by age at report?
  Difference *and* equivalence (SESOI 0.20 SD) are tested; "inconclusive" is a pre-allowed outcome.
- **Add Health is excluded**: its Conditions of Use forbid processing its data with AI tools (verified 2026-11-12).
- **Companion study**: HSLS:09 school-adult support in grade 9 vs grade 11 (the "freshman year" question, grade-anchored).
- **Paper 2 candidate**: PSID-CDS/TAS identical "how close" items at ages ~8–11 and ~12–15.

## Setup and reproduction

```bash
cd turning-point-project
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev,stata]"
```

```bash
pytest                                   # 38 tests, synthetic data only
```

```bash
python scripts/power_age_interaction.py --simulate
```

```bash
python scripts/build_site_data.py        # regenerate website/data/site.js from docs/
python -m http.server 8000               # then open http://localhost:8000/website/
```

```bash
tpp paths                                # resolved data/output folders
tpp check-repo                           # fails if any microdata are tracked by git
tpp validate nlsy97 data/raw/nlsy97/extract.csv   # after filling config/mappings/nlsy97.yaml
```

Data paths come from `TPP_DATA_DIR`, then `config/local.yaml` (copy `config/paths.example.yaml`),
then `data/`. Microdata never enter git (`.gitignore`, `tpp check-repo`, and a unit test).

## Reproduce paper 1

```bash
# download https://nlsinfo.org/cohort-data/nlsy97_all_1997-2023.zip, then stream the 24 mapped
# columns into data/raw/nlsy97/paper1_extract.csv (see docs/results_paper1.md, Verification)
python scripts/run_paper1.py --m 40          # ~10 min; writes outputs/paper1_results.json
python scripts/report_paper1.py              # figures + website/data/findings.js
python scripts/crosscheck_variance.py        # jackknife check of standard errors
```

## Open items

1. Paper 2: ages 8–11 vs 12–15 with PSID child-supplement "how close" items (needs a free PSID registration by the PI).
2. Grade-9 companion study with HSLS:09.
3. Read full texts of key mentoring meta-analyses; write the working paper.

## Licence and citation

Code: MIT (`LICENSE`). Cite via `CITATION.cff`. Survey data are © their stewards and are not redistributed.
