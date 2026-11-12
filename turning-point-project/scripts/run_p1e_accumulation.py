"""Exploratory: accumulation vs timing of maternal support, NLSY97 1997-2000 (docs/sap_nlsy97_accumulation.md)."""
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
import run_paper1 as rp  # noqa: E402
from turning_point.longitudinal import compare_lifecourse_models, exposure_patterns  # noqa: E402
from turning_point.modeling import fit_survey_glm  # noqa: E402

warnings.filterwarnings("ignore")
df, _ = rp.prepare()
acc = pd.read_csv(ROOT / "data/raw/nlsy97/accum_extract.csv")
assert (acc["id"].values == pd.read_csv(ROOT / "data/raw/nlsy97/paper1_extract.csv", usecols=["R0000100"])["R0000100"].values).all()
E = pd.DataFrame({"E1997": df["mother_vs"]}, index=df.index)
for y in (1998, 1999, 2000):
    v = acc[f"ysaq032_{y}"]
    E[f"E{y}"] = (v == 1).astype(float).where(v.isin([1, 2, 3])).values
covs = [c for c in rp.COVARIATES]
s = df[(df["age"] <= 14)].join(E)
flow = {"age_12_14_in_1996": int(len(s))}
s = s.dropna(subset=list(E.columns)); flow["complete_exposure_history"] = int(len(s))
s = s.dropna(subset=["hgc", *covs]); flow["complete_cases_analysed"] = int(len(s))
covs = [c for c in covs if s[c].nunique() > 1]
s["count"] = s[list(E.columns)].sum(axis=1)
full = rp.pad(s, df)


def X(frame, cols):
    return pd.concat([pd.Series(1.0, index=frame.index, name="const"), frame[["agec", *cols]], frame[covs].astype(float)], axis=1)


des = dict(weights=full["w"], strata=full["strata"], psu=full["psu"])
f_acc = fit_survey_glm(X(full, ["count"]), full["hgc"].fillna(0), **des)
f_sen = fit_survey_glm(X(full, ["count", "E1998", "E1999", "E2000"]), full["hgc"].fillna(0), **des)
f_all = fit_survey_glm(X(full, ["E1997", "E1998", "E1999", "E2000"]), full["hgc"].fillna(0), **des)
R = {"flow": flow, "patterns": exposure_patterns(s[list(E.columns)].astype(int)).to_dict(),
     "exposure_correlations": s[list(E.columns)].corr().round(3).to_dict(),
     "accumulation_slope": f_acc.summary().loc["count"].to_dict(),
     "accumulation_test_wald": f_sen.wald_test(["E1998", "E1999", "E2000"]),
     "per_round_coefficients": f_all.summary().loc[list(E.columns)].to_dict("index"),
     "lifecourse_aic_unweighted": compare_lifecourse_models(s["hgc"], s[list(E.columns)].astype(int), covariates=s[["agec", *covs]].astype(float)).round(4).to_dict("records")}
(ROOT / "outputs" / "p1e_accumulation_results.json").write_text(json.dumps(R, indent=2, default=float))
print(json.dumps({k: R[k] for k in ("flow", "accumulation_slope", "accumulation_test_wald")}, indent=1, default=float))
for k, v in R["per_round_coefficients"].items():
    print(k, round(v["estimate"], 3), round(v["ci_low"], 3), round(v["ci_high"], 3))
for r in R["lifecourse_aic_unweighted"]:
    print(r["model"], round(r["delta_aic"], 2), r.get("p_vs_saturated"))
print(R["exposure_correlations"]["E1997"])
