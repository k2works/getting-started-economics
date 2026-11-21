"""第 6 章: 生産関数と費用最小化のテスト。"""

import pytest

from lib.chapter06.production import (
    cost_minimizing_inputs,
    cost_minimizing_inputs_by_grid,
    isocost_k,
    isocost_slope,
    isoquant_k,
    marginal_product_capital,
    marginal_product_labor,
    minimum_cost,
    mrts,
    production,
)

# q = √(L·K)、賃金 w = 1、資本の価格 r = 4。生産量 10 の費用最小の投入は (L, K) = (20, 5)
W, R = 1, 4


def test_生産量は投入量の積のべき() -> None:
    assert production(20, 5) == pytest.approx(10)
    assert production(4, 9) == pytest.approx(6)
    assert production(8, 1, 1, 2) == 8


def test_生産量は投入量が増えると増える() -> None:
    assert production(21, 5) > production(20, 5)
    assert production(20, 6) > production(20, 5)


def test_生産量は投入量が負ならエラー() -> None:
    with pytest.raises(ValueError, match="投入量"):
        production(-1, 5)
    with pytest.raises(ValueError, match="投入量"):
        production(5, -1)


def test_生産関数のべき指数は正でなければエラー() -> None:
    with pytest.raises(ValueError, match="指数"):
        production(20, 5, 0, 0.5)
    with pytest.raises(ValueError, match="指数"):
        production(20, 5, 0.5, -1)


def test_限界生産性は投入を1単位増やしたときの生産量の増加() -> None:
    assert marginal_product_labor(20, 5) == pytest.approx(0.25)
    assert marginal_product_capital(20, 5) == pytest.approx(1)
    # 割線の傾きと近い
    h = 1e-6
    slope = (production(20 + h, 5) - production(20 - h, 5)) / (2 * h)
    assert marginal_product_labor(20, 5) == pytest.approx(slope, rel=1e-6)


def test_労働の限界生産性は労働が増えると逓減する() -> None:
    values = [marginal_product_labor(labor, 5) for labor in (5, 20, 80)]
    assert values == pytest.approx([0.5, 0.25, 0.125])
    assert all(a > b for a, b in zip(values, values[1:], strict=False))


def test_資本の限界生産性も逓減する() -> None:
    values = [marginal_product_capital(5, k) for k in (5, 20, 80)]
    assert values == pytest.approx([0.5, 0.25, 0.125])


def test_べき指数が違う限界生産性() -> None:
    # q = L^0.25 · K^0.75 の L = 16、K = 16: MPL = 0.25 · q ÷ L = 0.25
    assert marginal_product_labor(16, 16, 0.25, 0.75) == pytest.approx(0.25)
    assert marginal_product_capital(16, 16, 0.25, 0.75) == pytest.approx(0.75)


def test_限界生産性の投入量は正でなければエラー() -> None:
    with pytest.raises(ValueError, match="投入量"):
        marginal_product_labor(0, 5)
    with pytest.raises(ValueError, match="投入量"):
        marginal_product_capital(5, 0)


def test_等費用線の傾きは賃金と資本の価格の比のマイナス() -> None:
    assert isocost_slope(W, R) == pytest.approx(-0.25)
    assert isocost_slope(4, 1) == -4


def test_等費用線は費用を使い切る点を結ぶ() -> None:
    assert isocost_k(40, W, R, 0) == 10
    assert isocost_k(40, W, R, 20) == 5
    assert isocost_k(40, W, R, 40) == 0


def test_等費用線の価格は正でなければエラー() -> None:
    with pytest.raises(ValueError, match="価格"):
        isocost_slope(0, R)
    with pytest.raises(ValueError, match="価格"):
        isocost_k(40, W, 0, 1)


def test_等費用線は価格が1未満の正の値でも引ける() -> None:
    assert isocost_k(40, 0.5, 0.25, 0) == 160


def test_等産出量曲線は同じ生産量の点を結ぶ() -> None:
    for labor in (5, 10, 20, 40):
        k = isoquant_k(10, labor)
        assert production(labor, k) == pytest.approx(10)


def test_等産出量曲線は右下がりで右上ほど生産量が多い() -> None:
    ks = [isoquant_k(10, labor) for labor in (5, 10, 20, 40)]
    assert ks == pytest.approx([20, 10, 5, 2.5])
    assert isoquant_k(15, 20) > isoquant_k(10, 20)


def test_等産出量曲線は労働が正でなければエラー() -> None:
    with pytest.raises(ValueError, match="投入量"):
        isoquant_k(10, 0)
    with pytest.raises(ValueError, match="生産量"):
        isoquant_k(0, 5)


def test_技術的限界代替率は限界生産性の比() -> None:
    assert mrts(20, 5) == pytest.approx(0.25)
    assert mrts(20, 5) == pytest.approx(
        marginal_product_labor(20, 5) / marginal_product_capital(20, 5)
    )


def test_技術的限界代替率はべき指数の比も反映する() -> None:
    assert mrts(16, 16, 0.25, 0.75) == pytest.approx(0.25 / 0.75)


def test_技術的限界代替率は等産出量曲線に沿って右へ進むほど小さくなる() -> None:
    values = [mrts(labor, isoquant_k(10, labor)) for labor in (5, 10, 20, 40)]
    assert values == pytest.approx([4, 1, 0.25, 0.0625])


def test_技術的限界代替率の労働は正でなければエラー() -> None:
    with pytest.raises(ValueError, match="投入量"):
        mrts(0, 5)


def test_費用最小の投入は20と5() -> None:
    assert cost_minimizing_inputs(10, W, R) == pytest.approx((20, 5))


def test_最適点で技術的限界代替率は価格比と等しい() -> None:
    labor, k = cost_minimizing_inputs(10, W, R)
    assert mrts(labor, k) == pytest.approx(W / R)


def test_最適点で必要な生産量を作れる() -> None:
    labor, k = cost_minimizing_inputs(10, W, R)
    assert production(labor, k) == pytest.approx(10)


def test_最適点は等費用線と等産出量曲線の接点() -> None:
    labor, k = cost_minimizing_inputs(10, W, R)
    assert k == pytest.approx(isocost_k(40, W, R, labor))
    assert k == pytest.approx(isoquant_k(10, labor))


def test_賃金が上がると労働を減らして資本を増やす() -> None:
    assert cost_minimizing_inputs(10, 4, 1) == pytest.approx((5, 20))
    assert cost_minimizing_inputs(10, 1, 1) == pytest.approx((10, 10))


def test_べき指数が違う費用最小の投入も条件を満たす() -> None:
    labor, k = cost_minimizing_inputs(10, W, R, 0.25, 0.75)
    assert production(labor, k, 0.25, 0.75) == pytest.approx(10)
    assert mrts(labor, k, 0.25, 0.75) == pytest.approx(W / R)


def test_格子点の探索は閉じた式と一致する() -> None:
    result = cost_minimizing_inputs_by_grid(10, W, R, l_max=40)
    assert result == pytest.approx((20, 5))


def test_格子点の探索は別の価格でも近い() -> None:
    closed = cost_minimizing_inputs(10, 4, 1)
    grid = cost_minimizing_inputs_by_grid(10, 4, 1, l_max=40)
    assert grid == pytest.approx(closed, abs=0.1)


def test_格子点の探索は費用の低い点を選ぶ() -> None:
    labor, k = cost_minimizing_inputs_by_grid(10, W, R, l_max=40)
    best = W * labor + R * k
    for other in (5, 10, 30, 40):
        assert best <= W * other + R * isoquant_k(10, other) + 1e-9


def test_格子の分割数が2未満ならエラー() -> None:
    with pytest.raises(ValueError, match="分割"):
        cost_minimizing_inputs_by_grid(10, W, R, steps=1)


def test_格子の上限が正でなければエラー() -> None:
    with pytest.raises(ValueError, match="上限"):
        cost_minimizing_inputs_by_grid(10, W, R, l_max=0)


def test_最小の費用は投入の費用の合計() -> None:
    assert minimum_cost(10, W, R) == pytest.approx(40)
    assert minimum_cost(10, 4, 1) == pytest.approx(40)
    assert minimum_cost(10, 1, 1) == pytest.approx(20)


def test_規模に関して収穫一定なら費用は生産量に比例する() -> None:
    assert minimum_cost(20, W, R) == pytest.approx(2 * minimum_cost(10, W, R))
    assert minimum_cost(30, W, R) == pytest.approx(3 * minimum_cost(10, W, R))


def test_価格が正でなければ費用最小化はエラー() -> None:
    with pytest.raises(ValueError, match="価格"):
        cost_minimizing_inputs(10, 0, R)
    with pytest.raises(ValueError, match="価格"):
        cost_minimizing_inputs_by_grid(10, W, 0)
    with pytest.raises(ValueError, match="生産量"):
        cost_minimizing_inputs(0, W, R)
