"""SciPy による最適化（効用最大化・利潤最大化・費用最小化）。"""

from scipy.optimize import brentq, minimize, minimize_scalar

from lib.chapter04.cost import average_variable_cost, marginal_cost
from lib.chapter04.utility import cobb_douglas_utility

# 限界費用が最低になる生産量。これより右では限界費用が右上がり
_MC_MINIMUM_QUANTITY = 2
# 生産量を探す範囲の上限
_MAX_QUANTITY = 10
# 数値計算の誤差を許す幅
_EPSILON = 1e-9


def maximize_utility(
    price_x: float, price_y: float, income: float, alpha: float = 0.5
) -> tuple[float, float]:
    """予算 price_x·x + price_y·y = income のもとで、効用を最大にする (x, y) を返す。"""
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

    価格が平均可変費用の最低値（操業停止点）を下回れば、生産しない。
    そうでなければ、P = MC（限界費用が右上がりの部分）を満たす生産量を求める。
    """
    shutdown_price = minimize_scalar(
        average_variable_cost, bounds=(0, _MAX_QUANTITY), method="bounded"
    ).fun
    if price < shutdown_price - _EPSILON:
        return 0
    return float(
        brentq(
            lambda q: marginal_cost(q) - price,
            _MC_MINIMUM_QUANTITY,
            _MAX_QUANTITY,
        )
    )


def minimize_cost(
    output: float, wage: float, rental: float
) -> tuple[float, float, float]:
    """産出量 output を作る費用 wage·L + rental·K を最小にする (L, K, 費用) を返す。

    生産関数は、コブ・ダグラス型 Q = L^0.5 · K^0.5（第 4 章の関数と同じ形）。
    """
    result = minimize(
        lambda v: wage * v[0] + rental * v[1],
        x0=[output, output],
        bounds=[(_EPSILON, None), (_EPSILON, None)],
        constraints={
            "type": "eq",
            "fun": lambda v: cobb_douglas_utility(v[0], v[1]) - output,
        },
        method="SLSQP",
        options={"ftol": 1e-12},
    )
    if not result.success:
        raise RuntimeError(f"費用最小化が収束しなかった: {result.message}")
    return float(result.x[0]), float(result.x[1]), float(result.fun)
