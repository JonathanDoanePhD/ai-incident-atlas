# Results: study P3 — praise at ages 6–9 vs 10–14 within families (NLSY79 Children and Young Adults siblings)

Run 2026-11-13 under the frozen plan (`docs/sap_p3_cya_siblings.md`; `PLAN_FREEZE_P3.md`, hashes verified before running).
- **Deviation:** one bug fix to secondary analysis B1, made before any estimate was seen (D-045).
- **Outputs:** `outputs/p3_results.json`.
- **Interpretation status:** observational associations, not causal effects; the PI reviews before anything is written up.

## Summary

- **Within families:** praise at 6–9 and at 10–14 had about the same association with a sibling's bachelor's attainment.
  - The difference was **−0.2 percentage points per SD** (95% CI −2.9 to +2.4).
  - It was **equivalent within the prespecified ±3-point margin** (90% CI −2.4 to +2.0; TOST p = .019).
- **Between families, same children:** the same comparison favored the later window, at −2.7 points (−5.3 to −0.0; p = .047).
  - The fixed effect re-fit on exactly those children gave −0.6 (−3.4 to +2.1).
  - So the **between-family lean toward later praise reflects stable family characteristics, not the age at which praise was
    reported.**
- **Size of the association:** within families, praise was weakly associated with attainment in either window, at +1.2 and +1.4
  points per SD; neither is significant. Most of the praise–attainment association in Paper 2 lies between families.
- **Negative control:** praise did not "predict" low birth weight within families (joint p = .68). This gives no sign that praise
  tracks child traits present from birth, though it cannot rule out traits that emerge later.

## Sample

| Step | n |
|---|---|
| Praise analytic sample (Paper 2) | 6,190 children of 3,138 mothers |
| Outcome observed, child covariates complete, in families with 2+ such children (analyzed) | **4,513 children in 1,819 families** |
| Families whose siblings differ in BA (mainly identify the estimate) | 483 families, 1,248 children |

The plan's structure-only count was 484 families and 1,250 children. Requiring complete child covariates removes one family.

## Estimates (percentage points of BA attainment per SD of praise; 95% CI)

| Analysis | n children (families) | Ages 6–9 | Ages 10–14 | Difference (6–9 − 10–14) | Verdict (±3) |
|---|---|---|---|---|---|
| **Primary: mother fixed effects** | 4,513 (1,819) | +1.2 (−0.8, +3.1) | +1.4 (−0.5, +3.3) | **−0.2 (−2.9, +2.4)** | **equivalent** (90% CI −2.4, +2.0) |
| B1: no fixed effect (Paper 2 covariates) | 4,299 (1,732) | −0.5 (−2.1, +1.1) | +2.2 (+0.7, +3.7) | −2.7 (−5.3, −0.0) | different, undetermined |
| B1 sample, fixed effects | 4,299 (1,732) | +0.9 (−1.0, +2.9) | +1.6 (−0.4, +3.5) | −0.6 (−3.4, +2.1) | equivalent (90% CI −2.9, +1.7) |
| C1: closeness ("extremely close"), fixed effects | 2,344 (1,018) | +0.8 (−1.4, +2.9) | +2.7 (+0.5, +4.8) | −1.9 (−5.2, +1.5) | inconclusive |
| S1: without income and poverty covariates | 4,533 (1,828) | +1.2 (−0.7, +3.2) | +1.3 (−0.6, +3.2) | −0.1 (−2.7, +2.6) | equivalent |
| NC: low birth weight as outcome | 4,482 (1,819) | +0.6 (−1.0, +2.3) | +0.4 (−1.0, +1.7) | +0.3 (−1.8, +2.4) | joint test p = .68 |

**S2.** The within-family SD of each window score is about 0.5 of the total SD. A typical within-family difference in praise therefore
corresponds to about +0.6 points (6–9) and +0.7 points (10–14).

## Interpretation

1. **Timing.** This is the project's first design that removes stable family characteristics. In it, praise at 6–9 and at 10–14
   carry the same weight within the ±3-point margin. The margin is about twice the within-family associations themselves (+1.2 to
   +1.4), so equivalence rules out large timing differences relative to the margin, not small ones.
2. **Why the between-family pattern looked different.** Families who praise more in early adolescence differ in other stable ways that
   predict college. Comparing siblings removes those differences, and the later-window advantage disappears.
3. **Closeness.** Within families, closeness at 10–14 was associated with attainment (+2.7 points per SD) while closeness at 6–9 was
   not. The difference is not significant and is inconclusive. Closeness was reported in fewer families, and its windows are measured
   with fewer reports.
4. **Limits.**
   - The design removes only what is constant within a family. Siblings differ in birth order, birth year and the family
     circumstances they experienced at each age; these are partly adjusted.
   - Child-specific traits that develop after birth and elicit praise remain possible confounders.
   - Families with two or more children are not representative of all families.
   - Estimates are unweighted, and the outcome is complete-case: children whose outcome was not observed at 25 or later are
     excluded (8% of the Paper 2 sample).
5. **Not blind.** Paper 2's between-family results were known when this plan was written. The within-family estimates were not.

## Verification

- Before running, the frozen-file hashes were checked with `sha256sum -c`.
- The estimator was tested on synthetic sibling data: it recovers known within-family effects despite family-level confounding
  (`tests/test_p3_fixed_effects.py`).
- The negative-control extract matches the codebook's frequencies exactly (956 yes, 9,425 no).
