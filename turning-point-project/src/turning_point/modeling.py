"""Survey-weighted regression with design-based variance, age-moderation models,
multiple-imputation pooling, multiplicity control and sensitivity metrics.

Design-based variance uses Taylor linearisation with the with-replacement PSU
approximation (the default in R ``survey`` and Stata ``svy``):

    V = B M B,   B = (X' D X)^{-1},
    M = sum_h n_h/(n_h - 1) sum_{c in h} (u_hc - ubar_h)(u_hc - ubar_h)'

where u_hc is the weighted score total of PSU c in stratum h. Only canonical
links are supported (identity-Gaussian, logit-Binomial, log-Poisson), for which
D = diag(w * dmu/deta) and u_i = w_i x_i (y_i - mu_i). Inference uses a t
reference distribution with (#PSU - #strata) degrees of freedom.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.multitest import multipletests

FAMILIES = {"gaussian": sm.families.Gaussian(), "binomial": sm.families.Binomial(),
            "poisson": sm.families.Poisson()}


# --------------------------------------------------------------------------- splines
def default_knots(x: np.ndarray, k: int = 4) -> np.ndarray:
    """Harrell's recommended knot quantiles for k = 3..7 knots."""
    q = {3: [10, 50, 90], 4: [5, 35, 65, 95], 5: [5, 27.5, 50, 72.5, 95],
         6: [5, 23, 41, 59, 77, 95], 7: [2.5, 18.33, 34.17, 50, 65.83, 81.67, 97.5]}
    if k not in q:
        raise ValueError("k must be 3..7")
    knots = np.unique(np.percentile(np.asarray(x, float)[~np.isnan(x)], q[k]))
    if len(knots) < 3:
        raise ValueError("Too few distinct values for a spline; use categorical age bands instead")
    return knots


def rcs_basis(x: np.ndarray, knots: Sequence[float]) -> np.ndarray:
    """Restricted (natural) cubic spline basis, Harrell parameterisation.

    Returns an (n, K-1) matrix: column 0 is x itself, the remaining K-2 columns are the
    non-linear terms, scaled by (t_K - t_1)^2. The fitted function is linear beyond the
    boundary knots.
    """
    x = np.asarray(x, float)
    t = np.asarray(knots, float)
    K = len(t)
    if K < 3:
        raise ValueError("need at least 3 knots")
    pos3 = lambda u: np.where(u > 0, u, 0.0) ** 3  # noqa: E731
    scale = (t[-1] - t[0]) ** 2
    cols = [x]
    for j in range(K - 2):
        term = (pos3(x - t[j]) - pos3(x - t[-2]) * (t[-1] - t[j]) / (t[-1] - t[-2])
                + pos3(x - t[-1]) * (t[-2] - t[j]) / (t[-1] - t[-2]))
        cols.append(term / scale)
    return np.column_stack(cols)


# --------------------------------------------------------------------------- survey GLM
@dataclass
class SurveyDesign:
    """Column names of the design variables in the analysis frame (any may be None)."""

    weight: str | None = None
    strata: str | None = None
    psu: str | None = None
    lonely_psu: str = "error"  # "error" | "adjust" (centre singleton strata at the grand mean)


@dataclass
class SurveyFit:
    params: pd.Series
    cov: pd.DataFrame
    df_resid: float
    family: str
    n: int
    n_psu: int
    n_strata: int

    @property
    def se(self) -> pd.Series:
        return np.sqrt(pd.Series(np.diag(self.cov), index=self.params.index))

    def summary(self, alpha: float = 0.05) -> pd.DataFrame:
        tcrit = stats.t.ppf(1 - alpha / 2, self.df_resid)
        tval = self.params / self.se
        return pd.DataFrame({"estimate": self.params, "se": self.se,
                             "ci_low": self.params - tcrit * self.se, "ci_high": self.params + tcrit * self.se,
                             "t": tval, "p": 2 * stats.t.sf(np.abs(tval), self.df_resid)})

    def linear_combination(self, L: np.ndarray, alpha: float = 0.05) -> pd.DataFrame:
        """Estimates, SEs and CIs for rows of L @ beta."""
        L = np.atleast_2d(L)
        est = L @ self.params.to_numpy()
        se = np.sqrt(np.einsum("ij,jk,ik->i", L, self.cov.to_numpy(), L))
        tcrit = stats.t.ppf(1 - alpha / 2, self.df_resid)
        return pd.DataFrame({"estimate": est, "se": se, "ci_low": est - tcrit * se, "ci_high": est + tcrit * se})

    def wald_test(self, names: Sequence[str]) -> dict:
        """Joint test that the named coefficients are all zero (design-adjusted F)."""
        idx = [self.params.index.get_loc(n) for n in names]
        b = self.params.to_numpy()[idx]
        V = self.cov.to_numpy()[np.ix_(idx, idx)]
        q = len(idx)
        chi2 = float(b @ np.linalg.solve(V, b))
        ddf = self.df_resid
        # Adjusted F (Korn & Graubard style denominator df correction)
        F = chi2 / q * (ddf - q + 1) / ddf if ddf > q else float("nan")
        p = float(stats.f.sf(F, q, ddf - q + 1)) if ddf > q else float("nan")
        return {"q": q, "chi2": chi2, "F": F, "df1": q, "df2": ddf - q + 1, "p": p}


def fit_survey_glm(X: pd.DataFrame, y: pd.Series, *, family: str = "gaussian",
                   weights: pd.Series | None = None, strata: pd.Series | None = None,
                   psu: pd.Series | None = None, lonely_psu: str = "error") -> SurveyFit:
    """Weighted pseudo-maximum-likelihood GLM with linearised design-based covariance."""
    if family not in FAMILIES:
        raise ValueError(f"family must be one of {sorted(FAMILIES)}")
    n = len(y)
    w = np.ones(n) if weights is None else np.asarray(weights, float)
    if np.any(w < 0) or np.any(~np.isfinite(w)):
        raise ValueError("weights must be finite and non-negative")
    Xa = X.to_numpy(float)
    ya = np.asarray(y, float)
    if np.isnan(Xa).any() or np.isnan(ya).any():
        raise ValueError("NaNs in X or y: handle missing data (e.g. multiple imputation) before fitting")
    fam = FAMILIES[family]
    res = sm.GLM(ya, Xa, family=fam, var_weights=w).fit()
    beta = res.params
    eta = Xa @ beta
    mu = fam.link.inverse(eta)
    dmu = fam.link.inverse_deriv(eta)
    bread = np.linalg.inv(Xa.T @ (Xa * (w * dmu)[:, None]))
    u = Xa * (w * (ya - mu))[:, None]

    h = np.zeros(n, dtype=object) if strata is None else np.asarray(strata)
    c = np.arange(n) if psu is None else np.asarray(psu)
    frame = pd.DataFrame(u)
    frame["_h"], frame["_c"] = h, c
    totals = frame.groupby(["_h", "_c"], sort=False).sum()
    p = Xa.shape[1]
    meat = np.zeros((p, p))
    grand = totals.to_numpy().mean(axis=0)
    n_strata = 0
    for _, g in totals.groupby(level="_h", sort=False):
        n_strata += 1
        G = g.to_numpy()
        nh = len(G)
        if nh == 1:
            if lonely_psu == "adjust":
                d = G - grand
                meat += d.T @ d
                continue
            raise ValueError("Stratum with a single PSU; collapse strata or set lonely_psu='adjust'")
        d = G - G.mean(axis=0)
        meat += nh / (nh - 1) * (d.T @ d)
    cov = bread @ meat @ bread
    n_psu = len(totals)
    names = list(X.columns)
    return SurveyFit(params=pd.Series(beta, index=names), cov=pd.DataFrame(cov, index=names, columns=names),
                     df_resid=float(n_psu - n_strata), family=family, n=n, n_psu=n_psu, n_strata=n_strata)


# --------------------------------------------------------------------------- replicate weights
def replicate_variance(full_estimate: np.ndarray, replicate_estimates: np.ndarray, *, method: str = "brr",
                       fay_rho: float = 0.0, jk_factor: float | None = None) -> np.ndarray:
    """Covariance of estimates from replicate-weight re-estimation.

    ``replicate_estimates`` is (R, p): the statistic recomputed with each replicate weight.
    BRR/Fay: V = 1/(R (1-rho)^2) * sum_r (theta_r - theta)(theta_r - theta)'.
    JK1: V = (R-1)/R * sum_r (...). Generic: V = jk_factor * sum_r (...).
    Use the method and Fay coefficient stated in the study's documentation (e.g. the HSLS:09 and
    ELS:2002 data file documentation); do not assume them.
    """
    th = np.atleast_1d(np.asarray(full_estimate, float))
    reps = np.asarray(replicate_estimates, float).reshape(-1, th.size)
    R = reps.shape[0]
    d = reps - th
    ss = d.T @ d
    if jk_factor is not None:
        return jk_factor * ss
    if method == "brr":
        return ss / (R * (1 - fay_rho) ** 2)
    if method == "jk1":
        return (R - 1) / R * ss
    raise ValueError("method must be 'brr' or 'jk1' (or pass jk_factor)")


def fit_glm_replicate(X: pd.DataFrame, y: pd.Series, full_weight: pd.Series, replicate_weights: pd.DataFrame, *,
                      family: str = "gaussian", method: str = "brr", fay_rho: float = 0.0,
                      df: float | None = None) -> SurveyFit:
    """Weighted GLM with replicate-weight variance (for public files that suppress strata/PSU)."""
    fam = FAMILIES[family]
    Xa, ya = X.to_numpy(float), np.asarray(y, float)
    fit = lambda w: sm.GLM(ya, Xa, family=fam, var_weights=np.asarray(w, float)).fit().params  # noqa: E731
    beta = fit(full_weight)
    reps = np.vstack([fit(replicate_weights[c]) for c in replicate_weights.columns])
    cov = replicate_variance(beta, reps, method=method, fay_rho=fay_rho)
    names = list(X.columns)
    R = replicate_weights.shape[1]
    return SurveyFit(params=pd.Series(beta, index=names), cov=pd.DataFrame(cov, index=names, columns=names),
                     df_resid=float(df if df is not None else R), family=family, n=len(ya), n_psu=R, n_strata=0)


# --------------------------------------------------------------------------- equivalence
def equivalence_test(estimate: float, se: float, sesoi: float, df: float = np.inf, alpha: float = 0.05) -> dict:
    """Two one-sided tests (TOST) that |effect| < sesoi; also the (1-2alpha) CI used for the decision."""
    t_lo = (estimate + sesoi) / se
    t_hi = (estimate - sesoi) / se
    p = max(stats.t.sf(t_lo, df), stats.t.cdf(t_hi, df))
    tcrit = stats.t.ppf(1 - alpha, df)
    lo, hi = estimate - tcrit * se, estimate + tcrit * se
    if p < alpha:
        verdict = "equivalent (difference smaller than SESOI)"
    elif lo > sesoi or hi < -sesoi:
        verdict = "non-equivalent (difference larger than SESOI)"
    elif lo > 0 or hi < 0:
        verdict = "different from zero, equivalence undetermined"
    else:
        verdict = "inconclusive"
    return {"p_tost": float(p), "ci90_low": float(lo), "ci90_high": float(hi), "verdict": verdict}


# --------------------------------------------------------------------------- age moderation
@dataclass
class AgeModerationResult:
    fit: SurveyFit
    knots: np.ndarray | None
    effect_by_age: pd.DataFrame  # age, estimate, se, ci_low, ci_high
    interaction_test: dict
    exposure: str
    scale: str  # "linear predictor": difference (gaussian) or log-odds/log-rate


def build_age_moderation_design(df: pd.DataFrame, exposure: str, age: str, covariates: Sequence[str] = (),
                                knots: Sequence[float] | None = None, n_knots: int = 4,
                                age_bands: Sequence[float] | None = None) -> tuple[pd.DataFrame, np.ndarray | None, list[str]]:
    """Design matrix for outcome ~ exposure * f(age) + covariates.

    f(age) is a restricted cubic spline (default) or, if ``age_bands`` (cut points) are
    given, indicator bands. Returns (X, knots, interaction column names).
    """
    X = pd.DataFrame({"const": 1.0}, index=df.index)
    X[exposure] = df[exposure].astype(float)
    a = df[age].to_numpy(float)
    if age_bands is not None:
        bands = pd.cut(df[age], bins=[-np.inf, *age_bands, np.inf], right=False)
        D = pd.get_dummies(bands, drop_first=True, dtype=float)
        D.columns = [f"age_band_{i + 1}" for i in range(D.shape[1])]
        basis, used_knots = D, None
    else:
        used_knots = np.asarray(knots if knots is not None else default_knots(a, n_knots), float)
        B = rcs_basis(a, used_knots)
        basis = pd.DataFrame(B, index=df.index, columns=[f"age_s{j}" for j in range(B.shape[1])])
    X = pd.concat([X, basis], axis=1)
    inter = []
    for col in basis.columns:
        name = f"{exposure}:{col}"
        X[name] = X[exposure] * basis[col]
        inter.append(name)
    for cv in covariates:
        X[cv] = df[cv].astype(float)
    return X, used_knots, inter


def fit_age_moderation(df: pd.DataFrame, *, outcome: str, exposure: str, age: str,
                       covariates: Sequence[str] = (), family: str = "gaussian",
                       design: SurveyDesign | None = None, knots: Sequence[float] | None = None,
                       n_knots: int = 4, age_bands: Sequence[float] | None = None,
                       age_grid: Sequence[float] | None = None, alpha: float = 0.05) -> AgeModerationResult:
    """Fit the primary timing model and return the exposure effect as a function of age.

    The 'effect' is a conditional association on the model scale (mean difference,
    log-odds ratio or log-rate ratio). It is causal only under the assumptions in
    docs/causal_framework.md, which observational data alone cannot guarantee.
    """
    design = design or SurveyDesign()
    cols = [outcome, exposure, age, *covariates] + [c for c in (design.weight, design.strata, design.psu) if c]
    d = df[cols].dropna()
    X, used_knots, inter = build_age_moderation_design(d, exposure, age, covariates, knots, n_knots, age_bands)
    fit = fit_survey_glm(X, d[outcome], family=family,
                         weights=d[design.weight] if design.weight else None,
                         strata=d[design.strata] if design.strata else None,
                         psu=d[design.psu] if design.psu else None, lonely_psu=design.lonely_psu)
    grid = np.asarray(age_grid if age_grid is not None else np.linspace(d[age].min(), d[age].max(), 25), float)
    L = np.zeros((len(grid), X.shape[1]))
    L[:, X.columns.get_loc(exposure)] = 1.0
    if age_bands is not None:
        bands = pd.cut(pd.Series(grid), bins=[-np.inf, *age_bands, np.inf], right=False).cat.codes.to_numpy()
        for i, b in enumerate(bands):
            if b > 0:
                L[i, X.columns.get_loc(f"{exposure}:age_band_{b}")] = 1.0
    else:
        Bg = rcs_basis(grid, used_knots)
        for j, name in enumerate(inter):
            L[:, X.columns.get_loc(name)] = Bg[:, j]
    eff = fit.linear_combination(L, alpha=alpha)
    eff.insert(0, "age", grid)
    scale = {"gaussian": "mean difference", "binomial": "log odds ratio", "poisson": "log rate ratio"}[family]
    return AgeModerationResult(fit=fit, knots=used_knots, effect_by_age=eff,
                               interaction_test=fit.wald_test(inter), exposure=exposure, scale=scale)


# --------------------------------------------------------------------------- multiple imputation
def rubin_pool(estimates: Sequence[float], variances: Sequence[float], n_obs: int | None = None,
               k_params: int = 1) -> dict:
    """Pool a scalar estimate over m imputations (Rubin's rules, Barnard-Rubin df if n_obs given)."""
    q = np.asarray(estimates, float)
    u = np.asarray(variances, float)
    m = len(q)
    if m < 2:
        raise ValueError("need at least 2 imputations")
    qbar, ubar, b = q.mean(), u.mean(), q.var(ddof=1)
    T = ubar + (1 + 1 / m) * b
    lam = (1 + 1 / m) * b / T
    nu_old = (m - 1) / lam**2 if lam > 0 else np.inf
    if n_obs is not None and lam > 0:
        nu_com = n_obs - k_params
        nu_obs = (nu_com + 1) / (nu_com + 3) * nu_com * (1 - lam)
        nu = 1 / (1 / nu_old + 1 / nu_obs)
    else:
        nu = nu_old
    fmi = (lam + 2 / (nu + 3)) if np.isfinite(nu) else lam
    return {"estimate": qbar, "se": float(np.sqrt(T)), "df": float(nu), "within": ubar, "between": b,
            "lambda": lam, "fmi": float(fmi), "m": m}


# --------------------------------------------------------------------------- multiplicity & sensitivity
def adjust_pvalues(p: Sequence[float], method: str = "holm") -> np.ndarray:
    """Holm (family-wise, confirmatory) or 'fdr_bh' (exploratory) adjustment."""
    return multipletests(np.asarray(p, float), method=method)[1]


def e_value(rr: float, ci_limit: float | None = None) -> dict:
    """VanderWeele & Ding (2017) E-value for a risk ratio (and the CI limit nearer the null)."""
    def ev(r: float) -> float:
        r = 1 / r if r < 1 else r
        return float(r + np.sqrt(r * (r - 1)))
    out = {"point": ev(rr)}
    if ci_limit is not None:
        crosses = (rr >= 1 and ci_limit <= 1) or (rr < 1 and ci_limit >= 1)
        out["ci"] = 1.0 if crosses else ev(ci_limit)
    return out


def rr_from_or(odds_ratio: float, common_outcome: bool) -> float:
    """Approximate RR from an OR: identity if rare (<15%), sqrt(OR) if common (VanderWeele 2017)."""
    return float(np.sqrt(odds_ratio)) if common_outcome else float(odds_ratio)


def rr_from_smd(d: float) -> float:
    """Approximate RR for a standardised mean difference: exp(0.91 d) (VanderWeele & Ding 2017)."""
    return float(np.exp(0.91 * d))
