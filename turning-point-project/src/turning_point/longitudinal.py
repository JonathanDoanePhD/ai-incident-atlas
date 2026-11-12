"""Longitudinal utilities: reshaping, life-course hypothesis encodings, piecewise time,
and guarded individual change-point estimation.

The life-course 'structured approach' (Mishra et al., 2009; Smith et al., 2015)
compares nested models for a binary exposure measured in several periods E_1..E_k:

* saturated: all 2^k exposure patterns (reference model)
* critical period j: only E_j matters
* accumulation: the count sum_j E_j matters (equal weights)
* sensitive periods: each E_j has its own coefficient (additive, no interactions)
* social mobility (k = 2): only change matters - upward (0 -> 1) and downward (1 -> 0)
  differ from the stable patterns, which share one level

Each restricted model is tested against the saturated model. This maps directly onto
H1-H4 (critical/sensitive periods), H6 (accumulation) and H5 (no single best model).
It requires the *same* exposure measured comparably in each period.
"""
from __future__ import annotations

from itertools import product
from typing import Sequence

import numpy as np
import pandas as pd
from scipy import stats

from .modeling import fit_survey_glm


def wide_to_long(df: pd.DataFrame, id_col: str, stubs: Sequence[str], sep: str = "_w",
                 suffix: str = r"\d+") -> pd.DataFrame:
    """``var_w1, var_w2`` -> rows per (id, wave)."""
    long = pd.wide_to_long(df, stubnames=list(stubs), i=id_col, j="wave", sep=sep, suffix=suffix)
    return long.reset_index().sort_values([id_col, "wave"]).reset_index(drop=True)


def piecewise_time(t: np.ndarray, knots: Sequence[float]) -> np.ndarray:
    """Linear spline basis: t and (t - k)_+ for each knot (slope change at each knot)."""
    t = np.asarray(t, float)
    return np.column_stack([t] + [np.clip(t - k, 0, None) for k in knots])


def lifecourse_designs(E: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Design matrices (without intercept) for the life-course hypotheses."""
    E = E.astype(float)
    if not set(np.unique(E.to_numpy()[~np.isnan(E.to_numpy())])) <= {0.0, 1.0}:
        raise ValueError("exposures must be binary 0/1")
    k = E.shape[1]
    names = list(E.columns)
    designs: dict[str, pd.DataFrame] = {}
    pattern = E.astype(int).astype(str).agg("".join, axis=1)
    sat = pd.get_dummies(pattern, dtype=float)
    ref = "0" * k
    designs["saturated"] = sat.drop(columns=[ref]) if ref in sat else sat.iloc[:, 1:]
    for j, n in enumerate(names):
        designs[f"critical_{n}"] = E[[n]]
    designs["accumulation"] = E.sum(axis=1).to_frame("n_periods_exposed")
    designs["sensitive_periods"] = E[names]
    if k == 2:
        a, b = names
        designs["mobility"] = pd.DataFrame({"upward": ((E[a] == 0) & (E[b] == 1)).astype(float),
                                            "downward": ((E[a] == 1) & (E[b] == 0)).astype(float)})
    designs["null"] = pd.DataFrame(index=E.index)
    return designs


def compare_lifecourse_models(y: pd.Series, E: pd.DataFrame, covariates: pd.DataFrame | None = None,
                              family: str = "gaussian", weights: pd.Series | None = None) -> pd.DataFrame:
    """Fit each life-course model and compare it with the saturated model.

    Uses (weighted) quasi-likelihood deviance F/chi-square tests and AIC from
    statsmodels; with complex survey designs, treat these as descriptive model
    comparisons and report design-based Wald tests for the chosen contrasts.
    """
    import statsmodels.api as sm

    fam = {"gaussian": sm.families.Gaussian(), "binomial": sm.families.Binomial()}[family]
    w = np.ones(len(y)) if weights is None else np.asarray(weights, float)
    base = pd.DataFrame({"const": 1.0}, index=E.index)
    if covariates is not None:
        base = pd.concat([base, covariates.astype(float)], axis=1)
    fits = {}
    for name, D in lifecourse_designs(E).items():
        X = pd.concat([base, D], axis=1)
        fits[name] = (sm.GLM(np.asarray(y, float), X, family=fam, var_weights=w).fit(), X.shape[1])
    sat, p_sat = fits["saturated"]
    rows = []
    for name, (r, p) in fits.items():
        row = {"model": name, "n_params": p, "aic": r.aic, "deviance": r.deviance}
        if name != "saturated":
            ddev = r.deviance - sat.deviance
            dfd = p_sat - p
            if family == "gaussian":
                F = (ddev / dfd) / (sat.deviance / sat.df_resid) if dfd > 0 else np.nan
                row.update({"df_vs_saturated": dfd, "stat": F,
                            "p_vs_saturated": stats.f.sf(F, dfd, sat.df_resid) if dfd > 0 else np.nan})
            else:
                row.update({"df_vs_saturated": dfd, "stat": ddev,
                            "p_vs_saturated": stats.chi2.sf(ddev, dfd) if dfd > 0 else np.nan})
        rows.append(row)
    out = pd.DataFrame(rows).sort_values("aic").reset_index(drop=True)
    out["delta_aic"] = out["aic"] - out["aic"].min()
    return out


def segmented_fit(t: np.ndarray, y: np.ndarray, min_obs: int = 6, min_side: int = 3) -> dict:
    """Single change point in slope for one person's series, by grid search over observed times.

    Refuses to run with fewer than ``min_obs`` observations: with 3-5 survey waves a
    'change point' is not distinguishable from noise (Study C guard). Returns the best
    breakpoint, slopes before/after, and the SSE improvement over a straight line.
    """
    t = np.asarray(t, float)
    y = np.asarray(y, float)
    m = ~(np.isnan(t) | np.isnan(y))
    t, y = t[m], y[m]
    if len(t) < min_obs:
        raise ValueError(f"{len(t)} observations < min_obs={min_obs}: change-point estimation not justified")
    order = np.argsort(t)
    t, y = t[order], y[order]
    X0 = np.column_stack([np.ones_like(t), t])
    sse0 = float(np.sum((y - X0 @ np.linalg.lstsq(X0, y, rcond=None)[0]) ** 2))
    best = None
    for tau in t[min_side - 1: len(t) - min_side + 1]:
        X = np.column_stack([np.ones_like(t), t, np.clip(t - tau, 0, None)])
        b = np.linalg.lstsq(X, y, rcond=None)[0]
        sse = float(np.sum((y - X @ b) ** 2))
        if best is None or sse < best["sse"]:
            best = {"tau": float(tau), "slope_before": float(b[1]), "slope_after": float(b[1] + b[2]), "sse": sse}
    best["sse_linear"] = sse0
    best["r2_gain"] = 1 - best["sse"] / sse0 if sse0 > 0 else 0.0
    return best


def exposure_patterns(E: pd.DataFrame) -> pd.Series:
    """Counts of each exposure pattern (to check that every pattern has support)."""
    k = E.shape[1]
    pats = ["".join(p) for p in product("01", repeat=k)]
    obs = E.astype(int).astype(str).agg("".join, axis=1).value_counts()
    return obs.reindex(pats, fill_value=0)
