"""SYNTHETIC data generators for SOFTWARE TESTING ONLY.

Nothing here resembles, estimates or substitutes for any real survey. Parameters are
arbitrary values chosen to check that estimators recover what was simulated.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

SYNTHETIC_LABEL = "synthetic-test"


def age_moderation_sample(n_strata=20, psu_per_stratum=4, n_per_psu=60, seed=1):
    """Outcome = 0.2 + support * beta(age) + 0.3 * covariate + PSU effect + noise,
    with beta(age) = 0.5 - 0.1 * (age - 12): a known, linearly declining effect."""
    rng = np.random.default_rng(seed)
    rows = []
    for h in range(n_strata):
        for c in range(psu_per_stratum):
            u = rng.normal(0, 0.3)
            age = rng.uniform(12, 17, n_per_psu)
            cov = rng.normal(0, 1, n_per_psu)
            support = rng.binomial(1, 0.5, n_per_psu)
            beta = 0.5 - 0.1 * (age - 12)
            y = 0.2 + support * beta + 0.3 * cov + u + rng.normal(0, 1, n_per_psu)
            w = rng.uniform(0.5, 2.0, n_per_psu)
            rows.append(pd.DataFrame({"y": y, "support": support, "age": age, "cov": cov,
                                      "w": w, "stratum": h, "psu": f"{h}-{c}"}))
    return pd.concat(rows, ignore_index=True)


def lifecourse_sample(model="accumulation", n=6000, seed=2):
    """Three binary exposure periods; outcome generated under a named life-course model."""
    rng = np.random.default_rng(seed)
    E = pd.DataFrame(rng.binomial(1, 0.5, (n, 3)), columns=["E1", "E2", "E3"])
    if model == "accumulation":
        mu = 0.3 * E.sum(axis=1)
    elif model == "critical_E2":
        mu = 0.6 * E["E2"]
    else:
        raise ValueError(model)
    return E, mu + rng.normal(0, 1, n)
