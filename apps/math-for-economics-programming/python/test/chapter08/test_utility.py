import pytest

from lib.chapter05.derivative import numerical_derivative
from lib.chapter07.budget import (
    budget_status,
    consumption_given_leisure,
    full_income,
    lifetime_income_present_value,
    second_period_consumption,
)
from lib.chapter08.partial import Surface, numerical_partial_x, numerical_partial_y
from lib.chapter08.utility import (
    best_bundle_on_budget_line,
    budget_line_bundles,
    cobb_douglas_demand,
    cobb_douglas_indifference_y,
    cobb_douglas_lagrange_multiplier,
    cobb_douglas_marginal_utilities,
    cobb_douglas_mrs,
    cobb_douglas_utility,
    numerical_mrs,
    quasilinear_demand,
    quasilinear_utility,
)


def _cobb_douglas(share: float) -> Surface:
    """効用 U = x^a·y^(1−a) を、2 変数の関数にする（偏微分に渡すため）。"""
    return lambda x, y: cobb_douglas_utility(x, y, share)


def _quasilinear(weight: float) -> Surface:
    """効用 U = b·√x + y を、2 変数の関数にする。"""
    return lambda x, y: quasilinear_utility(x, y, weight)


def test_コブダグラス型の効用はxのa乗とyの1マイナスa乗の積() -> None:
    assert cobb_douglas_utility(25, 10, 0.5) == pytest.approx(250**0.5)
    assert cobb_douglas_utility(8, 27, 1 / 3) == pytest.approx(18)


def test_限界効用の公式は偏微分の数値と一致する() -> None:
    for x, y, share in [(25, 10, 0.5), (21, 14, 0.3), (0.4, 3, 0.8), (3, 0.6, 0.3)]:
        mu_x, mu_y = cobb_douglas_marginal_utilities(x, y, share)
        utility = _cobb_douglas(share)
        assert mu_x == pytest.approx(numerical_partial_x(utility, x, y))
        assert mu_y == pytest.approx(numerical_partial_y(utility, x, y))


def test_限界代替率は限界効用の比() -> None:
    assert cobb_douglas_mrs(25, 10, 0.5) == pytest.approx(0.4)
    assert cobb_douglas_mrs(21, 14, 0.3) == pytest.approx(0.3 / 0.7 * 14 / 21)
    assert numerical_mrs(_cobb_douglas(0.5), 25, 10) == pytest.approx(0.4)


def test_価格2と5で所得100ならxは25でyは10() -> None:
    assert cobb_douglas_demand([2, 5], 100, 0.5) == pytest.approx((25, 10))
    assert cobb_douglas_utility(25, 10, 0.5) == pytest.approx(15.81, abs=0.01)


def test_aが0点3なら所得の3割をxに使う() -> None:
    x, y = cobb_douglas_demand([2, 7], 140, 0.3)
    assert (x, y) == pytest.approx((21, 14))
    assert 2 * x == pytest.approx(0.3 * 140)


def test_最適点では限界代替率が価格比に等しく予算線上にある() -> None:
    for prices, income, share in [([2, 5], 100, 0.5), ([2, 7], 140, 0.3)]:
        x, y = cobb_douglas_demand(prices, income, share)
        assert cobb_douglas_mrs(x, y, share) == pytest.approx(prices[0] / prices[1])
        assert budget_status(prices, [x, y], income) == "on"


def test_ラグランジュ乗数は1円あたりの限界効用でどちらの財でも等しい() -> None:
    multiplier = cobb_douglas_lagrange_multiplier([2, 5], 100, 0.5)
    assert multiplier == pytest.approx(0.158, abs=1e-3)
    mu_x, mu_y = cobb_douglas_marginal_utilities(25, 10, 0.5)
    assert mu_x / 2 == pytest.approx(multiplier)
    assert mu_y / 5 == pytest.approx(multiplier)


@pytest.mark.parametrize(
    ("prices", "income", "share"), [([2, 5], 100, 0.5), ([2, 7], 140, 0.3)]
)
def test_ラグランジュ乗数は所得が1増えたときの効用の増え方(
    prices: list[float], income: float, share: float
) -> None:
    slope = numerical_derivative(
        lambda m: cobb_douglas_utility(*cobb_douglas_demand(prices, m, share), share),
        income,
    )
    assert slope == pytest.approx(
        cobb_douglas_lagrange_multiplier(prices, income, share)
    )


def test_予算線上の格子は2つの切片を結び全部が予算線上() -> None:
    bundles = budget_line_bundles([2, 5], 100, 5)
    assert bundles == [(0, 20), (12.5, 15), (25, 10), (37.5, 5), (50, 0)]
    assert all(budget_status([2, 5], list(b), 100) == "on" for b in bundles)


def test_格子探索の最大は解析解と一致する() -> None:
    for prices, income, share in [([2, 5], 100, 0.5), ([2, 7], 140, 0.3)]:
        best = best_bundle_on_budget_line(_cobb_douglas(share), prices, income, 2001)
        expected = cobb_douglas_demand(prices, income, share)
        assert best == pytest.approx(expected, abs=0.05)


def test_準線形効用は重み付きの平方根とyの和() -> None:
    assert quasilinear_utility(9, 2.5, 4) == pytest.approx(14.5)


def test_準線形効用の最適点は限界代替率が価格比に等しい() -> None:
    assert quasilinear_demand([2, 1], 20, 4) == pytest.approx((1, 18))
    x, y = quasilinear_demand([1, 2], 10, 1)
    assert (x, y) == pytest.approx((1, 4.5))
    assert numerical_mrs(_quasilinear(1), x, y) == pytest.approx(1 / 2)


def test_準線形効用ではxの需要が所得によらない() -> None:
    for income in [20, 50, 1000]:
        x, _ = quasilinear_demand([2, 1], income, 4)
        assert x == pytest.approx(1)


def test_準線形効用では価格と限界効用が等しい点が需要曲線になる() -> None:
    # y の価格を 1（お金）にすると、x の価格 p ＝ x の限界効用。逆需要曲線 p = 2 ÷ √x
    for price in [0.5, 1, 2.5]:
        x, _ = quasilinear_demand([price, 1], 1000, 4)
        assert numerical_partial_x(_quasilinear(4), x, 1) == pytest.approx(price)
        assert price == pytest.approx(2 / x**0.5)


def test_所得が少ないと準線形効用の最適点はyが0の端点解() -> None:
    assert quasilinear_demand([1, 2], 10, 4) == pytest.approx((10, 0))
    best = best_bundle_on_budget_line(_quasilinear(4), [1, 2], 10, 2001)
    assert best == pytest.approx((10, 0))
    # 端点では、U_x ÷ U_y（U_y = 1）が価格比 1/2 より大きい。x をもっと買いたいが、所得が尽きた
    assert numerical_partial_x(_quasilinear(4), 10, 0) > 1 / 2


def test_労働と余暇は価格1と賃金の予算での効用最大化() -> None:
    consumption, leisure = cobb_douglas_demand([1, 10], full_income(10, 24), 0.5)
    assert (consumption, leisure) == pytest.approx((120, 12))
    consumption, leisure = cobb_douglas_demand([1, 8], full_income(8, 24, 40), 0.6)
    assert (consumption, leisure) == pytest.approx((139.2, 11.6))
    assert consumption == pytest.approx(consumption_given_leisure(leisure, 8, 24, 40))


def test_消費と貯蓄は来期の価格1割る1プラスrの予算での効用最大化() -> None:
    wealth = lifetime_income_present_value(100, 110, 0.1)
    first, second = cobb_douglas_demand([1, 1 / 1.1], wealth, 0.6)
    assert (first, second) == pytest.approx((120, 88))
    assert second == pytest.approx(second_period_consumption(first, 100, 110, 0.1))


def test_数量が0なら効用は0で限界効用は決まらない() -> None:
    assert cobb_douglas_utility(0, 7, 0.4) == 0
    with pytest.raises(ValueError):
        cobb_douglas_marginal_utilities(0, 7, 0.4)
    with pytest.raises(ValueError):
        cobb_douglas_marginal_utilities(3, 0, 0.4)


def test_指数aは0より大きく1より小さい() -> None:
    for share in [0, 1, -0.2, 1.5]:
        with pytest.raises(ValueError):
            cobb_douglas_utility(2, 3, share)
        with pytest.raises(ValueError):
            cobb_douglas_demand([2, 5], 100, share)


def test_負の数量の効用は決まらない() -> None:
    with pytest.raises(ValueError):
        cobb_douglas_utility(-1, 3, 0.5)
    with pytest.raises(ValueError):
        cobb_douglas_utility(1, -3, 0.5)
    with pytest.raises(ValueError):
        quasilinear_utility(-1, 3, 2)
    with pytest.raises(ValueError):
        quasilinear_utility(1, -3, 2)


def test_所得0なら何も買わない() -> None:
    assert cobb_douglas_demand([2, 5], 0, 0.5) == (0, 0)
    assert quasilinear_demand([2, 1], 0, 4) == (0, 0)


def test_負の所得や2財でない予算では効用最大化は決まらない() -> None:
    for prices, income in [([2, 5], -1), ([2, 5, 1], 100), ([0, 5], 100)]:
        with pytest.raises(ValueError):
            cobb_douglas_demand(prices, income, 0.5)
        with pytest.raises(ValueError):
            quasilinear_demand(prices, income, 4)
        with pytest.raises(ValueError):
            budget_line_bundles(prices, income, 5)


def test_所得がちょうど足りるとき準線形効用の最適点はyが0() -> None:
    # x* = (4 × 2 ÷ 2)² = 16 で、所得 16 をちょうど使い切る
    assert quasilinear_demand([1, 2], 16, 4) == pytest.approx((16, 0))
    assert quasilinear_demand([1, 2], 16.5, 4) == pytest.approx((16, 0.25))


def test_格子は2点以上必要で2点なら2つの切片() -> None:
    assert budget_line_bundles([2, 5], 100, 2) == [(0, 20), (50, 0)]
    with pytest.raises(ValueError):
        budget_line_bundles([2, 5], 100, 1)


def test_無差別曲線上の点は効用が同じ水準() -> None:
    for x in [1, 6.25, 25, 0.4]:
        y = cobb_douglas_indifference_y(250**0.5, x, 0.5)
        assert cobb_douglas_utility(x, y, 0.5) == pytest.approx(250**0.5)
    assert cobb_douglas_indifference_y(18, 8, 1 / 3) == pytest.approx(27)


def test_無差別曲線はxが正のときだけ描ける() -> None:
    with pytest.raises(ValueError):
        cobb_douglas_indifference_y(10, 0, 0.5)


def test_負の効用水準の無差別曲線は決まらない() -> None:
    assert cobb_douglas_indifference_y(0, 4, 0.5) == 0
    with pytest.raises(ValueError):
        cobb_douglas_indifference_y(-1, 4, 0.5)


def test_準線形効用の重みが正でなければ需要は決まらない() -> None:
    for weight in [0, -4]:
        with pytest.raises(ValueError):
            quasilinear_demand([1, 2], 10, weight)
