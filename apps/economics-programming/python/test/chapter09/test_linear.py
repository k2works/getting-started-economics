"""第 9 章: NumPy による配列計算のテスト。"""

import numpy as np
import pytest

from lib.chapter01.demand import quantity_demanded
from lib.chapter07.surplus import equilibrium
from lib.chapter09.linear import (
    demand_quantities,
    equilibrium_by_linear_algebra,
    income_determination,
    multiplier,
    spending_rounds,
)


def test_限界消費性向が0_8なら乗数は5() -> None:
    assert multiplier(0.8) == pytest.approx(5)


@pytest.mark.parametrize("mpc", [-0.1, 1.0, 1.5])
def test_限界消費性向は0以上1未満でなければならない(mpc: float) -> None:
    with pytest.raises(ValueError):
        multiplier(mpc)


def test_支出の波及は各回で限界消費性向倍になる() -> None:
    rounds = spending_rounds(initial_spending=100, mpc=0.8, count=3)
    assert rounds.tolist() == pytest.approx([100, 80, 64])


def test_波及を足し合わせると初期支出かける乗数に近づく() -> None:
    rounds = spending_rounds(initial_spending=100, mpc=0.8, count=100)
    assert rounds.sum() == pytest.approx(100 * multiplier(0.8), abs=1e-6)


def test_累積の波及は3回目までで244() -> None:
    rounds = spending_rounds(initial_spending=100, mpc=0.8, count=3)
    assert np.cumsum(rounds).tolist() == pytest.approx([100, 180, 244])


def test_国民所得は消費と投資の和と等しくなる() -> None:
    # 消費 C = 20 + 0.8Y、投資 I = 30、Y = C + I を解くと Y = 250、C = 220
    income, consumption = income_determination(
        autonomous_consumption=20, mpc=0.8, investment=30
    )
    assert income == pytest.approx(250)
    assert consumption == pytest.approx(220)
    assert income == pytest.approx(consumption + 30)


def test_限界消費性向が1以上なら所得は決まらない() -> None:
    with pytest.raises(ValueError):
        income_determination(autonomous_consumption=20, mpc=1.0, investment=30)


def test_連立方程式で均衡価格20と均衡数量60を求める() -> None:
    price, quantity = equilibrium_by_linear_algebra(
        demand_intercept=100, demand_slope=2, supply_intercept=0, supply_slope=3
    )
    assert price == pytest.approx(20)
    assert quantity == pytest.approx(60)


def test_配列で需要量をまとめて計算できる() -> None:
    prices = np.array([0, 10, 20, 30])
    result = demand_quantities(prices, intercept=100, slope=2)
    assert result.tolist() == [100, 80, 60, 40]


def test_配列の計算結果は1つずつ計算した結果と一致する() -> None:
    prices = np.array([0, 10, 20, 30, 60])
    expected = [quantity_demanded(float(p), 100, 2) for p in prices]
    assert demand_quantities(prices, intercept=100, slope=2).tolist() == expected


def test_配列でも負の価格は受け付けない() -> None:
    with pytest.raises(ValueError):
        demand_quantities(np.array([10, -1]), intercept=100, slope=2)


@pytest.mark.parametrize(
    ("supply_intercept", "price", "quantity"),
    [(0, 20, 60), (10, 18, 64), (-30, 26, 48)],
)
def test_供給曲線の切片が違っても連立方程式で均衡を求められる(
    supply_intercept: float, price: float, quantity: float
) -> None:
    result = equilibrium_by_linear_algebra(
        demand_intercept=100,
        demand_slope=2,
        supply_intercept=supply_intercept,
        supply_slope=3,
    )
    assert result == pytest.approx((price, quantity))


@pytest.mark.parametrize("supply_intercept", [0, 10, -30])
def test_連立方程式の解は第7章の閉形式の解と一致する(supply_intercept: float) -> None:
    market = {
        "demand_intercept": 100,
        "demand_slope": 2,
        "supply_intercept": supply_intercept,
        "supply_slope": 3,
    }
    assert equilibrium_by_linear_algebra(**market) == pytest.approx(
        equilibrium(**market)
    )
