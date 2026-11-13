"""STROBE items 14a (participant characteristics), 14b (missing data) and 16a (unadjusted estimates) for Studies 1-4.

Descriptive reporting only: no new hypotheses or tests. Analytic samples are those of the official runs, before imputation.
- Characteristics: weighted (Studies 1, 2, 4: the analysis weight) or unweighted (Study 3, whose primary analysis is unweighted),
  among respondents with the value observed.
- Missing: number missing per variable in the analytic sample (imputed in Studies 1-3; Study 4 is complete-case by design,
  so its counts refer to the 3,870 youths with complete exposure histories).
- Unadjusted: the primary model without covariates, on respondents with the outcome observed (no imputation), same
  weights and variance method as the primary analysis.

Usage: python scripts/strobe_tables.py -> outputs/strobe_tables.json and docs/strobe_tables.md
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
import run_p2_cya as p2  # noqa: E402
import run_paper1 as p1  # noqa: E402
from turning_point.modeling import fit_survey_glm  # noqa: E402


def wmean(x, w=None):
    m = x.notna() if w is None else x.notna() & w.notna()
    if w is None:
        return float(x[m].mean())
    return float(np.average(x[m], weights=w[m]))


def describe(frame, spec, w=None):
    """spec: list of (label, series-or-callable, kind) with kind 'pct' or 'mean'."""
    rows = []
    for label, col, kind in spec:
        x = col(frame) if callable(col) else frame[col]
        v = wmean(x, w)
        rows.append({"variable": label, "value": round(100 * v, 1) if kind == "pct" else round(v, 2), "kind": kind,
                     "n_missing": int(x.isna().sum())})
    return rows


def hh(frame, codes):
    """NLSY97 CV_YTH_REL_HH_CURRENT groups from the hh_2..hh_10 dummies (code 1 = both biological parents)."""
    dummies = frame[[f"hh_{k}" for k in range(2, 11)]]
    one = (dummies.sum(axis=1) == 0).astype(float).where(dummies.notna().all(axis=1))
    parts = [one if k == 1 else frame[f"hh_{k}"] for k in codes]
    return pd.concat(parts, axis=1).sum(axis=1, min_count=1)


P1_SPEC = [
    ("Female", "female", "pct"),
    ("Black, non-Hispanic", "re_black", "pct"),
    ("Hispanic", "re_hispanic", "pct"),
    ("Mixed race, non-Hispanic", "re_mixed", "pct"),
    ("Household poverty ratio, log(1 + ratio)", "pov_log", "mean"),
    ("Urban residence", "urban", "pct"),
    ("Highest grade of residential parents", "parent_ed", "mean"),
    ("No residential parent education reported", "no_res_parent_ed", "pct"),
    ("Lives with both biological parents", lambda f: hh(f, [1]), "pct"),
    ("Two parents, one biological", lambda f: hh(f, [2, 3]), "pct"),
    ("One biological parent only", lambda f: hh(f, [4, 5]), "pct"),
    ("Other arrangement (adoptive, foster, relatives, other)", lambda f: hh(f, [6, 7, 8, 9, 10]), "pct"),
    ("Age at end of 1996 (years)", "age", "mean"),
]


def study1(out):
    df, _ = p1.prepare()
    out["study1"] = {}
    for who in ("mother", "father"):
        s = df[(df[f"{who}_universe"] == 1) & df[f"{who}_vs"].notna()]
        spec = [(f"Very supportive {who} (exposure)", f"{who}_vs", "pct"), *P1_SPEC,
                ("Highest grade completed (outcome, observed)", "hgc", "mean")]
        obs = s[s["hgc"].notna()][["hgc", f"{who}_vs", "agec", "w", "strata", "psu"]]
        fit = p1.linear_fit(p1.pad(obs, df), who)  # no covariate columns present -> unadjusted
        assert list(fit.params.index) == ["const", "s", "agec", "s_x_age"]
        out["study1"][who] = {"n": int(len(s)), "weighted": "SAMPLING_WEIGHT_CC (round 1)", "characteristics": describe(s, spec, s["w"]),
                              "unadjusted": {"n": int(len(obs)), "est": p1.single_contrasts(fit).to_dict("records")}}


def study4(out):
    df, _ = p1.prepare()
    acc = pd.read_csv(ROOT / "data/raw/nlsy97/accum_extract.csv")
    E = pd.DataFrame({"E1997": df["mother_vs"]}, index=df.index)
    for y in (1998, 1999, 2000):
        v = acc[f"ysaq032_{y}"]
        E[f"E{y}"] = (v == 1).astype(float).where(v.isin([1, 2, 3])).values
    s = df[df["age"] <= 14].join(E).dropna(subset=list(E.columns))  # complete exposure histories (3,870)
    s["count"] = s[list(E.columns)].sum(axis=1)
    spec = [("Years rated very supportive, 1997-2000 (0-4)", "count", "mean"), *P1_SPEC,
            ("Highest grade completed (outcome, observed)", "hgc", "mean")]
    cc = s.dropna(subset=["hgc", *p1.COVARIATES])
    full = p1.pad(cc[["hgc", "count", "agec", "w", "strata", "psu"]], df)
    X = pd.concat([pd.Series(1.0, index=full.index, name="const"), full[["agec", "count"]]], axis=1)
    f = fit_survey_glm(X, full["hgc"].fillna(0), weights=full["w"], strata=full["strata"], psu=full["psu"])
    sm = f.summary().loc["count"].to_dict()
    out["study4"] = {"n_exposure_history": int(len(s)), "n_analyzed": int(len(cc)), "weighted": "SAMPLING_WEIGHT_CC (round 1)",
                     "characteristics_analyzed": describe(cc, spec, cc["w"]),
                     "missing_among_exposure_history": {lab: int((c(s) if callable(c) else s[c]).isna().sum()) for lab, c, _ in spec},
                     "unadjusted": {"n": int(len(cc)), "count_slope": sm, "df": f.df_resid}}


def study2(out):
    df = b2.prepare()
    s = df[(df.w > 0)]
    s = s[s["sup9"].notna() & s["sup11"].notna()].copy()
    race_other = s["other_race"]
    spec = [("Grade-9 math-teacher support (1-4)", "sup9", "mean"), ("Grade-11 math-teacher support (1-4)", "sup11", "mean"),
            ("Female", "female", "pct"), ("Black", "black", "pct"), ("Hispanic", "hispanic", "pct"), ("Asian", "asian", "pct"),
            ("Other or multiracial", lambda f: race_other, "pct"), ("Socioeconomic status composite (X1SES)", "ses", "mean"),
            ("Two-parent household", "two_parent", "pct"), ("Grade-9 math score (theta)", "math9", "mean"),
            ("School locale: city", "loc_city", "pct"), ("Suburb", "loc_suburb", "pct"), ("Town", "loc_town", "pct"),
            ("Bachelor's degree or higher (outcome, observed)", "ba", "pct")]
    obs = s.dropna(subset=["ba"])
    un = b2.pool([b2.brr(obs, covs=[])])
    out["study2"] = {"n": int(len(s)), "weighted": "W2W1STU (grade 9-11 longitudinal)", "characteristics": describe(s, spec, s["w"]),
                     "unadjusted": {"n": int(len(obs)), "est": un}}


def study3(out):
    d = p2.prepare()
    s = d[d.cyrb.between(1979, 1995)]
    sp = s[(s.n_praiseC > 0) & (s.n_praiseD > 0)].copy()
    spec = [("Praise reports at 6-9 (number)", "n_praiseC", "mean"), ("Praise reports at 10-14 (number)", "n_praiseD", "mean"),
            ("Female", "female", "pct"), ("Hispanic", "hisp", "pct"), ("Black", "black", "pct"),
            ("Born 1984-87", "by_1984", "pct"), ("Born 1988-91", "by_1988", "pct"), ("Born 1992-95", "by_1992", "pct"),
            ("Second-born", "order2", "pct"), ("Third-born or later", "order3p", "pct"), ("Mother's age at birth", "mage", "mean"),
            ("Mother's highest grade (1990)", "mom_hgc", "mean"), ("Mother's AFQT percentile (/100)", "afqt", "mean"),
            ("Share of childhood years in poverty", "pov_share", "mean"), ("Mean log(1 + family income), ages 0-14", "log_inc", "mean"),
            ("Bachelor's degree or higher (outcome, observed)", "ba", "pct")]
    a, b = "praiseC", "praiseD"
    sp[a] = p2.zstd(sp[a]); sp[b] = p2.zstd(sp[b])  # standardized on the analytic sample, as in the primary analysis
    obs = sp.dropna(subset=["ba"])
    un = p2.pool([p2.contrasts(p2.fit(obs, a, b, covs=[]), a, b)], ("beta_6_9", "beta_10_14", "delta_C_minus_D"))
    out["study3"] = {"n": int(len(sp)), "mothers": int(sp.mid.nunique()), "weighted": "unweighted (as the primary analysis)",
                     "characteristics": describe(sp, spec), "unadjusted": {"n": int(len(obs)), "est": un}}


def fmt_ci(r, scale=1.0, nd=2):
    f = lambda x: f"{x:.{nd}f}".replace(f"-{0:.{nd}f}", f"{0:.{nd}f}")  # no negative zero
    return f"{f(scale * r['estimate'])} ({f(scale * r['ci_low'])}, {f(scale * r['ci_high'])})"


def markdown(out):
    adj = {k: json.loads((ROOT / "outputs" / f).read_text()) for k, f in
           (("p1", "paper1_results.json"), ("b2", "b2_results.json"), ("p2", "p2_results.json"), ("p1e", "p1e_accumulation_results.json"))}
    L = ["# STROBE tables: participant characteristics, missing data, unadjusted estimates (Studies 1-4)", "",
         "Generated by `scripts/strobe_tables.py` (descriptive reporting for STROBE items 14a, 14b, 16a; no new tests). Analytic samples",
         "are those of the official runs, before imputation. Percentages and means are weighted with the analysis weight for Studies 1, 2",
         "and 4, and unweighted for Study 3 (as its primary analysis). \"Missing\" = number of analyzed respondents without the value",
         "(imputed in Studies 1-3).", ""]
    s1 = out["study1"]
    L += ["## Study 1 (NLSY97)", "", "| Characteristic | Mother sample | Missing | Father sample | Missing |", "|---|---|---|---|---|"]
    for rm, rf in zip(s1["mother"]["characteristics"], s1["father"]["characteristics"]):
        lab = rm["variable"].replace("Very supportive mother", "Very supportive parent")
        u = "%" if rm["kind"] == "pct" else ""
        L.append(f"| {lab} | {rm['value']}{u} | {rm['n_missing']} | {rf['value']}{u} | {rf['n_missing']} |")
    L.append(f"| n analyzed | {s1['mother']['n']:,} | | {s1['father']['n']:,} | |")
    L += ["", "| Years of schooling (95% CI) | Unadjusted, outcome observed | Adjusted, primary (MI) |", "|---|---|---|"]
    for who in ("mother", "father"):
        un = {r["quantity"]: r for r in s1[who]["unadjusted"]["est"]}
        ad = {r["quantity"]: r for r in adj["p1"]["analyses"][who]["primary"]}
        for q, lab in (("theta_14", "association at 14"), ("delta_16_vs_12", "difference 16 vs 12")):
            L.append(f"| {who.capitalize()}, {lab} | {fmt_ci(un[q])} (n = {s1[who]['unadjusted']['n']:,}) | {fmt_ci(ad[q])} |")
    s2 = out["study2"]
    L += ["", "## Study 2 (HSLS:09)", "", f"n analyzed = {s2['n']:,}.", "", "| Characteristic | Value | Missing |", "|---|---|---|"]
    for r in s2["characteristics"]:
        L.append(f"| {r['variable']} | {r['value']}{'%' if r['kind'] == 'pct' else ''} | {r['n_missing']} |")
    L += ["", "| Percentage points per SD (95% CI) | Unadjusted, outcome observed | Adjusted, primary (MI) |", "|---|---|---|"]
    for i, lab in enumerate(("grade 9", "grade 11", "difference 11 - 9")):
        L.append(f"| {lab} | {fmt_ci(s2['unadjusted']['est'][i], 100, 1)} (n = {s2['unadjusted']['n']:,}) | {fmt_ci(adj['b2']['primary'][i], 100, 1)} |")
    s3 = out["study3"]
    L += ["", "## Study 3 (NLSY79 Children and Young Adults, praise)", "", f"n analyzed = {s3['n']:,} children of {s3['mothers']:,} mothers.", "",
          "| Characteristic | Value | Missing |", "|---|---|---|"]
    for r in s3["characteristics"]:
        L.append(f"| {r['variable']} | {r['value']}{'%' if r['kind'] == 'pct' else ''} | {r['n_missing']} |")
    L += ["", "| Percentage points per SD (95% CI) | Unadjusted, outcome observed | Adjusted, primary (MI) |", "|---|---|---|"]
    for i, lab in enumerate(("ages 6-9", "ages 10-14", "difference (6-9) - (10-14)")):
        L.append(f"| {lab} | {fmt_ci(s3['unadjusted']['est'][i], 100, 1)} (n = {s3['unadjusted']['n']:,}) | {fmt_ci(adj['p2']['praise']['primary'][i], 100, 1)} |")
    s4 = out["study4"]
    L += ["", "## Study 4 (NLSY97 accumulation, exploratory)", "",
          f"n with complete exposure histories = {s4['n_exposure_history']:,}; analyzed (complete cases) = {s4['n_analyzed']:,}.", "",
          "| Characteristic (analyzed) | Value | Missing among complete exposure histories |", "|---|---|---|"]
    for r in s4["characteristics_analyzed"]:
        L.append(f"| {r['variable']} | {r['value']}{'%' if r['kind'] == 'pct' else ''} | {s4['missing_among_exposure_history'][r['variable']]} |")
    u = s4["unadjusted"]["count_slope"]
    a = adj["p1e"]["accumulation_slope"]
    L += ["", "| Grades per year rated very supportive (95% CI) | Unadjusted | Adjusted |", "|---|---|---|",
          f"| Accumulation slope | {u['estimate']:.2f} ({u['ci_low']:.2f}, {u['ci_high']:.2f}) | {a['estimate']:.2f} ({a['ci_low']:.2f}, {a['ci_high']:.2f}) |", ""]
    L += ["Unadjusted estimates use respondents with the outcome observed; adjusted primary estimates in Studies 1-3 use multiple",
          "imputation, so the samples differ slightly. Larger unadjusted than adjusted estimates indicate confounding by background",
          "characteristics, as expected."]
    return "\n".join(L) + "\n"


def main():
    out = {}
    for f in (study1, study2, study3, study4):
        print("running", f.__name__, flush=True)
        f(out)
    (ROOT / "outputs" / "strobe_tables.json").write_text(json.dumps(out, indent=2, default=float))
    (ROOT / "docs" / "strobe_tables.md").write_text(markdown(out))
    print("wrote outputs/strobe_tables.json and docs/strobe_tables.md")


if __name__ == "__main__":
    main()
