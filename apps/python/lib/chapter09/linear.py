"""NumPy による乗数効果・国民所得の決定・連立方程式。"""

import numpy as np
from numpy.typing import NDArray


def _check_mpc(mpc: float) -> None:
    if not 0 <= mpc < 1:
        raise ValueError("限界消費性向は 0 以上 1 未満でなければならない")


def multiplier(mpc: float) -> float:
    """乗数 1 / (1 - c) を返す。c は限界消費性向。"""
    _check_mpc(mpc)
    return 1 / (1 - mpc)


def spending_rounds(
    initial_spending: float, mpc: float, count: int
) -> NDArray[np.float64]:
    """初期支出が各回で限界消費性向倍になって波及する様子を、count 回分返す。"""
    _check_mpc(mpc)
    return (initial_spending * mpc ** np.arange(count)).astype(np.float64)


def income_determination(
    autonomous_consumption: float, mpc: float, investment: float
) -> tuple[float, float]:
    """国民所得 Y と消費 C を求める。

    Y = C + I と C = C0 + cY を、Y と C についての連立方程式として解く。
        Y -  C = I
     -c·Y +  C = C0
    """
    _check_mpc(mpc)
    coefficients = np.array([[1.0, -1.0], [-mpc, 1.0]])
    constants = np.array([investment, autonomous_consumption])
    income, consumption = np.linalg.solve(coefficients, constants)
    return float(income), float(consumption)


def equilibrium_by_linear_algebra(
    demand_intercept: float,
    demand_slope: float,
    supply_intercept: float,
    supply_slope: float,
) -> tuple[float, float]:
    """均衡価格と均衡数量を、連立方程式として解いて返す。

    Q + bP = a（需要曲線）
    Q - dP = c（供給曲線）
    """
    coefficients = np.array([[1.0, demand_slope], [1.0, -supply_slope]])
    constants = np.array([demand_intercept, supply_intercept])
    quantity, price = np.linalg.solve(coefficients, constants)
    return float(price), float(quantity)


def demand_quantities(
    prices: NDArray[np.float64], intercept: float, slope: float
) -> NDArray[np.float64]:
    """価格の配列から、需要量の配列を一度に計算する。需要量は負にならない。"""
    if np.any(prices < 0):
        raise ValueError("価格は 0 以上でなければならない")
    return np.maximum(intercept - slope * prices.astype(float), 0)
