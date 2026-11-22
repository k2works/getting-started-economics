import numpy as np
import pytest
from numpy.typing import NDArray

from lib.chapter09.matrix import (
    Matrix,
    identity_matrix,
    is_singular_matrix,
    matrix_determinant,
    matrix_inverse,
    matrix_product,
    matrix_shape,
    matrix_trace,
    matrix_transpose,
)


def _array(a: Matrix) -> NDArray[np.float64]:
    """pytest.approx は入れ子のリストを比べられないので、配列にして比べる。"""
    return np.array(a, dtype=np.float64)


def test_2行3列の行列の形() -> None:
    assert matrix_shape([[1, 2, 3], [4, 5, 6]]) == (2, 3)


def test_行列の積は行と列の内積を並べる() -> None:
    a = [[1, 2], [3, 4]]
    b = [[5, 6], [7, 8]]
    assert matrix_product(a, b) == [[19, 22], [43, 50]]


def test_2行3列と3行1列の積は2行1列() -> None:
    a = [[1, 2, 3], [4, 5, 6]]
    b: Matrix = [[2], [0.5], [-1]]
    assert _array(matrix_product(a, b)) == pytest.approx(_array([[0], [4.5]]))


def test_行列の積は順番を入れ替えると変わる() -> None:
    a = [[1, 2], [3, 4]]
    b = [[0, 1], [1, 0]]
    assert matrix_product(a, b) == [[2, 1], [4, 3]]
    assert matrix_product(b, a) == [[3, 4], [1, 2]]


def test_転置は行と列を入れ替える() -> None:
    assert matrix_transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]


def test_積の転置は転置の積を逆順にしたもの() -> None:
    a = [[1, 2, 3], [4, 5, 6]]
    b: Matrix = [[2, -1], [0.5, 3], [1, 0]]
    left = matrix_transpose(matrix_product(a, b))
    right = matrix_product(matrix_transpose(b), matrix_transpose(a))
    assert _array(left) == pytest.approx(_array(right))


def test_自作の積と転置はNumPyと一致する() -> None:
    a: Matrix = [[1.5, -2, 0.25], [3, 0, -1]]
    b: Matrix = [[2, 1], [-0.5, 4], [1, 0.1]]
    expected = np.array(a) @ np.array(b)
    assert _array(matrix_product(a, b)) == pytest.approx(expected)
    assert matrix_transpose(a) == np.array(a).T.tolist()


def test_2行2列の行列式はadからbcを引く() -> None:
    assert matrix_determinant([[2, 1], [1, 3]]) == 5
    assert matrix_determinant([[4, 7], [2, 6]]) == 10


def test_3行3列の行列式は1行目で余因子展開する() -> None:
    a = [[3, 1, 2], [0, 4, 1], [2, -1, 5]]
    # 3(20 + 1) − 1(0 − 2) + 2(0 − 8) = 63 + 2 − 16
    assert matrix_determinant(a) == 49


def test_単位行列は掛けても変わらない() -> None:
    a = [[3, 1, 2], [0, 4, 1], [2, -1, 5]]
    assert identity_matrix(3) == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    assert matrix_product(a, identity_matrix(3)) == a
    assert matrix_product(identity_matrix(3), a) == a


def test_2行2列の逆行列() -> None:
    inverse = matrix_inverse([[2, 1], [1, 3]])
    assert _array(inverse) == pytest.approx(_array([[0.6, -0.2], [-0.2, 0.4]]))


def test_逆行列を掛けると単位行列になる() -> None:
    for a in ([[4, 7], [2, 6]], [[3, 1, 2], [0, 4, 1], [2, -1, 5]]):
        n = len(a)
        inverse = matrix_inverse(a)
        assert _array(matrix_product(a, inverse)) == pytest.approx(
            _array(identity_matrix(n))
        )
        assert _array(matrix_product(inverse, a)) == pytest.approx(
            _array(identity_matrix(n))
        )


def test_行列式が0の行列は特異で逆行列がない() -> None:
    # 2 行目は 1 行目の 2 倍。3 行 3 列では、3 行目が 1 行目と 2 行目の和
    for singular in ([[1, 2], [2, 4]], [[2, 0, 1], [1, 3, 2], [3, 3, 3]]):
        assert matrix_determinant(singular) == 0
        assert is_singular_matrix(singular)
        with pytest.raises(ValueError):
            matrix_inverse(singular)


def test_自作の行列式と逆行列はNumPyと一致する() -> None:
    a = [[3, 1, 2], [0, 4, 1], [2, -1, 5]]
    assert matrix_determinant(a) == pytest.approx(np.linalg.det(np.array(a)))
    assert _array(matrix_inverse(a)) == pytest.approx(np.linalg.inv(np.array(a)))


def test_トレースは対角成分の和() -> None:
    assert matrix_trace([[3, 1, 2], [0, 4, 1], [2, -1, 5]]) == 12


def test_成分が小さくても行の長さに比べて行列式が大きければ特異でない() -> None:
    tiny = [[1e-8, 0], [0, 1e-8]]
    # 行列式 1e-16 は、絶対値で 0 と比べると「0 とみなせる」が、成分の大きさに比べれば大きい
    assert matrix_determinant(tiny) == pytest.approx(1e-16)
    assert not is_singular_matrix(tiny)
    assert _array(matrix_inverse(tiny)) == pytest.approx(_array([[1e8, 0], [0, 1e8]]))


def test_成分が大きくても行が比例していれば特異() -> None:
    assert is_singular_matrix([[1e12, 2e12], [2e12, 4e12]])


def test_ほぼ比例する行は丸め誤差の範囲で特異とみなす() -> None:
    nearly: Matrix = [[1, 2], [2, 4 + 1e-15]]
    assert matrix_determinant(nearly) != 0
    assert is_singular_matrix(nearly)
    assert not is_singular_matrix([[1, 2], [2, 4.001]])


def test_0の行がある行列は特異() -> None:
    assert is_singular_matrix([[0, 0], [1, 2]])


def test_1行1列の行列式と逆行列() -> None:
    assert matrix_determinant([[4]]) == 4
    assert matrix_inverse([[4]]) == [[0.25]]


def test_空の行列や長さのそろわない行は行列でない() -> None:
    bad_matrices: list[Matrix] = [[], [[]], [[1, 2], [3]]]
    for bad in bad_matrices:
        with pytest.raises(ValueError):
            matrix_shape(bad)


def test_列と行の数が合わない積は決まらない() -> None:
    with pytest.raises(ValueError):
        matrix_product([[1, 2, 3], [4, 5, 6]], [[1, 2], [3, 4]])


def test_正方でない行列には行列式もトレースも逆行列もない() -> None:
    a = [[1, 2, 3], [4, 5, 6]]
    for func in (matrix_determinant, matrix_trace, matrix_inverse, is_singular_matrix):
        with pytest.raises(ValueError):
            func(a)


def test_特異の閾値は行の長さの積の1兆分の1() -> None:
    # [[1, 1], [1, 1 + d]] の行列式は d、行の長さの積は約 2。比は約 d ÷ 2
    assert not is_singular_matrix([[1, 1], [1, 1 + 2.4e-12]])
    assert is_singular_matrix([[1, 1], [1, 1 + 1.6e-12]])
    assert not is_singular_matrix([[1, 1], [1, 1 + 1.6e-12]], tolerance=1e-13)
