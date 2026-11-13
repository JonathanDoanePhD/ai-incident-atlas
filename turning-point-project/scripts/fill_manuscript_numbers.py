"""Fill {{TOKENS}} in a manuscript source from the stored outputs, so text and results cannot drift apart.
Usage: python scripts/fill_manuscript_numbers.py manuscripts/working_paper_v3.src.md manuscripts/working_paper_v3.filled.md"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
O = ROOT / "outputs"
J = lambda p: json.loads((O / p).read_text())  # noqa: E731
T = lambda rows, q: {r["quantity"]: r for r in rows}[q]  # noqa: E731
P1, B2, P2, AC, AU = J("paper1_results.json"), J("b2_results.json"), J("p2_results.json"), J("p1e_accumulation_results.json"), J("audit/audit_results.json")
ORIG = O / "audit/original_2026-11-12"


def yrs(r, ci=False):
    return f"{r['ci_low']:+.2f} to {r['ci_high']:+.2f}".replace("+", "") if ci else f"{r['estimate']:+.2f}".replace("+-", "−")


def _f1(x):
    return "0.0" if abs(x) < 0.05 else f"{x:+.1f}"


def pts(r, ci=False):
    return f"{_f1(100*r['ci_low'])} to {_f1(100*r['ci_high'])}" if ci else _f1(100 * r["estimate"])


def p_(x):
    return f"{x:.2f}".lstrip("0") if x >= 0.01 else "<.01"


V = {}
for tag, who in (("P1m", "mother"), ("P1f", "father")):
    A = P1["analyses"][who]
    for a in (12, 14, 16):
        V[f"{tag}_t{a}"] = yrs(T(A["primary"], f"theta_{a}"))
    V[f"{tag}_t14_ci"] = yrs(T(A["primary"], "theta_14"), ci=True)
    d = T(A["primary"], "delta_16_vs_12")
    V[f"{tag}_d"], V[f"{tag}_d_ci"], V[f"{tag}_p"] = yrs(d), yrs(d, ci=True), p_(d["p"])
    V[f"{tag}_eq_ci"] = f"{A['equivalence']['ci90_low']:.2f} to {A['equivalence']['ci90_high']:.2f}"
    V[f"{tag}_E"] = f"{A['e_values']['theta_14']['point']:.2f}"
V["P1_holm"] = p_(P1["holm_adjusted_p_delta"]["mother"])
for q, k in (("theta9", "B2_t9"), ("theta11", "B2_t11")):
    V[k] = pts(T(B2["primary"], q))
d = T(B2["primary"], "diff_11_minus_9")
V.update(B2_d=pts(d), B2_d_ci=pts(d, True), B2_p=p_(d["p"]), B2_n=f"{B2['flow']['math_items_both_grades (analytic)']:,}",
         B2_eq_ci=f"{100*B2['equivalence']['ci90_low']:+.2f} to {100*B2['equivalence']['ci90_high']:+.2f}")
pr = P2["praise"]["primary"]
d = T(pr, "delta_C_minus_D")
V.update(P2_b69=pts(T(pr, "beta_6_9")), P2_b1014=pts(T(pr, "beta_10_14")), P2_d=pts(d), P2_d_ci=pts(d, True), P2_p=p_(d["p"]),
         P2_eq_ci=f"{100*P2['praise']['equivalence']['ci90_low']:+.1f} to {100*P2['praise']['equivalence']['ci90_high']:+.1f}",
         P2_n=f"{P2['flow']['praise_both_windows']:,}", P2_mothers=f"{P2['flow']['praise_mothers']:,}")
s = AC["accumulation_slope"]
V.update(AC_slope=f"{s['estimate']:.2f}", AC_slope_ci=f"{s['ci_low']:.2f} to {s['ci_high']:.2f}", AC_wald_p=p_(AC["accumulation_test_wald"]["p"]),
         AC_n=f"{AC['flow']['complete_cases_analysed']:,}")
V["AUD_A_m"] = p_(AU["A_paper1_all_ages_equal_test"]["mother"]["wald_equal_all_ages"]["p"])
V["AUD_A_f"] = p_(AU["A_paper1_all_ages_equal_test"]["father"]["wald_equal_all_ages"]["p"])
one = AU["B_paper2_reliability_check"]["one report per window (first)"]["delta_C_minus_D"]
V["AUD_B_one"], V["AUD_B_one_ci"] = pts(one), pts(one, True)
V["AUD_C_within"] = p_(AU["C_wald_patterns_equal_within_count"]["p"])
stab = [m for m in AU["C_models"] if m["model"].startswith("stability")][0]["coefficients"]["all_four"]
V["AUD_C_all4"] = f"{stab['estimate']:+.2f}, 95% CI {stab['ci_low']:.2f} to {stab['ci_high']:.2f}"
# Monte Carlo difference vs original (v2) outputs on the reported scales
mx = 0.0
if ORIG.exists():
    o1, o2, o3 = (json.loads((ORIG / f).read_text()) for f in ("paper1_results.json", "b2_results.json", "p2_results.json"))
    for who in ("mother", "father"):
        for a, b in zip(o1["analyses"][who]["primary"], P1["analyses"][who]["primary"]):
            mx = max(mx, abs(a["estimate"] - b["estimate"]))
    for a, b in zip(o2["primary"], B2["primary"]):
        mx = max(mx, 100 * abs(a["estimate"] - b["estimate"]))
    for a, b in zip(o3["praise"]["primary"], P2["praise"]["primary"]):
        mx = max(mx, 100 * abs(a["estimate"] - b["estimate"]))
V["MC_maxdiff"] = f"{mx:.2f} (years or percentage points)"
# Study 8 (P3, NLSY79 Children and Young Adults siblings, mother fixed effects)
if (O / "p3_results.json").exists():
    P3 = J("p3_results.json")
    for key, tag in (("primary", "P3"), ("B1_no_fixed_effect_same_sample", "P3B"), ("B1_fixed_effect_on_B1_sample", "P3BF"),
                     ("C1_closeness_fixed_effect", "P3C"), ("S1_no_income_poverty", "P3S1")):
        R3 = P3[key]; e = R3["estimates"]
        V.update({f"{tag}_b69": pts(T(e, "beta_6_9")), f"{tag}_b1014": pts(T(e, "beta_10_14")),
                  f"{tag}_d": pts(T(e, "delta_C_minus_D")), f"{tag}_d_ci": pts(T(e, "delta_C_minus_D"), True),
                  f"{tag}_p": p_(T(e, "delta_C_minus_D")["p"]), f"{tag}_verdict": R3["verdict"]})
        if "equivalence" in R3:
            V[f"{tag}_eq_ci"] = f"{100*R3['equivalence']['ci90_low']:+.1f} to {100*R3['equivalence']['ci90_high']:+.1f}"
            V[f"{tag}_tost"] = p_(R3["equivalence"]["p_tost"])
    V.update(P3_n=f"{P3['primary']['n_children']:,}", P3_fam=f"{P3['primary']['n_families']:,}",
             P3_disc=f"{P3['primary']['identifying']['families_discordant_BA']:,}",
             P3B_n=f"{P3['B1_no_fixed_effect_same_sample']['n_children']:,}",
             P3NC_p=p_(P3["NC_low_birth_weight"]["joint_wald_betaC_betaD"]["p"]))
src, dst = sys.argv[1:3]
text = Path(src).read_text()
missing = sorted(set(re.findall(r"\{\{(\w+)\}\}", text)) - set(V) - {"REFERENCES"})
if missing:
    sys.exit(f"unfilled tokens: {missing}")
for k, v in V.items():
    text = text.replace("{{" + k + "}}", v.replace("+-", "−").replace("-", "−") if k.endswith("_ci") else v.replace("-", "−"))
Path(dst).write_text(text)
print(f"filled {len(V)} tokens -> {dst}")
