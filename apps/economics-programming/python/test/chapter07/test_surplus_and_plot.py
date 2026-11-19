"""第 7 章: 余剰・課税と図示のテスト。"""

from typing import Any

import pytest
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from lib.chapter07.plot import draw_market
from lib.chapter07.surplus import (
    consumer_surplus,
    equilibrium,
    equilibrium_with_tax,
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
