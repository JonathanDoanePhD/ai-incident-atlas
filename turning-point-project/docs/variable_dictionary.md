# Variable dictionary

Status: v0.1 (2026-11-12). This file is an index. The authoritative, row-level dictionaries (one row per
variable, with verbatim wording, response scale, wave, universe, missing-value convention, source URL and
verification status) are:

- `variable_dictionary_adolescent.csv` — NLSY97, Add Health (documentation only; see policy note), HSLS:09, ELS:2002 (93 rows)
- `variable_dictionary_early_childhood.csv` — PSID-CDS/TAS, NLSY79 CYA, FFCWS, ECLS-K, ECLS-K:2011, SECCYD and others (57 rows)

Rules: a variable identifier enters these files only if it was read in fetched documentation; anything
recalled rather than read sits in the `recalled_unverified` column. Variables used in paper 1 are mapped
in `config/mappings/nlsy97.yaml`, where `source` stays `TODO` until the Investigator reference number is
filled in, and the loader refuses unverified mappings.

**Add Health:** identifiers are recorded from codebooks (permitted metadata use), but Add Health data may not
be processed with AI tools under its Conditions of Use (verified 2026-11-12).

## Coverage: number of audited variables by construct group and dataset

| Construct group | Add Health | ECLS-K (1998-99) | ECLS-K:2011 | ELS:2002 | FFCWS | HSLS:09 | NLSY79 CYA | NLSY97 | PSID-CDS/TAS | SECCYD |
|---|---|---|---|---|---|---|---|---|---|---|
| Academic engagement | 2 |  |  |  |  | 2 |  | 1 |  |  |
| Adult support | 11 | 1 | 6 | 6 | 11 | 9 | 11 | 10 | 9 | 3 |
| Age |  |  |  |  |  |  |  | 1 |  |  |
| Design / weights | 1 |  |  | 1 |  | 1 | 1 | 2 |  |  |
| Educational aspirations/expectations | 2 |  |  | 1 |  | 3 |  | 2 |  |  |
| Educational attainment | 3 |  |  | 2 | 3 | 3 | 2 | 3 | 3 | 1 |
| Employment & earnings | 1 |  |  | 2 |  | 2 |  | 2 |  |  |
| Family circumstances | 1 |  |  | 3 |  | 4 |  | 3 |  |  |
| Other |  | 1 |  | 2 | 3 | 1 | 1 |  | 1 |  |
| Self-efficacy / control | 1 |  |  | 2 |  | 1 |  | 2 |  |  |

Construct grouping is a keyword heuristic for this overview only; see the CSVs for exact constructs.

## Variables for paper 1

See `statistical_analysis_plan.md` §4.
