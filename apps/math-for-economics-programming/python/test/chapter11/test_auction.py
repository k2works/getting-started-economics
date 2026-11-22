import functools
import statistics
from fractions import Fraction

import pytest

from lib.chapter02.quadratic import argmax_on_grid
from lib.chapter11.auction import (
    expected_auction_revenue_formula,
    expected_order_statistic,
    first_price_equilibrium_bid,
    first_price_expected_payoff,
    first_price_expected_revenue,
    order_statistic_density,
    second_price_expected_revenue,
    second_price_payoff,
    simulate_auction_revenues,
)
from lib.chapter11.distribution import continuous_expected_value
from lib.chapter11.integral import midpoint_rule_integral


def test_最高の評価額と2番目の評価額の密度() -> None:
    # 3 人なら、最高は 3v²、2 番目は 6v(1 − v)
    assert order_statistic_density(0.5, 3, 1) == pytest.approx(0.75)
    assert order_statistic_density(0.5, 3, 2) == pytest.approx(1.5)
    assert order_statistic_density(0.2, 4, 2) == pytest.approx(12 * 0.2**2 * 0.8)
    # 1 人なら、最高の評価額は一様分布そのもの
    assert order_statistic_density(0.3, 1, 1) == 1
    for bidders, rank in [(2, 1), (2, 2), (5, 1), (5, 2), (5, 4)]:
        density = functools.partial(order_statistic_density, bidders=bidders, rank=rank)
        assert midpoint_rule_integral(density, 0, 1, 1000) == pytest.approx(1, rel=1e-5)
    # 3 人の最高が 0.5 以下になる確率 = 3 人とも 0.5 以下 = (1/2)³
    below_half = midpoint_rule_integral(
        lambda v: order_statistic_density(v, 3, 1), 0, 0.5, 1000
    )
    assert below_half == pytest.approx(1 / 8, rel=1e-5)


def test_セカンドプライスでは評価額どおりの入札がどの入札より悪くない() -> None:
    assert second_price_payoff(0.7, 0.7, [0.4, 0.2]) == pytest.approx(0.3)
    # 高く入札しすぎると、評価額より高く払って損をする
    assert second_price_payoff(0.7, 0.9, [0.8]) == pytest.approx(-0.1)
    # 低く入札しすぎると、得られた 0.1 を逃す
    assert second_price_payoff(0.7, 0.5, [0.6]) == 0
    # 同じ入札額なら、勝たない（この章の約束）
    assert second_price_payoff(0.7, 0.6, [0.6]) == 0
    bids = [i / 20 for i in range(21)]
    for value in (0.25, 0.7):
        for rivals in ([0.1], [0.5, 0.3], [0.65, 0.9], [0.2, 0.24, 0.6]):
            truthful = second_price_payoff(value, value, rivals)
            assert all(truthful >= second_price_payoff(value, b, rivals) for b in bids)


def test_セカンドプライスの期待収入は2番目の評価額の期待値() -> None:
    assert expected_auction_revenue_formula(2) == Fraction(1, 3)
    assert second_price_expected_revenue(2) == pytest.approx(1 / 3, rel=1e-5)
    for bidders in (3, 4, 6):
        formula = expected_auction_revenue_formula(bidders)
        assert formula == Fraction(bidders - 1, bidders + 1)
        revenue = second_price_expected_revenue(bidders)
        assert revenue == pytest.approx(float(formula), rel=1e-5)


def test_ファーストプライスの均衡入札は評価額を割り引き期待収入は同じ() -> None:
    assert first_price_equilibrium_bid(0.6, 2) == pytest.approx(0.3)
    assert first_price_equilibrium_bid(0.9, 3) == pytest.approx(0.6)
    assert first_price_equilibrium_bid(0.8, 5) == pytest.approx(0.64)
    # 収入同値: 入札は低いが、最高の評価額の人が払うので、期待収入は同じ
    for bidders in (2, 3, 5):
        first = first_price_expected_revenue(bidders)
        assert first == pytest.approx(second_price_expected_revenue(bidders), rel=1e-5)
        formula = float(expected_auction_revenue_formula(bidders))
        assert first == pytest.approx(formula, rel=1e-5)


def test_シミュレーションの平均収入は公式に近い() -> None:
    for bidders in (2, 5):
        formula = float(expected_auction_revenue_formula(bidders))
        for rule in ("first", "second"):
            revenues = simulate_auction_revenues(bidders, 20_000, seed=1, rule=rule)
            assert len(revenues) == 20_000
            # 標準誤差は 0.002 以下。その 5 倍ほどの幅で比べる
            assert statistics.fmean(revenues) == pytest.approx(formula, abs=0.01)


def test_平均は同じでもセカンドプライスの収入のほうがばらつく() -> None:
    first = simulate_auction_revenues(2, 20_000, seed=2, rule="first")
    second = simulate_auction_revenues(2, 20_000, seed=2, rule="second")
    # 2 人なら、分散はファーストが 1/72、セカンドが 1/18
    assert statistics.pvariance(first) == pytest.approx(1 / 72, abs=0.002)
    assert statistics.pvariance(second) == pytest.approx(1 / 18, abs=0.004)
    # 2 人なら、ファーストの収入は最高の評価額の半分で 0.5 を超えない。セカンドは超える
    assert all(f <= 0.5 for f in first)
    assert max(second) > 0.9


def test_種が同じなら結果も同じ() -> None:
    first = simulate_auction_revenues(3, 50, seed=7, rule="second")
    assert first == simulate_auction_revenues(3, 50, seed=7, rule="second")
    assert first != simulate_auction_revenues(3, 50, seed=8, rule="second")


def test_オークションは2人以上で順位は1から人数まで() -> None:
    for bad in (1, 0):
        with pytest.raises(ValueError):
            second_price_expected_revenue(bad)
        with pytest.raises(ValueError):
            first_price_equilibrium_bid(0.5, bad)
        with pytest.raises(ValueError):
            simulate_auction_revenues(bad, 10, seed=1, rule="first")
        with pytest.raises(ValueError):
            expected_auction_revenue_formula(bad)
    with pytest.raises(ValueError):
        simulate_auction_revenues(2, 0, seed=1, rule="first")
    assert len(simulate_auction_revenues(2, 1, seed=1, rule="first")) == 1
    for bidders, rank in [(3, 0), (3, 4), (0, 1)]:
        with pytest.raises(ValueError):
            order_statistic_density(0.5, bidders, rank)
    with pytest.raises(ValueError):
        second_price_payoff(0.5, 0.5, [])


def test_k番目に高い評価額の期待値は人数と順位で決まる() -> None:
    # (n − k + 1) ÷ (n + 1)。4 人なら、4/5・3/5・2/5・1/5 と等間隔に並ぶ
    assert [expected_order_statistic(4, k) for k in (1, 2, 3, 4)] == [
        Fraction(4, 5),
        Fraction(3, 5),
        Fraction(2, 5),
        Fraction(1, 5),
    ]
    for bidders, rank in [(2, 2), (5, 1), (5, 3), (7, 6)]:
        density = functools.partial(order_statistic_density, bidders=bidders, rank=rank)
        mean = continuous_expected_value(density, 0, 1, 1000)
        expected = float(expected_order_statistic(bidders, rank))
        assert mean == pytest.approx(expected, rel=1e-5)
    with pytest.raises(ValueError):
        expected_order_statistic(3, 4)


def test_ファーストプライスで相手が均衡入札なら自分も均衡入札が最適() -> None:
    # 相手が 1 人で v/2 を入札するとき、評価額 0.8 の人の期待利得は (0.8 − b)·2b
    assert first_price_expected_payoff(0.8, 0.3, 2) == pytest.approx(0.5 * 0.6)
    # 入札が高すぎて、相手の入札の上限を超えると、必ず勝つ
    assert first_price_expected_payoff(0.8, 0.6, 2) == pytest.approx(0.2)
    for value, bidders in [(0.8, 2), (0.6, 3), (0.9, 5)]:
        payoff = functools.partial(first_price_expected_payoff, value, bidders=bidders)
        best = argmax_on_grid(payoff, 0, value, 10_001)
        expected = first_price_equilibrium_bid(value, bidders)
        assert best == pytest.approx(expected, abs=1e-3)
