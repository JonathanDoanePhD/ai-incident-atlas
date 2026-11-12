"""Out-of-sample evaluation for Study A (prediction, not causation).

Folds are grouped by PSU (or household) so that respondents sharing a cluster never
straddle train and test sets. Metrics are survey-weighted. Subgroup metrics are
returned only in aggregate and only for cells with at least ``min_n`` respondents;
the purpose is fairness auditing, never labelling individual young people.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import brier_score_loss, mean_squared_error, roc_auc_score
from sklearn.model_selection import GroupKFold, KFold


def calibration_slope_intercept(y: np.ndarray, p: np.ndarray, w: np.ndarray | None = None) -> tuple[float, float]:
    import statsmodels.api as sm
    p = np.clip(p, 1e-6, 1 - 1e-6)
    lp = np.log(p / (1 - p))
    w = np.ones_like(y, dtype=float) if w is None else w
    slope = sm.GLM(y, sm.add_constant(lp), family=sm.families.Binomial(), var_weights=w).fit().params[1]
    intercept = sm.GLM(y, np.ones_like(lp), family=sm.families.Binomial(), offset=lp, var_weights=w).fit().params[0]
    return float(slope), float(intercept)


def cross_validate(model, X: pd.DataFrame, y: pd.Series, *, weights: pd.Series | None = None,
                   groups: pd.Series | None = None, task: str = "binary", n_splits: int = 5,
                   seed: int = 20261112) -> pd.DataFrame:
    """K-fold (grouped if ``groups``) CV returning per-fold weighted metrics."""
    w = np.ones(len(y)) if weights is None else np.asarray(weights, float)
    splitter = GroupKFold(n_splits=n_splits) if groups is not None else KFold(n_splits, shuffle=True, random_state=seed)
    rows = []
    for fold, (tr, te) in enumerate(splitter.split(X, y, groups)):
        m = clone(model)
        try:
            m.fit(X.iloc[tr], y.iloc[tr], sample_weight=w[tr])
        except TypeError:
            m.fit(X.iloc[tr], y.iloc[tr])
        if task == "binary":
            p = m.predict_proba(X.iloc[te])[:, 1]
            slope, icpt = calibration_slope_intercept(y.iloc[te].to_numpy(float), p, w[te])
            rows.append({"fold": fold, "auc": roc_auc_score(y.iloc[te], p, sample_weight=w[te]),
                         "brier": brier_score_loss(y.iloc[te], p, sample_weight=w[te]),
                         "cal_slope": slope, "cal_intercept": icpt})
        else:
            pred = m.predict(X.iloc[te])
            rows.append({"fold": fold, "rmse": float(np.sqrt(mean_squared_error(y.iloc[te], pred, sample_weight=w[te])))})
    return pd.DataFrame(rows)


def subgroup_metrics(y: pd.Series, p: pd.Series, group: pd.Series, weights: pd.Series | None = None,
                     min_n: int = 50) -> pd.DataFrame:
    """Aggregate AUC/Brier/mean prediction vs observed by subgroup (small cells suppressed)."""
    w = pd.Series(1.0, index=y.index) if weights is None else weights
    rows = []
    for g, idx in y.groupby(group).groups.items():
        n = len(idx)
        row = {"group": g, "n": n}
        if n >= min_n and y[idx].nunique() == 2:
            row.update({"auc": roc_auc_score(y[idx], p[idx], sample_weight=w[idx]),
                        "brier": brier_score_loss(y[idx], p[idx], sample_weight=w[idx]),
                        "mean_pred": np.average(p[idx], weights=w[idx]),
                        "mean_obs": np.average(y[idx], weights=w[idx])})
        rows.append(row)
    return pd.DataFrame(rows)
