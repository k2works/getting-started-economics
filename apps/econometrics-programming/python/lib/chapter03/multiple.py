"""重回帰分析: 行列による最小二乗法、てこ比、FWL、分散拡大係数。"""

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray


@dataclass(frozen=True)
class OlsResult:
    """最小二乗法の推定結果。"""

    coefficients: pd.Series
    standard_errors: pd.Series
    residuals: NDArray[np.float64]
    r_squared: float
    n_obs: int
    df_resid: int


def regressor_names(x: ArrayLike, width: int) -> list[str]:
    """説明変数の名前。表の列名・系列の名前を使い、名前がなければ x1, x2, …。"""
    if isinstance(x, pd.DataFrame):
        return [str(c) for c in x.columns]
    if isinstance(x, pd.Series) and x.name is not None:
        return [str(x.name)]
    return [f"x{i + 1}" for i in range(width)]


def _matrix(x: ArrayLike, constant: bool) -> tuple[NDArray[np.float64], list[str]]:
    values = np.asarray(x, dtype=float)
    if values.ndim == 1:
        values = values.reshape(-1, 1)
    names = regressor_names(x, values.shape[1])
    if constant:
        values = np.column_stack([np.ones(len(values)), values])
        names = ["const", *names]
    return values, names


def fit_ols(y: ArrayLike, x: ArrayLike, constant: bool = True) -> OlsResult:
    """正規方程式 (X'X) b = X'y を解いて、係数・標準誤差・決定係数を求める。"""
    design, names = _matrix(x, constant)
    target = np.asarray(y, dtype=float)
    n, k = design.shape
    if n <= k:
        raise ValueError("観測値の数が係数の数以下なので、推定できない")
    gram = design.T @ design
    if np.linalg.matrix_rank(gram) < k:
        raise ValueError("多重共線性（説明変数の間に、完全な線形関係がある）")
    coefficients = np.linalg.solve(gram, design.T @ target)
    residuals: NDArray[np.float64] = target - design @ coefficients
    rss = float(residuals @ residuals)
    sigma2 = rss / (n - k)
    errors = np.sqrt(sigma2 * np.diag(np.linalg.inv(gram)))
    tss = float(np.sum((target - target.mean()) ** 2))
    return OlsResult(
        coefficients=pd.Series(coefficients, index=names),
        standard_errors=pd.Series(errors, index=names),
        residuals=residuals,
        r_squared=1 - rss / tss,
        n_obs=n,
        df_resid=n - k,
    )


def leverage(x: ArrayLike, constant: bool = True) -> NDArray[np.float64]:
    """てこ比（ハット行列 H = X (X'X)⁻¹ X' の対角成分）。"""
    design, _ = _matrix(x, constant)
    hat = design @ np.linalg.solve(design.T @ design, design.T)
    result: NDArray[np.float64] = np.diag(hat)
    return result


def partial_out(v: ArrayLike, others: ArrayLike) -> NDArray[np.float64]:
    """v を、定数項と others で回帰した残差（others の影響を除いた v）。"""
    return fit_ols(v, others).residuals


def fwl_coefficient(y: ArrayLike, x: ArrayLike, others: ArrayLike) -> float:
    """FWL: y と x から others の影響を除き、残差どうしの単回帰の傾きを求める。"""
    y_tilde = partial_out(y, others)
    x_tilde = partial_out(x, others)
    return float(x_tilde @ y_tilde / (x_tilde @ x_tilde))


def variance_inflation_factor(x: pd.DataFrame, column: str) -> float:
    """分散拡大係数 VIF = 1 ÷ (1 − R²)。R² は、column を他の列で回帰したもの。"""
    result = fit_ols(x[column], x.drop(columns=column))
    return 1 / (1 - result.r_squared)


def percent_effect(coefficient: float, change: float = 1) -> float:
    """対数の被説明変数の係数から、説明変数が change 増えたときの変化率（%）。"""
    return (math.exp(coefficient * change) - 1) * 100


def multicollinearity_experiment(
    correlation: float, n: int, repetitions: int, rng: np.random.Generator
) -> pd.DataFrame:
    """y = 1 + x1 + x2 + u の係数を、x1 と x2 の相関を指定して、繰り返し推定する。"""
    rows = []
    for _ in range(repetitions):
        z1, z2, u = rng.standard_normal((3, n))
        x1 = z1
        x2 = correlation * z1 + math.sqrt(1 - correlation**2) * z2
        y = 1 + x1 + x2 + u
        result = fit_ols(y, np.column_stack([x1, x2]))
        rows.append((result.coefficients["x1"], result.coefficients["x2"]))
    return pd.DataFrame(rows, columns=["x1", "x2"])
