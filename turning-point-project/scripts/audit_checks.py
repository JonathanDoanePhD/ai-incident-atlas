"""POST-HOC AUDIT CHECKS (2026-11-13). Not part of any frozen plan; results are labeled exploratory/audit.

A. Paper 1: joint test that the support association is equal at all five ages (4-df design-based Wald, categorical age),
   complete cases, mother and father.
B. Paper 2: measurement-reliability check. Window scores average ~1.8 reports at 6-9 vs ~2.0 at 10-14, so the later
   window may be measured more reliably (less attenuation). Re-estimate using exactly one report per window (the first),
   and using exactly two reports per window among children with >= 2 in each. Complete cases, clustered by mother.
C. Accumulation (NLSY97 1997-2000): cumulative, timing-specific, onset, loss-of-support, stability and saturated models;
   design-based Wald tests against the saturated model; complete-case selection diagnostics and an IPW sensitivity check.
Writes outputs/audit/audit_results.json.
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
import run_paper1 as rp  # noqa: E402
import run_p2_cya as p2  # noqa: E402
from turning_point.modeling import SurveyDesign, fit_age_moderation, fit_survey_glm  # noqa: E402
import statsmodels.api as sm  # noqa: E402

OUT = {}

# ---------------------------------------------------------------- A
df, _ = rp.prepare()
A = {}
for who in ("mother", "father"):
    s = df[(df[f"{who}_universe"] == 1) & df[f"{who}_vs"].notna()]
    covs = [c for c in rp.COVARIATES if c in s.columns]
    cc = s.dropna(subset=["hgc", *covs])
    covs = [c for c in covs if cc[c].nunique() > 1]
    full = rp.pad(cc, df)
    res = fit_age_moderation(full.assign(age=full["agec"] + 14), outcome="hgc", exposure=f"{who}_vs", age="age", covariates=covs,
                             design=SurveyDesign(weight="w", strata="strata", psu="psu"), age_bands=[13, 14, 15, 16], age_grid=[12, 13, 14, 15, 16])
    A[who] = {"n_complete": int(len(cc)), "theta_by_age": res.effect_by_age.round(4).to_dict("records"),
              "wald_equal_all_ages": {k: float(v) for k, v in res.interaction_test.items()}}
OUT["A_paper1_all_ages_equal_test"] = A

# ---------------------------------------------------------------- B
c = pd.read_csv(ROOT / "data/raw/nlsy79cya/cya_extract.csv")
d = p2.prepare()
cols = sorted([k for k in c.columns if k.startswith("PRAISE_")], key=lambda k: int(k.split("_")[1]))
Z = {}
for k in cols:
    v = c[k].where(c[k] >= 0)
    Z[k] = p2.normal_scores(v.clip(upper=17))
Z = pd.DataFrame(Z)
def take(part, nmax):
    ks = [k for k in cols if k.endswith("_" + part)]
    M = Z[ks]
    vals = M.apply(lambda r: list(r.dropna().values), axis=1)
    return vals.apply(lambda L: np.mean(L[:nmax]) if len(L) >= nmax else np.nan), vals.apply(len)
B = {}
s = d[d.cyrb.between(1979, 1995)].copy()
for label, nC, nD in (("one report per window (first)", 1, 1), ("two reports per window (first two; children with >=2 in each)", 2, 2)):
    eC, cntC = take("C", nC); eD, cntD = take("D", nD)
    x = s.assign(xC=eC, xD=eD).dropna(subset=["xC", "xD", "ba", *p2.COVS])
    x["xC"], x["xD"] = p2.zstd(x["xC"]), p2.zstd(x["xD"])
    f = p2.fit(x, "xC", "xD")
    est, var, dft = p2.contrasts(f, "xC", "xD")
    se = np.sqrt(var); t = stats.t.ppf(.975, dft)
    B[label] = {"n": int(len(x)), **{q: {"estimate": float(e), "se": float(sv), "ci_low": float(e - t * sv), "ci_high": float(e + t * sv)}
                                     for q, e, sv in zip(("beta_6_9", "beta_10_14", "delta_C_minus_D"), est, se)}}
# same complete-case sample with the original (all-report) window scores, for comparison
x = s.dropna(subset=["praiseC", "praiseD", "ba", *p2.COVS]).copy()
x["praiseC"], x["praiseD"] = p2.zstd(x["praiseC"]), p2.zstd(x["praiseD"])
f = p2.fit(x, "praiseC", "praiseD"); est, var, dft = p2.contrasts(f, "praiseC", "praiseD"); se = np.sqrt(var); t = stats.t.ppf(.975, dft)
B["all reports (primary scoring), complete cases"] = {"n": int(len(x)), **{q: {"estimate": float(e), "se": float(sv), "ci_low": float(e - t * sv), "ci_high": float(e + t * sv)}
                                                       for q, e, sv in zip(("beta_6_9", "beta_10_14", "delta_C_minus_D"), est, se)}}
B["mean_reports_per_child"] = {"C": float(d.loc[d.n_praiseC > 0, "n_praiseC"].mean()), "D": float(d.loc[d.n_praiseD > 0, "n_praiseD"].mean())}
OUT["B_paper2_reliability_check"] = B

# ---------------------------------------------------------------- C
acc = pd.read_csv(ROOT / "data/raw/nlsy97/accum_extract.csv")
E = pd.DataFrame({"E1997": df["mother_vs"]}, index=df.index)
for y in (1998, 1999, 2000):
    v = acc[f"ysaq032_{y}"]
    E[f"E{y}"] = (v == 1).astype(float).where(v.isin([1, 2, 3])).values
rounds = list(E.columns)
base = df[df["age"] <= 14].join(E)
covs = [k for k in rp.COVARIATES]
base["complete_hist"] = base[rounds].notna().all(axis=1)
base["complete_cc"] = base["complete_hist"] & base[["hgc", *covs]].notna().all(axis=1)
# selection diagnostics (weighted means, aggregate only)
sel = {}
for grp, m in (("analysed (complete history + complete cases)", base["complete_cc"]), ("excluded", ~base["complete_cc"])):
    g = base[m]
    wm = lambda col: float(np.average(g[col].dropna(), weights=g.loc[g[col].notna(), "w"])) if g[col].notna().sum() > 9 else None  # noqa: E731
    sel[grp] = {"n": int(m.sum()), "very_supportive_1997": wm("mother_vs"), "hgc_observed": wm("hgc"), "female": wm("female"),
                "black": wm("re_black"), "hispanic": wm("re_hispanic"), "pov_log": wm("pov_log"), "parent_ed": wm("parent_ed"),
                "two_bio_parents_hh": float(np.average((g["hh_struct"] if "hh_struct" in g else pd.Series(dtype=float)).fillna(0))) if "hh_struct" in g else None}
OUT["C_selection"] = sel
s = base[base["complete_cc"]].copy()
covs = [k for k in covs if s[k].nunique() > 1]
s["count"] = s[rounds].sum(axis=1)
pat = s[rounds].astype(int).astype(str).agg("".join, axis=1)
s["pattern"] = pat
first = s[rounds].values.argmax(axis=1).astype(float); first[s["count"].values == 0] = np.nan
s["onset_round"] = first
arr = s[rounds].values.astype(int)
s["n_losses"] = ((arr[:, :-1] == 1) & (arr[:, 1:] == 0)).sum(axis=1)
s["any_loss"] = (s["n_losses"] > 0).astype(float)
s["all_four"] = (s["count"] == 4).astype(float)
s["never"] = (s["count"] == 0).astype(float)
for r_ in rounds:
    s[f"on_{r_}"] = (s["onset_round"] == rounds.index(r_)).astype(float)
for p_ in sorted(pat.unique()):
    s[f"pat_{p_}"] = (pat == p_).astype(float)
full = rp.pad(s, df)
des = dict(weights=full["w"], strata=full["strata"], psu=full["psu"])
def X(cols_):
    return pd.concat([pd.Series(1.0, index=full.index, name="const"), full[["agec", *cols_]].astype(float), full[covs].astype(float)], axis=1)
pats = [f"pat_{p}" for p in sorted(pat.unique()) if p != "0000"]
models = {
    "null": [],
    "cumulative (count 0-4)": ["count"],
    "timing: 1997 only": ["E1997"], "timing: 1998 only": ["E1998"], "timing: 1999 only": ["E1999"], "timing: 2000 only (most recent)": ["E2000"],
    "sensitive periods (4 free round coefficients)": rounds,
    "onset (round support first reported; ref never)": [f"on_{r_}" for r_ in rounds],
    "loss of support (count + any 1->0 transition)": ["count", "any_loss"],
    "stability (all four years very supportive; ref otherwise) + count": ["count", "all_four"],
    "saturated (16 patterns)": pats,
}
fits = {}
for name, cl in models.items():
    fits[name] = fit_survey_glm(X(cl), full["hgc"].fillna(0), **des)
sat = fits["saturated (16 patterns)"]
rows = []
y = s["hgc"].to_numpy(float); w = s["w"].to_numpy(float)
for name, f in fits.items():
    k = len(models[name])
    pred = X(models[name]).loc[s.index].to_numpy(float) @ f.params.to_numpy()
    rss = float(np.sum(w * (y - pred) ** 2)); n = len(y); p = len(f.params)
    row = {"model": name, "n_exposure_params": k, "weighted_rss": rss, "pseudo_aic_weighted_norm": n * np.log(rss / w.sum()) + 2 * p,
           "coefficients": {c_: {"estimate": float(f.params[c_]), "ci_low": float(f.summary().loc[c_, "ci_low"]), "ci_high": float(f.summary().loc[c_, "ci_high"])} for c_ in models[name]}}
    rows.append(row)
# design-based Wald tests of nested restrictions within the saturated pattern model:
# accumulation <=> pattern effects depend only on count: test via saturated model reparametrized: compare using
# a Wald test that pattern means are equal within count groups.
pidx = list(sat.params.index)
def wald_equal(groups):
    L = []
    for g in groups:
        g = [f"pat_{p}" for p in g if p != "0000"]
        for a, b in zip(g[:-1], g[1:]):
            l = np.zeros(len(pidx)); l[pidx.index(a)] = 1; l[pidx.index(b)] = -1; L.append(l)
    L = np.array(L); bvec = sat.params.to_numpy(); V = sat.cov.to_numpy()
    est = L @ bvec; chi2 = float(est @ np.linalg.solve(L @ V @ L.T, est)); q = L.shape[0]; ddf = sat.df_resid
    F = chi2 / q * (ddf - q + 1) / ddf
    return {"q": q, "F": F, "df2": ddf - q + 1, "p": float(stats.f.sf(F, q, ddf - q + 1))}
by_count = {}
for p_ in sorted(pat.unique()):
    by_count.setdefault(p_.count("1"), []).append(p_)
# accumulation restriction inside saturated: equal means within each count AND linear in count
OUT["C_wald_patterns_equal_within_count"] = wald_equal([g for g in by_count.values() if len(g) > 1])
OUT["C_pattern_counts"] = pat.value_counts().sort_index().to_dict()
OUT["C_models"] = rows
# IPW for complete-case selection (among age 12-14 in 1996)
Zs = pd.DataFrame({"const": 1.0, "agec": base["agec"], "female": base["female"], "black": base["re_black"], "hisp": base["re_hispanic"],
                   "mvs97": base["mother_vs"].fillna(0), "mvs97_miss": base["mother_vs"].isna().astype(float),
                   "pov": base["pov_log"].fillna(base["pov_log"].median()), "pov_miss": base["pov_log"].isna().astype(float),
                   "urban": base["urban"].fillna(0), "urban_miss": base["urban"].isna().astype(float)})
pm = sm.GLM(base["complete_cc"].astype(float), Zs, family=sm.families.Binomial(), var_weights=base["w"]).fit().predict(Zs)
s["w_ipw"] = (base["w"] / pm).loc[s.index]
full2 = rp.pad(s, df); full2["w_ipw"] = full2["w_ipw"].fillna(0.0)
f_ipw = fit_survey_glm(pd.concat([pd.Series(1.0, index=full2.index, name="const"), full2[["agec", "count"]], full2[covs].astype(float)], axis=1),
                       full2["hgc"].fillna(0), weights=full2["w_ipw"], strata=full2["strata"], psu=full2["psu"])
OUT["C_cumulative_slope_ipw"] = f_ipw.summary().loc["count"].to_dict()
f_ipw2 = fit_survey_glm(pd.concat([pd.Series(1.0, index=full2.index, name="const"), full2[["agec", *rounds]], full2[covs].astype(float)], axis=1),
                        full2["hgc"].fillna(0), weights=full2["w_ipw"], strata=full2["strata"], psu=full2["psu"])
OUT["C_round_coefficients_ipw"] = f_ipw2.summary().loc[rounds][["estimate", "ci_low", "ci_high"]].to_dict("index")
(ROOT / "outputs/audit/audit_results.json").write_text(json.dumps(OUT, indent=2, default=float))
print("wrote outputs/audit/audit_results.json")
