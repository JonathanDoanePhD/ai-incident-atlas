"""Machine-readable table of primary estimands, estimates, SEs, CIs and tests -> outputs/primary_estimands.csv.
Reads the stored outputs (paper1_results.json, b2_results.json, p2_results.json, p1e_accumulation_results.json,
audit/audit_results.json). Equivalence statistics are recomputed here from estimate, SE and df (TOST, 90% CI)."""
import csv
import json
from pathlib import Path

from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
O = ROOT / "outputs"
rows = []


def add(study, plan, estimand, role, est, se, df, unit, sesoi=None, note="", p=None, adj_p=None):
    t95, t90 = stats.t.ppf(.975, df), stats.t.ppf(.95, df)
    r = dict(study=study, plan=plan, estimand=estimand, role=role, unit=unit, estimate=est, se=se, df=df,
             ci95_low=est - t95 * se, ci95_high=est + t95 * se, p_two_sided=p if p is not None else 2 * stats.t.sf(abs(est / se), df),
             p_adjusted_holm=adj_p, sesoi=sesoi, ci90_low=None, ci90_high=None, p_tost=None, equivalence_verdict=None, note=note)
    if sesoi is not None:
        r["ci90_low"], r["ci90_high"] = est - t90 * se, est + t90 * se
        r["p_tost"] = max(stats.t.sf((est + sesoi) / se, df), stats.t.cdf((est - sesoi) / se, df))
        r["equivalence_verdict"] = "equivalent within margin" if r["p_tost"] < .05 else "not shown"
    rows.append(r)


P1 = json.loads((O / "paper1_results.json").read_text())
for who in ("mother", "father"):
    A = P1["analyses"][who]; T = {r["quantity"]: r for r in A["primary"]}; sd = A["sd_hgc_weighted_observed"]
    for a in (12, 13, 14, 15, 16):
        r = T[f"theta_{a}"]
        add("P1 NLSY97", "statistical_analysis_plan.md", f"theta({a}): {who} very supportive vs not", "secondary (descriptive)", r["estimate"], r["se"], r["df"], "years of schooling")
    d = T["delta_16_vs_12"]
    add("P1 NLSY97", "statistical_analysis_plan.md", f"Delta = theta(16) - theta(12), {who}", "primary (Q1)" if who == "mother" else "secondary confirmatory (Q2)",
        d["estimate"], d["se"], d["df"], "years of schooling", adj_p=P1["holm_adjusted_p_delta"][who])
    add("P1 NLSY97", "statistical_analysis_plan.md", f"Delta in SD units, {who} (equivalence test)", "primary equivalence (H1b)",
        d["estimate"] / sd, d["se"] / sd, d["df"], "SD of highest grade completed", sesoi=0.20, note=f"SD = {sd:.3f} treated as fixed")
B2 = json.loads((O / "b2_results.json").read_text()); T = {r["quantity"]: r for r in B2["primary"]}
for q, lab, role in (("theta9", "theta9: grade-9 math-teacher support (per SD)", "secondary"), ("theta11", "theta11: grade-11 math-teacher support (per SD)", "secondary"),
                     ("diff_11_minus_9", "theta11 - theta9", "primary")):
    add("B2 HSLS:09", "sap_hsls09_grade9.md", lab, role, T[q]["estimate"], T[q]["se"], T[q]["df"], "probability of BA", sesoi=0.03 if q.startswith("diff") else None)
P2 = json.loads((O / "p2_results.json").read_text())
for key, lab, role in (("praise", "praise", "primary"), ("S1_closeness", "closeness", "secondary exposure")):
    T = {r["quantity"]: r for r in P2[key]["primary"]}
    add("P2 NLSY79 CYA", "sap_nlsy79cya_childhood.md", f"beta(6-9), {lab} (per SD)", "secondary", T["beta_6_9"]["estimate"], T["beta_6_9"]["se"], T["beta_6_9"]["df"], "probability of BA")
    add("P2 NLSY79 CYA", "sap_nlsy79cya_childhood.md", f"beta(10-14), {lab} (per SD)", "secondary", T["beta_10_14"]["estimate"], T["beta_10_14"]["se"], T["beta_10_14"]["df"], "probability of BA")
    add("P2 NLSY79 CYA", "sap_nlsy79cya_childhood.md", f"Delta = beta(6-9) - beta(10-14), {lab}", role, T["delta_C_minus_D"]["estimate"], T["delta_C_minus_D"]["se"],
        T["delta_C_minus_D"]["df"], "probability of BA", sesoi=0.03, adj_p=P2["holm_delta"]["praise" if key == "praise" else "closeness"])
AC = json.loads((O / "p1e_accumulation_results.json").read_text())
s = AC["accumulation_slope"]
add("P1E NLSY97 1997-2000", "sap_nlsy97_accumulation.md", "count of years 'very supportive' (0-4), per year", "primary exploratory", s["estimate"], s["se"], 117.0, "grades completed",
    note="complete cases n = %d; design df 117" % AC["flow"]["complete_cases_analysed"])
w = AC["accumulation_test_wald"]
rows.append(dict(study="P1E NLSY97 1997-2000", plan="sap_nlsy97_accumulation.md", estimand="Wald F: equal coefficients across rounds (accumulation restriction)",
                 role="primary exploratory test", unit="F", estimate=w["F"], df=f"{w['df1']:.0f},{w['df2']:.0f}", p_two_sided=w["p"], note="non-rejection is not evidence of accumulation"))
aud = O / "audit" / "audit_results.json"
if aud.exists():
    AU = json.loads(aud.read_text())
    for who, v in AU["A_paper1_all_ages_equal_test"].items():
        t = v["wald_equal_all_ages"]
        rows.append(dict(study="P1 NLSY97 (post-hoc audit)", plan="none (audit)", estimand=f"Wald F: theta equal at all five ages, {who}", role="post-hoc audit",
                         unit="F", estimate=t["F"], df=f"{t['df1']:.0f},{t['df2']:.0f}", p_two_sided=t["p"], note=f"complete cases n = {v['n_complete']}"))
    t = AU["C_wald_patterns_equal_within_count"]
    rows.append(dict(study="P1E NLSY97 (post-hoc audit)", plan="none (audit)", estimand="Wald F: pattern means equal within count (strict accumulation)", role="post-hoc audit",
                     unit="F", estimate=t["F"], df=f"{t['q']:.0f},{t['df2']:.0f}", p_two_sided=t["p"]))
    for label, v in AU["B_paper2_reliability_check"].items():
        if label == "mean_reports_per_child":
            continue
        d = v["delta_C_minus_D"]
        rows.append(dict(study="P2 NLSY79 CYA (post-hoc audit)", plan="none (audit)", estimand=f"Delta (praise), {label}", role="post-hoc audit", unit="probability of BA",
                         estimate=d["estimate"], se=d["se"], ci95_low=d["ci_low"], ci95_high=d["ci_high"], note=f"complete cases n = {v['n']}"))
fields = ["study", "plan", "estimand", "role", "unit", "estimate", "se", "df", "ci95_low", "ci95_high", "p_two_sided", "p_adjusted_holm",
          "sesoi", "ci90_low", "ci90_high", "p_tost", "equivalence_verdict", "note"]
with open(O / "primary_estimands.csv", "w", newline="") as f:
    w_ = csv.DictWriter(f, fieldnames=fields); w_.writeheader()
    for r in rows:
        w_.writerow({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()})
print(f"wrote outputs/primary_estimands.csv ({len(rows)} rows)")
