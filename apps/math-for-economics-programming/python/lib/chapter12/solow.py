"""ソロー・モデル: 資本の蓄積 k(t + 1) = s·f(k(t)) + (1 − δ)·k(t)、f(k) = k^α。"""

from lib.chapter02.quadratic import argmax_on_grid


def _check_solow(saving: float, alpha: float, depreciation: float) -> None:
    if not 0 <= saving <= 1:
        raise ValueError("貯蓄率 s は 0 以上 1 以下でなければなりません")
    if not 0 < alpha < 1:
        raise ValueError("資本の分配率 α は 0 < α < 1 でなければなりません")
    if not 0 < depreciation <= 1:
        raise ValueError("減耗率 δ は 0 より大きく 1 以下でなければなりません")


def solow_next_capital(
    capital: float, saving: float, alpha: float, depreciation: float
) -> float:
    """来期の資本 = 貯蓄（投資）s·k^α + 減耗の後に残る資本 (1 − δ)·k。"""
    _check_solow(saving, alpha, depreciation)
    if capital < 0:
        raise ValueError("資本は 0 以上でなければなりません")
    return float(saving * capital**alpha + (1 - depreciation) * capital)


def solow_capital_path(
    start: float, saving: float, alpha: float, depreciation: float, periods: int
) -> list[float]:
    """k(0) = start から、periods 期先までの資本の列（長さ periods + 1）。"""
    if periods < 0:
        raise ValueError("期数は 0 以上でなければなりません")
    path = [start]
    for _ in range(periods):
        path.append(solow_next_capital(path[-1], saving, alpha, depreciation))
    return path


def solow_steady_state_capital(
    saving: float, alpha: float, depreciation: float
) -> float:
    """s·k^α = δ·k を解いた定常状態 k* = (s ÷ δ)^(1 ÷ (1 − α))。"""
    _check_solow(saving, alpha, depreciation)
    return float((saving / depreciation) ** (1 / (1 - alpha)))


def solow_steady_state_consumption(
    saving: float, alpha: float, depreciation: float
) -> float:
    """定常状態の消費 c* = f(k*) − δ·k*（生産のうち、資本の維持に使わない分）。"""
    capital = solow_steady_state_capital(saving, alpha, depreciation)
    return float(capital**alpha - depreciation * capital)


def golden_rule_saving_by_grid(alpha: float, depreciation: float, points: int) -> float:
    """0 から 1 までの貯蓄率の格子で、定常状態の消費が最大の貯蓄率（黄金律）。"""
    return argmax_on_grid(
        lambda s: solow_steady_state_consumption(s, alpha, depreciation), 0, 1, points
    )


def solow_convergence_factor(alpha: float, depreciation: float) -> float:
    """定常状態での漸化式の傾き 1 − δ(1 − α)。差は、毎期ほぼこの倍になる。"""
    return 1 - depreciation * (1 - alpha)


def _checked_growth_factor(
    depreciation: float, population_growth: float, technology_growth: float
) -> float:
    growth = (1 + population_growth) * (1 + technology_growth)
    if depreciation + growth - 1 <= 0:
        raise ValueError("δ + n + g + n·g が正でなければ、定常状態は決まりません")
    return growth


def solow_next_capital_with_growth(
    capital: float,
    saving: float,
    alpha: float,
    depreciation: float,
    population_growth: float,
    technology_growth: float,
) -> float:
    """効率労働 1 単位あたりの資本: 来期の資本を (1 + n)(1 + g) で割る。"""
    growth = _checked_growth_factor(depreciation, population_growth, technology_growth)
    return solow_next_capital(capital, saving, alpha, depreciation) / growth


def solow_steady_state_with_growth(
    saving: float,
    alpha: float,
    depreciation: float,
    population_growth: float,
    technology_growth: float,
) -> float:
    """k* = (s ÷ (δ + n + g + n·g))^(1 ÷ (1 − α))。"""
    _check_solow(saving, alpha, depreciation)
    growth = _checked_growth_factor(depreciation, population_growth, technology_growth)
    return float((saving / (depreciation + growth - 1)) ** (1 / (1 - alpha)))
