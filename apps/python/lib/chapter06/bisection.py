"""二分法で均衡価格を求める。"""

from collections.abc import Callable

from lib.chapter01.demand import quantity_demanded
from lib.chapter03.schedule import quantity_supplied


class NoEquilibriumError(ValueError):
    """指定した区間に均衡価格が見つからないときの例外。"""


def make_excess_demand(
    demand_intercept: float,
    demand_slope: float,
    supply_intercept: float,
    supply_slope: float,
) -> Callable[[float], float]:
    """価格を受け取り超過需要（需要量 - 供給量）を返す関数を作る。"""

    def excess_demand(price: float) -> float:
        demand = quantity_demanded(price, demand_intercept, demand_slope)
        supply = quantity_supplied(price, supply_intercept, supply_slope)
        return demand - supply

    return excess_demand


def find_equilibrium_price(
    excess_demand: Callable[[float], float],
    low: float,
    high: float,
    tolerance: float = 1e-9,
    max_iterations: int = 100,
) -> float:
    """区間 [low, high] を半分ずつに絞り、超過需要が 0 になる価格を返す。"""
    if low >= high:
        raise ValueError("下限は上限より小さくなければならない")
    if excess_demand(low) * excess_demand(high) > 0:
        raise NoEquilibriumError(
            "区間の両端で超過需要の符号が同じなので均衡が見つからない"
        )
    for _ in range(max_iterations):
        if high - low < tolerance:
            break
        middle = (low + high) / 2
        if excess_demand(low) * excess_demand(middle) <= 0:
            high = middle
        else:
            low = middle
    return (low + high) / 2
