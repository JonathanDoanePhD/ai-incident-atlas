# Analysis plan freeze: study P3 (NLSY79 Children and Young Adults siblings)

Frozen 2026-11-13. The PI approved the scope and the ±3-point margin (D-044).

- **Data state:** at freezing, no within-family outcome model has been estimated, and the negative-control variable (low birth weight,
  C0328700) has not been extracted.
- **Seen before freezing:** only structure counts (children and families) and exposure/covariate structure for the power calculation.
- **Not blind:** Paper 2's between-family results on the same data are known (see the plan).
- **Imported code:** the script imports Paper 2's data preparation (`run_p2_cya.py`) and the project's survey estimator
  (`modeling.py`); both are hashed below.

```
fa1f0780a334e10327c7daa026cbd25f5f99c1a7ebe478cd0b5e80509338950b  docs/sap_p3_cya_siblings.md
790d3e61fd3c0d680dba3be76032a8e9206b7213ec26a12c0ce896d0914cc13b  scripts/run_p3_siblings.py
3d5f18a5c5a08e2a89f5f7645798fda3504b2ac63046e713c7cb578d702e2091  scripts/run_p2_cya.py
bfb58f4cd527802751691b82ad2897084e3ccb56590f2c92aed1e9d568216fcf  src/turning_point/modeling.py
ce43b1aac730f5d9a2cb124feda533fdb50d668dfecaa1f46611b4729cc82e57  config/mappings/nlsy79cya_p3_spec.json
5ebc9ae8268dfdf27446f0b82a8db331c2b60f917c64ec6b69d1178f5f7eb017  scripts/extract_nls.py
```
