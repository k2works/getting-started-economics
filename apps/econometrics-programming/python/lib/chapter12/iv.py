"""操作変数法と 2 段階最小二乗法（2SLS）。"""

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray

from lib.chapter01.statistics import Array, sample_covariance
from lib.chapter02.simple import SimpleFit, fit_simple
from lib.chapter03.multiple import fit_ols
from lib.chapter05.inference import TestResult, f_test


@dataclass(frozen=True)
class IvResult:
    """2SLS の推定結果。"""

    coefficients: pd.Series
    standard_errors: pd.Series
    residuals: NDArray[np.float64]
    n_obs: int
    df_resid: int


def iv_estimate(y: Array, x: Array, z: Array) -> SimpleFit:
    """単純な IV 推定（内生変数 x が 1 つ、操作変数 z が 1 つ）。

    傾き = Cov(z, y) ÷ Cov(z, x)、切片 = ȳ − 傾き · x̄。
    """
    slope = sample_covariance(z, y) / sample_covariance(z, x)
    mean_y = float(np.mean(np.asarray(y, dtype=float)))
    mean_x = float(np.mean(np.asarray(x, dtype=float)))
    return SimpleFit(intercept=mean_y - slope * mean_x, slope=slope)


def iv_slope_standard_error(y: Array, x: Array, z: Array, fit: SimpleFit) -> float:
    """単純な IV 推定の、傾きの標準誤差。

    残差は、元の x で計算する: u = y − 切片 − 傾き · x。
    Var = σ̂² · Σ(z − z̄)² ÷ (Σ(z − z̄)(x − x̄))²、σ̂² = Σu² ÷ (n − 2)。
    """
    values_z = np.asarray(z, dtype=float)
    centered_z = values_z - values_z.mean()
    values_x = np.asarray(x, dtype=float)
    centered_x = values_x - values_x.mean()
    u = np.asarray(y, dtype=float) - fit.intercept - fit.slope * values_x
    sigma2 = float(u @ u) / (len(u) - 2)
    return math.sqrt(
        sigma2 * float(centered_z @ centered_z) / float(centered_z @ centered_x) ** 2
    )


def _design(
    columns: pd.DataFrame, exogenous: pd.DataFrame | None
) -> tuple[NDArray[np.float64], list[str]]:
    """定数項・外生の説明変数・columns の順に並べた行列と、名前。"""
    parts = [np.ones((len(columns), 1))]
    names = ["const"]
    if exogenous is not None:
        parts.append(exogenous.to_numpy(dtype=float))
        names += list(exogenous.columns)
    parts.append(columns.to_numpy(dtype=float))
    names += list(columns.columns)
    return np.column_stack(parts), names


def _fitted_regressors(
    endogenous: pd.DataFrame,
    instruments: pd.DataFrame,
    exogenous: pd.DataFrame | None,
) -> tuple[NDArray[np.float64], NDArray[np.float64], list[str]]:
    """第 1 段階: 説明変数 R を、操作変数と外生の説明変数 Q で回帰した当てはめ値 R̂。"""
    if instruments.shape[1] < endogenous.shape[1]:
        raise ValueError("操作変数の数が、内生変数の数より少ないので、識別されない")
    regressors, names = _design(endogenous, exogenous)
    exogenous_part, _ = _design(instruments, exogenous)
    projection, *_ = np.linalg.lstsq(exogenous_part, regressors, rcond=None)
    return regressors, exogenous_part @ projection, names


def two_stage_least_squares(
    y: ArrayLike,
    endogenous: pd.DataFrame,
    instruments: pd.DataFrame,
    exogenous: pd.DataFrame | None = None,
) -> IvResult:
    """2SLS: β = (R̂′R)⁻¹ R̂′y。標準誤差の残差は、R̂ でなく、元の R で計算する。

    Var(β) = σ̂² · (R̂′R̂)⁻¹、σ̂² = Σ(y − Rβ)² ÷ (n − k)。
    """
    target = np.asarray(y, dtype=float)
    regressors, fitted, names = _fitted_regressors(endogenous, instruments, exogenous)
    coefficients = np.linalg.solve(fitted.T @ regressors, fitted.T @ target)
    residuals: NDArray[np.float64] = target - regressors @ coefficients
    n, k = regressors.shape
    sigma2 = float(residuals @ residuals) / (n - k)
    errors = np.sqrt(sigma2 * np.diag(np.linalg.inv(fitted.T @ fitted)))
    return IvResult(
        coefficients=pd.Series(coefficients, index=names),
        standard_errors=pd.Series(errors, index=names),
        residuals=residuals,
        n_obs=n,
        df_resid=n - k,
    )


def manual_second_stage(
    y: ArrayLike,
    endogenous: pd.DataFrame,
    instruments: pd.DataFrame,
    exogenous: pd.DataFrame | None = None,
) -> tuple[pd.Series, pd.Series]:
    """手作業の 2 段階: 第 2 段階の OLS の、係数と標準誤差。

    係数は 2SLS と同じだが、標準誤差は、当てはめ値 x̂ の残差で計算するので、正しくない。
    """
    _, fitted, names = _fitted_regressors(endogenous, instruments, exogenous)
    second = fit_ols(y, pd.DataFrame(fitted[:, 1:], columns=names[1:]))
    return second.coefficients, second.standard_errors


def first_stage_f(
    endogenous: pd.Series,
    instruments: pd.DataFrame,
    exogenous: pd.DataFrame | None = None,
) -> TestResult:
    """第 1 段階の F 検定: 操作変数の係数がすべて 0 という仮説（弱操作変数の目安）。"""
    columns = instruments if exogenous is None else exogenous.join(instruments)
    return f_test(endogenous, columns, list(instruments.columns))


def draw_iv_sample(
    n: int, strength: float, endogeneity: float, rng: np.random.Generator
) -> pd.DataFrame:
    """y = 1 + x + u、x = strength·z + v。u と v の相関は endogeneity（分散は 1）。

    z は操作変数（x と相関し、u と無関係）。
    OLS の傾きは、1 + endogeneity ÷ (1 + strength²) に近づく。
    """
    z = rng.standard_normal(n)
    v = rng.standard_normal(n)
    u = endogeneity * v + math.sqrt(1 - endogeneity**2) * rng.standard_normal(n)
    x = strength * z + v
    return pd.DataFrame({"y": 1 + x + u, "x": x, "z": z})


def weak_instrument_experiment(
    n: int, strength: float, repetitions: int, rng: np.random.Generator
) -> pd.DataFrame:
    """OLS と IV の傾きと第 1 段階の F 値を繰り返す（真の傾き 1、内生性 0.5）。"""
    rows = []
    for _ in range(repetitions):
        sample = draw_iv_sample(n, strength, 0.5, rng)
        stage = first_stage_f(sample["x"], sample[["z"]])
        rows.append(
            (
                fit_simple(sample["x"], sample["y"]).slope,
                iv_estimate(sample["y"], sample["x"], sample["z"]).slope,
                stage.statistic,
            )
        )
    return pd.DataFrame(rows, columns=["ols", "iv", "f"])
