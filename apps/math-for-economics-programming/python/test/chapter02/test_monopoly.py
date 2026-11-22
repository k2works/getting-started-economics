import pytest

from lib.chapter02.monopoly import (
    MarketOutcome,
    competitive_outcome,
    cournot_best_response,
    cournot_duopoly,
    cournot_outcome,
    inverse_demand_price,
    monopoly_deadweight_loss,
    monopoly_outcome,
    monopoly_profit,
)
from lib.chapter02.quadratic import argmax_on_grid, parabola_vertex

# 逆需要 P = 100 − Q、1 単位あたりの費用 20（この章で使い回す、手計算できる例）
A, B, COST = 100, 1, 20


def test_利潤は逆需要の価格から費用を引いて数量を掛けたもの() -> None:
    assert inverse_demand_price(30, A, B) == 70
    assert inverse_demand_price(30, 100, 2) == 40
    assert monopoly_profit(10, A, B, COST) == 700
    assert monopoly_profit(10, 100, 2, COST) == 600


def test_利潤は数量の2次関数() -> None:
    # π(Q) = (a − b·Q − c)·Q = −b·Q² + (a − c)·Q
    for q in [0, 0.5, 15, 40, 90]:
        expected = -2 * q**2 + 80 * q
        assert monopoly_profit(q, 100, 2, COST) == pytest.approx(expected)


def test_独占の利潤最大は放物線の頂点() -> None:
    assert monopoly_outcome(A, B, COST) == MarketOutcome(
        quantity=40, price=60, profit=1600
    )
    assert parabola_vertex(-B, A - COST, 0) == (40, 1600)
    # 需要の傾きが 1 でないとき（P = 100 − 2Q）
    assert monopoly_outcome(100, 2, COST) == MarketOutcome(
        quantity=20, price=60, profit=800
    )


@pytest.mark.parametrize(
    "params", [(100, 1, 20), (100, 2, 20), (50, 0.5, 10), (12, 3, 0)]
)
def test_頂点の式と格子探索の答えが一致する(
    params: tuple[float, float, float],
) -> None:
    a, b, cost = params
    points = 2001
    step = (a / b) / (points - 1)
    best = argmax_on_grid(lambda q: monopoly_profit(q, a, b, cost), 0, a / b, points)
    assert best == pytest.approx(monopoly_outcome(a, b, cost).quantity, abs=step)


def test_完全競争では価格が費用に等しく数量は独占の2倍() -> None:
    assert competitive_outcome(A, B, COST) == MarketOutcome(
        quantity=80, price=20, profit=0
    )
    assert competitive_outcome(100, 2, COST) == MarketOutcome(
        quantity=40, price=20, profit=0
    )
    assert monopoly_outcome(A, B, COST).price > competitive_outcome(A, B, COST).price


def test_死荷重は失われた三角形の面積() -> None:
    assert monopoly_deadweight_loss(A, B, COST) == 800
    assert monopoly_deadweight_loss(100, 2, COST) == 400


@pytest.mark.parametrize("params", [(100, 1, 20), (100, 2, 20), (30, 0.5, 6)])
def test_死荷重は総余剰の減少分に等しい(params: tuple[float, float, float]) -> None:
    a, b, cost = params
    monopoly = monopoly_outcome(a, b, cost)
    competition = competitive_outcome(a, b, cost)
    # 消費者余剰は、需要曲線の下・価格の上の三角形（価格軸の切片は a）
    surplus_monopoly = (a - monopoly.price) * monopoly.quantity / 2 + monopoly.profit
    surplus_competition = (a - competition.price) * competition.quantity / 2
    loss = surplus_competition - surplus_monopoly
    assert monopoly_deadweight_loss(a, b, cost) == pytest.approx(loss)


@pytest.mark.parametrize(
    "params", [(100, 0, 20), (100, -1, 20), (20, 1, 20), (100, 1, -1)]
)
def test_市場が成り立たない設定はエラー(params: tuple[float, float, float]) -> None:
    with pytest.raises(ValueError):
        monopoly_outcome(*params)
    with pytest.raises(ValueError):
        competitive_outcome(*params)


def test_最適反応は相手の数量が増えると減り0で止まる() -> None:
    assert cournot_best_response(0, A, B, COST) == 40  # 相手が 0 なら独占
    assert cournot_best_response(20, A, B, COST) == 30
    assert cournot_best_response(20, 100, 2, COST) == 10
    assert cournot_best_response(100, A, B, COST) == 0


def test_2社のクールノー均衡() -> None:
    q1, q2 = cournot_duopoly(A, B, COST, COST)
    assert q1 == pytest.approx(80 / 3)
    assert q2 == pytest.approx(80 / 3)


def test_費用の違う2社のクールノー均衡は互いに最適反応() -> None:
    q1, q2 = cournot_duopoly(A, B, 10, 40)
    assert (q1, q2) == pytest.approx((40, 10))
    assert cournot_best_response(q2, A, B, 10) == pytest.approx(q1)
    assert cournot_best_response(q1, A, B, 40) == pytest.approx(q2)


def test_1社のクールノーは独占に一致する() -> None:
    assert cournot_outcome(1, A, B, COST) == monopoly_outcome(A, B, COST)


def test_n社の対称なクールノー均衡() -> None:
    result = cournot_outcome(2, A, B, COST)
    assert result.quantity / 2 == pytest.approx(80 / 3)
    assert result.price == pytest.approx(140 / 3)
    assert result.profit / 2 == pytest.approx(6400 / 9)


def test_2社の対称均衡は連立方程式の解と一致する() -> None:
    assert cournot_outcome(2, 100, 2, COST).quantity == pytest.approx(
        sum(cournot_duopoly(100, 2, COST, COST))
    )


def test_企業が増えると価格は費用に近づく() -> None:
    prices = [cournot_outcome(n, A, B, COST).price for n in range(1, 11)]
    assert all(p1 > p2 for p1, p2 in zip(prices, prices[1:], strict=False))
    # 価格 − 費用 = (a − c) ÷ (n + 1)
    assert cournot_outcome(99, A, B, COST).price == pytest.approx(20.8)


@pytest.mark.parametrize("costs", [(10, 60), (10, 55), (55, 10)])
def test_一方の数量が0以下になる2社はエラー(costs: tuple[float, float]) -> None:
    with pytest.raises(ValueError):
        cournot_duopoly(A, B, *costs)


def test_数量が1未満でも正なら2社の均衡がある() -> None:
    assert cournot_duopoly(10, 1, 1, 5) == pytest.approx((13 / 3, 1 / 3))
    assert cournot_duopoly(10, 1, 5, 1) == pytest.approx((1 / 3, 13 / 3))


def test_企業の数が1未満ならエラー() -> None:
    with pytest.raises(ValueError):
        cournot_outcome(0, A, B, COST)
