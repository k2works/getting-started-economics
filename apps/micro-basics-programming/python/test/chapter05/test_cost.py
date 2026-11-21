"""第 5 章: 費用曲線のテスト。"""

import numpy as np
import pytest

from lib.chapter05.cost import (
    CostCurve,
    argmin_of,
    average_cost,
    average_variable_cost,
    cost_minima,
    marginal_cost,
    marginal_cost_by_gradient,
    total_cost,
    variable_cost,
)

# C(q) = q³ − 6q² + 15q + 32（固定費用 32）
CURVE = CostCurve(cubic=1, quadratic=-6, linear=15, fixed=32)
# 係数が違う例: C(q) = 0.5q³ − 3q² + 10q + 20
OTHER = CostCurve(cubic=0.5, quadratic=-3, linear=10, fixed=20)


def test_総費用は固定費用と可変費用の和() -> None:
    assert total_cost(CURVE, 0) == 32
    assert total_cost(CURVE, 2) == 46
    assert total_cost(CURVE, 5) == 82
    assert total_cost(CURVE, 5) == variable_cost(CURVE, 5) + CURVE.fixed


def test_可変費用は生産量0で0() -> None:
    assert variable_cost(CURVE, 0) == 0
    assert variable_cost(CURVE, 3) == 18


def test_係数が違う費用関数の総費用() -> None:
    assert total_cost(OTHER, 2) == 32
    assert variable_cost(OTHER, 2) == 12


def test_限界費用は総費用の接線の傾き() -> None:
    assert marginal_cost(CURVE, 2) == 3
    assert marginal_cost(CURVE, 3) == 6
    assert marginal_cost(CURVE, 4) == 15
    assert marginal_cost(CURVE, 5) == 30


def test_係数が違う費用関数の限界費用() -> None:
    assert marginal_cost(OTHER, 2) == 4


def test_限界費用は固定費用に依らない() -> None:
    bigger = CostCurve(1, -6, 15, 1000)
    assert marginal_cost(bigger, 4) == marginal_cost(CURVE, 4)


def test_限界費用は逓減のち逓増のU字型() -> None:
    values = [marginal_cost(CURVE, q) for q in (0, 1, 2, 3, 4)]
    assert values == [15, 6, 3, 6, 15]


def test_平均費用は総費用を生産量で割った値() -> None:
    assert average_cost(CURVE, 4) == 15
    assert average_cost(CURVE, 5) == pytest.approx(16.4)
    assert average_cost(CURVE, 3) == pytest.approx(50 / 3)


def test_平均可変費用は可変費用を生産量で割った値() -> None:
    assert average_variable_cost(CURVE, 3) == 6
    assert average_variable_cost(CURVE, 4) == 7


def test_平均費用はいつも平均可変費用より上() -> None:
    for q in (0.5, 1, 2, 3, 4, 8):
        gap = average_cost(CURVE, q) - average_variable_cost(CURVE, q)
        assert gap == pytest.approx(CURVE.fixed / q)
        assert gap > 0


def test_生産量が負ならエラー() -> None:
    with pytest.raises(ValueError, match="生産量"):
        total_cost(CURVE, -1)
    with pytest.raises(ValueError, match="生産量"):
        marginal_cost(CURVE, -0.1)


def test_生産量が0の平均費用は求められない() -> None:
    with pytest.raises(ValueError, match="生産量"):
        average_cost(CURVE, 0)
    with pytest.raises(ValueError, match="生産量"):
        average_variable_cost(CURVE, 0)


def test_生産量が1未満の正の値でも平均費用を求められる() -> None:
    assert average_cost(CURVE, 0.5) == pytest.approx(total_cost(CURVE, 0.5) / 0.5)


def test_費用関数の係数のチェック() -> None:
    with pytest.raises(ValueError, match="3 次"):
        CostCurve(0, -6, 15, 32)
    with pytest.raises(ValueError, match="固定費用"):
        CostCurve(1, -6, 15, -1)


def test_固定費用0は許される() -> None:
    assert total_cost(CostCurve(1, -6, 15, 0), 2) == 14


def test_限界費用は勾配の数値微分と一致する() -> None:
    qs = np.linspace(0, 10, 1001)
    costs = [total_cost(CURVE, float(q)) for q in qs]
    gradient = marginal_cost_by_gradient(costs, qs)
    expected = [marginal_cost(CURVE, float(q)) for q in qs]
    assert gradient[1:-1] == pytest.approx(expected[1:-1], abs=1e-3)


def test_勾配は点の数が揃っていなければエラー() -> None:
    with pytest.raises(ValueError, match="同じ"):
        marginal_cost_by_gradient([1, 2, 3], [0, 1])


def test_最小値の位置と値() -> None:
    assert argmin_of([5, 3, 4], [0, 1, 2]) == (1, 3)


def test_最小値が同じなら先の位置を返す() -> None:
    assert argmin_of([3, 3, 4], [0, 1, 2]) == (0, 3)


def test_最小値は点の数が揃っていなければエラー() -> None:
    with pytest.raises(ValueError, match="同じ"):
        argmin_of([1, 2, 3], [0, 1])


def test_3本の曲線の最低点() -> None:
    minima = cost_minima(CURVE)
    assert minima["MC"] == pytest.approx((2, 3), abs=1e-3)
    assert minima["AVC"] == pytest.approx((3, 6), abs=1e-3)
    assert minima["AC"] == pytest.approx((4, 15), abs=1e-3)


def test_最低点の順は限界費用_平均可変費用_平均費用() -> None:
    minima = cost_minima(CURVE)
    assert minima["MC"][0] < minima["AVC"][0] < minima["AC"][0]


def test_限界費用は平均可変費用と平均費用の最低点を通る() -> None:
    minima = cost_minima(CURVE)
    q_avc, v_avc = minima["AVC"]
    q_ac, v_ac = minima["AC"]
    assert marginal_cost(CURVE, q_avc) == pytest.approx(v_avc, abs=1e-2)
    assert marginal_cost(CURVE, q_ac) == pytest.approx(v_ac, abs=1e-2)


def test_係数が違う費用関数の最低点() -> None:
    # MC = 1.5q² − 6q + 10 の最低点は q = 2（値 4）。AVC = 0.5q² − 3q + 10 の最低点は q = 3（値 5.5）
    minima = cost_minima(OTHER)
    assert minima["MC"] == pytest.approx((2, 4), abs=1e-3)
    assert minima["AVC"] == pytest.approx((3, 5.5), abs=1e-3)


def test_最低点の探索範囲と点の数を変えられる() -> None:
    coarse = cost_minima(CURVE, q_max=6, points=601)
    assert coarse["AC"] == pytest.approx((4, 15), abs=1e-2)


def test_探索の点の数が2未満ならエラー() -> None:
    with pytest.raises(ValueError, match="点の数"):
        cost_minima(CURVE, points=2)


def test_探索の上限が正でなければエラー() -> None:
    with pytest.raises(ValueError, match="上限"):
        cost_minima(CURVE, q_max=0)


# --- 独立した変異確認で見つかった穴を埋めるテスト ---


def test_既定の探索の格子は最低点を正確に通る() -> None:
    minima = cost_minima(CURVE)
    assert minima["MC"][0] == pytest.approx(2, abs=1e-12)
    assert minima["AVC"][0] == pytest.approx(3, abs=1e-12)
    assert minima["AC"][0] == pytest.approx(4, abs=1e-12)


def test_点の数が3でも探索できる() -> None:
    # 格子は q = 0・5・10 の 3 点。MC は 15・30・195 なので、最小は q = 0
    minima = cost_minima(CURVE, q_max=10, points=3)
    assert set(minima) == {"MC", "AVC", "AC"}
    assert minima["MC"] == (0, 15)


def test_平均可変費用が右上がりなら最低点は最初の正の格子点() -> None:
    rising = CostCurve(1, 6, 15, 32)
    q, value = cost_minima(rising)["AVC"]
    assert q == pytest.approx(10 / 10000)
    assert value == pytest.approx(rising.cubic * q**2 + rising.quadratic * q + 15)
