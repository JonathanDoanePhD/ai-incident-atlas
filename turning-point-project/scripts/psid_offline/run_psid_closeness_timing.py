"""Study R1: closeness at ages 8-11 (CDS 2002) vs 12-15 (CDS 2007) -> BA (PSID).

RUN THIS YOURSELF, OUTSIDE ANY AI TOOL. PSID's Conditions of Use prohibit using AI programs or LLMs with PSID data.
Written from PSID documentation only (docs/sap_psid_childhood_replication.md). See docs/human_run_checklist.md.

Usage:
  python run_psid_closeness_timing.py --data FILE --edu ER34548 [ER... ...] --sex SEXVAR --birthyear YEARVAR --out FOLDER
  (education variables: list each wave's "YEARS COMPLETED EDUCATION" with its survey year, e.g. ER34548:2017)
Needs numpy, pandas, statsmodels, scipy (pyreadstat for .dta/.sav/.sas7bdat). Writes aggregate output only.
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

PLAN = Path(__file__).resolve().parents[2] / "docs" / "sap_psid_childhood_replication.md"
SESOI = 0.03
ADULTS = {"mother": ("Q23H5A", "Q33H5A"), "teachers": ("Q23H5G", "Q33H5G"), "other_adults": ("Q23H5H", "Q33H5H")}


def read_any(path):
    p = Path(path); s = p.suffix.lower()
    if s in (".csv", ".txt", ".tab"):
        d = pd.read_csv(p, sep=None, engine="python")
    else:
        import pyreadstat
        d, _ = {".dta": pyreadstat.read_dta, ".sav": pyreadstat.read_sav, ".sas7bdat": pyreadstat.read_sas7bdat}[s](str(p), apply_value_formats=False)
    d.columns = [str(c).upper() for c in d.columns]
    return d


def tost(b, se, df_t, bound=SESOI):
    p = max(stats.t.sf((b + bound) / se, df_t), stats.t.cdf((b - bound) / se, df_t))
    tc = stats.t.ppf(0.95, df_t); lo, hi = b - tc * se, b + tc * se
    v = "equivalent" if p < .05 else "non-equivalent" if (lo > bound or hi < -bound) else "different, undetermined" if (lo > 0 or hi < 0) else "inconclusive"
    return v, lo, hi


def prepare(d, edu, sexvar, byvar):
    out = pd.DataFrame({"fam": d["ER30001"]})
    by = pd.to_numeric(d[byvar], errors="coerce").where(lambda s: s.between(1980, 2010))
    out["by"] = by
    out["age02"], out["age07"] = 2002 - by, 2007 - by
    sex = pd.to_numeric(d[sexvar], errors="coerce")
    out["female"] = (sex == 2).astype(float).where(sex.isin([1, 2]))
    inc = pd.to_numeric(d["ER16462"], errors="coerce")
    out["log_inc"] = np.log1p(inc.clip(lower=0))
    race = pd.to_numeric(d["ER15928"], errors="coerce")
    out["black"] = (race == 2).astype(float).where(race.between(1, 7)); out["other_race"] = race.between(3, 7).astype(float).where(race.between(1, 7))
    best = pd.Series(np.nan, index=d.index)
    for spec in edu:
        var, yr = spec.split(":") if ":" in spec else (spec, None)
        if yr is None:
            sys.exit(f"Give the survey year with each education variable, e.g. {var}:2017")
        v = pd.to_numeric(d[var.upper()], errors="coerce").where(lambda s: s.between(1, 17))
        ok = (int(yr) - by) >= 25
        best = np.fmax(best, v.where(ok))
    out["ba"] = (best >= 16).astype(float).where(best.notna())
    for a, (v02, v07) in ADULTS.items():
        x02 = pd.to_numeric(d[v02], errors="coerce").where(lambda s: s.between(1, 4))
        x07 = pd.to_numeric(d[v07], errors="coerce").where(lambda s: s.between(1, 4))
        out[f"{a}_E"] = (x02 == 4).astype(float).where(x02.notna() & out["age02"].between(8, 11))
        out[f"{a}_A"] = (x07 == 4).astype(float).where(x07.notna() & out["age07"].between(12, 15))
        out[f"{a}_E_score"], out[f"{a}_A_score"] = x02.where(out[f"{a}_E"].notna()), x07.where(out[f"{a}_A"].notna())
    out["w"] = pd.to_numeric(d["CH07PRWT"], errors="coerce")
    return out


COVS = ["female", "by", "log_inc", "black", "other_race"]


def fit(df, a, weighted=True, score=False, alone=None):
    e, ad = (f"{a}_E_score", f"{a}_A_score") if score else (f"{a}_E", f"{a}_A")
    cols = [e, ad] if alone is None else [e if alone == "E" else ad]
    d = df.dropna(subset=["ba", "fam", *cols, *COVS] + (["w"] if weighted else []))
    if weighted:
        d = d[d["w"] > 0]
    X = d[cols].astype(float).copy()
    if score:
        X = (X - X.mean()) / X.std()
    X = sm.add_constant(pd.concat([X, d[COVS].astype(float)], axis=1))
    X = X.loc[:, (X.std() > 0) | (X.columns == "const")]
    r = sm.WLS(d["ba"].astype(float), X, weights=d["w"] if weighted else 1.0).fit(
        cov_type="cluster", cov_kwds={"groups": pd.factorize(d["fam"])[0]})
    return r, d, cols


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True); ap.add_argument("--edu", nargs="+", required=True)
    ap.add_argument("--sex", required=True); ap.add_argument("--birthyear", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    df = prepare(read_any(a.data), a.edu, a.sex.upper(), a.birthyear.upper())
    L = ["Study R1 (PSID) - aggregate results only. Do not share with AI tools (PSID Conditions of Use).",
         f"Plan SHA-256: {hashlib.sha256(PLAN.read_bytes()).hexdigest() if PLAN.exists() else 'plan file not found'}", ""]
    rows, ps = [], {}
    for adult in ADULTS:
        r, d, cols = fit(df, adult)
        G = d["fam"].nunique(); dft = G - 1
        bE, bA = r.params[cols[0]], r.params[cols[1]]
        cov = r.cov_params(); se = np.sqrt(cov.loc[cols[0], cols[0]] + cov.loc[cols[1], cols[1]] - 2 * cov.loc[cols[0], cols[1]])
        diff = bE - bA; p = 2 * stats.t.sf(abs(diff / se), dft); ps[adult] = p
        v, lo, hi = tost(diff, se, dft)
        L.append(f"{adult}: n = {len(d)} (families {G}); ages 8-11 {100*bE:+.1f} pts (SE {100*r.bse[cols[0]]:.1f}); "
                 f"ages 12-15 {100*bA:+.1f} (SE {100*r.bse[cols[1]]:.1f}); difference {100*diff:+.1f} (SE {100*se:.1f}), p = {p:.3f}; "
                 f"equivalence +/-3: {v} (90% CI {100*lo:+.1f} to {100*hi:+.1f})")
        rows.append({"analysis": "primary", "adult": adult, "n": len(d), "b_8_11": bE, "b_12_15": bA, "diff": diff, "se_diff": se, "p": p, "equivalence": v})
        for lab, kw in [("S1 unweighted", dict(weighted=False)), ("S2 1-4 score (z)", dict(score=True))]:
            r2, d2, c2 = fit(df, adult, **kw)
            rows.append({"analysis": lab, "adult": adult, "n": len(d2), "b_8_11": r2.params[c2[0]], "b_12_15": r2.params[c2[1]],
                         "diff": r2.params[c2[0]] - r2.params[c2[1]]})
        for w_ in ("E", "A"):
            r3, d3, c3 = fit(df, adult, alone=w_)
            rows.append({"analysis": f"S3 window {'8-11' if w_ == 'E' else '12-15'} alone", "adult": adult, "n": len(d3), "b_alone": r3.params[c3[0]], "se_alone": r3.bse[c3[0]]})
    order = sorted(ps, key=ps.get); m = len(ps)
    holm = {k: min(1.0, max((m - i) * ps[j] for i, j in enumerate(order[:order.index(k) + 1]))) for k in ps}
    L += ["", "Holm-adjusted p (difference), across the three adults: " + ", ".join(f"{k} {v:.3f}" for k, v in holm.items())]
    if min(r["n"] for r in rows if r["analysis"] == "primary") < 10:
        L.append("WARNING: some analysis has n < 10; do not report it.")
    pd.DataFrame(rows).to_csv(out / "r1_estimates.csv", index=False)
    (out / "r1_results.txt").write_text("\n".join(L)); print("\n".join(L)); print(f"\nWrote {out}")


if __name__ == "__main__":
    sys.exit(main())
