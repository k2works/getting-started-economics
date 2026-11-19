"""AD-AS 分析。総需要曲線は、第 13 章の IS-LM モデルから導く。"""

import dataclasses
from collections.abc import Callable

from lib.chapter06.bisection import find_equilibrium_price
from lib.chapter13.islm import IsLmModel, solve_equilibrium


def aggregate_demand(model: IsLmModel, price_level: float) -> float:
    """総需要: 物価水準 P のときの、IS-LM の均衡の所得。

    物価が上がると実質貨幣供給 M / P が減り、LM 曲線が左へ動いて、所得が減る。
    """
    income, _ = solve_equilibrium(dataclasses.replace(model, price_level=price_level))
    return income


def classical_supply(price: float, full_employment_income: float) -> float:
    """古典派の総供給: 物価によらず、完全雇用所得で垂直。"""
    return full_employment_income


def keynesian_supply(
    price: float,
    full_employment_income: float,
    full_employment_price: float,
    slope: float,
) -> float:
    """ケインズの総供給: 完全雇用の物価までは右上がり、それ以降は垂直。

    物価が 1 下がるごとに、所得が slope だけ減る。
    """
    return min(
        full_employment_income,
        full_employment_income - slope * (full_employment_price - price),
    )


def equilibrium_price_and_income(
    model: IsLmModel,
    supply: Callable[[float], float],
    low: float = 0.2,
    high: float = 5.0,
) -> tuple[float, float]:
    """総需要と総供給が等しくなる物価と所得を、二分法で求める。"""
    price = find_equilibrium_price(
        lambda p: aggregate_demand(model, p) - supply(p), low, high
    )
    return price, aggregate_demand(model, price)
