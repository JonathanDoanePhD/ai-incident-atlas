"""Export analysis-ready datasets for the independent R cross-check (crosscheck/crosscheck.R).

The cross-check re-estimates the confirmatory models in R with the `survey` and `mitools` packages, starting from the
*same* analysis-ready data used by the official Python runs:
  * Paper 1 (NLSY97): the m = 40 seeded imputations per parent (padded for domain estimation) and the complete-case file (S2).
  * B2 (HSLS:09): the m = 20 seeded imputations, the 200 BRR replicate weights, and the complete-case file (S2).

What it checks: model fitting, survey variance (Taylor linearization; BRR), contrasts and Rubin/Barnard-Rubin pooling,
implemented independently in R. What it does not check: data preparation and imputation (those are reproduced, not
re-implemented; a second analyst covers them).

Before writing, the script re-pools the regenerated imputations with the project code and asserts the result equals the
official outputs (outputs/paper1_results.json, outputs/b2_results.json), proving the exported data are the data behind
the reported numbers.

Usage: python scripts/export_crosscheck_data.py  ->  data/crosscheck/*.csv.gz (git-ignored) + crosscheck/python_reference.json
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
warnings.filterwarnings("ignore")
import run_b2_hsls as b2  # noqa: E402
import run_paper1 as p1  # noqa: E402

OUT = ROOT / "data" / "crosscheck"
TOL = 1e-9


def check(label, mine, official):
    for q_m, q_o in zip(mine, official):
        for k in ("estimate", "se"):
            if abs(q_m[k] - q_o[k]) > TOL * max(1.0, abs(q_o[k])):
                raise SystemExit(f"{label} {q_o.get('quantity')} {k}: regenerated {q_m[k]!r} != official {q_o[k]!r}")
    print(f"  {label}: regenerated estimates equal the official output")


def export_paper1(ref):
    off = json.loads((ROOT / "outputs" / "paper1_results.json").read_text())
    seed, m = off["seed"], off["m"]
    df, _ = p1.prepare()
    df_design = float(df.groupby("strata")["psu"].nunique().sum() - df["strata"].nunique())
    assert df_design == off["design_df"]
    ref["paper1"] = {"design_df": df_design, "m": m, "seed": seed}
    for i, who in enumerate(("mother", "father")):
        print(f"Paper 1, {who}: regenerating {m} imputations", flush=True)
        sample = df[(df[f"{who}_universe"] == 1) & df[f"{who}_vs"].notna()].copy()
        imps = [p1.pad(imp, df) for imp in p1.impute(sample, who, m, seed + i)]
        prim = p1.pooled_contrasts(imps, lambda d: p1.linear_fit(d, who), df_design).to_dict("records")
        check(f"paper1 {who} primary", prim, off["analyses"][who]["primary"])
        covs = [c for c in p1.COVARIATES if c in imps[0].columns]
        keep = ["hgc", f"{who}_vs", "agec", *covs, "w", "strata", "psu"]
        long = pd.concat([imp[keep].assign(imp=k + 1, dom=(imp["w"] > 0).astype(int)) for k, imp in enumerate(imps)])
        long = long.rename(columns={f"{who}_vs": "s"})
        long.to_csv(OUT / f"p1_{who}_imputed.csv.gz", index=False)
        cc = sample.dropna(subset=["hgc", *[c for c in p1.COVARIATES if c in sample.columns]])
        ccp = p1.pad(cc, df)
        s2 = p1.single_contrasts(p1.linear_fit(ccp, who)).to_dict("records")
        check(f"paper1 {who} S2", s2, off["analyses"][who]["sensitivity"]["S2_complete_case"]["est"])
        ccp[[c for c in keep if c in ccp.columns]].assign(dom=(ccp["w"] > 0).astype(int)).rename(
            columns={f"{who}_vs": "s"}).to_csv(OUT / f"p1_{who}_cc.csv.gz", index=False)
        ref["paper1"][who] = {"primary": prim, "S2": s2, "covariates": covs}


def export_b2(ref):
    off = json.loads((ROOT / "outputs" / "b2_results.json").read_text())
    m = off["m"]
    seed = 20261112  # run_b2_hsls.py default, used for the official run
    df = b2.prepare()
    s = df[(df.w > 0)]
    s = s[s["sup9"].notna() & s["sup11"].notna()].copy()
    print(f"B2: regenerating {m} imputations", flush=True)
    imps = b2.impute(s, m, seed)
    prim = b2.pool([b2.brr(i) for i in imps])
    check("b2 primary", prim, off["primary"])
    cc = s.dropna(subset=["ba", *b2.COVS])
    s2 = b2.pool([b2.brr(cc)])
    check("b2 S2", s2, off["S2_complete_case"]["est"])
    ids = pd.Series(np.arange(len(s)), index=s.index, name="id")
    s[["w", *b2.REPS]].assign(id=ids).to_csv(OUT / "b2_weights.csv.gz", index=False)
    cols = ["ba", "sup9", "sup11", *b2.COVS]
    pd.concat([imp[cols].assign(id=ids.values, imp=k + 1) for k, imp in enumerate(imps)]).to_csv(
        OUT / "b2_imputed.csv.gz", index=False)
    cc[cols].assign(id=ids.loc[cc.index].values).to_csv(OUT / "b2_cc.csv.gz", index=False)
    ref["b2"] = {"m": m, "seed": seed, "df_complete": b2.DF_COM, "n_replicates": len(b2.REPS),
                 "primary": prim, "S2": s2, "covariates": b2.COVS}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ref = {"note": "Official Python estimates the R cross-check is compared against (regenerated and verified)."}
    export_paper1(ref)
    export_b2(ref)
    path = ROOT / "crosscheck" / "python_reference.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(ref, indent=2, default=float))
    print("wrote", path.relative_to(ROOT), "and", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
