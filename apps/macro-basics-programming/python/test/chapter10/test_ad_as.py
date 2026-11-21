"""第 10 章: AD-AS のテスト。"""

import math

import pytest

from lib.chapter08.is_lm import solve_is_lm
from lib.chapter10.ad_as import (
    AdEconomy,
    aggregate_demand_income,
    classical_supply,
    expand_demand,
    keynesian_supply,
    shift_supply,
    solve_ad_as,
)

# c = 0.6、b = 20、IS の切片 450、k = 0.5、h = 100、名目貨幣供給 250
# AD: Y = 900 + 100 ÷ P
ECONOMY = AdEconomy(mpc=0.6, b=20, intercept=450, k=0.5, h=100, nominal_money=250)
FULL = 1000
BASE = 480
SLOPE = 400


def classical(price: float) -> float:
    return classical_supply(price, FULL)


def keynesian(price: float) -> float:
    return keynesian_supply(price, FULL, BASE, SLOPE)


def test_物価1での総需要は第8章のIS_LMの均衡所得() -> None:
    income, _ = solve_is_lm(0.6, 20, 450, 0.5, 100, 250)
    assert aggregate_demand_income(ECONOMY, 1) == pytest.approx(income)
    assert income == pytest.approx(1000)


def test_総需要は右下がりで物価が上がると所得は減る() -> None:
    assert aggregate_demand_income(ECONOMY, 2) == pytest.approx(950)
    assert aggregate_demand_income(ECONOMY, 0.5) == pytest.approx(1100)
    assert aggregate_demand_income(ECONOMY, 2) < aggregate_demand_income(ECONOMY, 1)


def test_物価が0以下ならエラー() -> None:
    with pytest.raises(ValueError, match="物価"):
        aggregate_demand_income(ECONOMY, 0)


def test_古典派の総供給は物価によらず完全雇用所得() -> None:
    assert [classical(p) for p in (0.5, 1, 3)] == [1000, 1000, 1000]


def test_ケインズの総供給は右上がりのち垂直() -> None:
    assert keynesian(0.5) == pytest.approx(680)
    assert keynesian(1.25) == pytest.approx(980)
    assert keynesian(1.3) == pytest.approx(1000)
    assert keynesian(2) == 1000


def test_総供給で物価が0以下ならエラー() -> None:
    with pytest.raises(ValueError, match="物価"):
        classical_supply(0, FULL)
    with pytest.raises(ValueError, match="物価"):
        keynesian_supply(-1, FULL, BASE, SLOPE)


def test_ケインズの総供給の傾きが0以下ならエラー() -> None:
    with pytest.raises(ValueError, match="傾き"):
        keynesian_supply(1, FULL, BASE, 0)


def test_古典派の均衡は物価1で所得は完全雇用所得() -> None:
    price, income = solve_ad_as(ECONOMY, classical)
    assert price == pytest.approx(1)
    assert income == pytest.approx(1000)


def test_古典派では拡張的な財政政策は物価だけを上げる() -> None:
    expanded = expand_demand(ECONOMY, delta_government=10)
    price, income = solve_ad_as(expanded, classical)
    assert income == pytest.approx(1000)
    assert price == pytest.approx(1.25)


def test_古典派では貨幣供給を増やしても物価だけが上がる() -> None:
    expanded = expand_demand(ECONOMY, delta_nominal_money=50)
    price, income = solve_ad_as(expanded, classical)
    assert income == pytest.approx(1000)
    assert price == pytest.approx(1.2)


def test_ケインズの均衡は右上がりの部分で物価1_25所得980() -> None:
    price, income = solve_ad_as(ECONOMY, keynesian)
    assert price == pytest.approx(1.25)
    assert income == pytest.approx(980)


def test_ケインズの右上がり部分では所得も物価も上がる() -> None:
    price0, income0 = solve_ad_as(ECONOMY, keynesian)
    expanded = expand_demand(ECONOMY, delta_government=10)
    price, income = solve_ad_as(expanded, keynesian)
    assert price == pytest.approx((4.4 + math.sqrt(35.36)) / 8)
    assert income == pytest.approx(BASE + SLOPE * price)
    assert price > price0
    assert income > income0
    assert income < FULL


def test_均衡は総需要と総供給の両方を満たす() -> None:
    expanded = expand_demand(ECONOMY, delta_government=10)
    price, income = solve_ad_as(expanded, keynesian)
    assert aggregate_demand_income(expanded, price) == pytest.approx(income)
    assert keynesian(price) == pytest.approx(income)


def test_ケインズの垂直部分では物価だけが上がる() -> None:
    expanded = expand_demand(ECONOMY, delta_government=20)
    price, income = solve_ad_as(expanded, keynesian)
    assert income == pytest.approx(1000)
    assert price == pytest.approx(5 / 3)


def test_需要を動かす() -> None:
    moved = expand_demand(ECONOMY, delta_government=10, delta_nominal_money=50)
    assert moved.intercept == 460
    assert moved.nominal_money == 300
    assert ECONOMY.intercept == 450


def test_古典派で生産性が上がると所得は増え物価は下がる() -> None:
    full, _ = shift_supply(FULL, BASE, 100)

    def shifted(price: float) -> float:
        return classical_supply(price, full)

    price, income = solve_ad_as(ECONOMY, shifted)
    assert income == pytest.approx(1100)
    assert price == pytest.approx(0.5)


def test_ケインズでも生産性が上がると所得は増え物価は下がる() -> None:
    full, base = shift_supply(FULL, BASE, 50)
    assert (full, base) == (1050, 530)

    def shifted(price: float) -> float:
        return keynesian_supply(price, full, base, SLOPE)

    price0, income0 = solve_ad_as(ECONOMY, keynesian)
    price, income = solve_ad_as(ECONOMY, shifted)
    assert income > income0
    assert price < price0


def test_総供給が左に動くと所得は減り物価は上がる() -> None:
    full, base = shift_supply(FULL, BASE, -50)

    def shifted(price: float) -> float:
        return keynesian_supply(price, full, base, SLOPE)

    price0, income0 = solve_ad_as(ECONOMY, keynesian)
    price, income = solve_ad_as(ECONOMY, shifted)
    assert income < income0
    assert price > price0


def test_供給をずらして完全雇用所得が0以下になるならエラー() -> None:
    with pytest.raises(ValueError, match="完全雇用所得"):
        shift_supply(FULL, BASE, -1000)


def test_交点が無ければエラー() -> None:
    def low(price: float) -> float:
        return classical_supply(price, 800)

    with pytest.raises(ValueError, match="交点"):
        solve_ad_as(ECONOMY, low)


def test_探す範囲の下限が高すぎてもエラー() -> None:
    with pytest.raises(ValueError, match="交点"):
        solve_ad_as(ECONOMY, classical, price_low=2)


def test_均衡の物価が初期の探す範囲の下の方にあっても求まる() -> None:
    def high(price: float) -> float:
        return classical_supply(price, 1200)

    price, income = solve_ad_as(ECONOMY, high)
    assert price == pytest.approx(1 / 3)
    assert income == pytest.approx(1200)
