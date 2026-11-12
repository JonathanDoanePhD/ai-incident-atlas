"""Scale scoring and reliability for multi-item constructs.

No composite is defined here by assumption. ``ConstructDefinition`` records where
the items come from so a scale is only scored after its items are verified in the
codebook. Reliability is reported, not assumed; measurement invariance across ages
must be tested separately before comparing a scale across waves.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class ConstructDefinition:
    name: str
    domain: str
    items: list[str]
    reverse: list[str] = field(default_factory=list)
    scale_min: float = 1
    scale_max: float = 4
    min_items: int | None = None  # minimum answered items to score; default ceil(k/2)
    source: str = ""  # codebook citation / URL
    verified: bool = False


def score_scale(df: pd.DataFrame, items: list[str], *, reverse: list[str] = (), lo: float = 1,
                hi: float = 4, min_items: int | None = None) -> pd.Series:
    """Person mean of answered items (reverse-coded where listed); NaN if too few answered."""
    X = df[items].astype(float).copy()
    for c in reverse:
        X[c] = lo + hi - X[c]
    k = len(items)
    need = min_items if min_items is not None else int(np.ceil(k / 2))
    n_ans = X.notna().sum(axis=1)
    return X.mean(axis=1).where(n_ans >= need)


def score_construct(df: pd.DataFrame, c: ConstructDefinition, *, allow_unverified: bool = False) -> pd.Series:
    if not c.verified and not allow_unverified:
        raise ValueError(f"Construct {c.name!r} items are not verified against a codebook")
    return score_scale(df, c.items, reverse=c.reverse, lo=c.scale_min, hi=c.scale_max,
                       min_items=c.min_items).rename(c.name)


def cronbach_alpha(items: pd.DataFrame) -> float:
    """Cronbach's alpha on complete cases."""
    X = items.dropna().to_numpy(float)
    k = X.shape[1]
    if k < 2 or len(X) < 3:
        return float("nan")
    item_var = X.var(axis=0, ddof=1).sum()
    total_var = X.sum(axis=1).var(ddof=1)
    return float(k / (k - 1) * (1 - item_var / total_var))


def corrected_item_total(items: pd.DataFrame) -> pd.Series:
    """Correlation of each item with the sum of the *other* items (complete cases)."""
    X = items.dropna()
    total = X.sum(axis=1)
    return pd.Series({c: np.corrcoef(X[c], total - X[c])[0, 1] for c in X.columns})


def reliability_report(df: pd.DataFrame, c: ConstructDefinition) -> dict:
    X = df[c.items].astype(float).copy()
    for col in c.reverse:
        X[col] = c.scale_min + c.scale_max - X[col]
    return {"construct": c.name, "k_items": len(c.items), "n_complete": int(X.dropna().shape[0]),
            "alpha": cronbach_alpha(X), "item_total": corrected_item_total(X).round(3).to_dict()}
