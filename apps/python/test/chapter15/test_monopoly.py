"""第 15 章: 独占のテスト。

需要曲線 Q = 100 - 2P（逆需要曲線 P = 50 - Q / 2）、限界費用は一定で 10。
"""

import pytest

from lib.chapter15.monopoly import (
    competitive_quantity,
    lerner_index,
    marginal_revenue,
    monopoly_outcome,
)

DEMAND = {"demand_intercept": 100, "demand_slope": 2}


def test_限界収入は需要曲線の2倍の傾き() -> None:
    # 逆需要曲線 P = 50 - 0.5Q の傾きは -0.5。限界収入 MR = 50 - Q の傾きは -1
    assert marginal_revenue(0, **DEMAND) == pytest.approx(50)
    assert marginal_revenue(10, **DEMAND) == pytest.approx(40)
    assert marginal_revenue(20, **DEMAND) == pytest.approx(30)


def test_完全競争の数量は価格が限界費用に等しくなる80() -> None:
    # P = MC = 10 のとき、需要量は 100 - 2 × 10
    assert competitive_quantity(**DEMAND, marginal_cost=10) == pytest.approx(80)


def test_独占の数量は40で価格は30() -> None:
    result = monopoly_outcome(**DEMAND, marginal_cost=10)
    assert result.quantity == pytest.approx(40)
    assert result.price == pytest.approx(30)


def test_独占の数量では限界収入が限界費用に等しい() -> None:
    result = monopoly_outcome(**DEMAND, marginal_cost=10)
    assert marginal_revenue(result.quantity, **DEMAND) == pytest.approx(10)


def test_独占は完全競争より価格が高く数量が少ない() -> None:
    result = monopoly_outcome(**DEMAND, marginal_cost=10)
    assert result.price > 10
    assert result.quantity < competitive_quantity(**DEMAND, marginal_cost=10)


def test_独占の利潤は価格から限界費用を引いた差かける数量() -> None:
    assert monopoly_outcome(**DEMAND, marginal_cost=10).profit == pytest.approx(800)


def test_独占の消費者余剰は400で死荷重は400() -> None:
    result = monopoly_outcome(**DEMAND, marginal_cost=10)
    # 消費者余剰: 底辺 40、高さ 50 - 30。死荷重: 底辺 80 - 40、高さ 30 - 10
    assert result.consumer_surplus == pytest.approx(400)
    assert result.deadweight_loss == pytest.approx(400)


def test_完全競争の総余剰は独占の消費者余剰と利潤と死荷重の合計() -> None:
    result = monopoly_outcome(**DEMAND, marginal_cost=10)
    # 完全競争の消費者余剰: 底辺 80、高さ 50 - 10 = 1600
    competitive = 0.5 * 80 * (50 - 10)
    assert competitive == pytest.approx(1600)
    total = result.consumer_surplus + result.profit + result.deadweight_loss
    assert total == pytest.approx(competitive)


def test_負の限界費用は受け付けない() -> None:
    with pytest.raises(ValueError):
        monopoly_outcome(**DEMAND, marginal_cost=-1)


def test_費用が0なら独占の数量は需要曲線の切片の半分() -> None:
    assert monopoly_outcome(**DEMAND, marginal_cost=0).quantity == pytest.approx(50)


def test_限界費用が需要曲線の切片以上なら生産しない() -> None:
    with pytest.raises(ValueError):
        monopoly_outcome(**DEMAND, marginal_cost=50)


def test_ラーナー指数は価格弾力性の逆数に等しい() -> None:
    result = monopoly_outcome(**DEMAND, marginal_cost=10)
    # 独占点での価格弾力性は b × P ÷ Q = 2 × 30 ÷ 40 = 1.5
    elasticity = 2 * result.price / result.quantity
    assert lerner_index(result.price, marginal_cost=10) == pytest.approx(1 / elasticity)
    assert lerner_index(result.price, marginal_cost=10) == pytest.approx(2 / 3)


def test_価格が0以下ならラーナー指数は求められない() -> None:
    with pytest.raises(ValueError):
        lerner_index(0, marginal_cost=10)
