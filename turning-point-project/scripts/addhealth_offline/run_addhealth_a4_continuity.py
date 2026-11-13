"""Study A4: onset, continuity and closeness of natural mentors -> bachelor's degree by Wave IV (Add Health public-use).

RUN THIS YOURSELF, OUTSIDE ANY AI TOOL. Add Health's Conditions of Use prohibit using AI tools to manage, process
or analyze Add Health data. This script was written from public codebooks only (docs/sap_addhealth_a4_continuity.md).
Follow docs/addhealth_human_analyst_checklist.md, as for A3.

Usage:
  python run_addhealth_a4_continuity.py --w1 FILE --w3 FILE --w4 FILE --weights FILE --out FOLDER

Needs: numpy, pandas, scipy, statsmodels (and pyreadstat for .dta/.sas7bdat/.sav). Self-contained: no project imports.
Writes aggregate tables only (cells < 10 suppressed) to FOLDER/a4_results.txt and FOLDER/a4_estimates.csv.
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

PLAN = Path(__file__).resolve().parent.parent.parent / "docs" / "sap_addhealth_a4_continuity.md"
MIN_CELL = 10
SESOI = 0.05
COVS = ["female", "age_w1", "hispanic", "black", "amind", "asian", "other_race", "parent_ed", "log_inc", "inc_missing"]


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
    return df[[c for c in cols if c in df.columns]].copy()


def clean(s: pd.Series, valid) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    return s.where(s.isin(valid)) if not callable(valid) else s.where(valid(s))


def build(w1, w3, w4, wt):
    d = w1.merge(w3, on="AID", how="inner").merge(w4, on="AID", how="inner").merge(wt, on="AID", how="inner")
    if "GSWGT134" not in d:
        raise ValueError("Use the Wave IV public-use weights file containing GSWGT134.")
    out = pd.DataFrame({"AID": d["AID"]})
    mn1 = clean(d["H3MN1"], [0, 1])
    onset = clean(d["H3MN6"], lambda s: s.between(0, 25))
    living = clean(d["H3MN3"], [0, 1])
    still = clean(d["H3MN7"], [0, 1])
    years = clean(d["H3MN8"], lambda s: s.between(0, 54))
    ended = pd.Series(np.nan, index=d.index)
    ended[(living == 1) & (still == 1)] = 0.0
    ended[(living == 0) | ((living == 1) & (still == 0))] = 1.0
    end_age = (onset + years).where(ended == 1)
    out["mentored_pre18"] = ((mn1 == 1) & onset.between(0, 17)).astype(float)
    out["onset"] = onset
    out["onset_lt14"] = (onset < 14).astype(float).where(onset.notna())
    out["ended"] = ended
    out["end_age"] = end_age
    e18 = pd.Series(np.nan, index=d.index)
    e18[ended == 0] = 0.0
    e18[(ended == 1) & (end_age >= 18)] = 0.0
    e18[(ended == 1) & (end_age < 18)] = 1.0
    out["ended_before_18"] = e18
    out["years"] = years
    out["still_important"] = still.where(living == 1)
    cl = clean(d["H3MN11"], [0, 1, 2, 3, 4])
    out["close"] = (cl >= 3).astype(float).where(cl.notna() & (living == 1))
    t = clean(d["H3MN2"], lambda s: s.between(1, 21))
    out["teacher"] = (t == 11).astype(float).where(t.notna())
    out["community"] = t.between(12, 21).astype(float).where(t.notna())
    ed = clean(d["H4ED2"], lambda s: s.between(1, 13))
    out["ba"] = (ed >= 7).astype(float).where(ed.notna())
    sex = clean(d["BIO_SEX"], [1, 2])
    out["female"] = (sex == 2).astype(float).where(sex.notna())
    by = clean(d["H1GI1Y"], lambda s: s.between(70, 90))
    iy = clean(d["IYEAR"], lambda s: s.between(94, 96))
    out["age_w1"] = iy - by
    iy3 = clean(d["IYEAR3"], lambda s: s.between(2000, 2003)) if "IYEAR3" in d else pd.Series(np.nan, index=d.index)
    out["age_w3"] = iy3 - (1900 + by)
    out["hispanic"] = clean(d["H1GI4"], [0, 1])
    for k, lab in zip("ABCDE", ["white", "black", "amind", "asian", "other_race"]):
        out[lab] = clean(d[f"H1GI6{k}"], [0, 1])
    pe = clean(d["PA12"], lambda s: s.between(1, 10))
    out["parent_ed"] = pe.where(pe != 10, 0)
    inc = clean(d["PA55"], lambda s: s.between(0, 9995))
    out["inc_missing"] = inc.isna().astype(float)
    out["log_inc"] = np.log1p(inc.fillna(inc.median()))
    out["w"] = pd.to_numeric(d["GSWGT134"], errors="coerce")
    out["cluster"] = d["CLUSTER2"]
    return out


def fit(df, terms, covs=COVS):
    d = df.dropna(subset=["ba", "cluster", "w", *terms, *covs])
    d = d[d["w"] > 0]
    X = pd.concat([pd.Series(1.0, index=d.index, name="const"), d[terms + covs].astype(float)], axis=1)
    X = X.loc[:, X.std() > 0].assign(const=1.0)
    res = sm.GLM(d["ba"].to_numpy(float), X, family=sm.families.Gaussian(), var_weights=d["w"].to_numpy(float)).fit(
        cov_type="cluster", cov_kwds={"groups": pd.factorize(d["cluster"])[0]})
    return res, d, d["cluster"].nunique()


def release_ok(sample, var):
    cells = sample.groupby([var, "ba"]).size().unstack(fill_value=0).reindex(columns=[0.0, 1.0], fill_value=0)
    return not cells.empty and len(cells) >= 2 and bool((cells >= MIN_CELL).all().all())


def row(res, G, term, sample, var):
    if not release_ok(sample, var) or term not in res.params.index:
        return None
    b, se = float(res.params[term]), float(res.bse[term])
    t = stats.t.ppf(0.975, G - 1)
    return {"term": term, "estimate": b, "se": se, "ci_low": b - t * se, "ci_high": b + t * se,
            "p": float(2 * stats.t.sf(abs(b / se), G - 1)), "n": len(sample), "clusters": G}


def tost(b, se, df_t, bound=SESOI, alpha=0.05):
    p = max(stats.t.sf((b + bound) / se, df_t), stats.t.cdf((b - bound) / se, df_t))
    tc = stats.t.ppf(1 - alpha, df_t)
    return {"p_tost": p, "ci90_low": b - tc * se, "ci90_high": b + tc * se,
            "verdict": "equivalent" if p < alpha else "equivalence not established"}


def describe(r, label):
    if r is None:
        return [f"{label}: withheld (small cells) or not estimable."]
    eq = tost(r["estimate"], r["se"], r["clusters"] - 1)
    sig = "significant" if r["p"] < 0.05 else "not significant"
    return [f"{label} (n = {r['n']}, clusters = {r['clusters']}): {100*r['estimate']:+.1f} points "
            f"(95% CI {100*r['ci_low']:+.1f} to {100*r['ci_high']:+.1f}), p = {r['p']:.3f} [{sig} at .05]",
            f"  Equivalence (+/-{100*SESOI:.0f} points): {eq['verdict']} (90% CI {100*eq['ci90_low']:+.1f} to "
            f"{100*eq['ci90_high']:+.1f}, TOST p = {eq['p_tost']:.3f})"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for a in ("w1", "w3", "w4", "weights", "out"):
        ap.add_argument(f"--{a}", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    w1 = read_any(a.w1, ["AID", "BIO_SEX", "H1GI1Y", "IYEAR", "H1GI4", "H1GI6A", "H1GI6B", "H1GI6C", "H1GI6D", "H1GI6E", "PA12", "PA55"])
    w3 = read_any(a.w3, ["AID", "IYEAR3", "H3MN1", "H3MN2", "H3MN3", "H3MN6", "H3MN7", "H3MN8", "H3MN11"])
    w4 = read_any(a.w4, ["AID", "H4ED2"])
    wt = read_any(a.weights, ["AID", "CLUSTER2", "GSWGT134"])
    df = build(w1, w3, w4, wt)
    m = df[(df["mentored_pre18"] == 1) & (df["w"] > 0)]
    lines = ["Study A4 (Add Health public-use) - aggregate results only. Share only your interpretation (D-037).",
             f"Plan SHA-256: {hashlib.sha256(PLAN.read_bytes()).hexdigest() if PLAN.exists() else 'plan file not found'}",
             f"Script SHA-256: {hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}",
             f"Merged respondents: {len(df)}; mentored with onset 0-17 and weight > 0: {len(m)}", ""]
    # descriptive checks
    si = m.dropna(subset=["still_important"])
    if len(si) >= MIN_CELL:
        lines.append(f"Share of living mentors still important (weighted): {np.average(si['still_important'], weights=si['w']):.3f}")
    ok = m[(m["ended"] == 0)].dropna(subset=["years", "age_w3", "onset"])
    if len(ok) >= MIN_CELL:
        r = np.corrcoef(ok["years"], ok["age_w3"] - ok["onset"])[0, 1]
        lines.append(f"Ongoing relationships: correlation of years important with (age at Wave III - onset) = {r:.3f} (n = {len(ok)})")
    en = m[m["ended"] == 1].dropna(subset=["end_age"])
    if len(en) >= MIN_CELL:
        q = en["end_age"].quantile([0.1, 0.25, 0.5, 0.75, 0.9]).round(1).to_dict()
        lines.append(f"Ended relationships: n = {len(en)}; end-age quantiles (unweighted) {q}")
        lines.append(f"Ended before 18: n = {int((m['ended_before_18'] == 1).sum())}")
    lines.append("")
    est = []
    res, d, G = fit(m, ["ended_before_18", "onset_lt14", "teacher", "community"])
    prim = row(res, G, "ended_before_18", d, "ended_before_18")
    lines += ["PRIMARY Q-A4a: ended before 18 minus continued to 18+"] + describe(prim, "  estimate") + [""]
    onset_adj = row(res, G, "onset_lt14", d, "onset_lt14")
    lines += ["SECONDARY Q-A4b: onset <14 minus 14-17, adjusted for continuity and type"] + describe(onset_adj, "  estimate") + [""]
    rc, dc, Gc = fit(m[m["close"].notna()], ["close", "ended_before_18", "onset_lt14", "teacher", "community"])
    close = row(rc, Gc, "close", dc, "close")
    lines += ["SECONDARY Q-A4c: quite/very close minus less close (living mentors; closeness reported at Wave III)"] + describe(close, "  estimate")
    for lab, r in (("Q-A4a ended_before_18", prim), ("Q-A4b onset_lt14 (adjusted)", onset_adj), ("Q-A4c close", close)):
        if r is not None:
            est.append(dict(analysis=lab, **r))
    pd.DataFrame(est).to_csv(out / "a4_estimates.csv", index=False)
    (out / "a4_results.txt").write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"\nWrote {out/'a4_results.txt'} and {out/'a4_estimates.csv'}")


if __name__ == "__main__":
    sys.exit(main())
