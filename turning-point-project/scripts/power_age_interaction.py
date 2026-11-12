"""Design calculation: minimum detectable difference in the support-outcome association
between two ages, for a linear support x age interaction.

This is a *planning* calculation using assumed inputs (no survey data). Inputs that must be
replaced with verified values from the chosen dataset: analytic n, exposure prevalence,
age range at measurement, design effect, and R^2 of covariates.

    SE(beta_int) ~= sigma * sqrt(DEFF * (1 - R2)) / sqrt(n * p(1-p) * Var(age))
    MDD(a1, a2)  = (z_{1-alpha/2} + z_{power}) * |a2 - a1| * SE(beta_int)

Outcome is in SD units (sigma = 1). The analytic formula is checked by simulation.

Usage: python scripts/power_age_interaction.py [--simulate]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def mdd(n, p, age_range, deff=2.0, r2=0.2, alpha=0.05, power=0.8, contrast=None):
    var_age = age_range**2 / 12  # uniform ages
    se = np.sqrt(deff * (1 - r2)) / np.sqrt(n * p * (1 - p) * var_age)
    contrast = age_range if contrast is None else contrast
    return (stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(power)) * contrast * se


def simulate(n=4000, p=0.5, age_range=5.0, true_diff=0.0, reps=400, seed=7):
    """Empirical SE of the interaction (iid, DEFF = 1, R2 = 0) to check the formula."""
    import statsmodels.api as sm
    rng = np.random.default_rng(seed)
    est = []
    for _ in range(reps):
        age = rng.uniform(0, age_range, n)
        s = rng.binomial(1, p, n)
        y = s * (true_diff / age_range) * age + rng.normal(0, 1, n)
        X = sm.add_constant(np.column_stack([s, age, s * age]))
        est.append(sm.OLS(y, X).fit().params[3])
    return float(np.std(est, ddof=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulate", action="store_true")
    a = ap.parse_args()
    rows = []
    for n in (2000, 4000, 6000, 8000):
        for p in (0.3, 0.5):
            for deff in (1.5, 2.5):
                rows.append({"n": n, "exposure_prevalence": p, "deff": deff, "age_range_years": 5,
                             "mdd_sd_units_full_range": round(float(mdd(n, p, 5, deff)), 3)})
    tab = pd.DataFrame(rows)
    print("PLANNING CALCULATION (assumed inputs, not data):")
    print(tab.to_string(index=False))
    out = Path(__file__).resolve().parents[1] / "outputs" / "design_power_age_interaction.csv"
    out.parent.mkdir(exist_ok=True)
    tab.to_csv(out, index=False)
    if a.simulate:
        emp = simulate()
        theory = 1 / np.sqrt(4000 * 0.25 * 25 / 12)
        print(f"\nSimulation check (n=4000, p=.5, iid): empirical SE {emp:.4f} vs formula {theory:.4f}")


if __name__ == "__main__":
    main()
