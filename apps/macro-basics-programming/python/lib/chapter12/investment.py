"""投資の理論: 加速度原理・資本ストック調整原理・トービンの q。"""

from collections.abc import Sequence


def accelerator_investment(capital_coefficient: float, income_change: float) -> float:
    """加速度原理 I = V × ΔY。資本係数 V は一定。所得の増加が止まると、0。"""
    if capital_coefficient < 0:
        raise ValueError("資本係数は、0 以上にする")
    return capital_coefficient * income_change


def accelerator_path(
    capital_coefficient: float, incomes: Sequence[float]
) -> list[float]:
    """所得の系列から、2 期目以降の投資を求める。"""
    return [
        accelerator_investment(capital_coefficient, now - before)
        for before, now in zip(incomes, incomes[1:], strict=False)
    ]


def desired_capital(capital_coefficient: float, income: float) -> float:
    """最適な資本ストック K* = V × Y。"""
    return capital_coefficient * income


def stock_adjustment_investment(
    adjust: float, desired: float, previous_capital: float
) -> float:
    """資本ストック調整原理 I = 加速子 × (最適な資本 − 前期の資本)。"""
    if adjust <= 0 or adjust > 1:
        raise ValueError("加速子は、0 より大きく 1 以下にする")
    return adjust * (desired - previous_capital)


def tobins_q(market_value: float, replacement_cost: float) -> float:
    """トービンの q = 企業の市場価値 ÷ 資本の再取得価格。"""
    if replacement_cost <= 0:
        raise ValueError("再取得価格は、正にする")
    return market_value / replacement_cost


def should_invest(q: float) -> bool:
    """q > 1 なら投資する。q ≤ 1 なら、投資しない。"""
    return q > 1
