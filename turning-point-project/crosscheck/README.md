# Independent R cross-check

This folder checks that the main survey estimates are reproduced by a second implementation in different software: R with the
`survey` and `mitools` packages, instead of the project's Python code.

## What is covered

| Study | Quantities | Analyses |
|---|---|---|
| Paper 1 (NLSY97) | θ(12)…θ(16) and Δ(16 − 12), mothers and fathers | primary (40 imputations); S2 complete cases |
| B2 (HSLS:09) | θ9, θ11 and their difference | primary (20 imputations); S2 complete cases |

**Independent:**
- model fitting
- survey variance:
  - Paper 1: Taylor linearization with strata and PSUs, and domain estimation via `subset()`
  - B2: BRR with 200 replicates via `svrepdesign`/`withReplicates`
- contrasts (`svycontrast`)
- multiple-imputation pooling (`MIcombine`, with the published Barnard–Rubin df)

**Not independent:**
- data preparation and the imputations, which are exported from the official seeded Python runs; a second analyst covers those
- Studies P2 (NLSY79 Children and Young Adults) and P1E (accumulation), which are not included

## Result (2026-11-13)

All 30 quantities agree: the largest differences are 2e-14 for estimates, standard errors and CI limits, and 3e-12 for df.

- **R version:** R 4.3.3 with survey 4.2-1 and mitools 2.4.
- **Output:** `outputs/crosscheck_r/crosscheck_summary.txt` and `outputs/crosscheck_r/crosscheck_results.csv`.
- **One finding:** `mitools::MIcombine` computes a slightly different small-sample df than Barnard & Rubin (1999).
  - mitools uses Ū/(Ū + B) where the published formula has 1 − γ = Ū/(Ū + (1 + 1/m)B).
  - The difference is up to 0.86 df and does not affect estimates or SEs. The script uses the published formula, as the Python
    code does, and reports the gap.

The run above was set up and executed by the same AI-assisted workflow that wrote the Python code. Re-running it on your own
computer adds independence of environment, but not of analyst.

## How to re-run it on your own computer

1. **Install R** (https://cran.r-project.org). Then, in R, run `install.packages(c("survey", "mitools", "jsonlite"))`.
2. **Get the data files.** Put the seven `.csv.gz` files from `data/crosscheck/` (about 22 MB) in the same place in your copy of
   the project.
   - These are public-use NLSY97 and HSLS:09 derived files and are git-ignored.
   - Ask Claude for the bundle, or regenerate them with `python scripts/export_crosscheck_data.py`. That needs the raw extracts and
     takes about 11 minutes; it also verifies they reproduce the official outputs.
3. **Run the check.** From the `turning-point-project` folder, run `Rscript crosscheck/crosscheck.R`. It takes about 2–3 minutes.
4. **Read the result.** The last line should say `RESULT: all quantities agree within tolerance.`
