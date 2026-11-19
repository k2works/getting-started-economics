"""需要表と供給表（価格 -> 数量の辞書）。"""

from collections.abc import Mapping

from lib.chapter01.demand import quantity_demanded


def quantity_supplied(price: float, intercept: float, slope: float) -> float:
    """価格 P のときの供給量 Q = c + dP を返す。供給量は負にならない。"""
    if price < 0:
        raise ValueError("価格は 0 以上でなければならない")
    return max(intercept + slope * price, 0)


def demand_schedule(
    prices: list[int], intercept: float, slope: float
) -> dict[int, float]:
    """価格ごとの需要量を並べた需要表を返す。"""
    return {p: quantity_demanded(p, intercept, slope) for p in prices}


def supply_schedule(
    prices: list[int], intercept: float, slope: float
) -> dict[int, float]:
    """価格ごとの供給量を並べた供給表を返す。"""
    return {p: quantity_supplied(p, intercept, slope) for p in prices}


def excess_demand(
    demand: Mapping[int, float], supply: Mapping[int, float]
) -> dict[int, float]:
    """価格ごとの超過需要（需要量 - 供給量）を返す。両方の表にある価格だけを扱う。"""
    return {p: demand[p] - supply[p] for p in demand if p in supply}


def market_clearing_prices(
    demand: Mapping[int, float], supply: Mapping[int, float]
) -> list[int]:
    """超過需要が 0 になる価格（市場均衡の価格）を返す。"""
    return [p for p, gap in excess_demand(demand, supply).items() if gap == 0]
