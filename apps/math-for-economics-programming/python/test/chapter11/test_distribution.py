import functools
import math
from fractions import Fraction

import pytest

from lib.chapter05.derivative import numerical_derivative
from lib.chapter10.expectation import discrete_expected_value, discrete_variance
from lib.chapter10.risk import certainty_equivalent_of_lottery
from lib.chapter11.distribution import (
    continuous_expectation,
    continuous_expected_value,
    discretized_uniform_distribution,
    uniform_cdf,
    uniform_density,
)
from lib.chapter11.integral import midpoint_rule_integral

TWO_TO_SIX = functools.partial(uniform_density, low=2, high=6)


def test_一様分布の密度は区間の中で一定で外では0() -> None:
    assert uniform_density(0.3) == 1
    assert [TWO_TO_SIX(x) for x in (2, 3, 5.5, 6)] == [0.25] * 4
    assert [TWO_TO_SIX(x) for x in (1.9, 6.1, -4)] == [0, 0, 0]
    # 密度の下の面積（全体の確率）は 1
    assert midpoint_rule_integral(TWO_TO_SIX, 2, 6, 100) == pytest.approx(1)


def test_分布関数はその値以下になる確率で密度の下の面積() -> None:
    def cdf(x: float) -> float:
        return uniform_cdf(x, low=2, high=6)

    assert [cdf(x) for x in (1, 2, 3, 4, 6, 9)] == [0, 0, 0.25, 0.5, 1, 1]
    assert [uniform_cdf(x) for x in (-1, 0.3, 2)] == [0, 0.3, 1]
    # 3 と 5 の間になる確率 = F(5) − F(3) = 密度の下の面積
    assert cdf(5) - cdf(3) == pytest.approx(0.5)
    assert midpoint_rule_integral(TWO_TO_SIX, 3, 5, 10) == pytest.approx(0.5)
    # 分布関数を微分すると、密度に戻る（微積分学の基本定理）
    for x in (2.5, 4.2, 5.9):
        assert numerical_derivative(cdf, x, step=1e-4) == pytest.approx(TWO_TO_SIX(x))


def test_連続の期待値はxかける密度の積分で一様分布なら区間の真ん中() -> None:
    assert continuous_expected_value(uniform_density, 0, 1) == pytest.approx(0.5)
    for low, high in [(2, 6), (-3, 1), (10, 10.5)]:
        density = functools.partial(uniform_density, low=low, high=high)
        mean = continuous_expected_value(density, low, high)
        assert mean == pytest.approx((low + high) / 2)


def test_一様分布を細かく離散化すると離散の期待値と分散が連続の値に近づく() -> None:
    ten = discretized_uniform_distribution(10)
    assert list(ten) == [Fraction(k, 10) for k in range(1, 11)]
    assert set(ten.values()) == {Fraction(1, 10)}
    assert discrete_expected_value(ten) == Fraction(11, 20)
    assert discrete_variance(ten) == Fraction(99, 1200)
    # 点を増やすと、期待値のずれは 1 ÷ (2n) で 0 に近づく
    for points in (10, 100, 1000):
        mean = discrete_expected_value(discretized_uniform_distribution(points))
        assert mean - Fraction(1, 2) == Fraction(1, 2 * points)
    fine = discretized_uniform_distribution(1000)
    variance = continuous_expectation(lambda x: (x - 0.5) ** 2, uniform_density, 0, 1)
    assert variance == pytest.approx(1 / 12)
    assert float(discrete_variance(fine)) == pytest.approx(variance, rel=1e-5)


def test_連続の期待効用は効用かける密度の積分() -> None:
    # 0 から 100 の一様分布で、効用 √x: (1/100)·∫₀¹⁰⁰ √x dx = 20/3
    density = functools.partial(uniform_density, low=0, high=100)
    expected_utility = continuous_expectation(math.sqrt, density, 0, 100)
    assert expected_utility == pytest.approx(20 / 3, rel=1e-6)
    # 確実性等価は (20/3)² ≈ 44.4。0 か 100 の賭け（第 10 章）の 25 より大きい
    certainty_equivalent = expected_utility**2
    assert certainty_equivalent == pytest.approx(400 / 9, rel=1e-5)
    coin = {0: Fraction(1, 2), 100: Fraction(1, 2)}
    assert certainty_equivalent > certainty_equivalent_of_lottery(coin, math.sqrt)
    assert continuous_expected_value(density, 0, 100) == pytest.approx(50)


def test_一様分布の区間は下端より上端が大きい() -> None:
    for low, high in [(1, 1), (3, 2)]:
        with pytest.raises(ValueError):
            uniform_density(1.5, low, high)
        with pytest.raises(ValueError):
            uniform_cdf(1.5, low, high)
    with pytest.raises(ValueError):
        discretized_uniform_distribution(0)
    assert discretized_uniform_distribution(1) == {Fraction(1): Fraction(1)}
