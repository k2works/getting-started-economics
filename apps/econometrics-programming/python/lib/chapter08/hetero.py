"""不均一分散: 頑健な標準誤差、Breusch-Pagan 検定、White 検定、RESET。"""

from itertools import combinations

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray
from scipy import stats

from lib.chapter03.multiple import fit_ols, leverage, regressor_names
from lib.chapter05.inference import TestResult, f_test

KINDS = ("HC0", "HC1", "HC2", "HC3")


def _frame(x: ArrayLike) -> pd.DataFrame:
    """説明変数を、列の名前のある表にそろえる。"""
    if isinstance(x, pd.DataFrame):
        return x
    values = np.asarray(x, dtype=float)
    if values.ndim == 1:
        values = values.reshape(-1, 1)
    return pd.DataFrame(values, columns=regressor_names(x, values.shape[1]))


def robust_standard_errors(y: ArrayLike, x: ArrayLike, kind: str = "HC1") -> pd.Series:
    """不均一分散に頑健な標準誤差（サンドイッチ推定量）。

    Var(b) = (X'X)⁻¹ · X' diag(w·e²) X · (X'X)⁻¹。重み w は HC0: 1、
    HC1: n ÷ (n − k)、HC2: 1 ÷ (1 − h)、HC3: 1 ÷ (1 − h)²（h はてこ比）。
    """
    if kind not in KINDS:
        raise ValueError(f"知らない種類: {kind}（HC0〜HC3 のどれか）")
    frame = _frame(x)
    result = fit_ols(y, frame)
    design = np.column_stack([np.ones(len(frame)), frame.to_numpy(dtype=float)])
    n, k = design.shape
    h = leverage(frame)
    weights = {
        "HC0": np.ones(n),
        "HC1": np.full(n, n / (n - k)),
        "HC2": 1 / (1 - h),
        "HC3": 1 / (1 - h) ** 2,
    }[kind]
    bread = np.linalg.inv(design.T @ design)
    meat = design.T @ (design * (weights * result.residuals**2)[:, None])
    variance = bread @ meat @ bread
    return pd.Series(np.sqrt(np.diag(variance)), index=result.coefficients.index)


def _squared_residual_test(
    y: ArrayLike, x: ArrayLike, auxiliary: pd.DataFrame
) -> TestResult:
    """残差の 2 乗を auxiliary で回帰し、LM = n · R² を、χ² 検定する。"""
    residuals = fit_ols(y, _frame(x)).residuals
    fit = fit_ols(residuals**2, auxiliary)
    statistic = len(residuals) * fit.r_squared
    return TestResult(
        float(statistic), float(stats.chi2.sf(statistic, auxiliary.shape[1]))
    )


def breusch_pagan(y: ArrayLike, x: ArrayLike) -> TestResult:
    """Breusch-Pagan 検定: 残差の 2 乗が、説明変数で決まるか（帰無仮説: 均一分散）。"""
    frame = _frame(x)
    return _squared_residual_test(y, frame, frame)


def white_test(y: ArrayLike, x: ArrayLike) -> TestResult:
    """White 検定: 説明変数・その 2 乗・交差項で、残差の 2 乗を説明する。

    ダミー変数は d² = d になるので、同じ値の列は 1 本にまとめる。
    自由度は、まとめたあとの列数。
    """
    frame = _frame(x)
    columns = {name: frame[name] for name in frame.columns}
    for name in frame.columns:
        columns[f"{name}^2"] = frame[name] ** 2
    for a, b in combinations(frame.columns, 2):
        columns[f"{a}*{b}"] = frame[a] * frame[b]
    auxiliary = pd.DataFrame(columns)
    auxiliary = auxiliary.loc[:, ~auxiliary.T.duplicated()]
    return _squared_residual_test(y, frame, auxiliary)


def reset_test(y: ArrayLike, x: ArrayLike) -> TestResult:
    """RESET: 当てはめ値の 2 乗・3 乗を足し、係数が 0 か F 検定する（線形性の検定）。"""
    frame = _frame(x)
    result = fit_ols(y, frame)
    fitted = np.asarray(y, dtype=float) - result.residuals
    augmented = frame.assign(fitted2=fitted**2, fitted3=fitted**3)
    return f_test(y, augmented, ["fitted2", "fitted3"])


def draw_fan_sample(
    n: int, rng: np.random.Generator, heteroskedastic: bool
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """y = 1 + 2x + u。x は 0〜4 の一様乱数。

    不均一分散なら、u の標準偏差は 0.05 + 0.25x²（x が大きいほど大きい）。
    均一分散なら、1。
    """
    x = rng.uniform(0, 4, n)
    sd = 0.05 + 0.25 * x**2 if heteroskedastic else 1.0
    return x, 1 + 2 * x + sd * rng.standard_normal(n)


def standard_error_comparison(
    n: int, repetitions: int, heteroskedastic: bool, rng: np.random.Generator
) -> dict[str, float]:
    """傾きの推定値の標準偏差（実際のばらつき）と、通常・頑健（HC1）な標準誤差の平均。"""
    slopes, classical, robust = [], [], []
    for _ in range(repetitions):
        x, y = draw_fan_sample(n, rng, heteroskedastic)
        result = fit_ols(y, x)
        slopes.append(result.coefficients["x1"])
        classical.append(result.standard_errors["x1"])
        robust.append(robust_standard_errors(y, x)["x1"])
    return {
        "sd": float(np.std(slopes, ddof=1)),
        "classical": float(np.mean(classical)),
        "hc1": float(np.mean(robust)),
    }
