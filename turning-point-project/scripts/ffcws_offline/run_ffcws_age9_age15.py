"""Study R2: closeness to mother at age 9 vs 15 -> postsecondary education by 22 (FFCWS).

Run by a human outside AI tools unless ICPSR has given written permission for AI use (see docs/sap_ffcws_age9_age15.md).
Written from the FFCWS metadata only. See docs/human_run_checklist.md.

Usage: python run_ffcws_age9_age15.py --files FILE [FILE ...] --out FOLDER   (files are merged on idnum)
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from functools import reduce
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

PLAN = Path(__file__).resolve().parents[2] / "docs" / "sap_ffcws_age9_age15.md"
SESOI = 0.03
NEED = ["idnum", "k5a2e", "k6c17", "ck7edu", "cm1bsex", "cm1ethrace", "cm1edu", "cm1inpov", "cm1relf", "cm1age", "k7natwt"]


def read_any(path):
    p = Path(path); s = p.suffix.lower()
    if s in (".csv", ".txt", ".tab"):
        d = pd.read_csv(p, sep=None, engine="python")
    else:
        import pyreadstat
        d, _ = {".dta": pyreadstat.read_dta, ".sav": pyreadstat.read_sav, ".sas7bdat": pyreadstat.read_sas7bdat}[s](str(p), apply_value_formats=False)
    d.columns = [str(c).lower() for c in d.columns]
    return d[[c for c in d.columns if c in NEED]]


def prepare(d):
    num = lambda c: pd.to_numeric(d[c], errors="coerce")  # noqa: E731
    o = pd.DataFrame(index=d.index)
    for c, lab in (("k5a2e", "c9"), ("k6c17", "c15")):
        x = num(c).where(lambda s: s.between(1, 4))
        o[lab] = (x == 1).astype(float).where(x.notna())
        o[lab + "_score"] = (5 - x)
    e = num("ck7edu")
    o["ps"] = e.isin([3, 4]).astype(float).where(e.between(1, 4))
    o["coll"] = (e == 4).astype(float).where(e.between(1, 4))
    o["girl"] = (num("cm1bsex") == 2).astype(float).where(num("cm1bsex").isin([1, 2]))
    r = num("cm1ethrace").where(lambda s: s > 0)
    for k in (2, 3, 4):
        o[f"race{k}"] = (r == k).astype(float).where(r.notna())
    o["medu"] = num("cm1edu").where(lambda s: s.between(1, 4))
    o["lpov"] = np.log1p(num("cm1inpov").where(lambda s: s >= 0))
    rel = num("cm1relf").where(lambda s: s > 0)
    o["married"] = (rel == 1).astype(float).where(rel.notna()); o["cohab"] = (rel == 2).astype(float).where(rel.notna())
    o["mage"] = num("cm1age").where(lambda s: s.between(12, 60))
    o["w"] = num("k7natwt")
    return o


COVS = ["girl", "race2", "race3", "race4", "medu", "lpov", "married", "cohab", "mage"]


def fit(o, y="ps", weighted=True, cols=("c9", "c15"), z=False):
    cols = list(cols)
    d = o.dropna(subset=[y, *cols, *COVS] + (["w"] if weighted else []))
    if weighted:
        d = d[d["w"] > 0]
    X = d[cols].astype(float)
    if z:
        X = (X - X.mean()) / X.std()
    X = sm.add_constant(pd.concat([X, d[COVS].astype(float)], axis=1))
    r = sm.WLS(d[y].astype(float), X, weights=d["w"] if weighted else 1.0).fit(cov_type="HC1")
    return r, d


def diff_line(r, a, b, n, label):
    cov = r.cov_params(); dlt = r.params[a] - r.params[b]
    se = np.sqrt(cov.loc[a, a] + cov.loc[b, b] - 2 * cov.loc[a, b])
    p = 2 * stats.norm.sf(abs(dlt / se))
    pt = max(stats.norm.sf((dlt + SESOI) / se), stats.norm.cdf((dlt - SESOI) / se)); lo, hi = dlt - 1.645 * se, dlt + 1.645 * se
    v = "equivalent" if pt < .05 else "non-equivalent" if (lo > SESOI or hi < -SESOI) else "different, undetermined" if (lo > 0 or hi < 0) else "inconclusive"
    return (f"{label}: n = {n}; age 9 {100*r.params[a]:+.1f} pts; age 15 {100*r.params[b]:+.1f}; difference {100*dlt:+.1f} "
            f"(95% CI {100*(dlt-1.96*se):+.1f} to {100*(dlt+1.96*se):+.1f}), p = {p:.3f}; equivalence +/-3: {v}"), dlt, se, p


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--files", nargs="+", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    d = reduce(lambda x, y: x.merge(y, on="idnum", how="outer"), [read_any(f) for f in a.files])
    missing = [c for c in NEED if c not in d.columns]
    if missing:
        sys.exit(f"Variables not found in the files given: {missing}")
    o = prepare(d)
    L = ["Study R2 (FFCWS) - aggregate results only.",
         f"Plan SHA-256: {hashlib.sha256(PLAN.read_bytes()).hexdigest() if PLAN.exists() else 'plan file not found'}", ""]
    rows = []
    for lab, kw in [("PRIMARY any postsecondary", {}), ("S1 unweighted", dict(weighted=False)),
                    ("S2 college or graduate", dict(y="coll")), ("S4 1-4 score (z)", dict(cols=("c9_score", "c15_score"), z=True))]:
        r, dd = fit(o, **kw); c = kw.get("cols", ("c9", "c15"))
        line, dlt, se, p = diff_line(r, c[0], c[1], len(dd), lab); L.append(line)
        rows.append({"analysis": lab, "n": len(dd), "b9": r.params[c[0]], "b15": r.params[c[1]], "diff": dlt, "se": se, "p": p})
    for c in ("c9", "c15"):
        r, dd = fit(o, cols=(c,))
        rows.append({"analysis": f"S3 {c} alone", "n": len(dd), "b_alone": r.params[c], "se_alone": r.bse[c]})
    pd.DataFrame(rows).to_csv(out / "r2_estimates.csv", index=False)
    (out / "r2_results.txt").write_text("\n".join(L)); print("\n".join(L)); print(f"\nWrote {out}")


if __name__ == "__main__":
    sys.exit(main())
