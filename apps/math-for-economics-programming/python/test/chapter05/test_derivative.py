import math

import pytest

from lib.chapter02.quadratic import parabola_vertex
from lib.chapter05.derivative import (
    Polynomial,
    classify_stationary_point,
    difference_quotient_errors,
    is_concave_on,
    numerical_derivative,
    stationary_points,
)


def test_多項式は係数の低い次数から並べて値を計算する() -> None:
    cost = Polynomial((100, 10, 1))  # C(q) = 100 + 10q + q²
    assert cost(0) == 100
    assert cost(20) == 700
    assert cost(0.5) == pytest.approx(105.25)
    assert Polynomial((0, -3, 0, 1))(2) == 2  # x³ − 3x


def test_導関数は冪の公式で係数をずらす() -> None:
    # (x^n)' = n·x^(n−1)。100 + 10q + q² の導関数は 10 + 2q
    assert Polynomial((100, 10, 1)).derivative() == Polynomial((10, 2))
    assert Polynomial((0, -3, 0, 1)).derivative() == Polynomial((-3, 0, 3))
    assert Polynomial((7,)).derivative() == Polynomial((0,))


def test_数値微分は中心差分で傾きを近似する() -> None:
    # x² の x = 3 での傾きは 6。中心差分は 2 次関数なら（丸めを除き）正確
    assert numerical_derivative(lambda x: x**2, 3) == pytest.approx(6)
    # eˣ・ln x の微分（eˣ と 1 ÷ x）は、第 6 章で説明する
    assert numerical_derivative(math.exp, 0) == pytest.approx(1)
    assert numerical_derivative(math.log, 0.5) == pytest.approx(2)


@pytest.mark.parametrize(
    "coefficients", [(100, 10, 1), (50, 4, 0.5), (0, -3, 0, 1), (20, 15, -6, 1)]
)
def test_公式の導関数と数値微分が一致する(coefficients: tuple[float, ...]) -> None:
    poly = Polynomial(coefficients)
    slope = poly.derivative()
    for x in [-2, 0, 0.3, 1, 7.5]:
        assert numerical_derivative(poly, x) == pytest.approx(slope(x), abs=1e-6)


def test_和と定数倍の導関数は導関数の和と定数倍() -> None:
    revenue = Polynomial((0, 50))  # 50q
    cost = Polynomial((100, 10, 1))
    profit = revenue + cost.scale(-1)
    assert profit == Polynomial((-100, 40, -1))
    assert profit.derivative() == revenue.derivative() + cost.derivative().scale(-1)
    assert cost.scale(0.5) == Polynomial((50, 5, 0.5))


def test_刻み幅が大きいと打ち切りの誤差が出る() -> None:
    # x³ の x = 1 での中心差分は 3 + h²。誤差は h² で、h を 1/10 にすると 1/100
    cube = Polynomial((0, 0, 0, 1))
    errors = difference_quotient_errors(cube, 3, 1, [1, 0.1, 0.01])
    assert errors == pytest.approx([1, 0.01, 0.0001], rel=1e-6)


def test_刻み幅が小さすぎると丸めの誤差で悪くなる() -> None:
    cube = Polynomial((0, 0, 0, 1))
    good, tiny = difference_quotient_errors(cube, 3, 1, [1e-5, 1e-13])
    assert good < 1e-9
    assert tiny > 1e-5
    assert tiny > 1000 * good


def test_刻み幅が正でなければ数値微分しない() -> None:
    for step in [0, -0.1]:
        with pytest.raises(ValueError):
            numerical_derivative(math.exp, 1, step)


def test_導関数の符号で増減がわかる() -> None:
    # x³ − 3x の導関数 3x² − 3 は、−1 < x < 1 で負（減少）、その外で正（増加）
    slope = Polynomial((0, -3, 0, 1)).derivative()
    assert all(slope(x) > 0 for x in [-2, -1.01, 1.01, 2])
    assert all(slope(x) < 0 for x in [-0.99, -0.5, 0, 0.5, 0.99])
    assert slope(-1) == slope(1) == 0


def test_x3乗引く3xの極値はプラスマイナス1() -> None:
    cubic = Polynomial((0, -3, 0, 1))
    assert stationary_points(cubic) == (-1, 1)
    assert classify_stationary_point(cubic, -1) == "maximum"
    assert classify_stationary_point(cubic, 1) == "minimum"
    # 符号を反対にすると、極大と極小が入れ替わる
    assert classify_stationary_point(cubic.scale(-1), -1) == "minimum"
    # 導関数 3x² − 12x + 9 の係数が対称でない例（係数の順の取り違えを見つける）
    assert stationary_points(Polynomial((0, 9, -6, 1))) == (1, 3)


def test_2次関数の極値は第2章の頂点と一致する() -> None:
    profit = Polynomial((0, 80, -1))  # 第 2 章の独占の利潤 −Q² + 80Q
    assert stationary_points(profit) == (40,)
    assert stationary_points(profit) == (parabola_vertex(-1, 80, 0)[0],)
    assert classify_stationary_point(profit, 40) == "maximum"
    assert stationary_points(Polynomial((100, 10, 2))) == (-2.5,)


def test_2階の導関数が0なら極大か極小かは判定できない() -> None:
    cube = Polynomial((0, 0, 0, 1))  # x³ は x = 0 で傾き 0 だが、極値ではない
    assert stationary_points(cube) == (0,)
    assert classify_stationary_point(cube, 0) == "undetermined"
    # 2 階の導関数が小さくても、正なら極小（0.25x² の f'' は 0.5）
    assert classify_stationary_point(Polynomial((0, 0, 0.25)), 0) == "minimum"


def test_末尾の0の係数は取り除き空の係数は0の多項式() -> None:
    assert Polynomial((1, 2, 0, 0)) == Polynomial((1, 2))
    assert Polynomial((3, 0)) == Polynomial((3,))
    assert Polynomial(()) == Polynomial((0,))
    assert Polynomial(())(5) == 0
    # 最高次の項が打ち消し合うと、次数が下がる
    assert Polynomial((1, 2, 3)) + Polynomial((0, 0, -3)) == Polynomial((1, 2))
    assert Polynomial((1,)) + Polynomial((0, 0, 4)) == Polynomial((1, 0, 4))
    assert Polynomial((0, 0, 4)) + Polynomial((1,)) == Polynomial((1, 0, 4))


def test_1次関数には極値がなく定数関数と4次以上は扱わない() -> None:
    assert stationary_points(Polynomial((5, -2))) == ()
    assert classify_stationary_point(Polynomial((5, -2)), 3) == "undetermined"
    with pytest.raises(ValueError):
        stationary_points(Polynomial((7,)))
    with pytest.raises(ValueError):
        stationary_points(Polynomial((0, 0, 1, 0, 1)))  # x⁴ + x²


def test_2階の導関数が0以下の区間で関数は凹() -> None:
    profit = Polynomial((-100, 40, -1))  # 価格 50 の利潤 −q² + 40q − 100
    assert is_concave_on(profit, 0, 100)
    cost = Polynomial((100, 10, 1))
    assert not is_concave_on(cost, 0, 100)
    assert is_concave_on(cost.scale(-1), 0, 100)  # −C が凹 ⇔ C は凸
    cubic = Polynomial((0, -3, 0, 1))  # 2 階の導関数 6x
    assert is_concave_on(cubic, -2, 0)
    assert not is_concave_on(cubic, -1, 1)
    assert not is_concave_on(cubic, 0.001, 2)
    assert not is_concave_on(Polynomial((0, 0, 0.25)), -1, 1)  # f'' = 0.5


def test_凹の判定は区間と点の数が正しくなければ行わない() -> None:
    line = Polynomial((1, 2))
    assert is_concave_on(line, 0, 1, points=2)  # 1 次関数は凹でもあり凸でもある
    # 2 点だけなら、両端だけを調べる（右端の 0.01 で f'' = 0.06 > 0）
    assert not is_concave_on(Polynomial((0, -3, 0, 1)), -1, 0.01, points=2)
    for low, high, points in [(1, 1, 11), (2, 1, 11), (0, 1, 1)]:
        with pytest.raises(ValueError):
            is_concave_on(line, low, high, points)


def test_積と商と合成関数の公式は数値微分と一致する() -> None:
    for x in [-1.5, 0.3, 2]:
        # 積: (f·g)' = f'·g + f·g'。(x²·(x + 1))' = 2x·(x + 1) + x²
        product = numerical_derivative(lambda t: t**2 * (t + 1), x)
        assert product == pytest.approx(2 * x * (x + 1) + x**2)
        # 商: (f ÷ g)' = (f'·g − f·g') ÷ g²。(1 ÷ x)' = −1 ÷ x²
        quotient = numerical_derivative(lambda t: 1 / t, x)
        assert quotient == pytest.approx(-1 / x**2)
        # 合成: (f(g(x)))' = f'(g(x))·g'(x)。((x² + 1)³)' = 3(x² + 1)²·2x
        chain = numerical_derivative(lambda t: (t**2 + 1) ** 3, x)
        assert chain == pytest.approx(3 * (x**2 + 1) ** 2 * 2 * x)
