import pytest

from lib.chapter01.market import demand_quantity, equilibrium
from lib.chapter06.elasticity import (
    arc_price_elasticity,
    classify_elasticity,
    constant_elasticity_demand,
    elasticity_by_logs,
    linear_demand_elasticity,
    point_price_elasticity,
    revenue_price_slope,
    sales_revenue,
)


def _demand(price: float) -> float:
    """第 1 章の需要 q = 120 − 2p（この章で使い回す）。"""
    return demand_quantity(price, 120, 2)


def _harvest_demand(price: float) -> float:
    """第 1 章の豊作貧乏の需要 q = 100 − 0.5p。"""
    return demand_quantity(price, 100, 0.5)


def _curved_demand(price: float) -> float:
    """弾力性が 1.5 で一定の需要 q = 50·p^(−1.5)。"""
    return constant_elasticity_demand(price, 50, 1.5)


def test_直線の需要の点弾力性は公式で求まる() -> None:
    assert linear_demand_elasticity(40, 120, 2) == 2  # 2 × 40 ÷ 40
    assert linear_demand_elasticity(60, 100, 0.5) == pytest.approx(3 / 7)
    assert linear_demand_elasticity(25, 90, 3) == pytest.approx(5)  # 75 ÷ 15


@pytest.mark.parametrize(
    ("a", "b", "price"), [(120, 2, 40), (120, 2, 0.5), (100, 0.5, 60), (90, 3, 25)]
)
def test_点弾力性は公式と数値微分で一致する(a: float, b: float, price: float) -> None:
    numeric = point_price_elasticity(lambda p: demand_quantity(p, a, b), price)
    assert numeric == pytest.approx(linear_demand_elasticity(price, a, b))


def test_弾力性が1より大きければ弾力的で小さければ非弾力的() -> None:
    assert classify_elasticity(2) == "elastic"
    assert classify_elasticity(0.43) == "inelastic"
    assert classify_elasticity(1) == "unit elastic"
    assert classify_elasticity(1 + 1e-12) == "unit elastic"
    assert classify_elasticity(1.01) == "elastic"
    assert classify_elasticity(0) == "inelastic"


def test_直線の需要の弾力性は価格が高いほど大きく中点で1() -> None:
    assert linear_demand_elasticity(30, 120, 2) == 1  # 中点 p = a ÷ (2b)
    assert linear_demand_elasticity(100, 100, 0.5) == 1
    assert linear_demand_elasticity(0, 120, 2) == 0
    values = [linear_demand_elasticity(p, 120, 2) for p in [5, 20, 35, 50]]
    assert values == sorted(values)


def test_収入の価格についての傾きは需要量かける1引く弾力性() -> None:
    assert sales_revenue(_demand, 40) == 1600
    for price in [10, 30, 40, 55]:
        expected = _demand(price) * (1 - point_price_elasticity(_demand, price))
        slope = revenue_price_slope(_demand, price)
        assert slope == pytest.approx(expected, abs=1e-6)
    assert revenue_price_slope(_demand, 40) == pytest.approx(-40)  # 40 × (1 − 2)


def test_弾力的なら値下げで収入が増え非弾力的なら減る() -> None:
    assert sales_revenue(_demand, 39.6) > sales_revenue(_demand, 40)
    assert sales_revenue(_harvest_demand, 59.4) < sales_revenue(_harvest_demand, 60)
    assert revenue_price_slope(_demand, 40) < 0
    assert revenue_price_slope(_harvest_demand, 60) > 0


def test_豊作貧乏は均衡が需要の非弾力的な部分にあるときに起きる() -> None:
    # 第 1 章: 需要 q = 100 − 0.5p、供給 q = 10 + p が、q = 40 + p に増える
    before, after = equilibrium(100, 0.5, 10, 1), equilibrium(100, 0.5, 40, 1)
    assert linear_demand_elasticity(before.price, 100, 0.5) == pytest.approx(3 / 7)
    assert linear_demand_elasticity(after.price, 100, 0.5) == pytest.approx(0.25)
    assert after.revenue < before.revenue
    # 第 1 章の弾力的な例: 需要 q = 120 − 2p、供給 q = p が、q = 20 + p に増える
    before, after = equilibrium(120, 2, 0, 1), equilibrium(120, 2, 20, 1)
    assert linear_demand_elasticity(before.price, 120, 2) == pytest.approx(2)
    assert linear_demand_elasticity(after.price, 120, 2) == pytest.approx(1.25)
    assert after.revenue > before.revenue


@pytest.mark.parametrize("price", [0.5, 2, 10])
def test_一定弾力性の需要はどの価格でも弾力性が同じ(price: float) -> None:
    assert _curved_demand(4) == pytest.approx(6.25)  # 50 ÷ 4^1.5
    assert point_price_elasticity(_curved_demand, price) == pytest.approx(1.5)
    inelastic = point_price_elasticity(
        lambda p: constant_elasticity_demand(p, 50, 0.4), price
    )
    assert inelastic == pytest.approx(0.4)


def test_対数の傾きで求めた弾力性は点弾力性と一致する() -> None:
    for demand, price in [(_demand, 40), (_demand, 0.5), (_curved_demand, 3)]:
        expected = point_price_elasticity(demand, price)
        assert elasticity_by_logs(demand, price) == pytest.approx(expected)


def test_弧弾力性は区間の中点で測り両端の点弾力性とは違う() -> None:
    # p: 40 → 30 で q: 40 → 60。(20 ÷ 50) ÷ (10 ÷ 35) = 1.4
    assert arc_price_elasticity(_demand, 40, 30) == pytest.approx(1.4)
    assert arc_price_elasticity(_demand, 30, 40) == pytest.approx(1.4)
    assert linear_demand_elasticity(40, 120, 2) == 2
    assert linear_demand_elasticity(30, 120, 2) == 1
    # 区間を狭めると、点弾力性に近づく
    assert arc_price_elasticity(_demand, 40, 39.99) == pytest.approx(2, abs=1e-3)


def test_需要量が正で価格が負でないときだけ弾力性を求める() -> None:
    with pytest.raises(ValueError, match="需要量"):
        point_price_elasticity(_demand, 60)  # q = 0
    with pytest.raises(ValueError, match="需要量"):
        linear_demand_elasticity(70, 120, 2)
    with pytest.raises(ValueError, match="価格"):
        point_price_elasticity(_demand, -1)
    with pytest.raises(ValueError, match="価格"):
        linear_demand_elasticity(-1, 120, 2)
    assert point_price_elasticity(_demand, 0) == pytest.approx(0)
    # 需要量が 0 < q < 1 でも、正なら求める（q = 0.5 で 2 × 59.75 ÷ 0.5）
    assert point_price_elasticity(_demand, 59.75) == pytest.approx(239)


def test_対数を使う計算は価格が正のときだけ() -> None:
    with pytest.raises(ValueError, match="価格"):
        constant_elasticity_demand(0, 50, 1.5)
    with pytest.raises(ValueError, match="価格"):
        elasticity_by_logs(lambda p: 10.0, 0)
    with pytest.raises(ValueError, match="需要量"):
        elasticity_by_logs(_demand, 60)


def test_弧弾力性は2つの価格が違うときだけ() -> None:
    with pytest.raises(ValueError, match="価格"):
        arc_price_elasticity(_demand, 40, 40)
