import pytest

from lib.chapter08.partial import (
    classify_critical_point_2d,
    euler_degree_of_homogeneity,
    is_quasi_concave_on_points,
    numerical_hessian_2d,
    numerical_partial_x,
    numerical_partial_y,
    quadratic_2d_critical_point,
)


def _two_product_profit(x: float, y: float) -> float:
    """2 つの製品を作る企業の利潤 π = 50x + 40y − x² − xy − y²。"""
    return 50 * x + 40 * y - x**2 - x * y - y**2


def _surface(x: float, y: float) -> float:
    """f(x, y) = x²y + 3y²。f_x = 2xy、f_y = x² + 6y。"""
    return x**2 * y + 3 * y**2


def test_偏微分はほかの変数を固定して微分する() -> None:
    assert numerical_partial_x(_surface, 2, 5) == pytest.approx(20)
    assert numerical_partial_y(_surface, 2, 5) == pytest.approx(34)


def test_偏微分の数値は公式と負や0や1未満の点でも一致する() -> None:
    for x, y in [(-1.5, 2), (0, 0.4), (0.3, -2), (4, 0)]:
        assert numerical_partial_x(_surface, x, y) == pytest.approx(2 * x * y, abs=1e-6)
        assert numerical_partial_y(_surface, x, y) == pytest.approx(
            x**2 + 6 * y, abs=1e-6
        )


def test_2製品の利潤は偏微分が両方0になる点で最大() -> None:
    x, y = quadratic_2d_critical_point(-1, -1, -1, 50, 40)
    assert (x, y) == pytest.approx((20, 10))
    assert _two_product_profit(x, y) == pytest.approx(700)
    assert numerical_partial_x(_two_product_profit, x, y) == pytest.approx(0, abs=1e-6)
    assert numerical_partial_y(_two_product_profit, x, y) == pytest.approx(0, abs=1e-6)


def test_停留点は係数が対称でない2次関数でも連立方程式の解() -> None:
    # f = 2x² + xy + 3y² − 9x − 13y。f_x = 4x + y − 9、f_y = x + 6y − 13
    assert quadratic_2d_critical_point(2, 1, 3, -9, -13) == pytest.approx(
        (41 / 23, 43 / 23)
    )


def test_ヘッセ行列の数値は2階の偏微分の公式と一致する() -> None:
    assert numerical_hessian_2d(_two_product_profit, 20, 10) == pytest.approx(
        (-2, -1, -2), abs=1e-6
    )
    # f = x²y + 3y² の 2 階の偏微分: f_xx = 2y、f_xy = 2x、f_yy = 6
    assert numerical_hessian_2d(_surface, 1.5, -0.4) == pytest.approx(
        (-0.8, 3, 6), abs=1e-6
    )


def test_ヘッセ行列の行列式と左上の符号で極大と極小を分ける() -> None:
    assert classify_critical_point_2d(-2, -1, -2) == "maximum"
    assert classify_critical_point_2d(2, 1, 3) == "minimum"
    assert classify_critical_point_2d(2, 0, -2) == "saddle"


def test_2階の偏微分が1未満の小さい値でも符号で判定する() -> None:
    assert classify_critical_point_2d(0.5, 0.1, 0.5) == "minimum"
    assert classify_critical_point_2d(-0.5, -0.1, -0.5) == "maximum"


def test_対角が両方負でも行列式が負なら鞍点() -> None:
    assert classify_critical_point_2d(-1, 2, -1) == "saddle"


def test_ヘッセ行列の行列式が0なら判定できない() -> None:
    assert classify_critical_point_2d(1, 1, 1) == "undetermined"
    assert classify_critical_point_2d(2, -2, 2) == "undetermined"


def _negative_square_of_sum(x: float, y: float) -> float:
    """f = −(x + y)²。ヘッセ行列は (−2, −2, −2) で、行列式は 0。"""
    return -((x + y) ** 2)


def test_数値のヘッセ行列で行列式がほぼ0なら判定できない() -> None:
    # 差分の丸め誤差で、行列式は ちょうど 0 にならない（1e-15 ほど）
    hessian = numerical_hessian_2d(_negative_square_of_sum, 1, -1)
    assert classify_critical_point_2d(*hessian) == "undetermined"
    assert classify_critical_point_2d(-2, -2 + 1e-12, -2) == "undetermined"


def test_行列式が0の2次関数には停留点が1つに決まらない() -> None:
    with pytest.raises(ValueError):
        quadratic_2d_critical_point(1, 2, 1, -4, -4)


def _cobb_douglas_03(x: float, y: float) -> float:
    """U = x^0.3·y^0.7（1 次同次）。"""
    return float(x**0.3 * y**0.7)


def _product(x: float, y: float) -> float:
    """U = xy（2 次同次）。"""
    return x * y


def _sum_of_squares(x: float, y: float) -> float:
    return x**2 + y**2


def _quasilinear_root(x: float, y: float) -> float:
    """U = √x + y（同次でない）。"""
    return float(x**0.5 + y)


def test_オイラーの定理で1次同次なら偏微分と量の積の和が元の値() -> None:
    for x, y in [(25, 10), (0.5, 3), (7, 7)]:
        assert euler_degree_of_homogeneity(_cobb_douglas_03, x, y) == pytest.approx(1)


def test_xyは2次同次で同次でない関数は点によって値が変わる() -> None:
    assert euler_degree_of_homogeneity(_product, 3, 5) == pytest.approx(2)
    assert euler_degree_of_homogeneity(_quasilinear_root, 1, 1) == pytest.approx(0.75)
    assert euler_degree_of_homogeneity(_quasilinear_root, 4, 4) == pytest.approx(5 / 6)


def test_関数の値が0の点では同次の次数を求めない() -> None:
    with pytest.raises(ValueError):
        euler_degree_of_homogeneity(_product, 0, 5)


_SAMPLE_POINTS = [(1, 9), (4, 4), (9, 1), (2, 6), (0.5, 0.5), (6, 3)]


def test_コブダグラス型とxyは準凹で2乗の和は準凹でない() -> None:
    assert is_quasi_concave_on_points(_cobb_douglas_03, _SAMPLE_POINTS)
    assert is_quasi_concave_on_points(_product, _SAMPLE_POINTS)
    assert not is_quasi_concave_on_points(_sum_of_squares, _SAMPLE_POINTS)


def test_準凹の判定は2点の間の点が両端の小さいほう以上かを見る() -> None:
    # (2, 0) と (0, 2) の中点 (1, 1) では、x² + y² = 2 が、両端の 4 より小さい
    assert not is_quasi_concave_on_points(_sum_of_squares, [(2, 0), (0, 2)])
    assert is_quasi_concave_on_points(_sum_of_squares, [(2, 0), (3, 0)])


def _negative_sum(x: float, y: float) -> float:
    """f = −x − y（1 次関数。凹なので準凹）。"""
    return -x - y


def test_1次関数は線分の上で両端の間の値をとるので準凹() -> None:
    assert is_quasi_concave_on_points(_negative_sum, [(1, 0), (0, 1), (2, 0)])


def test_分割が2つだと両端しか調べないので準凹でない関数を見逃す() -> None:
    assert is_quasi_concave_on_points(_sum_of_squares, [(2, 0), (0, 2)], steps=2)
    assert not is_quasi_concave_on_points(_sum_of_squares, [(2, 0), (0, 2)], steps=3)


def test_準凹の判定には2点以上と2つ以上の分割が必要() -> None:
    with pytest.raises(ValueError):
        is_quasi_concave_on_points(_product, [(1, 1)])
    with pytest.raises(ValueError):
        is_quasi_concave_on_points(_product, _SAMPLE_POINTS, steps=1)
