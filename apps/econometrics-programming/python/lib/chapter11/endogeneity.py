"""外生性が満たされない場合: 欠落変数・測定誤差・同時方程式のバイアス。"""

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from lib.chapter01.statistics import Array
from lib.chapter02.simple import fit_simple
from lib.chapter03.multiple import fit_ols


@dataclass(frozen=True)
class OvbDecomposition:
    """欠落変数バイアスの分解: 短い回帰の傾き = 長い回帰の傾き + β₂ · δ。"""

    short: float
    long: float
    beta2: float
    delta: float


def ovb_decomposition(y: Array, x1: Array, x2: Array) -> OvbDecomposition:
    """x2 を落とした回帰（短い）と、入れた回帰（長い）、補助回帰（x2 を x1 で回帰）。

    標本の中で、短い回帰の傾き = 長い回帰の x1 の係数 + x2 の係数 × 補助回帰の傾き
    が、ちょうど成り立つ。
    """
    long = fit_ols(y, np.column_stack([x1, x2])).coefficients
    return OvbDecomposition(
        short=fit_simple(x1, y).slope,
        long=float(long["x1"]),
        beta2=float(long["x2"]),
        delta=fit_simple(x1, x2).slope,
    )


def draw_omitted(
    n: int, correlation: float, rng: np.random.Generator
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """y = 1 + x1 + 2·x2 + u（x1 と x2 の相関は correlation、どちらも分散 1）。

    x2 を落とすと、x1 の係数は、1 + 2·correlation に近づく（バイアスは 2·correlation）。
    """
    x1 = rng.standard_normal(n)
    x2 = correlation * x1 + math.sqrt(1 - correlation**2) * rng.standard_normal(n)
    y = 1 + x1 + 2 * x2 + rng.standard_normal(n)
    return y, x1, x2


def simulate_omitted(
    n: int, correlation: float, repetitions: int, rng: np.random.Generator
) -> pd.DataFrame:
    """x2 を落とした回帰（short）と入れた回帰（long）の x1 の係数を繰り返す。"""
    rows = []
    for _ in range(repetitions):
        y, x1, x2 = draw_omitted(n, correlation, rng)
        d = ovb_decomposition(y, x1, x2)
        rows.append((d.short, d.long))
    return pd.DataFrame(rows, columns=["short", "long"])


def attenuation_factor(var_true: float, var_error: float) -> float:
    """測定誤差による減衰係数 = Var(真の x) ÷ (Var(真の x) + Var(誤差))。"""
    return var_true / (var_true + var_error)


def draw_measurement_error(
    n: int, error_sd: float, rng: np.random.Generator
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """y = 1 + x* + u。観測できるのは、誤差のある x = x* + e だけ（x* は分散 1）。"""
    x_true = rng.standard_normal(n)
    y = 1 + x_true + rng.standard_normal(n)
    return y, x_true + error_sd * rng.standard_normal(n)


def simulate_measurement_error(
    n: int, error_sd: float, repetitions: int, rng: np.random.Generator
) -> NDArray[np.float64]:
    """誤差のある x で回帰した傾きを、繰り返し推定する（真の傾きは 1）。"""
    slopes = []
    for _ in range(repetitions):
        y, x = draw_measurement_error(n, error_sd, rng)
        slopes.append(fit_simple(x, y).slope)
    return np.array(slopes)


def draw_market(
    n: int, sd_demand: float, sd_supply: float, rng: np.random.Generator
) -> pd.DataFrame:
    """需要・供給の均衡で決まる、価格 p と数量 q の標本。

    需要: q = 10 − p + u_d、供給: q = p + u_s（需要の傾き −1、供給の傾き +1）。
    均衡で、p = (10 + u_d − u_s) ÷ 2、q = (10 + u_d + u_s) ÷ 2。
    """
    u_d = sd_demand * rng.standard_normal(n)
    u_s = sd_supply * rng.standard_normal(n)
    return pd.DataFrame({"p": (10 + u_d - u_s) / 2, "q": (10 + u_d + u_s) / 2})


def simultaneity_slope(sd_demand: float, sd_supply: float) -> float:
    """q を p で回帰した傾きの、大標本での値 = (σ_d² − σ_s²) ÷ (σ_d² + σ_s²)。"""
    return (sd_demand**2 - sd_supply**2) / (sd_demand**2 + sd_supply**2)


def simulate_simultaneity(
    n: int,
    sd_demand: float,
    sd_supply: float,
    repetitions: int,
    rng: np.random.Generator,
) -> NDArray[np.float64]:
    """q を p で回帰した傾きを、繰り返し推定する。"""
    slopes = []
    for _ in range(repetitions):
        market = draw_market(n, sd_demand, sd_supply, rng)
        slopes.append(fit_simple(market["p"], market["q"]).slope)
    return np.array(slopes)
