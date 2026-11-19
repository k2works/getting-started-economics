"""第 7 章: 余剰・課税と図示のテスト。"""

from typing import Any

import pytest
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from lib.chapter01.demand import quantity_demanded
from lib.chapter06.bisection import NoEquilibriumError
from lib.chapter07.plot import draw_market
from lib.chapter07.surplus import (
    consumer_surplus,
    equilibrium,
    equilibrium_with_tax,
    inverse_demand,
    producer_surplus,
)

# 需要曲線 Q = 100 - 2P、供給曲線 Q = 3P
MARKET = {
    "demand_intercept": 100,
    "demand_slope": 2,
    "supply_intercept": 0,
    "supply_slope": 3,
}


def test_均衡価格は20で均衡数量は60() -> None:
    assert equilibrium(**MARKET) == pytest.approx((20, 60))


def test_消費者余剰は需要曲線と価格の間の三角形の面積() -> None:
    # 需要曲線の縦軸の切片は 100 / 2 = 50。底辺 60、高さ 50 - 20 = 30
    assert consumer_surplus(**MARKET) == pytest.approx(900)


def test_生産者余剰は価格と供給曲線の間の三角形の面積() -> None:
    # 供給曲線の縦軸の切片は 0。底辺 60、高さ 20 - 0 = 20
    assert producer_surplus(**MARKET) == pytest.approx(600)


def test_供給曲線の切片が正なら生産者余剰は求められない() -> None:
    with pytest.raises(ValueError):
        producer_surplus(100, 2, 10, 3)


def test_従量税を課すと買い手の価格は上がり売り手の受取は下がる() -> None:
    result = equilibrium_with_tax(**MARKET, tax=5)
    assert result.consumer_price == pytest.approx(23)
    assert result.producer_price == pytest.approx(18)
    assert result.quantity == pytest.approx(54)


def test_従量税の税収は税額かける取引量() -> None:
    assert equilibrium_with_tax(**MARKET, tax=5).tax_revenue == pytest.approx(270)


def test_死荷重は取引量の減少分と税額でできる三角形の面積() -> None:
    # 底辺は取引量の減少 60 - 54 = 6、高さは税額 5
    assert equilibrium_with_tax(**MARKET, tax=5).deadweight_loss == pytest.approx(15)


def test_税がなければ死荷重はない() -> None:
    result = equilibrium_with_tax(**MARKET, tax=0)
    assert result.deadweight_loss == pytest.approx(0)
    assert result.quantity == pytest.approx(60)


def test_余剰の合計と税収の合計は課税前より死荷重の分だけ減る() -> None:
    tax = 5
    result = equilibrium_with_tax(**MARKET, tax=tax)
    # 課税後の消費者余剰: 底辺 54、高さ 50 - 23。生産者余剰: 底辺 54、高さ 18 - 0
    consumer = 0.5 * 54 * (50 - result.consumer_price)
    producer = 0.5 * 54 * (result.producer_price - 0)
    before = consumer_surplus(**MARKET) + producer_surplus(**MARKET)
    after = consumer + producer + result.tax_revenue
    assert before - after == pytest.approx(result.deadweight_loss)


# 供給曲線に切片がある市場: Q = 10 + 3P（均衡は価格 18、数量 64）
MARKET_WITH_INTERCEPT = {
    "demand_intercept": 100,
    "demand_slope": 2,
    "supply_intercept": 10,
    "supply_slope": 3,
}

# 供給曲線の切片が負の市場: Q = -30 + 3P（価格 10 までは供給量が 0。均衡は価格 26、数量 48）
MARKET_WITH_NEGATIVE_INTERCEPT = {
    "demand_intercept": 100,
    "demand_slope": 2,
    "supply_intercept": -30,
    "supply_slope": 3,
}


def curve_points(line: Line2D) -> dict[float, float]:
    """線の (数量, 価格) の組を、数量をキーにした辞書にする。"""
    points: Any = line.get_xydata()
    return {float(x): float(y) for x, y in points}


def test_市場の図には需要曲線と供給曲線の2本の線がある() -> None:
    fig = draw_market(**MARKET)
    ax = fig.axes[0]
    assert isinstance(fig, Figure)
    assert [line.get_label() for line in ax.lines[:2]] == ["Demand", "Supply"]


def test_需要曲線は数量が0のとき価格50で数量60のとき価格20() -> None:
    ax = draw_market(**MARKET).axes[0]
    points = curve_points(ax.lines[0])
    assert points[0] == pytest.approx(50)
    assert points[60] == pytest.approx(20)


def test_供給曲線は数量60のとき価格20() -> None:
    ax = draw_market(**MARKET).axes[0]
    points = curve_points(ax.lines[1])
    assert points[60] == pytest.approx(20)


def test_負の税額は受け付けない() -> None:
    with pytest.raises(ValueError):
        equilibrium_with_tax(**MARKET, tax=-1)


def test_供給曲線に切片があっても均衡を求められる() -> None:
    # 100 - 2P = 10 + 3P から P = 90 / 5 = 18、Q = 100 - 36 = 64
    assert equilibrium(**MARKET_WITH_INTERCEPT) == pytest.approx((18, 64))


def test_供給曲線の切片が負の市場の均衡と余剰() -> None:
    # 100 - 2P = -30 + 3P から P = 26、Q = 48。供給曲線の縦軸の切片は 30 / 3 = 10
    assert equilibrium(**MARKET_WITH_NEGATIVE_INTERCEPT) == pytest.approx((26, 48))
    # 消費者余剰: 底辺 48、高さ 50 - 26。生産者余剰: 底辺 48、高さ 26 - 10
    assert consumer_surplus(**MARKET_WITH_NEGATIVE_INTERCEPT) == pytest.approx(576)
    assert producer_surplus(**MARKET_WITH_NEGATIVE_INTERCEPT) == pytest.approx(384)


def test_供給曲線に切片があるときの従量税() -> None:
    result = equilibrium_with_tax(**MARKET_WITH_INTERCEPT, tax=5)
    # (100 - 10 + 3 × 5) / 5 = 21、売り手の受取は 21 - 5 = 16、数量は 100 - 2 × 21 = 58
    assert result.consumer_price == pytest.approx(21)
    assert result.producer_price == pytest.approx(16)
    assert result.quantity == pytest.approx(58)
    assert result.tax_revenue == pytest.approx(290)
    # 死荷重: 底辺は取引量の減少 64 - 58 = 6、高さは税額 5
    assert result.deadweight_loss == pytest.approx(15)


def test_供給曲線に切片があるとき供給曲線は数量64で価格18() -> None:
    ax = draw_market(**MARKET_WITH_INTERCEPT).axes[0]
    # 供給曲線 P = (Q - 10) / 3。数量 10 で価格 0、数量 64 で価格 18
    points = curve_points(ax.lines[1])
    assert points[10] == pytest.approx(0)
    assert points[64] == pytest.approx(18)


def test_市場の図の均衡点は数量60と価格20() -> None:
    ax = draw_market(**MARKET).axes[0]
    ((quantity, price),) = curve_points(ax.lines[2]).items()
    assert quantity == pytest.approx(60)
    assert price == pytest.approx(20)


def test_供給曲線に切片があるとき図の均衡点は数量64と価格18() -> None:
    ax = draw_market(**MARKET_WITH_INTERCEPT).axes[0]
    ((quantity, price),) = curve_points(ax.lines[2]).items()
    assert quantity == pytest.approx(64)
    assert price == pytest.approx(18)


# 需要の切片が供給の切片より小さい市場: 価格が 0 でも供給が需要を上回る（P* = -4）
MARKET_WITH_NEGATIVE_PRICE = {
    "demand_intercept": 100,
    "demand_slope": 2,
    "supply_intercept": 120,
    "supply_slope": 3,
}

# 価格は正でも取引量が負になる市場: 需要は価格 10 でなくなり、供給は価格 30 まで始まらない
MARKET_WITH_NEGATIVE_QUANTITY = {
    "demand_intercept": 10,
    "demand_slope": 1,
    "supply_intercept": -30,
    "supply_slope": 1,
}


def test_価格が負になる市場では均衡を求められない() -> None:
    with pytest.raises(NoEquilibriumError):
        equilibrium(**MARKET_WITH_NEGATIVE_PRICE)


def test_取引量が負になる市場では均衡を求められない() -> None:
    with pytest.raises(NoEquilibriumError):
        equilibrium(**MARKET_WITH_NEGATIVE_QUANTITY)


def test_価格がちょうど0になる市場の均衡は許される() -> None:
    # 100 - 2P = 100 + 3P から P = 0、Q = 100
    assert equilibrium(100, 2, 100, 3) == pytest.approx((0, 100))


def test_均衡のない市場では余剰も図も求められない() -> None:
    with pytest.raises(NoEquilibriumError):
        consumer_surplus(**MARKET_WITH_NEGATIVE_PRICE)
    with pytest.raises(NoEquilibriumError):
        draw_market(**MARKET_WITH_NEGATIVE_PRICE)
    with pytest.raises(NoEquilibriumError):
        producer_surplus(**MARKET_WITH_NEGATIVE_QUANTITY)
    with pytest.raises(NoEquilibriumError):
        equilibrium_with_tax(**MARKET_WITH_NEGATIVE_PRICE, tax=5)


def test_傾きが0以下の曲線では均衡を求められない() -> None:
    with pytest.raises(ValueError, match="傾き"):
        equilibrium(
            demand_intercept=100, demand_slope=0, supply_intercept=0, supply_slope=3
        )
    with pytest.raises(ValueError, match="傾き"):
        equilibrium(
            demand_intercept=100, demand_slope=2, supply_intercept=0, supply_slope=0
        )


def test_税額が大きすぎて取引が成立しないときは均衡がない() -> None:
    with pytest.raises(NoEquilibriumError):
        equilibrium_with_tax(
            demand_intercept=100,
            demand_slope=2,
            supply_intercept=0,
            supply_slope=3,
            tax=100,
        )


def test_逆需要曲線は需要量から価格を求める() -> None:
    assert inverse_demand(quantity=20, intercept=100, slope=2) == 40
    assert inverse_demand(quantity=100, intercept=100, slope=2) == 0


def test_逆需要曲線は需要曲線の逆関数() -> None:
    price = inverse_demand(quantity=30, intercept=100, slope=2)
    assert quantity_demanded(price, intercept=100, slope=2) == 30


def test_逆需要曲線は負の数量と傾き0以下を受け付けない() -> None:
    with pytest.raises(ValueError, match="数量"):
        inverse_demand(quantity=-1, intercept=100, slope=2)
    with pytest.raises(ValueError, match="傾き"):
        inverse_demand(quantity=10, intercept=100, slope=0)
