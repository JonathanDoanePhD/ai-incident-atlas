# Reproducibility checklist

Status: 2026-11-13 (independent review response). "Verified" means checked in this environment on this date. Items that
cannot be verified here are marked as such, with what is needed.

## A. Environment

| Item | Status |
|---|---|
| Python 3.13; numpy 2.5, pandas 3.0, scipy 1.18, statsmodels 0.15, scikit-learn 1.9 | Recorded; **no lock file** (pin versions in `requirements-lock.txt` before release) |
| R / Stata cross-check of survey estimates | **Not available here.** Needed: R `survey` (svydesign with strata/PSU; svrepdesign for BRR) or Stata `svy` |
| Random seeds | Fixed (`--seed 20261112`). **Audit fix:** the seed is now passed to statsmodels `MICEData(rng=seed)`. Before the fix it was ignored, and MI results were not reproducible. Two seeded runs are now byte-identical |

## B. Data provenance

| Study | Source file | Access | Integrity check |
|---|---|---|---|
| P1, P1E | `nlsy97_all_1997-2023.zip` (nlsinfo.org), extracts `data/raw/nlsy97/*.csv` | Public; NLS terms permit AI processing (PI, D-023) | Extract counts match codebook (exposure items, age, last round, sex); SHA-256 manifest in `data/processed/` |
| B2 | `HSLS_2009-16_PETS_Pear_v1_0_CSV_Datasets.zip` (NCES DataLab) | Public | Counts match codebook for checked items; BRR structure checked |
| P2 | `nlscya_all_1979-2020.zip`, `nlsy79_all_1979-2022.zip` (nlsinfo.org) | Public | Counts match codebook (degree, praise, closeness, race, sex, birth order); all children link to mothers |
| A3, R1, R2 | Add Health, PSID, FFCWS | AI processing prohibited or requires permission | Human-run only (not executed) |

Microdata are git-ignored (`tpp check-repo`, unit test). Download dates: 2026-11-12.

## C. Plans and freezes

| Study | Plan | Frozen (commit, UTC) | Data first opened (file mtime, UTC) | Hashes still match | External registry |
|---|---|---|---|---|---|
| P1 | `statistical_analysis_plan.md`, `preregistration_draft.md` | a54c783, 2026-11-12 20:39 | 20:41 | Yes | **None** (OSF registration not done) |
| B2 | `sap_hsls09_grade9.md` | f67dff6, 21:18 | 21:21 | Yes | None |
| P2 | `sap_nlsy79cya_childhood.md` | cc928cb, 21:46 | 21:47 | Yes | None |
| P1E | `sap_nlsy97_accumulation.md` | f9e0833, 21:50 | 21:51 (1998–2000 items) | Yes | None. Written **after** paper 1 results were known |

Caveat: freezes are commits in a repository controlled by the investigator, pushed to GitHub. They show the plan text existed
before the data files were created, but are weaker evidence than a time-stamped external registration. B2, P2 and P1E were all
planned **after** paper 1's results were known.

## D. Re-running the analyses

```bash
python scripts/run_paper1.py --m 40          # ~10 min
python scripts/run_b2_hsls.py --m 20
python scripts/run_p2_cya.py --m 20
python scripts/run_p1e_accumulation.py
python scripts/crosscheck_variance.py        # JK2 vs Taylor SEs (paper 1)
python scripts/audit_checks.py               # post-hoc audit checks (outputs/audit/)
python scripts/build_estimands_table.py      # outputs/primary_estimands.csv
pytest -q                                    # software tests (synthetic data)
```

Re-run results versus stored outputs: see `independent_review_response.md` §3.4. Current `outputs/*.json` are the seeded re-runs; v2 originals are in `outputs/audit/original_2026-11-12/`.

## E. Independent verification status

| Check | Status |
|---|---|
| Taylor-linearized SEs (P1) vs independent paired-PSU jackknife | Done earlier: agreement to 3 decimals (one imputation) |
| Equivalence statistics recomputed with independent code | Done (this audit) |
| Survey estimates in R `survey` / Stata | **Not done**: software unavailable |
| BRR variance (B2) vs another implementation | **Not done**. Needs R `survey::svrepdesign(type = "BRR")` |
| Independent re-analysis by a second analyst | **Done**: the second analyst confirmed the results (reported by the PI, 2026-11-13; D-041). R reproduction of the survey estimates: `crosscheck/` (D-039) |
| Code review of `src/turning_point/modeling.py` by a statistician | **Not done** |
