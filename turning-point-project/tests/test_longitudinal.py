import numpy as np
import pandas as pd
import pytest

from synthetic import lifecourse_sample
from turning_point.longitudinal import (compare_lifecourse_models, exposure_patterns, lifecourse_designs,
                                        piecewise_time, segmented_fit, wide_to_long)


def test_lifecourse_selects_generating_model():
    E, y = lifecourse_sample("accumulation", seed=5)
    tab = compare_lifecourse_models(pd.Series(y), E)
    acc = tab.set_index("model").loc["accumulation"]
    assert acc["p_vs_saturated"] > 0.01  # restriction compatible with data
    crit = tab.set_index("model").loc["critical_E1"]
    assert crit["p_vs_saturated"] < 1e-6

    E2, y2 = lifecourse_sample("critical_E2", seed=6)
    tab2 = compare_lifecourse_models(pd.Series(y2), E2).set_index("model")
    assert tab2.loc["critical_E2", "p_vs_saturated"] > 0.01
    assert tab2.loc["accumulation", "p_vs_saturated"] < 1e-6


def test_saturated_design_has_2k_minus_1_columns():
    E, _ = lifecourse_sample(seed=1)
    assert lifecourse_designs(E)["saturated"].shape[1] == 7
    assert exposure_patterns(E).sum() == len(E)


def test_mobility_model_two_periods_is_restriction():
    E = pd.DataFrame({"a": [0, 0, 1, 1], "b": [0, 1, 0, 1]})
    d = lifecourse_designs(E)
    assert d["mobility"].shape[1] == 2 < d["saturated"].shape[1]


def test_nonbinary_exposure_rejected():
    with pytest.raises(ValueError):
        lifecourse_designs(pd.DataFrame({"a": [0, 2], "b": [1, 0]}))


def test_segmented_fit_guard_and_recovery():
    with pytest.raises(ValueError, match="not justified"):
        segmented_fit(np.arange(4), np.arange(4))
    t = np.arange(12, dtype=float)
    y = np.where(t < 6, 0.0, 2.0 * (t - 6))
    r = segmented_fit(t, y)
    assert r["tau"] == 6 and r["slope_after"] == pytest.approx(2.0)


def test_piecewise_and_reshape():
    B = piecewise_time(np.array([0, 1, 2, 3]), [1.5])
    assert np.allclose(B[:, 1], [0, 0, 0.5, 1.5])
    df = pd.DataFrame({"id": [1, 2], "x_w1": [1, 2], "x_w2": [3, 4]})
    long = wide_to_long(df, "id", ["x"])
    assert list(long["x"]) == [1, 3, 2, 4]
