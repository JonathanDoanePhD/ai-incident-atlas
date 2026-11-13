"""Turn outputs/paper1_results.json into outputs/paper1_effect_by_age.html and a findings
block for the website (website/data/findings.js). Aggregate estimates only."""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from turning_point.visualization import effect_by_age_figure  # noqa: E402

R = json.loads((ROOT / "outputs" / "paper1_results.json").read_text())


def tab(rows):
    return pd.DataFrame(rows).set_index("quantity")


def main():
    site = {"design_df": R["design_df"], "m": R["m"], "sesoi_sd": R["sesoi_sd"], "holm": R["holm_adjusted_p_delta"], "parents": {}}
    for who in ("mother", "father"):
        A = R["analyses"][who]
        prim = tab(A["primary"])
        eff = pd.DataFrame({"age": [12, 13, 14, 15, 16]})
        for k in ("estimate", "ci_low", "ci_high"):
            eff[k] = [prim.loc[f"theta_{a}", k] for a in eff["age"]]
        fig = effect_by_age_figure(eff, provenance="validated", ylabel="Difference in highest grade completed (years)",
                                   title=f"'Very supportive' {who} in 1997 and highest grade completed, by age at report")
        fig.write_html(ROOT / "outputs" / f"paper1_effect_by_age_{who}.html", include_plotlyjs="cdn")
        cat = tab(A["sensitivity"]["S1_categorical_age"])
        sens = {}
        for key, val in A["sensitivity"].items():
            if key.startswith("S1"):
                continue
            rows = val["est"] if isinstance(val, dict) else val
            t = tab(rows)
            sens[key] = {q: [round(t.loc[q, "estimate"], 3), round(t.loc[q, "ci_low"], 3), round(t.loc[q, "ci_high"], 3)]
                         for q in ("theta_14", "delta_16_vs_12")}
        s6b = ROOT / "outputs" / "paper1_s6b_results.json"
        if s6b.exists():
            t = tab(json.loads(s6b.read_text())[who]["estimates"])
            sens["S6b_custom_longitudinal_weight_complete_case"] = {q: [round(t.loc[q, "estimate"], 3), round(t.loc[q, "ci_low"], 3), round(t.loc[q, "ci_high"], 3)]
                                                                     for q in ("theta_14", "delta_16_vs_12")}
        site["parents"][who] = {
            "flow": A["flow"], "sd": A["sd_hgc_weighted_observed"], "descriptives": A["descriptives_by_age"],
            "theta": [{"age": a, "est": prim.loc[f"theta_{a}", "estimate"], "lo": prim.loc[f"theta_{a}", "ci_low"],
                       "hi": prim.loc[f"theta_{a}", "ci_high"]} for a in range(12, 17)],
            "theta_categorical": [{"age": a, "est": cat.loc[f"theta_{a}", "estimate"], "lo": cat.loc[f"theta_{a}", "ci_low"],
                                   "hi": cat.loc[f"theta_{a}", "ci_high"]} for a in range(12, 17)],
            "delta": {k: prim.loc["delta_16_vs_12", k] for k in ("estimate", "ci_low", "ci_high", "p", "fmi")},
            "delta_sd": A["delta_sd"], "equivalence": A["equivalence"], "e_values": A["e_values"], "sensitivity": sens,
            "exploratory": {k: {q: [round(r["estimate"], 3)] + ([round(r["ci_low"], 3), round(r["ci_high"], 3)] if "ci_low" in r else [round(r["se"], 3)])
                                for q, r in tab(v).iterrows() if q in ("theta_14", "delta_16_vs_12")} for k, v in A["exploratory"].items()},
        }
    b2 = ROOT / "outputs" / "b2_results.json"
    if b2.exists():
        B = json.loads(b2.read_text())
        P = {r["quantity"]: r for r in B["primary"]}
        site["b2"] = {"flow": B["flow"], "theta9": P["theta9"], "theta11": P["theta11"], "diff": P["diff_11_minus_9"],
                      "equivalence": B["equivalence"], "talk9": B["E3_talk_to_adult_grade9"][0], "sesoi": B["sesoi"], "m": B["m"],
                      "sens": {k: {r["quantity"]: [r["estimate"], r["ci_low"], r["ci_high"]] for r in (B[k]["est"] if isinstance(B[k], dict) else B[k])}
                               for k in ("S1_positive_items_only", "S2_complete_case", "S4_minimal_covariates")}}
    p2 = ROOT / "outputs" / "p2_results.json"
    if p2.exists():
        Q = json.loads(p2.read_text())
        T = lambda rows: {r["quantity"]: r for r in rows}  # noqa: E731
        site["p2"] = {"flow": Q["flow"], "praise": T(Q["praise"]["primary"]), "close": T(Q["S1_closeness"]["primary"]),
                      "equivalence": Q["praise"]["equivalence"], "sesoi": Q["sesoi"], "m": Q["m"]}
    p3 = ROOT / "outputs" / "p3_results.json"
    if p3.exists():
        Z = json.loads(p3.read_text())
        T3 = lambda rows: {r["quantity"]: r for r in rows}  # noqa: E731
        site["p3"] = {k: {"est": T3(Z[k]["estimates"]), "n": Z[k]["n_children"], "fam": Z[k]["n_families"], "verdict": Z[k].get("verdict"),
                          "eq": Z[k].get("equivalence")} for k in ("primary", "B1_no_fixed_effect_same_sample", "B1_fixed_effect_on_B1_sample",
                                                                    "C1_closeness_fixed_effect")}
        site["p3"]["nc_p"] = Z["NC_low_birth_weight"]["joint_wald_betaC_betaD"]["p"]
        site["p3"]["disc"] = Z["primary"]["identifying"]["families_discordant_BA"]
        site["p3"]["sesoi"] = Z["sesoi"]
    p1e = ROOT / "outputs" / "p1e_accumulation_results.json"
    if p1e.exists():
        A = json.loads(p1e.read_text())
        site["accum"] = {"n": A["flow"]["complete_cases_analysed"], "slope": A["accumulation_slope"], "wald": A["accumulation_test_wald"]}
    (ROOT / "website" / "data" / "findings.js").write_text(
        "/* generated by scripts/report_paper1.py - aggregate estimates only */\nwindow.FINDINGS = " + json.dumps(site, indent=1, default=float) + ";\n")
    print(json.dumps({w: {"delta": site["parents"][w]["delta"], "equiv": site["parents"][w]["equivalence"]["verdict"]} for w in site["parents"]}, indent=1, default=float))


if __name__ == "__main__":
    main()
