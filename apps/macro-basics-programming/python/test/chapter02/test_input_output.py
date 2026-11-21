"""第 2 章: 産業連関表のテスト。"""

import numpy as np
import pytest

from lib.chapter02.input_output import (
    input_coefficients,
    io_totals,
    is_io_balanced,
    leontief_inverse,
    output_for_demand,
)

# 投入係数と最終需要。生産量は、手計算で [250, 1000 / 3]（(I − A) の行列式は 0.6）
A = [[0.2, 0.3], [0.4, 0.1]]
FINAL_DEMAND = [100, 200]

# 2 部門（製造・サービス）の産業連関表（億円）。行は販売元、列は購入先の部門
TRANSACTIONS = [[60, 120], [90, 80]]
TABLE_FINAL_DEMAND = [120, 230]
TABLE_VALUE_ADDED = [150, 200]
TABLE_OUTPUT = [300, 400]


def test_投入係数は中間取引を産出で割った値() -> None:
    coefficients = input_coefficients(TRANSACTIONS, TABLE_OUTPUT)
    assert np.allclose(coefficients, [[0.2, 0.3], [0.3, 0.2]])


def test_産出が0の部門があればエラー() -> None:
    with pytest.raises(ValueError, match="産出が 0"):
        input_coefficients(TRANSACTIONS, [300, 0])


def test_最終需要から生産量を求める() -> None:
    output = output_for_demand(A, FINAL_DEMAND)
    assert output == pytest.approx([250, 1000 / 3])


def test_求めた生産量は需給の式を満たす() -> None:
    output = output_for_demand(A, FINAL_DEMAND)
    assert output - np.array(A) @ output == pytest.approx(FINAL_DEMAND)


def test_表の投入係数と最終需要から表の生産量が戻る() -> None:
    coefficients = input_coefficients(TRANSACTIONS, TABLE_OUTPUT)
    output = output_for_demand(coefficients, TABLE_FINAL_DEMAND)
    assert output == pytest.approx(TABLE_OUTPUT)


def test_最終需要が2倍なら生産量も2倍で0なら0() -> None:
    once = output_for_demand(A, FINAL_DEMAND)
    twice = output_for_demand(A, [200, 400])
    assert twice == pytest.approx(2 * once)
    assert output_for_demand(A, [0, 0]) == pytest.approx([0, 0])


def test_レオンチェフ逆行列の値() -> None:
    inverse = leontief_inverse(A)
    assert np.allclose(inverse, [[1.5, 0.5], [2 / 3, 4 / 3]])


def test_レオンチェフ逆行列は単位行列から投入係数を引いた行列の逆行列() -> None:
    inverse = leontief_inverse(A)
    assert (np.eye(2) - np.array(A)) @ inverse == pytest.approx(np.eye(2))


def test_レオンチェフ逆行列を最終需要にかけると生産量() -> None:
    inverse = leontief_inverse(A)
    assert inverse @ FINAL_DEMAND == pytest.approx(output_for_demand(A, FINAL_DEMAND))


@pytest.mark.parametrize(
    "coefficients", [[[0.2, 0.3, 0.1], [0.4, 0.1, 0.1]], [0.2, 0.3]]
)
def test_投入係数が正方行列でなければエラー(coefficients: list[object]) -> None:
    with pytest.raises(ValueError, match="正方行列"):
        leontief_inverse(coefficients)  # type: ignore[arg-type]


def test_最終需要の長さが部門の数と違えばエラー() -> None:
    with pytest.raises(ValueError, match="部門の数"):
        output_for_demand(A, [100, 200, 300])
    with pytest.raises(ValueError, match="部門の数"):
        output_for_demand(A, [100])
    with pytest.raises(ValueError, match="部門の数"):
        output_for_demand(A, [[100, 200]])


def test_投入係数が負ならエラー() -> None:
    with pytest.raises(ValueError, match="負"):
        leontief_inverse([[0.2, -0.1], [0.4, 0.1]])


def test_単位行列から投入係数を引いた行列が特異ならエラー() -> None:
    singular = [[1.0, 0.0], [0.0, 0.5]]
    with pytest.raises(ValueError, match="特異"):
        leontief_inverse(singular)
    with pytest.raises(ValueError, match="特異"):
        output_for_demand(singular, FINAL_DEMAND)


def test_行列式が負なら生産が成り立たないのでエラー() -> None:
    # 部門 1 は、自分の産出より多くを、投入に使う（付加価値が負）
    unproductive = [[1.5, 0.0], [0.0, 0.2]]
    with pytest.raises(ValueError, match="特異"):
        leontief_inverse(unproductive)


def test_横計は販売先の合計で縦計は投入の合計() -> None:
    rows, columns = io_totals(TRANSACTIONS, TABLE_FINAL_DEMAND, TABLE_VALUE_ADDED)
    assert rows == pytest.approx([300, 400])
    assert columns == pytest.approx([300, 400])


def test_縦計と横計が一致すれば表は整合している() -> None:
    assert is_io_balanced(TRANSACTIONS, TABLE_FINAL_DEMAND, TABLE_VALUE_ADDED)


def test_最終需要か付加価値がずれると表は整合しない() -> None:
    assert sum(TABLE_FINAL_DEMAND) == sum(TABLE_VALUE_ADDED) == 350
    assert not is_io_balanced(TRANSACTIONS, [121, 230], TABLE_VALUE_ADDED)
    # 合計は合っていても、部門ごとにずれていれば、整合していない
    assert not is_io_balanced(TRANSACTIONS, [121, 229], TABLE_VALUE_ADDED)
    assert not is_io_balanced(TRANSACTIONS, TABLE_FINAL_DEMAND, [150, 201])


def test_表の形が合わなければエラー() -> None:
    with pytest.raises(ValueError, match="部門の数"):
        io_totals(TRANSACTIONS, TABLE_FINAL_DEMAND, [150, 200, 10])
    with pytest.raises(ValueError, match="正方行列"):
        io_totals([[1, 2, 3], [4, 5, 6]], TABLE_FINAL_DEMAND, TABLE_VALUE_ADDED)
