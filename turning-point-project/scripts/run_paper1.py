"""Paper 1: parental support x age (12-16) -> highest grade completed, NLSY97.

Implements docs/statistical_analysis_plan.md (frozen; see docs/PLAN_FREEZE.md). Reads the
git-ignored extract data/raw/nlsy97/paper1_extract.csv (built from the public release with the
verified mapping in config/mappings/nlsy97.yaml) and writes only aggregate results to outputs/.

Usage: python scripts/run_paper1.py [--m 40] [--seed 20261112]
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from turning_point.ingestion import DatasetSpec, load_extract, load_mapping  # noqa: E402
from turning_point.modeling import (SurveyDesign, adjust_pvalues, e_value, equivalence_test,  # noqa: E402
                                    fit_age_moderation, fit_survey_glm, rr_from_smd, rubin_pool)
from turning_point.preprocessing import recode_missing  # noqa: E402

warnings.filterwarnings("ignore", category=FutureWarning)
SESOI_SD = 0.20
AGES = [12, 13, 14, 15, 16]
MIN_CELL = 10


# ----------------------------------------------------------------------------- data
def prepare() -> tuple[pd.DataFrame, dict]:
    mapping = load_mapping("nlsy97")
    raw, manifest = load_extract(ROOT / "data/raw/nlsy97/paper1_extract.csv", mapping, dataset="nlsy97",
                                 manifest_dir=ROOT / "data/processed")
    spec = DatasetSpec.from_registry("nlsy97")
    d, reasons = recode_missing(raw, spec.missing_codes)
    out = pd.DataFrame(index=d.index)
    out["age"] = d["age_1996"]
    out["agec"] = d["age_1996"] - 14
    out["female"] = (d["sex"] == 2).astype(float)
    for k, lab in {1: "black", 2: "hispanic", 3: "mixed"}.items():
        out[f"re_{lab}"] = (d["race_eth"] == k).astype(float)
    pov = d["poverty_ratio"] / 100.0
    out["pov_log"] = np.log1p(pov)
    out["urban"] = d["urban_rural"].where(d["urban_rural"].isin([0, 1]))
    hh = d["household_structure"]
    for k in range(2, 11):
        out[f"hh_{k}"] = (hh == k).astype(float).where(hh.notna())
    med = d["mom_hgc_res"].where(d["mom_hgc_res"] != 95)
    ded = d["dad_hgc_res"].where(d["dad_hgc_res"] != 95)
    out["parent_ed"] = pd.concat([med, ded], axis=1).max(axis=1)
    # "missing-indicator for absent parent": both residential-parent items valid-skipped
    out["no_res_parent_ed"] = ((raw["mom_hgc_res"] == -4) & (raw["dad_hgc_res"] == -4)).astype(float)
    out["hgc97"] = d["hgc_1997"].where(d["hgc_1997"] != 95)
    out["enrolled97"] = (d["enroll_1997"] == 8).astype(float).where(d["enroll_1997"].notna())
    out["asvab"] = d["asvab_pct"] / 1000.0
    observed = d["last_round"] >= 14
    hgc = d["highest_grade_ever"].where(d["highest_grade_ever"] != 95)
    out["hgc"] = hgc.where(observed)
    out["ba_plus"] = (d["highest_degree_ever"] >= 4).astype(float).where(observed & d["highest_degree_ever"].notna())
    for who in ("mother", "father"):
        s = d[f"{who}_support"]
        out[f"{who}_vs"] = (s == 1).astype(float).where(s.isin([1, 2, 3]))
        out[f"{who}_ord"] = (4 - s).where(s.isin([1, 2, 3]))  # 3 very, 2 somewhat, 1 not very
        out[f"{who}_scale"] = d[f"{who}_support_scale"] / 100.0
        out[f"{who}_universe"] = (raw[f"{who}_support"] != -4).astype(float)  # -4 = valid skip (outside universe)
    out["w"] = d["weight"] / 100.0
    out["strata"] = d["strata"]
    out["psu"] = d["strata"].astype(int).astype(str) + "-" + d["psu"].astype(int).astype(str)
    out["last_round"] = d["last_round"]
    return out, manifest


COVARIATES = ["female", "re_black", "re_hispanic", "re_mixed", "pov_log", "urban", "parent_ed", "no_res_parent_ed"] + \
    [f"hh_{k}" for k in range(2, 11)]
AUX = ["hgc97", "enrolled97", "asvab"]


def flow(df: pd.DataFrame, who: str) -> dict:
    u = df[df[f"{who}_universe"] == 1]
    s = u[u[f"{who}_vs"].notna()]
    return {"round1_respondents": int(len(df)), "in_item_universe": int(len(u)), "valid_exposure": int(len(s)),
            "outcome_observed_round14plus": int(s["hgc"].notna().sum()),
            "outcome_imputed": int(s["hgc"].isna().sum())}


# ----------------------------------------------------------------------------- imputation
def impute(sample: pd.DataFrame, who: str, m: int, seed: int) -> list[pd.DataFrame]:
    from statsmodels.imputation.mice import MICEData
    cols = ["hgc", "ba_plus", f"{who}_vs", "agec", *COVARIATES, *AUX]
    data = sample[cols].copy()
    data["sxa"] = data[f"{who}_vs"] * data["agec"]
    data["logw"] = np.log(sample["w"])
    # drop all-zero dummy columns (empty categories in this subsample) from the imputation model
    data = data.loc[:, (data.fillna(0) != 0).any() | data.isna().any()]
    data.columns = [c.replace("-", "_") for c in data.columns]
    np.random.seed(seed)
    md = MICEData(data, k_pmm=5, rng=seed)  # seed the imputation RNG explicitly (np.random.seed is ignored by statsmodels >= 0.14 MICEData)
    md.update_all(10)
    imps = []
    for _ in range(m):
        md.update_all(5)
        imp = md.data.copy()
        imp.index = sample.index
        for c in ("w", "strata", "psu", f"{who}_ord", f"{who}_scale"):
            imp[c] = sample[c].values
        imps.append(imp)
    return imps


# ----------------------------------------------------------------------------- models
def design(df):
    return dict(weights=df["w"], strata=df["strata"], psu=df["psu"])


def linear_fit(df, who, extra=(), exposure=None, weighted=True, wcol="w"):
    exp = exposure or f"{who}_vs"
    live = df[wcol] > 0 if weighted else pd.Series(True, index=df.index)
    covs = [c for c in [*COVARIATES, *extra] if c in df.columns and df.loc[live, c].nunique() > 1]
    X = pd.DataFrame({"const": 1.0, "s": df[exp], "agec": df["agec"], "s_x_age": df[exp] * df["agec"]}, index=df.index)
    X = pd.concat([X, df[covs].astype(float)], axis=1)
    if weighted:
        return fit_survey_glm(X, df["hgc"], weights=df[wcol], strata=df["strata"], psu=df["psu"])
    return fit_survey_glm(X, df["hgc"])


def contrasts(fit):
    """theta(a) for a in 12..16 and Delta = theta(16) - theta(12) = 4*beta3."""
    names = list(fit.params.index)
    rows = []
    for a in AGES:
        L = np.zeros(len(names)); L[names.index("s")] = 1; L[names.index("s_x_age")] = a - 14
        rows.append(L)
    L = np.zeros(len(names)); L[names.index("s_x_age")] = 4
    rows.append(L)
    lc = fit.linear_combination(np.vstack(rows))
    return lc["estimate"].to_numpy(), (lc["se"] ** 2).to_numpy()


def pooled_contrasts(imps, fitter, df_design):
    ests, vars_ = [], []
    for imp in imps:
        e, v = contrasts(fitter(imp))
        ests.append(e); vars_.append(v)
    ests, vars_ = np.array(ests), np.array(vars_)
    out = []
    labels = [f"theta_{a}" for a in AGES] + ["delta_16_vs_12"]
    for j, lab in enumerate(labels):
        r = rubin_pool(ests[:, j], vars_[:, j], n_obs=df_design, k_params=0)
        t = stats.t.ppf(0.975, r["df"])
        p = 2 * stats.t.sf(abs(r["estimate"] / r["se"]), r["df"])
        out.append({"quantity": lab, "estimate": r["estimate"], "se": r["se"], "df": r["df"],
                    "ci_low": r["estimate"] - t * r["se"], "ci_high": r["estimate"] + t * r["se"], "p": p, "fmi": r["fmi"]})
    return pd.DataFrame(out)


def single_contrasts(fit):
    e, v = contrasts(fit)
    se = np.sqrt(v); t = stats.t.ppf(0.975, fit.df_resid)
    labels = [f"theta_{a}" for a in AGES] + ["delta_16_vs_12"]
    return pd.DataFrame({"quantity": labels, "estimate": e, "se": se, "df": fit.df_resid, "ci_low": e - t * se,
                         "ci_high": e + t * se, "p": 2 * stats.t.sf(np.abs(e / se), fit.df_resid)})


def pad(frame: pd.DataFrame, full: pd.DataFrame) -> pd.DataFrame:
    """Append respondents outside the analysed subpopulation with zero weight (domain estimation),
    so strata/PSU totals reflect the full round-1 design."""
    rest = full.loc[~full.index.isin(frame.index), ["strata", "psu"]].copy()
    for c in frame.columns:
        if c not in ("strata", "psu"):
            rest[c] = 0.0
    rest["w"] = 0.0
    if "w_ipw" in frame.columns:
        rest["w_ipw"] = 0.0
    return pd.concat([frame, rest[frame.columns]])


def domain(imp, mask, fill_cols=()):
    """Domain (subpopulation) estimation: keep every row so the design is intact, zero the weight outside."""
    d = imp.copy()
    d["w"] = d["w"].where(mask, 0.0)
    for c in fill_cols:
        d[c] = d[c].fillna(0.0)
    return d


def weighted_sd(x, w):
    m = x.notna() & w.notna()
    mu = np.average(x[m], weights=w[m])
    return float(np.sqrt(np.average((x[m] - mu) ** 2, weights=w[m])))


def categorical_age(imps, who, df_design):
    """S1: separate theta for each age (age bands at every integer)."""
    rows = {a: ([], []) for a in AGES}
    for imp in imps:
        covs = [c for c in COVARIATES if c in imp.columns and imp.loc[imp["w"] > 0, c].nunique() > 1]
        res = fit_age_moderation(imp.assign(age=imp["agec"] + 14), outcome="hgc", exposure=f"{who}_vs", age="age",
                                 covariates=covs, design=SurveyDesign(weight="w", strata="strata", psu="psu"),
                                 age_bands=[13, 14, 15, 16], age_grid=AGES)
        for _, r in res.effect_by_age.iterrows():
            rows[int(r["age"])][0].append(r["estimate"]); rows[int(r["age"])][1].append(r["se"] ** 2)
    out = []
    for a, (e, v) in rows.items():
        r = rubin_pool(e, v, n_obs=df_design, k_params=0); t = stats.t.ppf(0.975, r["df"])
        out.append({"quantity": f"theta_{a}", "estimate": r["estimate"], "se": r["se"],
                    "ci_low": r["estimate"] - t * r["se"], "ci_high": r["estimate"] + t * r["se"]})
    return pd.DataFrame(out)


def ipw_universe(df, who):
    """S3: inverse probability of being in the item universe, from pre-exposure covariates (complete-case)."""
    Z = pd.DataFrame({"const": 1.0, "agec": df["agec"], "agec2": df["agec"] ** 2, "female": df["female"],
                      "re_black": df["re_black"], "re_hispanic": df["re_hispanic"], "re_mixed": df["re_mixed"],
                      "urban": df["urban"].fillna(-1).eq(1).astype(float), "urban_unknown": df["urban"].isna().astype(float),
                      "pov_log": df["pov_log"].fillna(df["pov_log"].median()), "pov_missing": df["pov_log"].isna().astype(float)})
    y = df[f"{who}_universe"]
    p = sm.GLM(y, Z, family=sm.families.Binomial(), var_weights=df["w"]).fit().predict(Z)
    return df["w"] / p


def tabulate_by_age(df, who):
    s = df[(df[f"{who}_universe"] == 1) & df[f"{who}_vs"].notna()]
    rows = []
    for a in AGES:
        g = s[s["age"] == a]
        o = g[g["hgc"].notna()]
        rows.append({"age_1996": a, "n_valid_exposure": len(g),
                     "pct_very_supportive_weighted": round(100 * np.average(g[f"{who}_vs"], weights=g["w"]), 1),
                     "n_outcome_observed": len(o),
                     "mean_hgc_weighted_observed": round(float(np.average(o["hgc"], weights=o["w"])), 2) if len(o) >= MIN_CELL else None})
    return rows


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m", type=int, default=40)
    ap.add_argument("--seed", type=int, default=20261112)
    a = ap.parse_args()
    df, manifest = prepare()
    df_design = float(df.groupby("strata")["psu"].nunique().sum() - df["strata"].nunique())
    results = {"manifest": {k: manifest[k] for k in ("file", "sha256", "n_rows")}, "m": a.m, "seed": a.seed,
               "design_df": df_design, "sesoi_sd": SESOI_SD, "analyses": {}}
    p_primary = {}
    for i, who in enumerate(("mother", "father")):
        print(f"--- {who} support ---", flush=True)
        sample = df[(df[f"{who}_universe"] == 1) & df[f"{who}_vs"].notna()].copy()
        sd = weighted_sd(sample["hgc"], sample["w"])
        imps_raw = impute(sample, who, a.m, a.seed + i)
        imps = [pad(imp, df) for imp in imps_raw]
        R = {"flow": flow(df, who), "descriptives_by_age": tabulate_by_age(df, who), "sd_hgc_weighted_observed": sd}
        prim = pooled_contrasts(imps, lambda d: linear_fit(d, who), df_design)
        R["primary"] = prim.to_dict("records")
        dl = prim.set_index("quantity").loc["delta_16_vs_12"]
        p_primary[who] = dl["p"]
        R["equivalence"] = equivalence_test(dl["estimate"] / sd, dl["se"] / sd, SESOI_SD, df=dl["df"])
        R["delta_sd"] = {"estimate": dl["estimate"] / sd, "ci_low": dl["ci_low"] / sd, "ci_high": dl["ci_high"] / sd}
        th14 = prim.set_index("quantity").loc["theta_14"]
        R["e_values"] = {"theta_14": e_value(rr_from_smd(th14["estimate"] / sd), rr_from_smd(th14["ci_low"] / sd)),
                         "delta": e_value(rr_from_smd(abs(dl["estimate"]) / sd),
                                          rr_from_smd(min(abs(dl["ci_low"]), abs(dl["ci_high"])) / sd
                                                      if np.sign(dl["ci_low"]) == np.sign(dl["ci_high"]) else 0.0))}
        S = {}
        print("  S1", flush=True); S["S1_categorical_age"] = categorical_age(imps, who, df_design).to_dict("records")
        cc = sample.dropna(subset=["hgc", *[c for c in COVARIATES if c in sample.columns]])
        print("  S2/S3", flush=True)
        S["S2_complete_case"] = {"n": len(cc), "est": single_contrasts(linear_fit(pad(cc, df), who)).to_dict("records")}
        full = df.copy(); full["w_ipw"] = ipw_universe(full, who)
        cc3 = cc.assign(w_ipw=full.loc[cc.index, "w_ipw"])
        S["S3_ipw_universe_complete_case"] = {"n": len(cc3), "est": single_contrasts(linear_fit(pad(cc3, df), who, wcol="w_ipw")).to_dict("records")}
        print("  S4-S8", flush=True)
        S["S4_adjust_grade_1997"] = pooled_contrasts(imps, lambda d: linear_fit(d, who, extra=["hgc97"]), df_design).to_dict("records")
        S["S5a_ordinal_exposure"] = pooled_contrasts(imps, lambda d: linear_fit(d, who, exposure=f"{who}_ord"), df_design).to_dict("records")
        sc = [domain(imp, imp[f"{who}_scale"].notna(), fill_cols=[f"{who}_scale"]) for imp in imps]
        S["S5b_scale_exposure_per_point"] = {"n": int(sample[f"{who}_scale"].notna().sum()), "est": pooled_contrasts(
            sc, lambda d: linear_fit(d, who, exposure=f"{who}_scale"), df_design).to_dict("records")}
        S["S6_unweighted_no_design"] = pooled_contrasts(imps_raw, lambda d: linear_fit(d, who, weighted=False), df_design).to_dict("records")
        S["S8_adjust_asvab"] = pooled_contrasts(imps, lambda d: linear_fit(d, who, extra=["asvab"]), df_design).to_dict("records")
        R["sensitivity"] = S
        # exploratory
        E = {}
        def heter(flag):
            sub = [domain(imp, (np.expm1(imp["pov_log"]) < 1.0) == flag) for imp in imps]
            return pooled_contrasts(sub, lambda d: linear_fit(d, who), df_design).to_dict("records")
        E["poverty_below_100pct"] = heter(True)
        E["poverty_at_or_above_100pct"] = heter(False)
        ba = []
        for imp in imps:
            covs = [c for c in COVARIATES if c in imp.columns and imp.loc[imp["w"] > 0, c].nunique() > 1]
            X = pd.concat([pd.DataFrame({"const": 1.0, "s": imp[f"{who}_vs"], "agec": imp["agec"],
                                         "s_x_age": imp[f"{who}_vs"] * imp["agec"]}), imp[covs]], axis=1)
            ba.append(fit_survey_glm(X, imp["ba_plus"].clip(0, 1).round(), family="binomial", **design(imp)))
        e = np.array([contrasts(f)[0] for f in ba]); v = np.array([contrasts(f)[1] for f in ba])
        E["ba_plus_log_odds"] = [dict(quantity=q, **{k: rubin_pool(e[:, j], v[:, j], n_obs=df_design)[k] for k in ("estimate", "se")})
                                 for j, q in enumerate([f"theta_{x}" for x in AGES] + ["delta_16_vs_12"])]
        R["exploratory"] = E
        results["analyses"][who] = R
    holm = adjust_pvalues([p_primary["mother"], p_primary["father"]], "holm")
    results["holm_adjusted_p_delta"] = {"mother": float(holm[0]), "father": float(holm[1])}
    out = ROOT / "outputs" / "paper1_results.json"
    out.write_text(json.dumps(results, indent=2, default=float))
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
