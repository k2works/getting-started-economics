"""産業連関表: 投入係数、レオンチェフ逆行列、縦計と横計。"""

import numpy as np
from numpy.typing import ArrayLike, NDArray

# (I − A) の条件数が、これを超えるなら、特異（逆行列がない）と見なす。
# 行列式は、部門の数が多いと、健全な経済でも小さくなる（0.5 の 50 乗は 9e-16）ので、
# 絶対値では、判定しない。
# 生産が成り立つ（付加価値が、すべて正の）経済では、行列式は、正になる
_MAX_CONDITION = 1e12


def _square(matrix: ArrayLike) -> NDArray[np.float64]:
    """正方行列として読む。違えばエラー。"""
    array = np.asarray(matrix, dtype=float)
    if array.ndim != 2 or array.shape[0] != array.shape[1]:
        raise ValueError("正方行列（部門 × 部門）にする")
    return array


def _vector(values: ArrayLike, size: int) -> NDArray[np.float64]:
    """部門の数 size の、ベクトルとして読む。違えばエラー。"""
    array = np.asarray(values, dtype=float)
    if array.shape != (size,):
        raise ValueError(f"長さは、部門の数（{size}）にする")
    return array


def _leontief_matrix(coefficients: ArrayLike) -> NDArray[np.float64]:
    """I − A を返す。A が不正、または I − A が特異なら、エラー。"""
    a = _square(coefficients)
    if (a < 0).any():
        raise ValueError("投入係数は、負にならない")
    m = np.eye(len(a)) - a
    if np.linalg.det(m) <= 0 or np.linalg.cond(m) > _MAX_CONDITION:
        raise ValueError(
            "単位行列から投入係数を引いた行列が特異（行列式が 0 以下）で、解けない"
        )
    return m


def input_coefficients(
    transactions: ArrayLike, output: ArrayLike
) -> NDArray[np.float64]:
    """投入係数 a_ij = 部門 j が部門 i から買った額 ÷ 部門 j の産出。"""
    z = _square(transactions)
    x = _vector(output, len(z))
    if (x == 0).any():
        raise ValueError("産出が 0 の部門があり、投入係数を計算できない")
    return z / x


def leontief_inverse(coefficients: ArrayLike) -> NDArray[np.float64]:
    """レオンチェフ逆行列 (I − A)⁻¹。"""
    return np.linalg.inv(_leontief_matrix(coefficients))


def output_for_demand(
    coefficients: ArrayLike, final_demand: ArrayLike
) -> NDArray[np.float64]:
    """最終需要 f を満たす生産量 x。(I − A) x = f を解く。"""
    m = _leontief_matrix(coefficients)
    f = _vector(final_demand, len(m))
    return np.linalg.solve(m, f)


def io_totals(
    transactions: ArrayLike, final_demand: ArrayLike, value_added: ArrayLike
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """（横計, 縦計）。横計 = 販売先の合計、縦計 = 投入の合計。"""
    z = _square(transactions)
    f = _vector(final_demand, len(z))
    v = _vector(value_added, len(z))
    return z.sum(axis=1) + f, z.sum(axis=0) + v


def is_io_balanced(
    transactions: ArrayLike, final_demand: ArrayLike, value_added: ArrayLike
) -> bool:
    """部門ごとに、縦計と横計が一致するか。"""
    rows, columns = io_totals(transactions, final_demand, value_added)
    return bool(np.allclose(rows, columns))
