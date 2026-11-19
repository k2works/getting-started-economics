"""第 6 章: 二分法による均衡価格のテスト。"""

import pytest

from lib.chapter06.bisection import (
    NoEquilibriumError,
    find_equilibrium_price,
    make_excess_demand,
)


def test_超過需要の関数は需要量から供給量を引く() -> None:
    excess = make_excess_demand(
        demand_intercept=100, demand_slope=2, supply_intercept=0, supply_slope=3
    )
    assert excess(10) == 50


def test_二分法で均衡価格20を求める() -> None:
    excess = make_excess_demand(
        demand_intercept=100, demand_slope=2, supply_intercept=0, supply_slope=3
    )
    assert find_equilibrium_price(excess, low=0, high=100) == pytest.approx(20)


def test_表にない価格の均衡も求められる() -> None:
    # 100 - 2P = 10 + 3P のとき P = 18。第 3 章の表（0, 10, 20, 30）には載っていない
    excess = make_excess_demand(
        demand_intercept=100, demand_slope=2, supply_intercept=10, supply_slope=3
    )
    assert find_equilibrium_price(excess, low=0, high=100) == pytest.approx(18)


def test_区間の両端で超過需要の符号が同じなら均衡は見つからない() -> None:
    excess = make_excess_demand(
        demand_intercept=100, demand_slope=2, supply_intercept=0, supply_slope=3
    )
    with pytest.raises(NoEquilibriumError):
        find_equilibrium_price(excess, low=30, high=100)


def test_均衡が見つからない例外は値の誤りの一種() -> None:
    assert issubclass(NoEquilibriumError, ValueError)


def test_下限が上限以上なら区間として成り立たない() -> None:
    excess = make_excess_demand(
        demand_intercept=100, demand_slope=2, supply_intercept=0, supply_slope=3
    )
    with pytest.raises(ValueError):
        find_equilibrium_price(excess, low=50, high=10)
