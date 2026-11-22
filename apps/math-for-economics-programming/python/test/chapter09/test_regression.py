import numpy as np
import pytest

from lib.chapter07.vectors import vector_dot
from lib.chapter09.matrix import (
    matrix_product,
    matrix_trace,
    matrix_transpose,
)
from lib.chapter09.regression import (
    coefficient_of_determination,
    least_squares_beta,
    noisy_regression_sample,
    regression_design_matrix,
    regression_fitted_values,
    regression_projection_matrix,
    regression_residuals,
    simple_regression_coefficients,
)

PRICES = [2, 4, 6, 8, 10]
QUANTITIES = [18, 15, 13, 8, 6]


def test_単回帰の傾きは共分散を分散で割る() -> None:
    # 偏差の積の和 −62 ÷ 偏差の2乗の和 40 = −1.55、切片 12 + 1.55 × 6 = 21.3
    intercept, slope = simple_regression_coefficients(PRICES, QUANTITIES)
    assert slope == pytest.approx(-1.55)
    assert intercept == pytest.approx(21.3)


def test_計画行列は1の列と説明変数の列を並べる() -> None:
    assert regression_design_matrix([[2, 4, 6]]) == [[1, 2], [1, 4], [1, 6]]
    assert regression_design_matrix([[2, 4], [20, 10]]) == [[1, 2, 20], [1, 4, 10]]


def test_正規方程式の係数は単回帰の公式と一致する() -> None:
    design = regression_design_matrix([PRICES])
    beta = least_squares_beta(design, QUANTITIES)
    assert beta == pytest.approx(simple_regression_coefficients(PRICES, QUANTITIES))
    assert beta == pytest.approx([21.3, -1.55])


def test_直線にちょうど乗る4点では係数がその直線になる() -> None:
    design = regression_design_matrix([[1, 2, 3, 4]])
    ys = [3, 5, 7, 9]
    beta = least_squares_beta(design, ys)
    assert beta == pytest.approx([1, 2])
    residuals = regression_residuals(design, ys, beta)
    assert residuals == pytest.approx([0, 0, 0, 0], abs=1e-9)
    assert coefficient_of_determination(ys, residuals) == pytest.approx(1)


def test_当てはめた値と残差() -> None:
    design = regression_design_matrix([PRICES])
    beta = [21.3, -1.55]
    fitted = regression_fitted_values(design, beta)
    assert fitted == pytest.approx([18.2, 15.1, 12, 8.9, 5.8])
    residuals = regression_residuals(design, QUANTITIES, beta)
    assert residuals == pytest.approx([-0.2, -0.1, 1, -0.9, 0.2])


def test_決定係数は1から残差の2乗和と全変動の比を引く() -> None:
    design = regression_design_matrix([PRICES])
    beta = least_squares_beta(design, QUANTITIES)
    residuals = regression_residuals(design, QUANTITIES, beta)
    # 残差の2乗和 1.9、平均 12 からの偏差の2乗和 98
    assert coefficient_of_determination(QUANTITIES, residuals) == pytest.approx(
        1 - 1.9 / 98
    )


def test_残差は説明変数の列と直交する() -> None:
    design = regression_design_matrix([PRICES])
    beta = least_squares_beta(design, QUANTITIES)
    residuals = regression_residuals(design, QUANTITIES, beta)
    for column in matrix_transpose(design):
        assert vector_dot(column, residuals) == pytest.approx(0, abs=1e-9)


def test_説明変数が2つの重回帰はちょうど乗るデータの係数を当てる() -> None:
    incomes = [20, 10, 40, 30, 50]
    quantities = [30 - 2 * p + 0.5 * m for p, m in zip(PRICES, incomes, strict=True)]
    design = regression_design_matrix([PRICES, incomes])
    assert least_squares_beta(design, quantities) == pytest.approx([30, -2, 0.5])


def test_ノイズ入りの重回帰はNumPyの最小2乗法と一致する() -> None:
    incomes = [20, 10, 40, 30, 50, 25, 35, 15]
    prices = [2, 4, 6, 8, 10, 3, 7, 9]
    design = regression_design_matrix([prices, incomes])
    ys = noisy_regression_sample(design, [30, -2, 0.5], 0.5, seed=9)
    beta = least_squares_beta(design, ys)
    x = np.array(design, dtype=np.float64)
    expected, *_ = np.linalg.lstsq(x, np.array(ys), rcond=None)
    assert beta == pytest.approx(expected.tolist())
    assert beta == pytest.approx(np.linalg.solve(x.T @ x, x.T @ np.array(ys)).tolist())
    residuals = regression_residuals(design, ys, beta)
    for column in matrix_transpose(design):
        assert vector_dot(column, residuals) == pytest.approx(0, abs=1e-9)


def test_射影行列を掛けると当てはめた値になる() -> None:
    design = regression_design_matrix([PRICES])
    projection = regression_projection_matrix(design)
    fitted = [vector_dot(row, QUANTITIES) for row in projection]
    assert fitted == pytest.approx([18.2, 15.1, 12, 8.9, 5.8])


def test_射影行列は2回掛けても同じで対称でトレースは係数の数() -> None:
    incomes = [20, 10, 40, 30, 50]
    for design in (
        regression_design_matrix([PRICES]),
        regression_design_matrix([PRICES, incomes]),
    ):
        projection = np.array(regression_projection_matrix(design))
        twice = np.array(matrix_product(projection.tolist(), projection.tolist()))
        assert twice == pytest.approx(projection)
        assert projection.T == pytest.approx(projection)
        assert matrix_trace(projection.tolist()) == pytest.approx(len(design[0]))


def test_当てはめた値と残差は直交する() -> None:
    design = regression_design_matrix([PRICES])
    beta = least_squares_beta(design, QUANTITIES)
    fitted = regression_fitted_values(design, beta)
    residuals = regression_residuals(design, QUANTITIES, beta)
    assert vector_dot(fitted, residuals) == pytest.approx(0, abs=1e-9)


def test_2点だけなら回帰直線は2点を通る() -> None:
    assert simple_regression_coefficients([1, 3], [5, 1]) == pytest.approx((7, -2))
    design = regression_design_matrix([[1, 3]])
    assert least_squares_beta(design, [5, 1]) == pytest.approx([7, -2])


def test_負や1未満のxでも公式と正規方程式は一致する() -> None:
    xs = [-1.5, -0.25, 0.1, 0.6, 2]
    design = regression_design_matrix([xs])
    ys = noisy_regression_sample(design, [-3, 0.4], 0.3, seed=2)
    expected = simple_regression_coefficients(xs, ys)
    assert least_squares_beta(design, ys) == pytest.approx(list(expected))


def test_xと関係のないデータでは傾きも決定係数も0() -> None:
    xs, ys = [1, 2, 3, 4], [1, 3, 3, 1]
    intercept, slope = simple_regression_coefficients(xs, ys)
    assert (intercept, slope) == pytest.approx((2, 0))
    design = regression_design_matrix([xs])
    residuals = regression_residuals(design, ys, [intercept, slope])
    assert coefficient_of_determination(ys, residuals) == pytest.approx(0)


def test_誤差の標準偏差が0ならデータは式にちょうど乗る() -> None:
    design = regression_design_matrix([[1, 2, 3]])
    assert noisy_regression_sample(design, [4, -0.5], 0, seed=1) == [3.5, 3, 2.5]


def test_同じ種なら同じデータで種が違えば違うデータ() -> None:
    design = regression_design_matrix([PRICES])
    first = noisy_regression_sample(design, [21.3, -1.55], 1, seed=5)
    assert noisy_regression_sample(design, [21.3, -1.55], 1, seed=5) == first
    assert noisy_regression_sample(design, [21.3, -1.55], 1, seed=6) != first
    assert all(isinstance(y, float) for y in first)


def test_負の標準偏差の誤差は作れない() -> None:
    with pytest.raises(ValueError):
        noisy_regression_sample(regression_design_matrix([PRICES]), [1, 2], -1, seed=0)


def test_1点だけやxがすべて同じでは単回帰の係数は決まらない() -> None:
    with pytest.raises(ValueError):
        simple_regression_coefficients([3], [5])
    with pytest.raises(ValueError):
        simple_regression_coefficients([2, 2, 2], [1, 2, 3])
    with pytest.raises(ValueError):
        least_squares_beta(regression_design_matrix([[2, 2, 2]]), [1, 2, 3])


def test_説明変数が比例していると重回帰の係数は決まらない() -> None:
    incomes = [3 * p for p in PRICES]
    design = regression_design_matrix([PRICES, incomes])
    with pytest.raises(ValueError):
        least_squares_beta(design, QUANTITIES)


def test_係数の数よりデータが少ないと係数は決まらない() -> None:
    design = regression_design_matrix([[2, 4], [20, 10]])
    with pytest.raises(ValueError):
        least_squares_beta(design, [30, 27])


def test_長さの違うデータでは回帰は決まらない() -> None:
    with pytest.raises(ValueError):
        simple_regression_coefficients([1, 2, 3], [1, 2])
    with pytest.raises(ValueError):
        regression_design_matrix([[1, 2, 3], [4, 5]])
    with pytest.raises(ValueError):
        least_squares_beta(regression_design_matrix([PRICES]), [1, 2, 3])


def test_yがすべて同じでは決定係数は決まらない() -> None:
    with pytest.raises(ValueError):
        coefficient_of_determination([4, 4, 4], [0, 0, 0])


def test_誤差は同じ種の正規乱数を式の値に足したもの() -> None:
    design = regression_design_matrix([PRICES])
    ys = noisy_regression_sample(design, [21.3, -1.55], 2, seed=5)
    fitted = regression_fitted_values(design, [21.3, -1.55])
    noise = np.random.default_rng(5).normal(0, 2, size=5)
    errors = [y - f for y, f in zip(ys, fitted, strict=True)]
    assert errors == pytest.approx(noise.tolist())


def test_丸め誤差で平均がずれてもxやyがすべて同じなら決まらない() -> None:
    # 0.1 × 3 ÷ 3 は 0.10000000000000002 で、偏差の 2 乗和が 0 にならない
    with pytest.raises(ValueError):
        simple_regression_coefficients([0.1] * 3, [1, 2, 3])
    with pytest.raises(ValueError):
        coefficient_of_determination([0.1] * 3, [0, 0, 0])
