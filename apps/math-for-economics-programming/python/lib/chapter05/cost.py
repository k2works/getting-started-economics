"""費用関数 C(q)（多項式）の諸概念と、価格を所与とする企業の利潤最大化。"""

import math

from lib.chapter05.derivative import (
    Polynomial,
    classify_stationary_point,
    stationary_points,
)


def _require_positive(quantity: float) -> None:
    if quantity <= 0:
        raise ValueError("平均費用は、正の数量でだけ定義されます")


def _require_convex_cost(cost: Polynomial) -> None:
    degree = len(cost.coefficients) - 1
    if degree not in (2, 3) or cost.coefficients[-1] <= 0:
        raise ValueError("最高次の係数が正の、2 次か 3 次の費用だけを扱います")


def fixed_cost(cost: Polynomial) -> float:
    """固定費用: 作らなくてもかかる費用 C(0)。"""
    return cost(0)


def variable_cost(cost: Polynomial, quantity: float) -> float:
    """可変費用: 作る量に応じてかかる費用 C(q) − C(0)。"""
    return cost(quantity) - fixed_cost(cost)


def average_cost(cost: Polynomial, quantity: float) -> float:
    """平均費用 AC = C(q) ÷ q。"""
    _require_positive(quantity)
    return cost(quantity) / quantity


def average_variable_cost(cost: Polynomial, quantity: float) -> float:
    """平均可変費用 AVC = (C(q) − C(0)) ÷ q。"""
    _require_positive(quantity)
    return variable_cost(cost, quantity) / quantity


def marginal_cost(cost: Polynomial, quantity: float) -> float:
    """限界費用 MC = C'(q): あと 1 単位作るときに増える費用（の近似）。"""
    return cost.derivative()(quantity)


def competitive_profit(price: float, cost: Polynomial, quantity: float) -> float:
    """価格 P を所与とする企業の利潤 π(q) = P·q − C(q)。"""
    return price * quantity - cost(quantity)


def profit_maximizing_quantity(price: float, cost: Polynomial) -> float:
    """P = MC（MC が右上がり）の数量。利潤が、作らないとき（−固定費用）未満なら 0。"""
    _require_convex_cost(cost)
    profit = Polynomial((0, price)) + cost.scale(-1)
    candidates = [
        q
        for q in stationary_points(profit)
        if q > 0 and classify_stationary_point(profit, q) == "maximum"
    ]
    best = max(candidates, key=profit, default=0.0)
    return best if profit(best) >= profit(0) else 0.0


def minimum_average_cost(cost: Polynomial) -> tuple[float, float]:
    """2 次の費用 c₀ + c₁q + c₂q² の平均費用の最小点。AC' = −c₀ ÷ q² + c₂ = 0。"""
    if len(cost.coefficients) != 3:
        raise ValueError("2 次の費用だけを扱います")
    c0, _, c2 = cost.coefficients
    if c0 <= 0 or c2 <= 0:
        raise ValueError("固定費用と 2 乗の係数は、正でなければなりません")
    q = math.sqrt(c0 / c2)
    return q, average_cost(cost, q)


def minimum_average_variable_cost(cost: Polynomial) -> tuple[float, float]:
    """平均可変費用 c₁ + c₂q + c₃q² の最小点（操業停止点）。頂点が負なら q → 0。"""
    _require_convex_cost(cost)
    avc = Polynomial(cost.coefficients[1:])
    if len(avc.coefficients) == 3:
        (q,) = stationary_points(avc)
        if q > 0:
            return q, avc(q)
    return 0.0, avc(0)
