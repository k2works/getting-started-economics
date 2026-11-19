"""第 3 章: 需要表・供給表のテスト。"""

import pytest

from lib.chapter03.schedule import (
    demand_schedule,
    excess_demand,
    market_clearing_prices,
    quantity_supplied,
    supply_schedule,
)

PRICES = [0, 10, 20, 30]


def test_供給量は価格に比例して増える() -> None:
    assert quantity_supplied(price=10, intercept=0, slope=3) == 30


def test_負の価格は受け付けない() -> None:
    with pytest.raises(ValueError):
        quantity_supplied(price=-1, intercept=0, slope=3)


def test_需要表は価格ごとの需要量を並べた辞書() -> None:
    assert demand_schedule(PRICES, intercept=100, slope=2) == {
        0: 100,
        10: 80,
        20: 60,
        30: 40,
    }


def test_供給表は価格ごとの供給量を並べた辞書() -> None:
    assert supply_schedule(PRICES, intercept=0, slope=3) == {
        0: 0,
        10: 30,
        20: 60,
        30: 90,
    }


def test_超過需要は需要量から供給量を引いたもの() -> None:
    demand = demand_schedule(PRICES, intercept=100, slope=2)
    supply = supply_schedule(PRICES, intercept=0, slope=3)
    assert excess_demand(demand, supply) == {0: 100, 10: 50, 20: 0, 30: -50}


def test_超過需要が0になる価格が市場均衡の価格() -> None:
    demand = demand_schedule(PRICES, intercept=100, slope=2)
    supply = supply_schedule(PRICES, intercept=0, slope=3)
    assert market_clearing_prices(demand, supply) == [20]


def test_需要表と供給表で価格が共通でなければ超過需要は共通の価格だけ求める() -> None:
    demand = {10: 80, 20: 60}
    supply = {20: 60, 30: 90}
    assert excess_demand(demand, supply) == {20: 0}
