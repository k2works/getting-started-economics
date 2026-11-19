"""ソロー・モデル: k(t+1) = s·A·k(t)^α + (1−δ)·k(t)。

k は労働者 1 人当たりの資本、s は貯蓄率、δ は減耗率、A は技術水準、α は資本分配率。
定常状態 k* のまわりで、対数の乖離 ln k − ln k* は、毎期 (1 − λ) 倍になる。
λ = (1 − α)·δ が、収束の速さ。
"""

import math

import numpy as np

from lib.chapter04.difference import closed_form


def _check(
    saving_rate: float, depreciation: float, alpha: float, technology: float
) -> None:
    if not 0 < alpha < 1:
        raise ValueError("資本分配率は 0 より大きく 1 より小さくなければならない")
    if not 0 < saving_rate < 1:
        raise ValueError("貯蓄率は 0 より大きく 1 より小さくなければならない")
    if not 0 < depreciation <= 1:
        raise ValueError("減耗率は 0 より大きく 1 以下でなければならない")
    if technology <= 0:
        raise ValueError("技術水準は正でなければならない")


def steady_state_capital(
    saving_rate: float, depreciation: float, alpha: float, technology: float = 1
) -> float:
    """定常状態の資本 k* = (s·A ÷ δ)^(1 ÷ (1−α))（貯蓄 = 減耗となる資本）。"""
    _check(saving_rate, depreciation, alpha, technology)
    return float((saving_rate * technology / depreciation) ** (1 / (1 - alpha)))


def steady_state_output(
    saving_rate: float, depreciation: float, alpha: float, technology: float = 1
) -> float:
    """定常状態の所得 y* = A·k*^α。"""
    k = steady_state_capital(saving_rate, depreciation, alpha, technology)
    return float(technology * k**alpha)


def solow_step(
    capital: float,
    saving_rate: float,
    depreciation: float,
    alpha: float,
    technology: float = 1,
) -> float:
    """次の期の資本 s·A·k^α + (1−δ)·k を返す。"""
    _check(saving_rate, depreciation, alpha, technology)
    if capital <= 0:
        raise ValueError("資本は正でなければならない")
    return float(
        saving_rate * technology * capital**alpha + (1 - depreciation) * capital
    )


def solow_path(
    capital: float,
    saving_rate: float,
    depreciation: float,
    alpha: float,
    periods: int,
    technology: float = 1,
) -> list[float]:
    """初期の資本から、periods 期先までの資本の経路（初期値を含む）を返す。"""
    if periods < 0:
        raise ValueError("繰り返しの回数は 0 以上でなければならない")
    path = [capital]
    for _ in range(periods):
        path.append(solow_step(path[-1], saving_rate, depreciation, alpha, technology))
    return path


def convergence_speed(alpha: float, depreciation: float) -> float:
    """収束の速さ λ = (1 − α)·δ。定常状態の近くで、対数の乖離が毎期 λ の割合で縮む。"""
    return (1 - alpha) * depreciation


def half_life(speed: float) -> float:
    """乖離が半分になる期間 = ln 2 ÷ (−ln(1 − λ))。"""
    if not 0 < speed < 1:
        raise ValueError("収束の速さは 0 より大きく 1 より小さくなければならない")
    return math.log(2) / -math.log(1 - speed)


def log_linear_path(
    capital: float, steady_capital: float, speed: float, periods: int
) -> list[float]:
    """対数線形近似の経路: ln k(t) − ln k* = (1 − λ)^t·(ln k(0) − ln k*)。

    第 4 章の閉じた形（a = 1 − λ、b = λ·ln k*）を、対数の資本に使う。
    """
    log_steady = math.log(steady_capital)
    return [
        float(np.exp(closed_form(1 - speed, speed * log_steady, math.log(capital), t)))
        for t in range(periods + 1)
    ]


def approximation_error(
    capital: float,
    saving_rate: float,
    depreciation: float,
    alpha: float,
    periods: int,
    technology: float = 1,
) -> float:
    """厳密な経路と、対数線形近似の経路の差（絶対値）の最大値。"""
    exact = solow_path(capital, saving_rate, depreciation, alpha, periods, technology)
    approx = log_linear_path(
        capital,
        steady_state_capital(saving_rate, depreciation, alpha, technology),
        convergence_speed(alpha, depreciation),
        periods,
    )
    return max(abs(e - a) for e, a in zip(exact, approx, strict=True))
