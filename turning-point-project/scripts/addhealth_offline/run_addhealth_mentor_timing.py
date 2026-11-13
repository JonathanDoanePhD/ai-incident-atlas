"""Study A3: age a natural mentor became important -> bachelor's degree by Wave IV (Add Health public-use).

RUN THIS YOURSELF, OUTSIDE ANY AI TOOL. Add Health's Conditions of Use prohibit using AI tools to manage, process
or analyze Add Health data. This script was written from public codebooks only (docs/sap_addhealth_mentor_timing.md).
See docs/addhealth_human_analyst_checklist.md before running.

Usage:
  python run_addhealth_mentor_timing.py --w1 FILE --w3 FILE --w4 FILE --weights FILE --out FOLDER

Needs: numpy, pandas, statsmodels (and pyreadstat for .dta/.sas7bdat/.sav). Self-contained: no project imports.
Writes aggregate tables only (cells < 10 suppressed) to FOLDER/a3_results.txt and FOLDER/a3_estimates.csv.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

PLAN = Path(__file__).resolve().parent.parent.parent / "docs" / "sap_addhealth_mentor_timing.md"
MIN_CELL = 10
SESOI = 0.05
GROUPS = ["no_mentor", "onset_lt14", "onset_14_17", "onset_18plus"]


def read_any(path: str, cols: list[str]) -> pd.DataFrame:
    p = Path(path)
    suf = p.suffix.lower()
    if suf in (".csv", ".tab", ".tsv", ".txt"):
        df = pd.read_csv(p, sep=None, engine="python")
    else:
        import pyreadstat
        reader = {".dta": pyreadstat.read_dta, ".sas7bdat": pyreadstat.read_sas7bdat, ".sav": pyreadstat.read_sav}[suf]
        df, _ = reader(str(p))
    df.columns = [str(c).upper() for c in df.columns]
    have = [c for c in cols if c in df.columns]
    return df[have].copy()


def clean(s: pd.Series, valid) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    return s.where(s.isin(valid)) if not callable(valid) else s.where(valid(s))


def build(w1, w3, w4, wt):
    d = w1.merge(w3, on="AID", how="inner").merge(w4, on="AID", how="inner").merge(wt, on="AID", how="inner")
    out = pd.DataFrame({"AID": d["AID"]})
    mn1 = clean(d["H3MN1"], [0, 1])
    onset = clean(d["H3MN6"], lambda s: s.between(0, 25))
    grp = pd.Series(np.nan, index=d.index, dtype=object)
    grp[mn1 == 0] = "no_mentor"
    grp[(mn1 == 1) & (onset < 14)] = "onset_lt14"
    grp[(mn1 == 1) & onset.between(14, 17)] = "onset_14_17"
    grp[(mn1 == 1) & (onset >= 18)] = "onset_18plus"
    out["group"] = grp
    out["onset"] = onset
    t = clean(d["H3MN2"], lambda s: s.between(1, 21))
    out["mtype"] = np.where(t == 11, "teacher", np.where(t.between(1, 10), "kin", np.where(t.between(12, 21), "community", None)))
    ed = clean(d["H4ED2"], lambda s: s.between(1, 13))
    out["ba"] = (ed >= 7).astype(float).where(ed.notna())
    out["female"] = (clean(d["BIO_SEX"], [1, 2]) == 2).astype(float).where(clean(d["BIO_SEX"], [1, 2]).notna())
    by = clean(d["H1GI1Y"], lambda s: s.between(70, 90))
    iy = clean(d["IYEAR"], lambda s: s.between(94, 96))
    out["age_w1"] = iy - by
    out["hispanic"] = clean(d["H1GI4"], [0, 1])
    for k, lab in zip("ABCDE", ["white", "black", "amind", "asian", "other_race"]):
        out[lab] = clean(d[f"H1GI6{k}"], [0, 1])
    pe = clean(d["PA12"], lambda s: s.between(1, 10))
    out["parent_ed"] = pe.where(pe != 10, 0)  # 10 = never went to school -> lowest
    inc = clean(d["PA55"], lambda s: s.between(0, 9995))
    out["inc_missing"] = inc.isna().astype(float)
    out["log_inc"] = np.log1p(inc.fillna(inc.median()))
    gr = pd.concat([clean(d[c], [1, 2, 3, 4]) for c in ["H1ED11", "H1ED12", "H1ED13", "H1ED14"] if c in d], axis=1)
    out["gpa"] = 5 - gr.mean(axis=1)
    wcol = "GSWGT134"
    if wcol not in d:
        raise ValueError("Use the Wave IV public-use weights file containing GSWGT134.")
    out["w"] = pd.to_numeric(d[wcol], errors="coerce")
    out["cluster"] = d["CLUSTER2"]
    return out, wcol


COVS = ["female", "age_w1", "hispanic", "black", "amind", "asian", "other_race", "parent_ed", "log_inc", "inc_missing"]


def fit(df, covs=COVS, weighted=True, logistic=False, ref="onset_14_17", groups=GROUPS):
    d = df.dropna(subset=["ba", "group", "cluster", *covs] + (["w"] if weighted else []))
    d = d[d["group"].isin(groups)]
    if weighted:
        d = d[d["w"] > 0]
    X = pd.get_dummies(d["group"], dtype=float).drop(columns=[ref])
    X = pd.concat([pd.Series(1.0, index=d.index, name="const"), X, d[covs].astype(float)], axis=1)
    X = X.loc[:, X.std() > 0].assign(const=1.0)
    w = d["w"].to_numpy(float) if weighted else np.ones(len(d))
    fam = sm.families.Binomial() if logistic else sm.families.Gaussian()
    res = sm.GLM(d["ba"].to_numpy(float), X, family=fam, var_weights=w).fit(
        cov_type="cluster", cov_kwds={"groups": pd.factorize(d["cluster"])[0]})
    G = d["cluster"].nunique()
    return res, d, G


def table(res, G, names, sample):
    # Suppress the whole model if any contributing group has a small outcome cell.
    if not release_ok(sample):
        names = []
    df_t = G - 1
    rows = []
    for n in names:
        if n in res.params.index:
            b, se = res.params[n], res.bse[n]
            t = stats.t.ppf(0.975, df_t)
            rows.append({"term": n, "estimate": b, "se": se, "ci_low": b - t * se, "ci_high": b + t * se,
                         "p": 2 * stats.t.sf(abs(b / se), df_t)})
    return pd.DataFrame(rows, columns=["term", "estimate", "se", "ci_low", "ci_high", "p"])


def release_ok(sample):
    cells = sample.groupby(["group", "ba"]).size().unstack(fill_value=0)
    cells = cells.reindex(columns=[0.0, 1.0], fill_value=0)
    return not cells.empty and bool((cells >= MIN_CELL).all().all())


def tost(b, se, df_t, bound=SESOI, alpha=0.05):
    p = max(stats.t.sf((b + bound) / se, df_t), stats.t.cdf((b - bound) / se, df_t))
    tc = stats.t.ppf(1 - alpha, df_t)
    lo, hi = b - tc * se, b + tc * se
    verdict = "equivalent" if p < alpha else "equivalence not established"
    return {"p_tost": p, "ci90_low": lo, "ci90_high": hi, "verdict": verdict}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for a in ("w1", "w3", "w4", "weights", "out"):
        ap.add_argument(f"--{a}", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    w1 = read_any(a.w1, ["AID", "BIO_SEX", "H1GI1Y", "IYEAR", "H1GI4", "H1GI6A", "H1GI6B", "H1GI6C", "H1GI6D", "H1GI6E",
                         "PA12", "PA55", "H1ED11", "H1ED12", "H1ED13", "H1ED14"])
    w3 = read_any(a.w3, ["AID", "H3MN1", "H3MN2", "H3MN6", "H3MN8"])
    w4 = read_any(a.w4, ["AID", "H4ED2"])
    wt = read_any(a.weights, ["AID", "CLUSTER2", "GSWGT134"])
    df, wcol = build(w1, w3, w4, wt)
    lines = ["Study A3 (Add Health public-use) - aggregate results only. Do not share with AI tools without Add Health's written OK.",
             f"Plan SHA-256: {hashlib.sha256(PLAN.read_bytes()).hexdigest() if PLAN.exists() else 'plan file not found'}",
             f"Merged respondents (Waves I, III, IV, weights): {len(df)}; weight used: {wcol}", ""]
    observed = df.dropna(subset=["group", "ba", "w"])
    observed = observed[observed["w"] > 0]
    lines += ["Weighted BA rates (groups with small outcome cells omitted):"]
    for group, sample in observed.groupby("group"):
        if release_ok(sample):
            rate = np.average(sample["ba"], weights=sample["w"])
            lines.append(f"{group}: n = {len(sample)}, weighted BA rate = {rate:.3f}")
    lines.append("")
    est = []
    res, d, G = fit(df)
    T = table(res, G, ["onset_lt14", "no_mentor", "onset_18plus"], d); T["analysis"] = "primary (ref: onset 14-17)"; est.append(T)
    primary = T[T["term"] == "onset_lt14"]
    if primary.empty:
        lines.append("PRIMARY: estimate withheld or unavailable.")
    else:
        row = primary.iloc[0]
        eq = tost(row["estimate"], row["se"], G - 1)
        lines += [f"PRIMARY (n = {len(d)}, clusters = {G}): onset <14 minus onset 14-17 = "
                  f"{100*row['estimate']:+.1f} points "
                  f"(95% CI {100*row['ci_low']:+.1f} to {100*row['ci_high']:+.1f}), p = {row['p']:.3f}",
                  f"Equivalence (+/-{100*SESOI:.0f} points): {eq['verdict']} "
                  f"(90% CI {100*eq['ci90_low']:+.1f} to {100*eq['ci90_high']:+.1f}, "
                  f"TOST p = {eq['p_tost']:.3f})", ""]
    res2, d2, G2 = fit(df, ref="no_mentor")
    T = table(res2, G2, ["onset_lt14", "onset_14_17", "onset_18plus"], d2); T["analysis"] = "secondary (ref: no mentor)"; est.append(T)
    for lab, kw in [("S1 unweighted", dict(weighted=False)), ("S2 + Wave I GPA", dict(covs=COVS + ["gpa"])),
                    ("S3 logistic (log odds)", dict(logistic=True))]:
        r, dd, g = fit(df, **kw); T = table(r, g, ["onset_lt14", "no_mentor", "onset_18plus"], dd); T["analysis"] = lab; est.append(T)
    alt = df.copy()
    alt["group"] = np.where(alt["group"].isin(["onset_lt14", "onset_14_17"]),
                            np.where(alt["onset"] < 12, "onset_lt14", "onset_14_17"), alt["group"])
    r, dd, g = fit(alt); T = table(r, g, ["onset_lt14"], dd); T["analysis"] = "S4 cut at 12 (before 12 vs 12-17)"; est.append(T)
    for mt in ("teacher", "kin", "community"):
        sub = df[(df["mtype"] == mt) | (df["group"] == "no_mentor")]
        try:
            r, dd, g = fit(sub, ref="no_mentor")
            T = table(r, g, ["onset_lt14", "onset_14_17", "onset_18plus"], dd); T["analysis"] = f"exploratory: {mt} mentors vs no mentor"; est.append(T)
        except Exception as e:  # small cells
            lines.append(f"exploratory {mt}: not estimable ({e.__class__.__name__})")
    E = pd.concat(est, ignore_index=True)
    E.to_csv(out / "a3_estimates.csv", index=False)
    lines += ["All estimates (linear-probability scale unless logistic; percentage points = 100 x estimate):",
              E[["analysis", "term", "estimate", "ci_low", "ci_high", "p"]].round(4).to_string(index=False)]
    (out / "a3_results.txt").write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"\nWrote {out/'a3_results.txt'} and {out/'a3_estimates.csv'}")


if __name__ == "__main__":
    sys.exit(main())
