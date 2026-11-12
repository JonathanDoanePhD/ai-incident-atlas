"""Study B2: perceived math-teacher support in grade 9 vs grade 11 -> BA+ by June 2021 (HSLS:09).

Implements docs/sap_hsls09_grade9.md (frozen; docs/PLAN_FREEZE_B2.md). Reads the git-ignored
extract data/raw/hsls09/b2_extract.csv and writes aggregate results to outputs/b2_results.json.
Variance: standard BRR (200 replicates, no Fay factor - inferred from replicate structure:
exactly half of replicate/full weight ratios are zero), pooled over m imputations by Rubin's rules.
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
from turning_point.constructs import cronbach_alpha  # noqa: E402
from turning_point.modeling import equivalence_test, replicate_variance, rubin_pool  # noqa: E402

warnings.filterwarnings("ignore")
REPS = [f"W2W1STU{i:03d}" for i in range(1, 201)]
DF_COM = 199.0
SESOI = 0.03


def prepare():
    d = pd.read_csv(ROOT / "data/raw/hsls09/b2_extract.csv")
    out = pd.DataFrame(index=d.index)
    for g, p in (("9", "S1"), ("11", "S2")):
        items = {}
        for it in ("TREAT", "INTRST", "EASY"):
            x = d[f"{p}MTCH{it}"].where(d[f"{p}MTCH{it}"].between(1, 4))
            items[it] = x if it == "TREAT" else 5 - x  # higher = more supportive
        I = pd.DataFrame(items)
        out[f"items{g}_answered"] = I.notna().sum(axis=1)
        out[f"sup{g}"] = I.mean(axis=1).where(I.notna().sum(axis=1) >= 2)
        out[f"sup{g}_pos"] = I[["INTRST", "EASY"]].mean(axis=1).where(I[["INTRST", "EASY"]].notna().sum(axis=1) >= 1)
        out[f"universe{g}"] = (d[f"{p}MTCHINTRST"] != -7) & (d[f"{p}MTCHINTRST"] != -8)
        for it in items:
            out[f"{it.lower()}{g}"] = items[it]
    hd = d["X6HIGHDEG"]
    out["ba"] = np.where(hd.isin([3, 5, 7]), 1.0, np.where(hd.isin([0, 1, 2, 8, 9, 10]), 0.0, np.nan))
    out["female"] = (d["X1SEX"] == 2).astype(float).where(d["X1SEX"].isin([1, 2]))
    r = d["X1RACE"]
    for lab, codes in {"black": [3], "hispanic": [4, 5], "asian": [2], "other_race": [1, 6, 7]}.items():
        out[lab] = r.isin(codes).astype(float).where(r > 0)
    out["ses"] = d["X1SES"].where(d["X1SES"] > -8)
    out["two_parent"] = (d["X1PARPATTERN"] == 1).astype(float).where(d["X1PARPATTERN"] > 0)
    out["math9"] = d["X1TXMTSCOR"].where(d["X1TXMTSCOR"] > -8)
    for k, lab in {1: "city", 2: "suburb", 3: "town"}.items():
        out[f"loc_{lab}"] = (d["X1LOCALE"] == k).astype(float)
    out["math11"] = d["X2TXMTSCOR"].where(d["X2TXMTSCOR"] > -8)
    out["evercoll"] = d["X4EVRATNDCLG"].where(d["X4EVRATNDCLG"].isin([0, 1]))
    out["talk9"] = (5 - d["S1TALKPROB"]).where(d["S1TALKPROB"].between(1, 4))
    out["w"] = d["W2W1STU"]
    for c in REPS:
        out[c] = d[c]
    return out


COVS = ["female", "black", "hispanic", "asian", "other_race", "ses", "two_parent", "math9", "loc_city", "loc_suburb", "loc_town"]
AUX = ["math11", "evercoll", "talk9"]


def impute(s, m, seed):
    from statsmodels.imputation.mice import MICEData
    cols = ["ba", "sup9", "sup11", *COVS, *AUX]
    data = s[cols].copy()
    data["logw"] = np.log(s["w"])
    np.random.seed(seed)
    md = MICEData(data, k_pmm=5)
    md.update_all(10)
    imps = []
    for _ in range(m):
        md.update_all(5)
        imp = md.data.copy(); imp.index = s.index
        for c in ["w", *REPS, "sup9_pos", "sup11_pos", "talk9"]:
            imp[c] = s[c].values
        imps.append(imp)
    return imps


def wstd(x, w):
    mu = np.average(x, weights=w)
    return (x - mu) / np.sqrt(np.average((x - mu) ** 2, weights=w))


def wls_coef(X, y, w):
    sw = np.sqrt(w)
    return np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)[0]


def thetas(df, wcol, exp9="sup9", exp11="sup11", covs=COVS, logistic=False, joint=False):
    """theta9, theta11 (and their difference) under weight column wcol."""
    w = df[wcol].to_numpy(float)
    keep = w > 0
    d = df[keep]; w = w[keep]
    y = d["ba"].to_numpy(float)
    C = d[covs].to_numpy(float)
    z9 = wstd(d[exp9].to_numpy(float), w); z11 = wstd(d[exp11].to_numpy(float), w)
    one = np.ones((len(d), 1))
    if joint:
        X = np.column_stack([one, z9, z11, C])
        b = wls_coef(X, y, w) if not logistic else sm.GLM(y, X, family=sm.families.Binomial(), var_weights=w).fit().params
        return np.array([b[1], b[2], b[2] - b[1]])
    out = []
    for z in (z9, z11):
        X = np.column_stack([one, z, C])
        b = wls_coef(X, y, w) if not logistic else sm.GLM(y, X, family=sm.families.Binomial(), var_weights=w).fit().params
        out.append(b[1])
    return np.array([out[0], out[1], out[1] - out[0]])


def brr(df, **kw):
    full = thetas(df, "w", **kw)
    reps = np.vstack([thetas(df, r, **kw) for r in REPS])
    V = replicate_variance(full, reps, method="brr")
    return full, np.diag(V)


def pool(results, labels=("theta9", "theta11", "diff_11_minus_9")):
    E = np.array([r[0] for r in results]); V = np.array([r[1] for r in results])
    out = []
    for j, lab in enumerate(labels):
        if E.shape[0] > 1:
            r = rubin_pool(E[:, j], V[:, j], n_obs=DF_COM, k_params=0)
        else:
            r = {"estimate": E[0, j], "se": np.sqrt(V[0, j]), "df": DF_COM, "fmi": 0.0}
        t = stats.t.ppf(0.975, r["df"])
        out.append({"quantity": lab, "estimate": r["estimate"], "se": r["se"], "df": r["df"],
                    "ci_low": r["estimate"] - t * r["se"], "ci_high": r["estimate"] + t * r["se"],
                    "p": 2 * stats.t.sf(abs(r["estimate"] / r["se"]), r["df"]), "fmi": r.get("fmi")})
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--m", type=int, default=20); ap.add_argument("--seed", type=int, default=20261112)
    a = ap.parse_args()
    df = prepare()
    flow = {"student_records": int(len(df)), "by_f1_longitudinal_weight_positive": int((df.w > 0).sum())}
    s = df[(df.w > 0)]
    flow["math_items_grade9"] = int(s["sup9"].notna().sum())
    s = s[s["sup9"].notna() & s["sup11"].notna()].copy()
    flow["math_items_both_grades (analytic)"] = int(len(s))
    flow["outcome_observed"] = int(s["ba"].notna().sum()); flow["outcome_imputed"] = int(s["ba"].isna().sum())
    rel = {f"alpha_grade{g}": cronbach_alpha(s[[f"treat{g}", f"intrst{g}", f"easy{g}"]]) for g in ("9", "11")}
    rel["corr_sup9_sup11"] = float(np.corrcoef(s["sup9"], s["sup11"])[0, 1])
    desc = {"ba_rate_weighted_observed": float(np.average(s["ba"].dropna(), weights=s.loc[s["ba"].notna(), "w"]))}
    print(flow, rel, desc, flush=True)
    imps = impute(s, a.m, a.seed)
    R = {"flow": flow, "reliability": rel, "descriptives": desc, "m": a.m, "sesoi": SESOI, "brr": "standard BRR, 200 replicates, no Fay factor"}
    print("primary", flush=True)
    prim = pool([brr(i) for i in imps]); R["primary"] = prim
    d = prim[2]
    R["equivalence"] = equivalence_test(d["estimate"], d["se"], SESOI, df=d["df"])
    print("sensitivity", flush=True)
    R["S1_positive_items_only"] = pool([brr(i, exp9="sup9_pos", exp11="sup11_pos") for i in imps])
    cc = s.dropna(subset=["ba", *COVS])
    R["S2_complete_case"] = {"n": int(len(cc)), "est": pool([brr(cc)])}
    R["S4_minimal_covariates"] = pool([brr(i, covs=["female", "black", "hispanic", "asian", "other_race"]) for i in imps])
    R["S3_logistic_log_odds"] = pool([brr(i, logistic=True) for i in imps[:5]])
    R["S3_note"] = "logistic run on the first 5 imputations to limit runtime (1,005 fits per imputation)"
    print("exploratory", flush=True)
    R["E1_joint_model"] = pool([brr(i, joint=True) for i in imps], labels=("theta9_adj", "theta11_adj", "diff"))
    t9 = [i.assign(talk=i["talk9"]) for i in imps]
    R["E3_talk_to_adult_grade9"] = pool([brr(i.dropna(subset=["talk9"]), exp9="talk9", exp11="talk9") for i in t9])[:1]
    # E2: top-tercile patterns (weighted terciles), adjusted mean differences vs low/low, first imputation pooled
    def patterns(df, wcol):
        w = df[wcol].to_numpy(float); keep = w > 0; d = df[keep]; w = w[keep]
        h9 = d["sup9"] >= np.quantile(d["sup9"], 2 / 3); h11 = d["sup11"] >= np.quantile(d["sup11"], 2 / 3)
        X = np.column_stack([np.ones(len(d)), (h9 & ~h11), (~h9 & h11), (h9 & h11), d[COVS].to_numpy(float)]).astype(float)
        b = wls_coef(X, d["ba"].to_numpy(float), w)
        return b[1:4]
    pr = []
    for i in imps:
        full = patterns(i, "w"); reps = np.vstack([patterns(i, r) for r in REPS])
        pr.append((full, np.diag(replicate_variance(full, reps))))
    R["E2_patterns_vs_low_low"] = pool(pr, labels=("high9_only", "high11_only", "high_both"))
    out = ROOT / "outputs" / "b2_results.json"
    out.write_text(json.dumps(R, indent=2, default=float))
    print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
