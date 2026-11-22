"""最小 2 乗法: 単回帰の公式と、行列の正規方程式 β = (XᵀX)⁻¹Xᵀy。"""

from collections.abc import Sequence

import numpy as np

from lib.chapter07.vectors import mean_by_dot, vector_dot
from lib.chapter09.matrix import (
    Matrix,
    matrix_inverse,
    matrix_product,
    matrix_transpose,
)


def _matrix_times_vector(a: Matrix, v: Sequence[float]) -> list[float]:
    """行列とベクトルの積 Av（各行と v の内積）。"""
    return [vector_dot(row, v) for row in a]


def simple_regression_coefficients(
    xs: Sequence[float], ys: Sequence[float]
) -> tuple[float, float]:
    """単回帰 y = β₀ + β₁x の係数。β₁ = x と y の共分散 ÷ x の分散、β₀ = ȳ − β₁x̄。"""
    if len(xs) < 2:
        raise ValueError("回帰には、2 点以上のデータが要ります")
    # 平均の丸め誤差で、偏差の 2 乗和は 0 にならないことがあるので、値そのものを比べる
    if max(xs) == min(xs):
        raise ValueError("x がすべて同じ値では、傾きが決まりません")
    x_bar, y_bar = mean_by_dot(xs), mean_by_dot(ys)
    dx = [x - x_bar for x in xs]
    dy = [y - y_bar for y in ys]
    slope = vector_dot(dx, dy) / vector_dot(dx, dx)
    return y_bar - slope * x_bar, slope


def regression_design_matrix(
    regressors: Sequence[Sequence[float]],
) -> list[list[float]]:
    """計画行列 X。各行は (1, x₁, x₂, …)。regressors は、説明変数ごとの列のリスト。"""
    return [[1, *row] for row in zip(*regressors, strict=True)]


def least_squares_beta(design: Matrix, ys: Sequence[float]) -> list[float]:
    """正規方程式 XᵀXβ = Xᵀy の解 β = (XᵀX)⁻¹Xᵀy。"""
    xt = matrix_transpose(design)
    return _matrix_times_vector(
        matrix_inverse(matrix_product(xt, design)), _matrix_times_vector(xt, ys)
    )


def regression_fitted_values(design: Matrix, beta: Sequence[float]) -> list[float]:
    """当てはめた値 ŷ = Xβ。"""
    return _matrix_times_vector(design, beta)


def regression_residuals(
    design: Matrix, ys: Sequence[float], beta: Sequence[float]
) -> list[float]:
    """残差 e = y − Xβ。"""
    fitted = regression_fitted_values(design, beta)
    return [y - f for y, f in zip(ys, fitted, strict=True)]


def coefficient_of_determination(
    ys: Sequence[float], residuals: Sequence[float]
) -> float:
    """決定係数 R² = 1 − e·e ÷ (y − ȳ)·(y − ȳ)。"""
    if max(ys) == min(ys):
        raise ValueError("y がすべて同じ値では、決定係数が決まりません")
    y_bar = mean_by_dot(ys)
    deviations = [y - y_bar for y in ys]
    return 1 - vector_dot(residuals, residuals) / vector_dot(deviations, deviations)


def regression_projection_matrix(design: Matrix) -> list[list[float]]:
    """射影行列 P = X(XᵀX)⁻¹Xᵀ。y に掛けると、当てはめた値 ŷ = Py になる。"""
    xt = matrix_transpose(design)
    return matrix_product(
        matrix_product(design, matrix_inverse(matrix_product(xt, design))), xt
    )


def noisy_regression_sample(
    design: Matrix, beta: Sequence[float], noise_sd: float, seed: int
) -> list[float]:
    """y = Xβ + 誤差（平均 0・標準偏差 noise_sd の正規分布。種 seed で固定）。"""
    if noise_sd < 0:
        raise ValueError("誤差の標準偏差は、0 以上でなければなりません")
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, noise_sd, size=len(design))
    fitted = regression_fitted_values(design, beta)
    return [float(f + e) for f, e in zip(fitted, noise, strict=True)]
