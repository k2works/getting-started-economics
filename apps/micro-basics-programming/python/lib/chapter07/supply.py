"""利潤最大化と供給曲線（完全競争）。

完全競争の企業は、価格を決められない（プライステイカー）。利潤が最大になるのは、価格が限界費用と
等しい点（P = MC）。
- 損益分岐点: 価格が AC の最低点（利潤 0）
- 操業停止点: 価格が AVC の最低点（これ未満では、作るほど損）
- 供給曲線: 操業停止点より上の、限界費用曲線
"""

from collections.abc import Callable, Sequence

import numpy as np

from lib.chapter01.validation import validate_non_negative, validate_positive
from lib.chapter05.cost import CostCurve, cost_minima, marginal_cost, total_cost

_STEP = 1e-6


def shutdown_price(curve: CostCurve) -> float:
    """操業停止点の価格 = 平均可変費用 AVC の最低値。

    AVC = a·q² + b·q + c なので、最低点は q = −b ÷ (2a)（b ≥ 0 なら、q = 0）。
    """
    q = max(0.0, -curve.quadratic / (2 * curve.cubic))
    return curve.cubic * q**2 + curve.quadratic * q + curve.linear


def break_even_price(
    curve: CostCurve, q_max: float = 10.0, points: int = 10001
) -> float:
    """損益分岐点の価格 = 平均費用 AC の最低値（格子点の探索）。"""
    return cost_minima(curve, q_max, points)["AC"][1]


def profit(curve: CostCurve, price: float, q: float) -> float:
    """利潤 = 価格 × 生産量 − 総費用 = (P − AC) × q。"""
    return price * q - total_cost(curve, q)


def profit_maximizing_output(curve: CostCurve, price: float) -> float:
    """利潤を最大にする生産量（閉じた式）。P = MC の、右上がりの側の解。

    価格が操業停止点より低ければ、作らない（0）。
    MC = 3a·q² + 2b·q + c = P を、q について解く。
    """
    validate_non_negative(price, "価格は、0 以上にする")
    if price < shutdown_price(curve):
        return 0.0
    a, b, c = curve.cubic, curve.quadratic, curve.linear
    return float((-b + (b**2 - 3 * a * (c - price)) ** 0.5) / (3 * a))


def profit_maximizing_output_by_grid(
    curve: CostCurve, price: float, q_max: float = 10.0, points: int = 10001
) -> float:
    """生産量を格子点で動かして、利潤が最大の点を探す（閉じた式の答え合わせ用）。"""
    validate_positive(points - 2, "点の数は、3 以上にする")
    grid = np.linspace(0.0, q_max, points)
    profits = [profit(curve, price, float(q)) for q in grid]
    return float(grid[int(np.argmax(profits))])


def supply_curve(
    curve: CostCurve, prices: Sequence[float]
) -> list[tuple[float, float]]:
    """価格ごとの供給量 (価格, 供給量) の並び。操業停止点で、0 から跳ね上がる。"""
    return [(p, profit_maximizing_output(curve, p)) for p in prices]


def market_supply(curves: Sequence[CostCurve], price: float) -> float:
    """市場供給。各企業の供給を、同じ価格で、横に足す。操業停止点が高い企業は、退出する。"""
    return sum(profit_maximizing_output(curve, price) for curve in curves)


def market_supply_curve(
    curves: Sequence[CostCurve], prices: Sequence[float]
) -> list[tuple[float, float]]:
    """価格ごとの市場供給 (価格, 市場供給) の並び。"""
    return [(p, market_supply(curves, p)) for p in prices]


def supply_elasticity(
    supply: Callable[[float], float], price: float, step: float = _STEP
) -> float:
    """供給の価格弾力性 e = (dQ/dP) × P ÷ Q（中心差分による数値微分）。"""
    validate_positive(price, "価格は、正にする")
    quantity = supply(price)
    validate_positive(quantity, "供給量が 0 のとき、供給の価格弾力性は求められない")
    slope = (supply(price + step) - supply(price - step)) / (2 * step)
    return slope * price / quantity


def supply_price(curve: CostCurve, q: float) -> float:
    """生産量 q を供給する価格（逆供給曲線）。右上がりの側では、限界費用に等しい。"""
    return marginal_cost(curve, q)


def _check_rate(rate: float) -> None:
    validate_non_negative(rate, "税率は、0 以上にする")
    validate_positive(1 - rate, "税率は、1 未満にする")


def supply_price_unit_tax(curve: CostCurve, q: float, tax: float) -> float:
    """従量税（1 単位あたり tax 円）のもとで、生産量 q を供給する価格。MC + tax。"""
    validate_non_negative(tax, "税額は、0 以上にする")
    return marginal_cost(curve, q) + tax


def supply_price_ad_valorem(curve: CostCurve, q: float, rate: float) -> float:
    """従価税（税率 rate）のもとで、生産量 q を供給する価格。MC ÷ (1 − rate)。"""
    _check_rate(rate)
    return marginal_cost(curve, q) / (1 - rate)


def supply_after_unit_tax(curve: CostCurve, price: float, tax: float) -> float:
    """従量税のもとの供給量。企業の手取りは、価格 − tax。"""
    validate_non_negative(tax, "税額は、0 以上にする")
    return profit_maximizing_output(curve, max(price - tax, 0.0))


def supply_after_ad_valorem_tax(curve: CostCurve, price: float, rate: float) -> float:
    """従価税のもとの供給量。企業の手取りは、価格 × (1 − rate)。"""
    _check_rate(rate)
    return profit_maximizing_output(curve, price * (1 - rate))
