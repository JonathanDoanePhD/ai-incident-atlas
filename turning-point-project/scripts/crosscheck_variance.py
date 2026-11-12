"""Independent check of the Taylor-linearised SEs: delete-one-PSU jackknife (JK2 for 2-PSU strata).

For each stratum h and each of its PSUs, the PSU is dropped and the other PSU in h is double-
weighted; the model is refitted with plain weighted least squares (statsmodels WLS, no shared
variance code). JK2 variance: sum_h (1/2) sum_{c in h} (theta_(hc) - theta)^2.
Run on one imputed dataset of the primary (mother) model.
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import statsmodels.api as sm

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
import run_paper1 as rp  # noqa: E402

df, _ = rp.prepare()
sample = df[(df["mother_universe"] == 1) & df["mother_vs"].notna()]
imp = rp.pad(rp.impute(sample, "mother", 1, 99)[0], df)
fit = rp.linear_fit(imp, "mother")
X = fit.params.index
names = list(X)
L = np.zeros(len(names)); L[names.index("s_x_age")] = 4
covs = [c for c in names if c not in ("const", "s", "agec", "s_x_age")]


def theta(w):
    Xm = sm.add_constant(imp[["mother_vs", "agec"]].assign(sxa=imp["mother_vs"] * imp["agec"]).join(imp[covs]))
    b = sm.WLS(imp["hgc"], Xm, weights=w).fit().params.to_numpy()
    return np.array([b[1], b[3] * 4])  # theta(14), delta


base = theta(imp["w"])
reps = []
for h, g in imp.groupby("strata"):
    psus = g["psu"].unique()
    for c in psus:
        w = imp["w"].copy()
        w[(imp["strata"] == h) & (imp["psu"] == c)] = 0
        w[(imp["strata"] == h) & (imp["psu"] != c)] *= 2
        reps.append(theta(w))
reps = np.array(reps)
var_jk = 0.5 * ((reps - base) ** 2).sum(axis=0)
lin = fit.linear_combination(np.vstack([np.eye(len(names))[names.index("s")], L]))
print("estimate (theta14, delta):", np.round(base, 4), "| linearised:", np.round(lin["estimate"].to_numpy(), 4))
print("SE jackknife:  ", np.round(np.sqrt(var_jk), 4))
print("SE linearised: ", np.round(lin["se"].to_numpy(), 4))
print("ratio:", np.round(np.sqrt(var_jk) / lin["se"].to_numpy(), 3))
