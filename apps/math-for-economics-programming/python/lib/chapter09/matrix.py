"""行列を、リストのリスト（標準ライブラリ）で計算する。"""

import math
from collections.abc import Sequence

from lib.chapter07.vectors import vector_dot, vector_length

Matrix = Sequence[Sequence[float]]


def matrix_shape(a: Matrix) -> tuple[int, int]:
    """行列の形（行の数, 列の数）。空の行列や、長さのそろわない行は、行列でない。"""
    if not a or not a[0]:
        raise ValueError("行列は、1 行 1 列以上でなければなりません")
    columns = len(a[0])
    if any(len(row) != columns for row in a):
        raise ValueError("行列の行は、すべて同じ長さでなければなりません")
    return len(a), columns


def matrix_transpose(a: Matrix) -> list[list[float]]:
    """転置（行と列を入れ替える）。"""
    _, columns = matrix_shape(a)
    return [[row[j] for row in a] for j in range(columns)]


def matrix_product(a: Matrix, b: Matrix) -> list[list[float]]:
    """行列の積 AB。(i, j) 成分は、A の第 i 行と B の第 j 列の内積。"""
    if matrix_shape(a)[1] != matrix_shape(b)[0]:
        raise ValueError("A の列の数と、B の行の数が、等しくなければなりません")
    b_columns = matrix_transpose(b)
    return [[vector_dot(row, column) for column in b_columns] for row in a]


def identity_matrix(size: int) -> list[list[float]]:
    """n 行 n 列の単位行列（対角が 1、ほかが 0）。"""
    return [[1 if i == j else 0 for j in range(size)] for i in range(size)]


def _square_size(a: Matrix) -> int:
    """正方行列の大きさ。正方でなければ、エラー。"""
    rows, columns = matrix_shape(a)
    if rows != columns:
        raise ValueError("正方行列（行と列の数が等しい）でなければなりません")
    return rows


def matrix_trace(a: Matrix) -> float:
    """トレース（対角成分の和）。"""
    return sum(a[i][i] for i in range(_square_size(a)))


def _minor(a: Matrix, row: int, column: int) -> list[list[float]]:
    """第 row 行と第 column 列を取り除いた行列。"""
    return [
        [x for j, x in enumerate(r) if j != column] for i, r in enumerate(a) if i != row
    ]


def _cofactor(a: Matrix, row: int, column: int) -> float:
    """余因子 (−1)^(row + column) × (第 row 行と第 column 列を除いた行列式)。"""
    sign = 1 if (row + column) % 2 == 0 else -1
    return sign * matrix_determinant(_minor(a, row, column))


def matrix_determinant(a: Matrix) -> float:
    """行列式。1 行目で余因子展開する（2 行 2 列なら ad − bc）。"""
    size = _square_size(a)
    if size == 1:
        return a[0][0]
    return sum(a[0][j] * _cofactor(a, 0, j) for j in range(size))


_SINGULAR_TOLERANCE = 1e-12


def _is_negligible_determinant(a: Matrix, det: float, tolerance: float) -> bool:
    """|det A| と行の長さの積（アダマールの不等式の上限）の比が、tolerance 以下か。"""
    scale = math.prod(vector_length(row) for row in a)
    return abs(det) <= tolerance * scale


def is_singular_matrix(a: Matrix, tolerance: float = _SINGULAR_TOLERANCE) -> bool:
    """行列式が、行の長さの積に比べて 0 とみなせるほど小さいか（相対的な判定）。"""
    return _is_negligible_determinant(a, matrix_determinant(a), tolerance)


def matrix_inverse(a: Matrix) -> list[list[float]]:
    """逆行列 A⁻¹ = 余因子行列の転置 ÷ 行列式。特異なら、エラー。"""
    size = _square_size(a)
    det = matrix_determinant(a)
    if _is_negligible_determinant(a, det, _SINGULAR_TOLERANCE):
        raise ValueError("特異な行列（行列式が 0）には、逆行列がありません")
    if size == 1:
        return [[1 / det]]
    # (i, j) 成分は、(j, i) の余因子（余因子行列の転置）
    return [[_cofactor(a, j, i) / det for j in range(size)] for i in range(size)]
