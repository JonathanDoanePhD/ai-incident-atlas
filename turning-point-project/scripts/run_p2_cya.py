"""Paper 2: maternal warmth at ages 6-9 (HOME Part C) vs 10-14 (Part D) -> BA+ (NLSY79 CYA).

Implements docs/sap_nlsy79cya_childhood.md (frozen; docs/PLAN_FREEZE_P2.md). Inputs are git-ignored
extracts in data/raw/nlsy79cya/. Writes aggregate results to outputs/p2_results.json.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from turning_point.longitudinal import compare_lifecourse_models, exposure_patterns  # noqa: E402
from turning_point.modeling import adjust_pvalues, equivalence_test, fit_survey_glm, rubin_pool  # noqa: E402

warnings.filterwarnings("ignore")
SESOI = 0.03


def normal_scores(s: pd.Series) -> pd.Series:
    r = s.rank(method="average")
    return pd.Series(stats.norm.ppf((r - 0.5) / s.notna().sum()), index=s.index).where(s.notna())


def window_scores(c: pd.DataFrame, stem: str, transform) -> pd.DataFrame:
    cols = [k for k in c.columns if k.startswith(stem + "_")]
    out = {"C": [], "D": []}
    for k in cols:
        _, year, part = k.split("_")
        v = c[k].where(c[k] >= 0)
        z = transform(v)
        out[part].append(z.rename(year))
    res = {}
    for part in ("C", "D"):
        M = pd.concat(out[part], axis=1)
        res[f"n_{part}"] = M.notna().sum(axis=1)
        res[part] = M.mean(axis=1)
        res[f"first_year_{part}"] = M.apply(lambda r: min((int(y) for y, x in r.items() if pd.notna(x)), default=np.nan), axis=1)
    return pd.DataFrame(res)


def prepare():
    c = pd.read_csv(ROOT / "data/raw/nlsy79cya/cya_extract.csv")
    m = pd.read_csv(ROOT / "data/raw/nlsy79cya/n79_extract.csv").set_index("CASEID")
    praise = window_scores(c, "PRAISE", lambda v: normal_scores(v.clip(upper=17)))
    close = window_scores(c, "CLOSE", lambda v: (v == 1).astype(float).where(v.notna()))
    d = pd.DataFrame({"cid": c.CPUBID, "mid": c.MPUBID, "cyrb": c.CYRB})
    d["female"] = (c.CSEX == 2).astype(float)
    d["hisp"] = (c.CRACE == 1).astype(float); d["black"] = (c.CRACE == 2).astype(float)
    for lo, hi in ((1984, 1987), (1988, 1991), (1992, 1995)):
        d[f"by_{lo}"] = c.CYRB.between(lo, hi).astype(float)
    d["order2"] = (c.BTHORDR == 2).astype(float); d["order3p"] = (c.BTHORDR >= 3).astype(float)
    d["mage"] = c.MAGEBIR.where(c.MAGEBIR > 0)
    d["mom_hgc"] = c.MOM_HGC_1990.where(c.MOM_HGC_1990.between(0, 20))
    mm = m.reindex(c.MPUBID)
    d["afqt"] = (mm["AFQT3"].where(mm["AFQT3"] >= 0) / 1000).to_numpy()
    povc = [k for k in m.columns if k.startswith("POV_")]; incc = [k for k in m.columns if k.startswith("TNFI_")]
    pv, ic = [], []
    for i, (by, mid) in enumerate(zip(c.CYRB, c.MPUBID)):
        row = m.loc[mid]
        ys = [int(k.split("_")[1]) for k in povc]
        p = [row[f"POV_{y}"] for y in ys if 0 <= y - by <= 14 and row[f"POV_{y}"] in (0, 1)]
        inc = [np.log1p(row[f"TNFI_{y}"]) for y in ys if 0 <= y - by <= 14 and row[f"TNFI_{y}"] >= 0]
        pv.append(np.mean(p) if p else np.nan); ic.append(np.mean(inc) if inc else np.nan)
    d["pov_share"] = pv; d["log_inc"] = ic
    deg = c.HSTDEGREE_DLI.where(c.HSTDEGREE_DLI >= 0)
    age_last = c.LASTINTYR.where(c.LASTINTYR > 0) - c.CYRB
    d["ba"] = (deg >= 4).astype(float).where(deg.notna() & (age_last >= 25))
    d["age_last"] = age_last
    for nm, W in (("praise", praise), ("close", close)):
        for part in ("C", "D"):
            d[f"{nm}{part}"] = W[part]; d[f"n_{nm}{part}"] = W[f"n_{part}"]
        d[f"first_D_{nm}"] = W["first_year_D"]
    # child weight from year of first Part D praise report
    w = np.full(len(c), np.nan)
    for i, y in enumerate(d["first_D_praise"]):
        if pd.notna(y) and f"CSAMWT{int(y)}" in c.columns:
            v = c.at[i, f"CSAMWT{int(y)}"]
            w[i] = v if v > 0 else np.nan
    d["w"] = w
    return d


COVS = ["female", "hisp", "black", "by_1984", "by_1988", "by_1992", "order2", "order3p", "mage", "mom_hgc", "afqt", "pov_share", "log_inc"]


def zstd(x):
    return (x - x.mean()) / x.std()


def impute(s, cols, m, seed):
    from statsmodels.imputation.mice import MICEData
    np.random.seed(seed)
    md = MICEData(s[cols].copy(), k_pmm=5); md.update_all(10)
    out = []
    for _ in range(m):
        md.update_all(5); x = md.data.copy(); x.index = s.index
        for k in s.columns:
            if k not in x.columns:
                x[k] = s[k].values
        out.append(x)
    return out


def fit(d, a, b, covs=COVS, weights=None, joint=True):
    covs = [k for k in covs if d[k].nunique() > 1]
    X = pd.concat([pd.Series(1.0, index=d.index, name="const"), d[[a, b] if joint else [a]], d[covs]], axis=1)
    return fit_survey_glm(X, d["ba"], weights=weights, psu=d["mid"])


def contrasts(f, a, b):
    names = list(f.params.index)
    L = np.zeros((3, len(names)))
    L[0, names.index(a)] = 1; L[1, names.index(b)] = 1; L[2, names.index(a)] = 1; L[2, names.index(b)] = -1
    lc = f.linear_combination(L)
    return lc["estimate"].to_numpy(), (lc["se"] ** 2).to_numpy(), f.df_resid


def pool(res, labels):
    E = np.array([r[0] for r in res]); V = np.array([r[1] for r in res]); dfc = res[0][2]
    out = []
    for j, lab in enumerate(labels):
        r = rubin_pool(E[:, j], V[:, j], n_obs=dfc, k_params=0) if len(res) > 1 else {"estimate": E[0, j], "se": np.sqrt(V[0, j]), "df": dfc, "fmi": 0}
        t = stats.t.ppf(0.975, r["df"])
        out.append({"quantity": lab, "estimate": r["estimate"], "se": r["se"], "df": r["df"], "ci_low": r["estimate"] - t * r["se"],
                    "ci_high": r["estimate"] + t * r["se"], "p": 2 * stats.t.sf(abs(r["estimate"] / r["se"]), r["df"]), "fmi": r.get("fmi")})
    return out


def analyse(s, expo, m, seed, extra=None):
    a, b = f"{expo}C", f"{expo}D"
    s = s.copy(); s[a] = zstd(s[a]); s[b] = zstd(s[b])
    imps = impute(s, ["ba", a, b, *COVS], m, seed)
    lab = ("beta_6_9", "beta_10_14", "delta_C_minus_D")
    R = {"primary": pool([contrasts(fit(i, a, b), a, b) for i in imps], lab)}
    d = R["primary"][2]
    R["equivalence"] = equivalence_test(d["estimate"], d["se"], SESOI, df=d["df"])
    R["corr_C_D"] = float(np.corrcoef(s[a], s[b])[0, 1])
    if extra:
        cc = s.dropna(subset=["ba", *COVS])
        R["S2_complete_case"] = {"n": int(len(cc)), "est": pool([contrasts(fit(cc, a, b), a, b)], lab)}
        ww = [i[i["w"].notna()] for i in imps]
        R["S3_child_weights"] = {"n": int(len(ww[0])), "est": pool([contrasts(fit(i, a, b, weights=i["w"]), a, b) for i in ww], lab)}
        sep = []
        for i in imps:
            fa = fit(i, a, a, joint=False); fb = fit(i, b, b, joint=False)
            sep.append((np.array([fa.params[a], fb.params[b], fa.params[a] - fb.params[b]]),
                        np.array([fa.cov.loc[a, a], fb.cov.loc[b, b], np.nan]), fa.df_resid))
        E = np.array([r[0] for r in sep]); V = np.array([r[1] for r in sep])
        R["S4_window_alone"] = {k: rubin_pool(E[:, j], V[:, j], n_obs=sep[0][2], k_params=0) for j, k in enumerate(("beta_6_9_alone", "beta_10_14_alone"))}
        noinc = [k for k in COVS if k not in ("pov_share", "log_inc")]
        R["S5_no_income_poverty"] = pool([contrasts(fit(i, a, b, covs=noinc), a, b) for i in imps], lab)
        # E1 life-course structured approach on binary top-tercile exposures (first imputation; descriptive)
        i0 = imps[0]
        E2 = pd.DataFrame({"C": (i0[a] >= i0[a].quantile(2 / 3)).astype(int), "D": (i0[b] >= i0[b].quantile(2 / 3)).astype(int)})
        covs = [k for k in COVS if i0[k].nunique() > 1]
        tab = compare_lifecourse_models(i0["ba"].clip(0, 1).round(), E2, covariates=i0[covs], family="binomial")
        R["E1_lifecourse"] = {"patterns": exposure_patterns(E2).to_dict(), "models": tab.round(4).to_dict("records")}
    return R


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--m", type=int, default=20); ap.add_argument("--seed", type=int, default=20261112)
    a = ap.parse_args()
    d = prepare()
    flow = {"children": int(len(d)), "born_1979_1995": int(d.cyrb.between(1979, 1995).sum())}
    s = d[d.cyrb.between(1979, 1995)]
    flow["praise_both_windows"] = int((s.n_praiseC > 0).mul(s.n_praiseD > 0).sum())
    flow["close_both_windows"] = int((s.n_closeC > 0).mul(s.n_closeD > 0).sum())
    sp = s[(s.n_praiseC > 0) & (s.n_praiseD > 0)].copy()
    flow["praise_outcome_observed"] = int(sp.ba.notna().sum()); flow["praise_outcome_imputed"] = int(sp.ba.isna().sum())
    flow["praise_mothers"] = int(sp.mid.nunique())
    flow["praise_reports_per_child_C_mean"] = float(sp.n_praiseC.mean()); flow["praise_reports_per_child_D_mean"] = float(sp.n_praiseD.mean())
    flow["ba_rate_observed_unweighted"] = float(sp.ba.mean())
    print(flow, flush=True)
    R = {"flow": flow, "m": a.m, "sesoi": SESOI}
    R["praise"] = analyse(sp, "praise", a.m, a.seed, extra=True)
    print("praise done", flush=True)
    sc = s[(s.n_closeC > 0) & (s.n_closeD > 0)].copy()
    R["flow"]["close_outcome_observed"] = int(sc.ba.notna().sum())
    R["S1_closeness"] = analyse(sc, "close", a.m, a.seed + 1)
    holm = adjust_pvalues([R["praise"]["primary"][2]["p"], R["S1_closeness"]["primary"][2]["p"]], "holm")
    R["note"] = "Holm across praise and closeness Delta shown for reference; closeness is a pre-specified secondary exposure."
    R["holm_delta"] = {"praise": float(holm[0]), "closeness": float(holm[1])}
    (ROOT / "outputs" / "p2_results.json").write_text(json.dumps(R, indent=2, default=float))
    print("wrote outputs/p2_results.json")


if __name__ == "__main__":
    main()
