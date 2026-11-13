"""Study P3 (frozen plan docs/sap_p3_cya_siblings.md): maternal praise at 6-9 vs 10-14 within families, NLSY79 Children and Young Adults.

Usage: python scripts/run_p3_siblings.py  ->  outputs/p3_results.json
Needs data/raw/nlsy79cya/{cya,n79}_extract.csv (Paper 2) and data/raw/nlsy79cya/p3_nc_extract.csv (negative control):
  python scripts/extract_nls.py <cya zip> nlscya_all_1979-2020.csv config/mappings/nlsy79cya_p3_spec.json nc data/raw/nlsy79cya/p3_nc_extract.csv
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
warnings.filterwarnings("ignore")
import run_p2_cya as p2  # noqa: E402
from turning_point.modeling import equivalence_test, fit_survey_glm  # noqa: E402

SESOI = 0.03
CHILD_COVS = ["female", "order2", "order3p", "by_1984", "by_1988", "by_1992", "mage", "pov_share", "log_inc"]
LABELS = ("beta_6_9", "beta_10_14", "delta_C_minus_D")


def verdict(est, se, df_t, eq):
    t = stats.t.ppf(0.975, df_t)
    lo, hi = est - t * se, est + t * se
    if eq["p_tost"] < 0.05:
        return "equivalent"
    if lo > SESOI or hi < -SESOI:
        return "non-equivalent"
    if lo > 0 or hi < 0:
        return "different, undetermined"
    return "inconclusive"


def contrasts(f, a, b, df_t):
    names = list(f.params.index)
    L = np.zeros((3, len(names)))
    L[0, names.index(a)] = 1; L[1, names.index(b)] = 1; L[2, names.index(a)] = 1; L[2, names.index(b)] = -1
    lc = f.linear_combination(L)
    t = stats.t.ppf(0.975, df_t)
    out = []
    for j, lab in enumerate(LABELS):
        e, se = float(lc["estimate"].iloc[j]), float(lc["se"].iloc[j])
        out.append({"quantity": lab, "estimate": e, "se": se, "df": df_t, "ci_low": e - t * se, "ci_high": e + t * se,
                    "p": float(2 * stats.t.sf(abs(e / se), df_t))})
    return out


def fe_fit(d, a, b, covs, outcome="ba"):
    """Within-family (mother fixed effects) linear model; SEs clustered by mother; df = families - 1."""
    d = d.dropna(subset=[outcome, a, b, *covs])
    k = d.groupby("mid")[outcome].transform("size")
    d = d[k >= 2]
    cols = [a, b, *covs]
    X = d[cols].astype(float) - d.groupby("mid")[cols].transform("mean")
    X = X.loc[:, X.std() > 1e-10]
    y = d[outcome].astype(float) - d.groupby("mid")[outcome].transform("mean")
    f = fit_survey_glm(X, y, psu=d["mid"])
    G = int(d["mid"].nunique())
    return f, d, G


def between_fit(d, a, b, covs):
    """B1: no fixed effect, Paper 2 covariates, SEs clustered by mother, same sample as the primary analysis."""
    covs = [c for c in covs if d[c].nunique() > 1]
    X = pd.concat([pd.Series(1.0, index=d.index, name="const"), d[[a, b]], d[covs]], axis=1).astype(float)
    f = fit_survey_glm(X, d["ba"].astype(float), psu=d["mid"])
    return f, int(d["mid"].nunique())


def summarize(rows, G, n, extra=None):
    d = rows[2]
    eq = equivalence_test(d["estimate"], d["se"], SESOI, df=d["df"])
    out = {"n_children": n, "n_families": G, "estimates": rows, "equivalence": eq,
           "verdict": verdict(d["estimate"], d["se"], d["df"], eq)}
    out.update(extra or {})
    return out


def main():
    d = p2.prepare()
    s = d[d.cyrb.between(1979, 1995)].copy()
    sp = s[(s.n_praiseC > 0) & (s.n_praiseD > 0)].copy()
    sp["zC"] = p2.zstd(sp["praiseC"]); sp["zD"] = p2.zstd(sp["praiseD"])  # Paper 2 scale (full praise analytic sample)
    R = {"plan": "docs/sap_p3_cya_siblings.md", "sesoi": SESOI}

    f, dd, G = fe_fit(sp, "zC", "zD", CHILD_COVS)
    prim = contrasts(f, "zC", "zD", G - 1)
    R["primary"] = summarize(prim, G, int(len(dd)))
    disc = dd.groupby("mid")["ba"].transform("nunique") > 1
    R["primary"]["identifying"] = {"families_discordant_BA": int(dd.loc[disc, "mid"].nunique()), "children_in_them": int(disc.sum())}
    within_sd = {k: float((dd[k] - dd.groupby("mid")[k].transform("mean")).std()) for k in ("zC", "zD")}

    # Deviation D-045 (fixed before any estimate was seen): Paper 2's family-level covariates (mother's education, AFQT) are
    # missing for some children, so B1 uses children complete on all covariates, and the fixed-effect model is re-fit on that
    # same sample so that the with/without fixed-effect comparison is like-for-like.
    db = dd.dropna(subset=p2.COVS)
    fb, Gb = between_fit(db, "zC", "zD", p2.COVS)
    R["B1_no_fixed_effect_same_sample"] = summarize(contrasts(fb, "zC", "zD", Gb - 1), Gb, int(len(db)))
    fbf, dbf, Gbf = fe_fit(db, "zC", "zD", CHILD_COVS)
    R["B1_fixed_effect_on_B1_sample"] = summarize(contrasts(fbf, "zC", "zD", Gbf - 1), Gbf, int(len(dbf)))

    sc = s[(s.n_closeC > 0) & (s.n_closeD > 0)].copy()
    sc["cC"] = p2.zstd(sc["closeC"]); sc["cD"] = p2.zstd(sc["closeD"])
    fc, dc, Gc = fe_fit(sc, "cC", "cD", CHILD_COVS)
    R["C1_closeness_fixed_effect"] = summarize(contrasts(fc, "cC", "cD", Gc - 1), Gc, int(len(dc)))

    nc = pd.read_csv(ROOT / "data/raw/nlsy79cya/p3_nc_extract.csv")
    lbw = nc.set_index("CPUBID")["LBW"]
    sp["lbw"] = sp["cid"].map(lbw.where(lbw.isin([0, 1])))
    fn, dn, Gn = fe_fit(sp, "zC", "zD", CHILD_COVS, outcome="lbw")
    rows = contrasts(fn, "zC", "zD", Gn - 1)
    R["NC_low_birth_weight"] = {"n_children": int(len(dn)), "n_families": Gn, "estimates": rows,
                                "joint_wald_betaC_betaD": fn.wald_test(["zC", "zD"]),
                                "lbw_rate_unweighted": float(dn["lbw"].mean())}

    fs, ds, Gs = fe_fit(sp, "zC", "zD", [c for c in CHILD_COVS if c not in ("pov_share", "log_inc")])
    R["S1_no_income_poverty"] = summarize(contrasts(fs, "zC", "zD", Gs - 1), Gs, int(len(ds)))

    R["S2_per_within_family_SD"] = {"within_sd": within_sd,
                                    "beta_6_9": prim[0]["estimate"] * within_sd["zC"], "beta_10_14": prim[1]["estimate"] * within_sd["zD"]}
    out = ROOT / "outputs" / "p3_results.json"
    out.write_text(json.dumps(R, indent=2, default=float))
    print(json.dumps({k: (v.get("verdict"), [round(100 * r["estimate"], 2) for r in v["estimates"]]) for k, v in R.items()
                      if isinstance(v, dict) and "estimates" in v}, indent=1))
    print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
