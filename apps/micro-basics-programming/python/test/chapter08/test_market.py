"""第 8 章: 市場均衡と調整過程のテスト。"""

import pytest

from lib.chapter08.market import (
    LinearMarket,
    equilibrium,
    excess_demand,
    marshall_adjustment,
    price_state,
    quantity_demanded,
    quantity_supplied,
    shift_demand,
    shift_supply,
    walras_adjustment,
)

# 需要 Q = 100 − P、供給 Q = P − 10。均衡は P = 55、Q = 45
MARKET = LinearMarket(
    demand_intercept=100, demand_slope=-1, supply_intercept=-10, supply_slope=1
)


def test_需要量は価格が上がると減る() -> None:
    assert quantity_demanded(MARKET, 30) == 70
    assert quantity_demanded(MARKET, 55) == 45
    assert quantity_demanded(MARKET, 100) == 0


def test_需要量は負にならない() -> None:
    assert quantity_demanded(MARKET, 150) == 0


def test_供給量は価格が上がると増える() -> None:
    assert quantity_supplied(MARKET, 10) == 0
    assert quantity_supplied(MARKET, 55) == 45
    assert quantity_supplied(MARKET, 80) == 70


def test_供給量は負にならない() -> None:
    assert quantity_supplied(MARKET, 5) == 0


def test_均衡は需要と供給の交点() -> None:
    assert equilibrium(MARKET) == (55, 45)


def test_均衡で需要量と供給量は等しい() -> None:
    price, quantity = equilibrium(MARKET)
    assert quantity_demanded(MARKET, price) == pytest.approx(quantity)
    assert quantity_supplied(MARKET, price) == pytest.approx(quantity)


def test_傾きが違う市場の均衡() -> None:
    market = LinearMarket(72.5, -0.5, -10, 1)
    assert equilibrium(market) == pytest.approx((55, 45))
    assert equilibrium(LinearMarket(100, -2, -20, 4)) == pytest.approx((20, 60))


def test_正の均衡がなければエラー() -> None:
    with pytest.raises(ValueError, match="均衡"):
        equilibrium(LinearMarket(5, -1, 20, 1))


def test_需要の傾きは負で供給の傾きは正でなければエラー() -> None:
    with pytest.raises(ValueError, match="需要の傾き"):
        LinearMarket(100, 0, -10, 1)
    with pytest.raises(ValueError, match="供給の傾き"):
        LinearMarket(100, -1, -10, 0)
    with pytest.raises(ValueError, match="供給の傾き"):
        LinearMarket(100, -1, -10, -1)


def test_傾きが1未満の正の値でも市場を作れる() -> None:
    market = LinearMarket(100, -0.5, -10, 0.25)
    price, quantity = equilibrium(market)
    assert quantity_demanded(market, price) == pytest.approx(quantity)


def test_超過需要は需要量引く供給量() -> None:
    assert excess_demand(MARKET, 30) == 70 - 20
    assert excess_demand(MARKET, 80) == 20 - 70
    assert excess_demand(MARKET, 55) == 0


def test_価格が均衡より高ければ供給超過で下がる() -> None:
    assert price_state(MARKET, 80) == "供給超過（価格が下がる）"


def test_価格が均衡より低ければ需要超過で上がる() -> None:
    assert price_state(MARKET, 30) == "需要超過（価格が上がる）"


def test_価格が均衡なら均衡() -> None:
    assert price_state(MARKET, 55) == "均衡"


def test_均衡の判定は許容誤差を持つ() -> None:
    assert price_state(MARKET, 55 + 4e-10) == "均衡"
    assert price_state(MARKET, 55 + 1.2e-9) == "供給超過（価格が下がる）"
    assert price_state(MARKET, 55 - 1.2e-9) == "需要超過（価格が上がる）"


def test_ワルラス的調整は価格を超過需要に比例して動かす() -> None:
    prices = walras_adjustment(MARKET, 80, 0.25, 3)
    assert prices == pytest.approx([80, 67.5, 61.25, 58.125])


def test_ワルラス的調整は均衡との差が半分ずつ縮む() -> None:
    prices = walras_adjustment(MARKET, 80, 0.25, 10)
    gaps = [abs(p - 55) for p in prices]
    assert all(b == pytest.approx(a / 2) for a, b in zip(gaps, gaps[1:], strict=False))


def test_ワルラス的調整は均衡に収束する() -> None:
    assert walras_adjustment(MARKET, 80, 0.25, 40)[-1] == pytest.approx(55, abs=1e-9)


def test_ワルラス的調整は下からも収束する() -> None:
    prices = walras_adjustment(MARKET, 30, 0.25, 40)
    assert prices[1] > prices[0]
    assert prices[-1] == pytest.approx(55, abs=1e-9)


def test_調整が速すぎると発散する() -> None:
    prices = walras_adjustment(MARKET, 80, 1.5, 4)
    gaps = [abs(p - 55) for p in prices]
    assert all(a < b for a, b in zip(gaps, gaps[1:], strict=False))


def test_調整の速さが正でなければエラー() -> None:
    with pytest.raises(ValueError, match="速さ"):
        walras_adjustment(MARKET, 80, 0, 3)
    with pytest.raises(ValueError, match="速さ"):
        marshall_adjustment(MARKET, 0, -0.1, 3)


def test_調整の回数が負ならエラー() -> None:
    with pytest.raises(ValueError, match="回数"):
        walras_adjustment(MARKET, 80, 0.25, -1)
    with pytest.raises(ValueError, match="回数"):
        marshall_adjustment(MARKET, 0, 0.25, -1)


def test_調整の回数0は初期値だけ() -> None:
    assert walras_adjustment(MARKET, 80, 0.25, 0) == [80]
    assert marshall_adjustment(MARKET, 0, 0.25, 0) == [0]


def test_マーシャル的調整は需要価格と供給価格の差に比例して数量を動かす() -> None:
    quantities = marshall_adjustment(MARKET, 0, 0.25, 3)
    assert quantities == pytest.approx([0, 22.5, 33.75, 39.375])


def test_マーシャル的調整は均衡に収束する() -> None:
    assert marshall_adjustment(MARKET, 0, 0.25, 40)[-1] == pytest.approx(45, abs=1e-9)


def test_マーシャル的調整は上からも収束する() -> None:
    quantities = marshall_adjustment(MARKET, 80, 0.25, 40)
    assert quantities[1] < quantities[0]
    assert quantities[-1] == pytest.approx(45, abs=1e-9)


def test_需要の右シフトは価格も数量も上げる() -> None:
    shifted = shift_demand(MARKET, 20)
    assert equilibrium(shifted) == pytest.approx((65, 55))


def test_需要の左シフトは価格も数量も下げる() -> None:
    assert equilibrium(shift_demand(MARKET, -20)) == pytest.approx((45, 35))


def test_供給の右シフトは価格を下げ数量を増やす() -> None:
    assert equilibrium(shift_supply(MARKET, 20)) == pytest.approx((45, 55))


def test_供給の左シフトは価格を上げ数量を減らす() -> None:
    assert equilibrium(shift_supply(MARKET, -20)) == pytest.approx((65, 35))


def test_シフトは元の市場を変えない() -> None:
    shift_demand(MARKET, 20)
    assert equilibrium(MARKET) == (55, 45)
    assert MARKET.demand_intercept == 100


def test_シフトで傾きは変わらない() -> None:
    shifted = shift_supply(shift_demand(MARKET, 20), 20)
    assert shifted.demand_slope == -1
    assert shifted.supply_slope == 1
    assert shifted.demand_intercept == 120
    assert shifted.supply_intercept == 10
