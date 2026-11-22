"""需要の価格弾力性: 価格が 1% 変わると、需要量が何 % 変わるか。"""

import math
from collections.abc import Callable

from lib.chapter01.market import demand_quantity
from lib.chapter05.derivative import numerical_derivative


def _require_elasticity_point(price: float, quantity: float) -> None:
    if price < 0:
        raise ValueError("価格は、負であってはなりません")
    if quantity <= 0:
        raise ValueError("需要量が正の点でだけ、弾力性を求めます")


def point_price_elasticity(
    demand: Callable[[float], float], price: float, step: float = 1e-5
) -> float:
    """点弾力性 ε = −(dq/dp)·(p/q)。傾き dq/dp は、中心差分で求める。"""
    quantity = demand(price)
    _require_elasticity_point(price, quantity)
    return -numerical_derivative(demand, price, step) * price / quantity


def linear_demand_elasticity(price: float, a: float, b: float) -> float:
    """直線の需要 q = a − b·p の点弾力性 ε = b·p ÷ q（公式）。"""
    quantity = demand_quantity(price, a, b)
    _require_elasticity_point(price, quantity)
    return b * price / quantity


def classify_elasticity(elasticity: float) -> str:
    """ε > 1 なら弾力的、< 1 なら非弾力的、ほぼ 1 なら単位弾力的。"""
    if math.isclose(elasticity, 1, abs_tol=1e-9):
        return "unit elastic"
    return "elastic" if elasticity > 1 else "inelastic"


def sales_revenue(demand: Callable[[float], float], price: float) -> float:
    """売り手の収入 R(p) = p·q(p)。"""
    return price * demand(price)


def revenue_price_slope(
    demand: Callable[[float], float], price: float, step: float = 1e-5
) -> float:
    """収入の価格についての傾き dR/dp（数値微分）。公式では q·(1 − ε)。"""
    return numerical_derivative(lambda p: sales_revenue(demand, p), price, step)


def constant_elasticity_demand(price: float, scale: float, elasticity: float) -> float:
    """弾力性が一定の需要 q = A·p^(−ε)。"""
    if price <= 0:
        raise ValueError("価格が正のときだけ、p^(−ε) を計算します")
    factor: float = price**-elasticity
    return scale * factor


def elasticity_by_logs(
    demand: Callable[[float], float], price: float, step: float = 1e-5
) -> float:
    """ε = −d ln q ÷ d ln p。u = ln p とおき、ln q(e^u) を u で微分する。"""
    if price <= 0:
        raise ValueError("価格が正のときだけ、ln p を計算します")
    _require_elasticity_point(price, demand(price))

    def log_demand(u: float) -> float:
        return math.log(demand(math.exp(u)))

    return -numerical_derivative(log_demand, math.log(price), step)


def arc_price_elasticity(
    demand: Callable[[float], float], price0: float, price1: float
) -> float:
    """弧弾力性: 変化率を、区間の両端の平均（中点）で割って測る。"""
    if price0 == price1:
        raise ValueError("弧弾力性には、違う 2 つの価格が必要です")
    q0, q1 = demand(price0), demand(price1)
    quantity_change = (q1 - q0) / ((q0 + q1) / 2)
    price_change = (price1 - price0) / ((price0 + price1) / 2)
    return -quantity_change / price_change
