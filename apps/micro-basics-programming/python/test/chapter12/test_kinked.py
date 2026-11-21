"""第 12 章: 屈折需要曲線（価格の硬直性）のテスト。"""

import pytest

from lib.chapter12.kinked import (
    KinkedDemand,
    marginal_revenue_above,
    marginal_revenue_below,
    marginal_revenue_gap,
    price_stays,
    price_when_demand_shifts,
)

# 屈折点 (数量 40、価格 50)。上は緩やか（傾き 0.5）、下は急（傾き 2）
KINKED = KinkedDemand(kink_quantity=40, kink_price=50, upper_slope=0.5, lower_slope=2)


def test_屈折点で限界収入は上下に分かれる() -> None:
    assert marginal_revenue_above(KINKED) == pytest.approx(50 - 0.5 * 40)
    assert marginal_revenue_below(KINKED) == pytest.approx(50 - 2 * 40)


def test_限界収入の途切れの大きさ() -> None:
    assert marginal_revenue_gap(KINKED) == pytest.approx(60)
    assert marginal_revenue_gap(KINKED) == pytest.approx(
        marginal_revenue_above(KINKED) - marginal_revenue_below(KINKED)
    )


def test_限界費用が途切れの中なら価格は変わらない() -> None:
    assert price_stays(KINKED, 10)
    assert price_stays(KINKED, 30)
    assert price_stays(KINKED, -30)
    assert not price_stays(KINKED, 31)
    assert not price_stays(KINKED, -31)


def test_限界費用が変わっても価格は同じ() -> None:
    assert price_when_demand_shifts(KINKED, 10) == 50
    assert price_when_demand_shifts(KINKED, 30) == 50


def test_途切れを出る費用の上昇は価格を動かす() -> None:
    with pytest.raises(ValueError, match="屈折"):
        price_when_demand_shifts(KINKED, 40)


def test_屈折には上の傾きが下より小さいことが必要() -> None:
    with pytest.raises(ValueError, match="傾き"):
        KinkedDemand(40, 50, 2, 0.5)
    with pytest.raises(ValueError, match="傾き"):
        KinkedDemand(40, 50, 0, 2)
    with pytest.raises(ValueError, match="屈折点"):
        KinkedDemand(0, 50, 0.5, 2)
    with pytest.raises(ValueError, match="屈折点"):
        KinkedDemand(40, 0, 0.5, 2)


def test_傾きの差が大きいほど途切れが大きい() -> None:
    wide = KinkedDemand(40, 50, 0.5, 4)
    assert marginal_revenue_gap(wide) > marginal_revenue_gap(KINKED)
    assert marginal_revenue_gap(wide) == pytest.approx((4 - 0.5) * 40)


def test_1より小さい屈折点も作れる() -> None:
    small = KinkedDemand(0.5, 0.5, 0.5, 2)
    assert marginal_revenue_gap(small) == pytest.approx(0.75)
