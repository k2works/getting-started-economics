"""需要曲線と弾力性。

価格を動かしながら、最適消費点（第 2 章）を求め、財 x の量を価格に対して並べたものが、
需要曲線。価格弾力性は、需要の変化率を、価格の変化率で割った値（大きさ）。
"""

from collections.abc import Callable, Sequence

from lib.chapter01.validation import validate_positive
from lib.chapter02.budget import optimal_bundle

# 数値微分の幅と、弾力性の分類で、同じ値と見なす誤差
_STEP = 1e-6
_TOLERANCE = 1e-6


def demand_x(
    income: float, px: float, py: float, a: float = 1.0, b: float = 1.0
) -> float:
    """財 x の需要量（最適消費点の x）。a = b なら、m ÷ (2·Px)。"""
    return optimal_bundle(income, px, py, a, b)[0]


def demand_curve(
    income: float, prices: Sequence[float], py: float, a: float = 1.0, b: float = 1.0
) -> list[tuple[float, float]]:
    """価格ごとの需要量 (価格, 需要量) の並び。価格を下げると、需要量が増える。"""
    return [(p, demand_x(income, p, py, a, b)) for p in prices]


def market_demand(
    incomes: Sequence[float], px: float, py: float, a: float = 1.0, b: float = 1.0
) -> float:
    """市場需要。所得の違う消費者の需要を、同じ価格で、横に足す。"""
    return sum(demand_x(m, px, py, a, b) for m in incomes)


def market_demand_curve(
    incomes: Sequence[float],
    prices: Sequence[float],
    py: float,
    a: float = 1.0,
    b: float = 1.0,
) -> list[tuple[float, float]]:
    """価格ごとの市場需要 (価格, 市場需要) の並び。"""
    return [(p, market_demand(incomes, p, py, a, b)) for p in prices]


def linear_demand_quantity(intercept: float, slope: float, price: float) -> float:
    """直線の需要曲線 Q = 切片 + 傾き × P。需要量は、負にならない。"""
    return max(0.0, intercept + slope * price)


def price_elasticity_linear(intercept: float, slope: float, price: float) -> float:
    """直線の需要曲線の価格弾力性 e = −傾き × P ÷ Q。点の位置で変わる。"""
    quantity = linear_demand_quantity(intercept, slope, price)
    validate_positive(quantity, "需要量が 0 のとき、価格弾力性は求められない")
    return -slope * price / quantity


def price_elasticity(
    demand: Callable[[float], float], price: float, step: float = _STEP
) -> float:
    """価格弾力性 e = −(dQ/dP) × P ÷ Q（中心差分による数値微分）。"""
    validate_positive(price, "価格は、正にする")
    quantity = demand(price)
    validate_positive(quantity, "需要量が 0 のとき、価格弾力性は求められない")
    slope = (demand(price + step) - demand(price - step)) / (2 * step)
    return -slope * price / quantity


def elasticity_type(elasticity: float) -> str:
    """弾力性の大きさで、弾力的（> 1）・単位弾力的（= 1）・非弾力的（< 1）に分ける。"""
    size = abs(elasticity)
    if abs(size - 1) <= _TOLERANCE:
        return "単位弾力的"
    return "弾力的" if size > 1 else "非弾力的"


def income_elasticity(
    demand: Callable[[float], float], income: float, step: float = _STEP
) -> float:
    """所得弾力性 e = (dQ/dm) × m ÷ Q（中心差分による数値微分）。"""
    validate_positive(income, "所得は、正にする")
    quantity = demand(income)
    validate_positive(quantity, "需要量が 0 のとき、所得弾力性は求められない")
    slope = (demand(income + step) - demand(income - step)) / (2 * step)
    return slope * income / quantity


def classify_by_income_elasticity(elasticity: float) -> str:
    """所得弾力性で財を分ける。1 以上は奢侈品、0〜1 は必需品、負は下級財。"""
    if elasticity < -_TOLERANCE:
        return "下級財"
    if elasticity <= _TOLERANCE:
        return "中立財"
    return "奢侈品" if elasticity >= 1 - _TOLERANCE else "必需品"


def income_consumption_curve(
    incomes: Sequence[float], px: float, py: float, a: float = 1.0, b: float = 1.0
) -> list[tuple[float, float]]:
    """所得消費曲線。所得を動かしたときの、最適消費点 (x, y) の並び。"""
    return [optimal_bundle(m, px, py, a, b) for m in incomes]
