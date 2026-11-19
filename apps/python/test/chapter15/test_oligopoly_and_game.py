"""第 15 章: 寡占（クールノー競争）とゲーム理論のテスト。

逆需要曲線 P = 50 - Q / 2、各企業の限界費用は一定で 10。
"""

from typing import TypedDict

import pytest

from lib.chapter15.game import pure_nash_equilibria
from lib.chapter15.oligopoly import (
    best_response,
    cournot_by_iteration,
    cournot_symmetric,
    duopoly_profits,
)


class Market(TypedDict):
    demand_intercept: float
    demand_slope: float
    marginal_cost: float


MARKET: Market = {"demand_intercept": 100, "demand_slope": 2, "marginal_cost": 10}


def test_相手が生産しなければ最適反応は独占の数量40() -> None:
    assert best_response(0, **MARKET) == pytest.approx(40)


def test_相手の生産量が増えると最適反応は減る() -> None:
    # 最適反応 q = 40 - 0.5 × (相手の生産量)
    assert best_response(20, **MARKET) == pytest.approx(30)
    assert best_response(40, **MARKET) == pytest.approx(20)


def test_相手が非常に多く生産すれば最適反応は0() -> None:
    assert best_response(100, **MARKET) == 0


def test_2社のクールノー均衡は各社80_3で価格は70_3() -> None:
    q1, q2 = cournot_by_iteration(**MARKET)
    assert q1 == pytest.approx(80 / 3, abs=1e-6)
    assert q2 == pytest.approx(80 / 3, abs=1e-6)


def test_均衡では互いが相手の生産量に対して最適反応をとっている() -> None:
    q1, q2 = cournot_by_iteration(**MARKET)
    assert best_response(q2, **MARKET) == pytest.approx(q1, abs=1e-6)
    assert best_response(q1, **MARKET) == pytest.approx(q2, abs=1e-6)


def test_初期値が違っても同じ均衡に収束する() -> None:
    q1, q2 = cournot_by_iteration(**MARKET, initial=(80, 0))
    assert q1 == pytest.approx(80 / 3, abs=1e-6)
    assert q2 == pytest.approx(80 / 3, abs=1e-6)


def test_収束しなければ例外になる() -> None:
    with pytest.raises(RuntimeError):
        cournot_by_iteration(**MARKET, max_iterations=1)


def test_企業が1社なら独占と同じ() -> None:
    quantity, price, profit = cournot_symmetric(1, **MARKET)
    assert quantity == pytest.approx(40)
    assert price == pytest.approx(30)
    assert profit == pytest.approx(800)


def test_企業が2社なら生産量の合計は独占より多く完全競争より少ない() -> None:
    quantity, price, profit = cournot_symmetric(2, **MARKET)
    assert quantity * 2 == pytest.approx(160 / 3)
    assert price == pytest.approx(70 / 3)
    assert profit == pytest.approx(3200 / 9)
    assert 40 < quantity * 2 < 80


def test_企業が増えると完全競争に近づく() -> None:
    quantity, price, _ = cournot_symmetric(100, **MARKET)
    assert quantity * 100 == pytest.approx(79.2, abs=0.1)
    assert price == pytest.approx(10.4, abs=0.1)


def test_企業の数が0以下なら求められない() -> None:
    with pytest.raises(ValueError):
        cournot_symmetric(0, **MARKET)


def test_2社の利潤は価格から限界費用を引いた差かける自社の生産量() -> None:
    # 2 社とも 20 ずつ: 価格 30、利潤は各社 (30 - 10) × 20
    profit1, profit2 = duopoly_profits(20, 20, **MARKET)
    assert profit1 == pytest.approx(400)
    assert profit2 == pytest.approx(400)


def test_囚人のジレンマの均衡は両者が裏切る() -> None:
    payoffs = {
        ("協力", "協力"): (3, 3),
        ("協力", "裏切り"): (0, 5),
        ("裏切り", "協力"): (5, 0),
        ("裏切り", "裏切り"): (1, 1),
    }
    assert pure_nash_equilibria(payoffs) == [("裏切り", "裏切り")]


def test_調整ゲームには均衡が2つある() -> None:
    payoffs = {
        ("A", "A"): (2, 2),
        ("A", "B"): (0, 0),
        ("B", "A"): (0, 0),
        ("B", "B"): (1, 1),
    }
    assert pure_nash_equilibria(payoffs) == [("A", "A"), ("B", "B")]


def test_コイン合わせには純粋戦略の均衡がない() -> None:
    payoffs = {
        ("表", "表"): (1, -1),
        ("表", "裏"): (-1, 1),
        ("裏", "表"): (-1, 1),
        ("裏", "裏"): (1, -1),
    }
    assert pure_nash_equilibria(payoffs) == []


def test_生産量の選択も囚人のジレンマになる() -> None:
    # 各社が「協調（独占の半分の 20）」か「クールノー（80 / 3）」を選ぶ
    cooperate, cournot = 20.0, 80 / 3
    quantities = {"協調": cooperate, "クールノー": cournot}
    payoffs = {
        (a, b): duopoly_profits(quantities[a], quantities[b], **MARKET)
        for a in quantities
        for b in quantities
    }
    assert payoffs[("協調", "協調")] == pytest.approx((400, 400))
    assert payoffs[("クールノー", "クールノー")] == pytest.approx((3200 / 9, 3200 / 9))
    # 協調すれば両社とも得なのに、均衡は両社がクールノーの生産量を選ぶ点
    assert pure_nash_equilibria(payoffs) == [("クールノー", "クールノー")]
