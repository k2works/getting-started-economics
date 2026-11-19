"""確率的ソロー・モデルと、景気循環の要素分解。

生産関数  Y = A·B·K^α·H^(1-α)（A: 変動する TFP、B: トレンド、H: 総労働時間）
資本の蓄積  K(t+1) = s·Y(t) + (1-δ)·K(t)、消費 C = (1-s)·Y、投資 I = s·Y
TFP の変動  log A(t) = ρ·log A(t-1) + ε(t)、ε は、平均 0、標準偏差 σ のホワイト・ノイズ

要素分解: log Y = log A + α·log K + (1-α)·log H なので、GDP の乖離 y は、
y = a + α·k + (1-α)·h（どれも、トレンドからの乖離）。Var(y) = Cov(y, y) を、
Cov(y, a) + α·Cov(y, k) + (1-α)·Cov(y, h) に分けると、各要素の寄与になる（合計 1）。
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from lib.chapter08.stochastic import white_noise
from lib.chapter09.cycles import load_quarterly, log_cycle

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "solow_quarterly.csv"


@dataclass(frozen=True)
class SolowParameters:
    """資本分配率 α、貯蓄率 s、減耗率 δ、TFP の ρ と σ、総労働時間 H、成長率 g。"""

    alpha: float = 0.36
    saving: float = 0.2
    depreciation: float = 0.025
    rho: float = 0.55
    sigma: float = 0.0078
    hours: float = 1.0
    growth: float = 0.0

    def __post_init__(self) -> None:
        if not (
            0 < self.alpha < 1
            and 0 < self.saving < 1
            and 0 < self.depreciation < 1
            and abs(self.rho) < 1
            and self.sigma >= 0
            and self.hours > 0
        ):
            raise ValueError(
                "パラメーターは、α・s・δ が 0 と 1 の間、"
                "|ρ| < 1、σ ≥ 0、H > 0 でなければならない"
            )


def total_factor_productivity(
    gdp: pd.Series, capital: pd.Series, hours: pd.Series, alpha: float
) -> pd.Series:
    """TFP = Y ÷ (K^α·H^(1-α))。"""
    return gdp / (capital**alpha * hours ** (1 - alpha))


def steady_state_capital(params: SolowParameters) -> float:
    """TFP の乱れがないときの定常状態の資本 K* = (s·H^(1-α) ÷ δ)^(1÷(1-α))。"""
    return float(
        (params.saving * params.hours ** (1 - params.alpha) / params.depreciation)
        ** (1 / (1 - params.alpha))
    )


def simulate_with_shocks(
    params: SolowParameters,
    shocks: NDArray[np.float64],
    initial_capital: float | None = None,
) -> pd.DataFrame:
    """TFP のショック ε(t) の系列を与えて、A・K・Y・C・I の水準を計算する。

    初期の資本は、既定で、定常状態の値。最初の期の log A は、ショックそのもの。
    """
    capital = (
        steady_state_capital(params) if initial_capital is None else initial_capital
    )
    log_a = 0.0
    rows = []
    for t, shock in enumerate(shocks):
        log_a = params.rho * log_a + float(shock)
        trend = (1 + params.growth) ** t
        output = (
            float(np.exp(log_a))
            * trend
            * capital**params.alpha
            * params.hours ** (1 - params.alpha)
        )
        rows.append(
            {
                "A": float(np.exp(log_a)),
                "K": capital,
                "Y": output,
                "C": (1 - params.saving) * output,
                "I": params.saving * output,
            }
        )
        capital = params.saving * output + (1 - params.depreciation) * capital
    return pd.DataFrame(rows)


def stochastic_solow(
    params: SolowParameters, n: int, rng: np.random.Generator
) -> pd.DataFrame:
    """毎期、TFP にショックが起きる、n 期間のシミュレーション（乱数の生成器を渡す）。"""
    return simulate_with_shocks(params, white_noise(n, params.sigma, rng))


def log_deviations(df: pd.DataFrame, params: SolowParameters) -> pd.DataFrame:
    """定常状態からの、対数の乖離（%）。列は a・y・k・c・i（トレンドがない場合）。"""
    k_star = steady_state_capital(params)
    y_star = k_star**params.alpha * params.hours ** (1 - params.alpha)
    return pd.DataFrame(
        {
            "a": 100 * np.log(df["A"]),
            "y": 100 * np.log(df["Y"] / y_star),
            "k": 100 * np.log(df["K"] / k_star),
            "c": 100 * np.log(df["C"] / ((1 - params.saving) * y_star)),
            "i": 100 * np.log(df["I"] / (params.saving * y_star)),
        }
    )


def fit_ar1_without_constant(x: pd.Series) -> tuple[float, float]:
    """x(t) を x(t-1) に、定数項なしで回帰する。係数 ρ と、残差の標準偏差 σ を返す。"""
    lag = x.shift().dropna()
    now = x.iloc[1:]
    rho = float((now * lag).sum() / (lag**2).sum())
    return rho, float((now - rho * lag).std())


def load_solow_quarterly(path: Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """GDP・資本ストック・総労働時間（水準）の四半期データを読み込む。"""
    return load_quarterly(path)


def business_cycle_components(df: pd.DataFrame, alpha: float) -> pd.DataFrame:
    """GDP・資本・総労働時間・TFP の、トレンドからの乖離（%）。列は y・k・h・a。"""
    gdp = pd.Series(df["gdp"])
    capital = pd.Series(df["capital"])
    hours = pd.Series(df["total_hours"])
    tfp = total_factor_productivity(gdp, capital, hours, alpha)
    return pd.DataFrame(
        {
            "y": log_cycle(gdp),
            "k": log_cycle(capital),
            "h": log_cycle(hours),
            "a": log_cycle(tfp),
        }
    )


def decompose_business_cycle(cycles: pd.DataFrame, alpha: float) -> pd.Series:
    """GDP の変動の、TFP・資本・労働の寄与（合計 1）。"""
    var_y = cycles["y"].var()
    return pd.Series(
        {
            "tfp": cycles["y"].cov(cycles["a"]) / var_y,
            "capital": alpha * cycles["y"].cov(cycles["k"]) / var_y,
            "labour": (1 - alpha) * cycles["y"].cov(cycles["h"]) / var_y,
        }
    )
