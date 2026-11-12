"""Recoding survey conventions into analysable values, without losing information.

Survey files encode *why* a value is missing (refusal, don't know, valid skip,
non-interview). ``recode_missing`` converts those codes to NaN but returns the
reasons alongside, so missing-data analyses can treat a valid skip differently
from a refusal or attrition.
"""
from __future__ import annotations

from typing import Iterable, Mapping

import numpy as np
import pandas as pd


def recode_missing(df: pd.DataFrame, codes: Mapping[int, str],
                   columns: Iterable[str] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Replace reserved missing-value codes with NaN.

    Returns ``(clean, reasons)`` where ``reasons`` has the same shape and holds the
    reason label (e.g. ``"valid_skip"``) where a code was replaced, else ``None``.
    Values that are NaN in the input get reason ``"system_missing"``.
    """
    cols = list(columns) if columns is not None else list(df.columns)
    clean = df.copy()
    reasons = pd.DataFrame(None, index=df.index, columns=cols, dtype=object)
    for c in cols:
        s = df[c]
        if not pd.api.types.is_numeric_dtype(s):
            continue
        reasons.loc[s.isna(), c] = "system_missing"
        for code, label in codes.items():
            hit = s == code
            if hit.any():
                reasons.loc[hit, c] = label
                clean.loc[hit, c] = np.nan
    return clean, reasons


def reverse_code(s: pd.Series, lo: float, hi: float) -> pd.Series:
    """Reverse a Likert item on [lo, hi]: x -> lo + hi - x."""
    out = lo + hi - s
    bad = s.notna() & ((s < lo) | (s > hi))
    if bad.any():
        raise ValueError(f"{int(bad.sum())} values of {s.name!r} outside [{lo}, {hi}]")
    return out


def age_in_years(birth_year: pd.Series, birth_month: pd.Series,
                 ref_year: pd.Series, ref_month: pd.Series) -> pd.Series:
    """Age in fractional years at a reference (interview) month; month-level precision only."""
    months = (ref_year - birth_year) * 12 + (ref_month - birth_month)
    return months / 12.0


def standardize(s: pd.Series, weights: pd.Series | None = None) -> pd.Series:
    """(Weighted) z-score; weights use the same rows as ``s``."""
    m = s.notna() if weights is None else s.notna() & weights.notna()
    w = np.ones(m.sum()) if weights is None else weights[m].to_numpy(float)
    x = s[m].to_numpy(float)
    mu = np.average(x, weights=w)
    sd = np.sqrt(np.average((x - mu) ** 2, weights=w))
    return (s - mu) / sd


def attainment_years(levels: pd.Series, years_map: Mapping) -> pd.Series:
    """Map a categorical highest-degree code to approximate years of schooling.

    The mapping must be supplied from the study's documentation; there is no default,
    because degree codes differ across studies.
    """
    out = levels.map(years_map)
    unmapped = levels.notna() & out.isna()
    if unmapped.any():
        raise ValueError(f"Unmapped attainment codes: {sorted(levels[unmapped].unique())}")
    return out.astype(float)
