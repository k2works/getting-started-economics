"""第 7 章: 利潤最大化と供給曲線のテスト。"""

import pytest

from lib.chapter05.cost import CostCurve, marginal_cost, total_cost
from lib.chapter07.supply import (
    break_even_price,
    free_entry_output,
    free_entry_price,
    market_supply,
    market_supply_curve,
    number_of_firms,
    profit,
    profit_maximizing_output,
    profit_maximizing_output_by_grid,
    shutdown_price,
    supply_after_ad_valorem_tax,
    supply_after_unit_tax,
    supply_curve,
    supply_elasticity,
    supply_price,
    supply_price_ad_valorem,
    supply_price_unit_tax,
)

# C(q) = q³ − 6q² + 15q + 32（第 5 章）。損益分岐点 15（q = 4）、操業停止点 6（q = 3）
CURVE = CostCurve(1, -6, 15, 32)
# 係数が違う例: C(q) = 0.5q³ − 3q² + 10q + 20。操業停止点 5.5（q = 3）
OTHER = CostCurve(0.5, -3, 10, 20)


def test_価格30の利潤最大の生産量は5() -> None:
    q = profit_maximizing_output(CURVE, 30)
    assert q == pytest.approx(5)
    assert marginal_cost(CURVE, q) == pytest.approx(30)


def test_価格が限界費用と等しい点で利潤が最大() -> None:
    best = profit(CURVE, 30, 5)
    for q in (3, 4, 4.5, 5.5, 6, 7):
        assert profit(CURVE, 30, q) < best


def test_価格30の利潤は68() -> None:
    assert profit(CURVE, 30, 5) == pytest.approx(68)
    assert profit(CURVE, 30, 5) == pytest.approx((30 - 82 / 5) * 5)


def test_利潤は価格かける生産量引く総費用() -> None:
    assert profit(CURVE, 30, 5) == 30 * 5 - total_cost(CURVE, 5)
    assert profit(CURVE, 30, 0) == -32


def test_損益分岐点の価格は平均費用の最低点() -> None:
    assert break_even_price(CURVE) == pytest.approx(15, rel=1e-6)


def test_損益分岐点で利潤は0() -> None:
    price = break_even_price(CURVE)
    q = profit_maximizing_output(CURVE, price)
    assert q == pytest.approx(4, abs=1e-3)
    assert profit(CURVE, price, q) == pytest.approx(0, abs=1e-3)


def test_操業停止点の価格は平均可変費用の最低点() -> None:
    assert shutdown_price(CURVE) == pytest.approx(6)
    assert shutdown_price(OTHER) == pytest.approx(5.5)


def test_操業停止点で作っても作らなくても損失は固定費用() -> None:
    price = shutdown_price(CURVE)
    q = profit_maximizing_output(CURVE, price)
    assert q == pytest.approx(3)
    assert profit(CURVE, price, q) == pytest.approx(-32)
    assert profit(CURVE, price, 0) == -32


def test_操業停止点の探索は格子点の最低点と一致する() -> None:
    from lib.chapter05.cost import cost_minima

    assert shutdown_price(CURVE) == pytest.approx(
        cost_minima(CURVE)["AVC"][1], abs=1e-4
    )


def test_価格が操業停止点未満なら作らない() -> None:
    assert profit_maximizing_output(CURVE, 5.99) == 0
    assert profit_maximizing_output(CURVE, 0) == 0


def test_価格が損益分岐点と操業停止点の間なら赤字でも固定費の一部を回収する() -> None:
    q = profit_maximizing_output(CURVE, 10)
    assert q == pytest.approx((6 + 21**0.5) / 3)
    loss = profit(CURVE, 10, q)
    assert -32 < loss < 0


def test_価格が負ならエラー() -> None:
    with pytest.raises(ValueError, match="価格"):
        profit_maximizing_output(CURVE, -1)


def test_係数が違う費用関数の利潤最大化() -> None:
    q = profit_maximizing_output(OTHER, 30)
    assert marginal_cost(OTHER, q) == pytest.approx(30)
    assert q == pytest.approx(2 + (4 + 40 / 3) ** 0.5)


def test_格子点の探索は閉じた式と一致する() -> None:
    assert profit_maximizing_output_by_grid(CURVE, 30) == pytest.approx(5, abs=1e-3)
    assert profit_maximizing_output_by_grid(CURVE, 10) == pytest.approx(
        profit_maximizing_output(CURVE, 10), abs=1e-3
    )


def test_格子点の探索は操業停止の価格では作らない() -> None:
    assert profit_maximizing_output_by_grid(CURVE, 5) == 0


def test_格子点の探索の点の数が少なすぎればエラー() -> None:
    with pytest.raises(ValueError, match="点の数"):
        profit_maximizing_output_by_grid(CURVE, 30, points=2)


def test_供給曲線は価格と供給量の組() -> None:
    curve = supply_curve(CURVE, [5, 6, 15, 30])
    assert [p for p, _ in curve] == [5, 6, 15, 30]
    assert [q for _, q in curve] == pytest.approx([0, 3, 4, 5])


def test_供給曲線は操業停止点を境に不連続にジャンプする() -> None:
    below, above = (q for _, q in supply_curve(CURVE, [5.99, 6]))
    assert below == 0
    assert above == pytest.approx(3)


def test_供給曲線は右上がり() -> None:
    quantities = [q for _, q in supply_curve(CURVE, [6, 10, 15, 30, 60])]
    assert all(a < b for a, b in zip(quantities, quantities[1:], strict=False))


def test_市場供給は各企業の供給を横に足したもの() -> None:
    assert market_supply([CURVE, CURVE], 30) == pytest.approx(10)
    assert market_supply([CURVE, OTHER], 30) == pytest.approx(
        5 + 2 + (4 + 40 / 3) ** 0.5
    )


def test_市場供給は企業が参入すると増える() -> None:
    assert market_supply([CURVE, CURVE, CURVE], 30) > market_supply([CURVE, CURVE], 30)


def test_市場供給は操業停止点より低い価格の企業が退出する() -> None:
    # 価格 5.7 は CURVE の操業停止点（6）より低いが、OTHER の（5.5）より高い
    assert market_supply([CURVE, OTHER], 5.7) == pytest.approx(
        profit_maximizing_output(OTHER, 5.7)
    )
    assert profit_maximizing_output(CURVE, 5.7) == 0


def test_市場供給曲線は各価格の合計() -> None:
    curve = market_supply_curve([CURVE, CURVE], [6, 30])
    assert [p for p, _ in curve] == [6, 30]
    assert [q for _, q in curve] == pytest.approx([6, 10])


def test_供給の価格弾力性は価格30で3分の1() -> None:
    e = supply_elasticity(lambda p: profit_maximizing_output(CURVE, p), 30)
    assert e == pytest.approx(1 / 3, rel=1e-5)


def test_供給の価格弾力性は価格とともに増えて0_5に近づく() -> None:
    def supply(p: float) -> float:
        return profit_maximizing_output(CURVE, p)

    values = [supply_elasticity(supply, p) for p in (10, 30, 60, 300, 3000)]
    assert values == pytest.approx([0.3093, 0.3333, 0.3608, 0.4205, 0.4707], abs=1e-4)
    assert all(a < b < 0.5 for a, b in zip(values, values[1:], strict=False))


def test_供給量が0なら供給の弾力性は求められない() -> None:
    with pytest.raises(ValueError, match="供給量"):
        supply_elasticity(lambda p: 0.0, 10)


def test_供給の弾力性の価格は正でなければエラー() -> None:
    with pytest.raises(ValueError, match="価格"):
        supply_elasticity(lambda p: p, 0)


def test_供給価格は限界費用() -> None:
    assert supply_price(CURVE, 5) == 30
    assert supply_price(CURVE, 4) == 15


def test_従量税は供給曲線を税額だけ上へ動かす() -> None:
    assert supply_price_unit_tax(CURVE, 5, 6) == 36
    assert supply_after_unit_tax(CURVE, 36, 6) == pytest.approx(5)


def test_従量税のもとで同じ量を作る価格は税額だけ高い() -> None:
    for q in (3, 4, 5):
        gap = supply_price_unit_tax(CURVE, q, 6) - supply_price(CURVE, q)
        assert gap == 6


def test_従価税は供給曲線の傾きを急にする() -> None:
    assert supply_price_ad_valorem(CURVE, 5, 0.2) == pytest.approx(37.5)
    assert supply_after_ad_valorem_tax(CURVE, 37.5, 0.2) == pytest.approx(5)


def test_従価税のもとの価格の上乗せは生産量が増えると大きくなる() -> None:
    gaps = [
        supply_price_ad_valorem(CURVE, q, 0.2) - supply_price(CURVE, q)
        for q in (3, 4, 5)
    ]
    assert gaps == pytest.approx([1.5, 3.75, 7.5])
    assert all(a < b for a, b in zip(gaps, gaps[1:], strict=False))


def test_税率は0以上1未満でなければエラー() -> None:
    with pytest.raises(ValueError, match="税率"):
        supply_price_ad_valorem(CURVE, 5, 1)
    with pytest.raises(ValueError, match="税率"):
        supply_price_ad_valorem(CURVE, 5, -0.1)
    with pytest.raises(ValueError, match="税率"):
        supply_after_ad_valorem_tax(CURVE, 30, 1)


def test_税率0は課税なしと同じ() -> None:
    assert supply_price_ad_valorem(CURVE, 5, 0) == 30
    assert supply_after_ad_valorem_tax(CURVE, 30, 0) == pytest.approx(5)


def test_従量税の税額が負ならエラー() -> None:
    with pytest.raises(ValueError, match="税額"):
        supply_price_unit_tax(CURVE, 5, -1)
    with pytest.raises(ValueError, match="税額"):
        supply_after_unit_tax(CURVE, 30, -1)


def test_課税後の価格が手取りの操業停止点以下なら供給は0() -> None:
    assert supply_after_unit_tax(CURVE, 10, 6) == 0
    assert supply_after_unit_tax(CURVE, 3, 6) == 0
    assert supply_after_ad_valorem_tax(CURVE, 6, 0.2) == 0


# --- 独立した変異確認で見つかった穴を埋めるテスト ---

RISING = CostCurve(
    1, 6, 15, 32
)  # AVC = q² + 6q + 15 は、右上がり（最低値は q → 0 の 15）


def test_平均可変費用が右上がりなら操業停止点は限界費用の切片() -> None:
    assert shutdown_price(RISING) == 15


def test_平均可変費用が右上がりの費用関数の利潤最大化() -> None:
    q = profit_maximizing_output(RISING, 20)
    assert marginal_cost(RISING, q) == pytest.approx(20)
    assert q == pytest.approx((-6 + 51**0.5) / 3)
    assert profit_maximizing_output(RISING, 14.9) == 0


def test_既定の格子は損益分岐点と利潤最大の点を正確に通る() -> None:
    assert break_even_price(CURVE) == pytest.approx(15, rel=1e-12)
    assert profit_maximizing_output_by_grid(CURVE, 30) == pytest.approx(5, abs=1e-12)


def test_点の数が3でも利潤最大の点を探せる() -> None:
    assert profit_maximizing_output_by_grid(CURVE, 30, points=3) == 5


def test_供給の弾力性は傾きと価格を供給量で割る() -> None:
    # 供給 Q = 2P（傾き 2）の P = 10 で、e = 2 × 10 ÷ 20 = 1
    assert supply_elasticity(lambda p: 2 * p, 10) == pytest.approx(1)
    assert supply_elasticity(lambda p: 5 + 2 * p, 10) == pytest.approx(2 * 10 / 25)


def test_自由参入の長期均衡は平均費用の最低点() -> None:
    assert free_entry_price(CURVE) == pytest.approx(15)
    assert free_entry_output(CURVE) == pytest.approx(4)
    assert profit(
        CURVE, free_entry_price(CURVE), free_entry_output(CURVE)
    ) == pytest.approx(0)


def test_長期の供給曲線は平均費用の最低価格で水平() -> None:
    price = free_entry_price(CURVE)
    assert profit_maximizing_output(CURVE, price) == pytest.approx(
        free_entry_output(CURVE)
    )
    assert free_entry_price(OTHER) == pytest.approx(break_even_price(OTHER))


def test_長期の企業数は市場の需要量を企業の生産量で割った値() -> None:
    assert number_of_firms(CURVE, 100) == pytest.approx(25)
    assert number_of_firms(CURVE, 200) == pytest.approx(50)


def test_企業数の市場の数量は正でなければエラー() -> None:
    with pytest.raises(ValueError, match="数量"):
        number_of_firms(CURVE, 0)
