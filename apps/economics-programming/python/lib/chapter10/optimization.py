"""SciPy による最適化（効用最大化・利潤最大化・費用最小化）。"""

from scipy.optimize import brentq, minimize, minimize_scalar

from lib.chapter04.cost import average_variable_cost, marginal_cost
from lib.chapter04.utility import cobb_douglas_utility

# 生産量を探す範囲の上限（下限は 0）
_MAX_QUANTITY = 10
# 数値計算の誤差を許す幅
_EPSILON = 1e-9
# 生産関数 Q = L^0.5 · K^0.5 の、労働の指数
_LABOR_SHARE = 0.5


def production(labor: float, capital: float) -> float:
    """生産関数 Q = L^0.5 · K^0.5（コブ・ダグラス型）。第 4 章の効用関数とは別。"""
    if labor < 0 or capital < 0:
        raise ValueError("生産要素の量は 0 以上でなければならない")
    return float(labor**_LABOR_SHARE * capital ** (1 - _LABOR_SHARE))


def maximize_utility(
    price_x: float, price_y: float, income: float, alpha: float = 0.5
) -> tuple[float, float]:
    """予算 price_x·x + price_y·y = income のもとで、効用を最大にする (x, y) を返す。"""
    if price_x <= 0 or price_y <= 0:
        raise ValueError("財の価格は正でなければならない")
    if income <= 0:
        raise ValueError("所得は正でなければならない")
    result = minimize(
        lambda v: -cobb_douglas_utility(v[0], v[1], alpha),
        x0=[income / (2 * price_x), income / (2 * price_y)],
        bounds=[(_EPSILON, None), (_EPSILON, None)],
        constraints={
            "type": "eq",
            "fun": lambda v: price_x * v[0] + price_y * v[1] - income,
        },
        method="SLSQP",
        options={"ftol": 1e-12},
    )
    if not result.success:
        raise RuntimeError(f"効用最大化が収束しなかった: {result.message}")
    return float(result.x[0]), float(result.x[1])


def profit_maximizing_quantity(price: float) -> float:
    """価格 price のとき、利潤を最大にする生産量を返す。

    P = MC（限界費用が右上がりの部分）を満たす生産量を求める。その生産量で
    価格が平均可変費用を下回るなら、操業を停止して、生産しない。
    探索範囲（0〜10）の上限での限界費用より高い価格は、受け付けない。
    """
    # 限界費用が最低になる生産量。これより右では、限界費用が右上がり
    rising_start = float(
        minimize_scalar(marginal_cost, bounds=(0, _MAX_QUANTITY), method="bounded").x
    )
    if price <= marginal_cost(rising_start):
        return 0
    if price > marginal_cost(_MAX_QUANTITY):
        raise ValueError("価格が高すぎて、生産量の探索範囲（0〜10）に解がない")
    quantity = float(
        brentq(lambda q: marginal_cost(q) - price, rising_start, _MAX_QUANTITY)
    )
    if price < average_variable_cost(quantity) - _EPSILON:
        return 0
    return quantity


def minimize_cost(
    output: float, wage: float, rental: float
) -> tuple[float, float, float]:
    """産出量 output を作る費用 wage·L + rental·K を最小にする (L, K, 費用) を返す。

    生産関数は、コブ・ダグラス型 Q = L^0.5 · K^0.5（上の `production`）。
    """
    if output <= 0:
        raise ValueError("産出量は正でなければならない")
    if wage <= 0 or rental <= 0:
        raise ValueError("生産要素の価格は正でなければならない")
    result = minimize(
        lambda v: wage * v[0] + rental * v[1],
        x0=[output, output],
        bounds=[(_EPSILON, None), (_EPSILON, None)],
        constraints={
            "type": "eq",
            "fun": lambda v: production(v[0], v[1]) - output,
        },
        method="SLSQP",
        options={"ftol": 1e-12},
    )
    if not result.success:
        raise RuntimeError(f"費用最小化が収束しなかった: {result.message}")
    return float(result.x[0]), float(result.x[1]), float(result.fun)
