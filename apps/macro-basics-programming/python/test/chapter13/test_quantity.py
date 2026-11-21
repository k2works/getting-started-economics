"""第 13 章: 貨幣数量説のテスト。"""

import pytest

from lib.chapter13.quantity import (
    inflation_from_money_growth,
    marshall_k,
    nominal_money_demand,
    price_level_from_quantity,
)


def test_交換方程式から物価水準を求める() -> None:
    assert price_level_from_quantity(100, 4, 200) == pytest.approx(2)


def test_貨幣量が2倍なら物価も2倍() -> None:
    before = price_level_from_quantity(100, 4, 200)
    after = price_level_from_quantity(200, 4, 200)
    assert after == pytest.approx(2 * before)


def test_生産量が2倍なら物価は半分() -> None:
    assert price_level_from_quantity(100, 4, 400) == pytest.approx(1)


def test_生産量が0なら物価は計算できない() -> None:
    with pytest.raises(ValueError, match="生産量"):
        price_level_from_quantity(100, 4, 0)


def test_マーシャルのkは流通速度の逆数() -> None:
    assert marshall_k(4) == pytest.approx(0.25)


def test_流通速度が0以下ならエラー() -> None:
    with pytest.raises(ValueError, match="流通速度"):
        marshall_k(0)
    with pytest.raises(ValueError, match="流通速度"):
        marshall_k(-4)


def test_貨幣需要は名目所得のk倍で利子率を含まない() -> None:
    assert nominal_money_demand(0.25, 2, 200) == pytest.approx(100)


def test_貨幣需要は交換方程式の貨幣量と一致する() -> None:
    money, velocity, output = 100, 4, 200
    price = price_level_from_quantity(money, velocity, output)
    assert nominal_money_demand(marshall_k(velocity), price, output) == pytest.approx(
        money
    )


def test_インフレ率は貨幣増加率と流通速度の変化率から実質成長率を引いた値() -> None:
    assert inflation_from_money_growth(10, 2, 0) == pytest.approx(8)
    assert inflation_from_money_growth(10, 2, -3) == pytest.approx(5)


def test_流通速度と実質成長が一定ならインフレ率は貨幣増加率に等しい() -> None:
    assert inflation_from_money_growth(7, 0, 0) == pytest.approx(7)


def test_インフレ率の近似は交換方程式の厳密な値に近い() -> None:
    exact = price_level_from_quantity(110, 4, 204) / price_level_from_quantity(
        100, 4, 200
    )
    approx = inflation_from_money_growth(10, 2, 0)
    assert (exact - 1) * 100 == pytest.approx(approx, abs=0.2)
