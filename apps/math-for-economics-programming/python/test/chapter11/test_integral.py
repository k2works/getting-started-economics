import functools
import math

import pytest

from lib.chapter05.derivative import Polynomial, numerical_derivative
from lib.chapter11.integral import (
    midpoint_rule_integral,
    polynomial_antiderivative,
    polynomial_definite_integral,
    quadrature_errors,
    trapezoid_rule_integral,
)

CUBIC = Polynomial((1, -2, 0, 3))


def _cube(x: float) -> float:
    return x**3


def test_直線の下の面積は中点法でも台形法でも台形の面積に一致する() -> None:
    # 2x + 1 の 1 から 4 までの面積: 台形 (3 + 9) × 3 ÷ 2 = 18
    for rule in (midpoint_rule_integral, trapezoid_rule_integral):
        assert rule(lambda x: 2 * x + 1, 1, 4, 3) == pytest.approx(18)
        assert rule(lambda x: 2 * x + 1, 1, 4, 1) == pytest.approx(18)


def test_曲線では分割を細かくするほど正しい面積に近づく() -> None:
    # x³ の 0 から 2 までの面積は 2⁴ ÷ 4 = 4
    assert midpoint_rule_integral(_cube, 0, 2, 1) == pytest.approx(2)
    assert trapezoid_rule_integral(_cube, 0, 2, 1) == pytest.approx(8)
    assert midpoint_rule_integral(_cube, 0, 2, 2) == pytest.approx(3.5)
    assert trapezoid_rule_integral(_cube, 0, 2, 2) == pytest.approx(5)
    assert midpoint_rule_integral(_cube, 0, 2, 1000) == pytest.approx(4, abs=1e-5)
    assert trapezoid_rule_integral(_cube, 0, 2, 1000) == pytest.approx(4, abs=1e-5)


def test_分割数を2倍にすると誤差はおよそ4分の1になる() -> None:
    pieces = [10, 20, 40, 80]
    for rule in (midpoint_rule_integral, trapezoid_rule_integral):
        errors = quadrature_errors(rule, math.exp, math.e - 1, 0, 1, pieces)
        for coarse, fine in zip(errors, errors[1:], strict=False):
            assert coarse / fine == pytest.approx(4, rel=0.01)
    # 同じ分割数なら、中点法の誤差は台形法の誤差のおよそ半分
    midpoint = quadrature_errors(
        midpoint_rule_integral, math.exp, math.e - 1, 0, 1, [10]
    )
    trapezoid = quadrature_errors(
        trapezoid_rule_integral, math.exp, math.e - 1, 0, 1, [10]
    )
    assert midpoint[0] / trapezoid[0] == pytest.approx(0.5, rel=0.01)


def test_多項式の不定積分は冪の公式の逆で微分すると元に戻る() -> None:
    # 1 − 2x + 3x³ の不定積分は x − x² + (3/4)x⁴（定数は 0）
    antiderivative = polynomial_antiderivative(CUBIC)
    assert antiderivative.coefficients == pytest.approx((0, 1, -1, 0, 0.75))
    assert antiderivative.derivative() == CUBIC
    assert polynomial_antiderivative(Polynomial((5,))).coefficients == (0, 5)


def test_定積分は不定積分の差で数値積分と一致する() -> None:
    # F(2) − F(−1) = (2 − 4 + 12) − (−1 − 1 + 0.75) = 11.25
    assert polynomial_definite_integral(CUBIC, -1, 2) == pytest.approx(11.25)
    for low, high in [(-1, 2), (0, 0.5), (1.5, 3)]:
        exact = polynomial_definite_integral(CUBIC, low, high)
        assert midpoint_rule_integral(CUBIC, low, high, 2000) == pytest.approx(exact)
        assert trapezoid_rule_integral(CUBIC, low, high, 2000) == pytest.approx(exact)


def test_積分してから微分すると元の関数に戻る() -> None:
    # 微積分学の基本定理: F(x) = ∫₀ˣ f(t) dt なら F'(x) = f(x)
    for func in (math.cos, math.exp, lambda t: 1 / (1 + t)):
        area = functools.partial(midpoint_rule_integral, func, 0, pieces=2000)
        for x in (0.3, 1.0, 2.5):
            slope = numerical_derivative(area, x, step=1e-3)
            assert slope == pytest.approx(func(x), rel=1e-5)


def test_上端と下端を入れ替えると符号が変わり同じ点なら0() -> None:
    for rule in (midpoint_rule_integral, trapezoid_rule_integral):
        assert rule(math.exp, 1, 0, 100) == pytest.approx(-rule(math.exp, 0, 1, 100))
        assert rule(math.exp, 0.7, 0.7, 10) == 0
    assert polynomial_definite_integral(CUBIC, 2, -1) == pytest.approx(-11.25)


def test_分割数は1以上() -> None:
    for rule in (midpoint_rule_integral, trapezoid_rule_integral):
        for pieces in (0, -3):
            with pytest.raises(ValueError):
                rule(math.exp, 0, 1, pieces)
    with pytest.raises(ValueError):
        quadrature_errors(midpoint_rule_integral, math.exp, 1, 0, 1, [])
