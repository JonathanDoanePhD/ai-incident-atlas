import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm

from synthetic import age_moderation_sample
from turning_point.modeling import (SurveyDesign, adjust_pvalues, default_knots, e_value, fit_age_moderation,
                                    fit_survey_glm, rcs_basis, rubin_pool)


def test_rcs_is_linear_beyond_boundary_knots():
    knots = [1.0, 2.0, 3.0, 4.0]
    x = np.linspace(5, 10, 6)
    B = rcs_basis(x, knots)
    second_diff = np.diff(B, n=2, axis=0)
    assert np.allclose(second_diff, 0, atol=1e-9)
    assert np.allclose(rcs_basis(np.array([0.5]), knots)[0, 1:], 0)  # below first knot: only linear term


def test_default_knots_harrell_quantiles():
    x = np.arange(101, dtype=float)
    assert np.allclose(default_knots(x, 3), [10, 50, 90])


def test_unweighted_point_estimates_match_ols():
    df = age_moderation_sample(n_strata=5)
    X = sm.add_constant(df[["support", "cov"]])
    fit = fit_survey_glm(X, df["y"])
    ols = sm.OLS(df["y"], X).fit()
    assert np.allclose(fit.params, ols.params)


def test_cluster_variance_matches_statsmodels_up_to_known_factor():
    """Single stratum: our linearised variance = G/(G-1) * sandwich; statsmodels' default
    cluster correction additionally multiplies by (N-1)/(N-K)."""
    df = age_moderation_sample(n_strata=10)
    X = sm.add_constant(df[["support", "cov"]])
    fit = fit_survey_glm(X, df["y"], psu=df["psu"])
    groups = pd.factorize(df["psu"])[0]
    ref = sm.OLS(df["y"], X).fit(cov_type="cluster", cov_kwds={"groups": groups})
    N, K = X.shape
    assert np.allclose(fit.cov.to_numpy() * (N - 1) / (N - K), ref.cov_params().to_numpy(), rtol=1e-8)


def test_weighted_logistic_point_estimates_match_freq_weights():
    rng = np.random.default_rng(0)
    n = 3000
    x = rng.normal(size=n)
    y = rng.binomial(1, 1 / (1 + np.exp(-(-0.5 + 0.8 * x))))
    w = rng.integers(1, 4, n).astype(float)
    X = sm.add_constant(pd.DataFrame({"x": x}))
    fit = fit_survey_glm(X, pd.Series(y), family="binomial", weights=pd.Series(w))
    ref = sm.GLM(y, X, family=sm.families.Binomial(), freq_weights=w).fit()
    assert np.allclose(fit.params, ref.params, atol=1e-6)


def test_singleton_stratum_raises_unless_adjusted():
    df = age_moderation_sample(n_strata=3, psu_per_stratum=2)
    df.loc[df["stratum"] == 0, "psu"] = "0-0"  # stratum 0 now has one PSU
    X = sm.add_constant(df[["support"]])
    with pytest.raises(ValueError, match="single PSU"):
        fit_survey_glm(X, df["y"], strata=df["stratum"], psu=df["psu"])
    fit_survey_glm(X, df["y"], strata=df["stratum"], psu=df["psu"], lonely_psu="adjust")


def test_age_moderation_monte_carlo_bias_and_coverage():
    """Simulation check of the primary estimator: across replicates the age-specific effect
    should be ~unbiased and its 95% design-based CI should cover the truth ~95% of the time."""
    grid = np.array([12.5, 14.5, 16.5])
    truth = 0.5 - 0.1 * (grid - 12)
    ests, cover, dfs = [], [], set()
    for seed in range(120):
        df = age_moderation_sample(n_strata=15, psu_per_stratum=4, n_per_psu=40, seed=1000 + seed)
        res = fit_age_moderation(df, outcome="y", exposure="support", age="age", covariates=["cov"],
                                 design=SurveyDesign(weight="w", strata="stratum", psu="psu"),
                                 knots=[13.0, 14.5, 16.0], age_grid=grid)
        e = res.effect_by_age
        ests.append(e["estimate"].to_numpy())
        cover.append(((e["ci_low"] < truth) & (truth < e["ci_high"])).to_numpy())
        dfs.add(res.fit.df_resid)
    assert dfs == {15 * 4 - 15}
    assert np.all(np.abs(np.mean(ests, axis=0) - truth) < 0.03)
    cov = np.mean(cover, axis=0)
    assert np.all((cov > 0.87) & (cov <= 1.0)), cov


def test_age_bands_parameterisation():
    df = age_moderation_sample(seed=3)
    res = fit_age_moderation(df, outcome="y", exposure="support", age="age", age_bands=[14, 16],
                             design=SurveyDesign(psu="psu", strata="stratum"), age_grid=[13, 15, 16.5])
    assert res.effect_by_age.shape == (3, 5)
    assert res.fit.params.index.tolist()[:2] == ["const", "support"]
    assert {"support:age_band_1", "support:age_band_2"} <= set(res.fit.params.index)
    assert res.interaction_test["q"] == 2


def test_nan_inputs_rejected():
    X = pd.DataFrame({"const": [1.0, 1.0, 1.0], "x": [1.0, np.nan, 2.0]})
    with pytest.raises(ValueError, match="NaNs"):
        fit_survey_glm(X, pd.Series([1.0, 2.0, 3.0]))


def test_rubin_pool_hand_computed():
    r = rubin_pool([1.0, 2.0, 3.0], [0.5, 0.5, 0.5])
    # B = 1, Ubar = 0.5, T = 0.5 + (4/3)*1
    assert r["estimate"] == pytest.approx(2.0)
    assert r["se"] == pytest.approx(np.sqrt(0.5 + 4 / 3))


def test_e_value_known_values():
    assert e_value(3.9)["point"] == pytest.approx(3.9 + np.sqrt(3.9 * 2.9))
    assert e_value(0.5)["point"] == pytest.approx(2 + np.sqrt(2))
    assert e_value(1.5, ci_limit=0.9)["ci"] == 1.0


def test_holm_adjustment():
    adj = adjust_pvalues([0.01, 0.04, 0.03], "holm")
    assert np.allclose(adj, [0.03, 0.06, 0.06])
