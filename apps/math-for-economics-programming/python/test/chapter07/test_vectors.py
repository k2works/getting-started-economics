import math

import numpy as np
import pytest

from lib.chapter07.vectors import (
    line_normal_form,
    mean_by_dot,
    variance_by_dot,
    vector_angle_degrees,
    vector_dot,
    vector_length,
)


def test_1と2と3と4の内積は11() -> None:
    assert vector_dot([1, 2], [3, 4]) == 11


def test_3財のベクトルの内積は成分ごとの積の和() -> None:
    assert vector_dot([2, 3, 0.5], [10, 4, 6]) == pytest.approx(35)


def test_長さの違うベクトルの内積は決まらない() -> None:
    with pytest.raises(ValueError):
        vector_dot([1, 2, 3], [1, 2])


def test_ベクトルの大きさは自分との内積の平方根() -> None:
    assert vector_length([3, 4]) == 5
    assert vector_length([1, 2, 2]) == 3


def test_1と0と1と1のなす角は45度() -> None:
    assert vector_angle_degrees([1, 0], [1, 1]) == pytest.approx(45)


def test_内積が0のベクトルは直交する() -> None:
    assert vector_dot([2, 3], [3, -2]) == 0
    assert vector_angle_degrees([2, 3], [3, -2]) == pytest.approx(90)
    assert vector_angle_degrees([1, 0, 0], [0, 0, 5]) == pytest.approx(90)


def test_同じ向きは0度で逆向きは180度() -> None:
    # 0 度・180 度の近くでは、acos が丸め誤差を拡大する（cos の誤差 1e-16 が、1e-6 度に）
    assert vector_angle_degrees([1, 2], [2, 4]) == pytest.approx(0, abs=1e-5)
    assert vector_angle_degrees([1, 2], [-3, -6]) == pytest.approx(180, abs=1e-5)


def test_丸め誤差でcosが1を超えても角は0度() -> None:
    # 0.1 は 2 進数で割り切れず、cos θ が 1.0000000000000002 になる
    assert vector_angle_degrees([0.1, 1], [0.2, 2]) == pytest.approx(0, abs=1e-5)
    assert vector_angle_degrees([0.1, 1], [-0.2, -2]) == pytest.approx(180, abs=1e-5)


def test_0ベクトルとのなす角は決まらない() -> None:
    with pytest.raises(ValueError):
        vector_angle_degrees([0, 0], [1, 1])
    with pytest.raises(ValueError):
        vector_angle_degrees([1, 1], [0, 0])


def test_自作の内積と大きさはNumPyと一致する() -> None:
    pairs: list[tuple[list[float], list[float]]] = [
        ([1, 2], [3, 4]),
        ([2, 3, 0.5], [10, 4, 6]),
        ([0.1, -0.7, 0.3, 2], [-5, 0.25, 4, 0]),
        ([0, 0, 0], [1, 2, 3]),
    ]
    for u, v in pairs:
        assert vector_dot(u, v) == pytest.approx(float(np.dot(u, v)))
        assert vector_length(u) == pytest.approx(float(np.linalg.norm(u)))


def test_NumPyの配列の掛け算は成分ごとで内積は和をとる() -> None:
    u = np.array([1, 2, 3], dtype=np.float64)
    v = np.array([4, 5, 6], dtype=np.float64)
    assert (u * v).tolist() == [4, 10, 18]
    assert float(np.dot(u, v)) == float((u * v).sum()) == 32


def test_5つの値の平均3は1のベクトルとの内積を5で割る() -> None:
    assert mean_by_dot([1, 2, 3, 4, 5]) == 3


def test_5つの値の分散2は偏差の内積を5で割る() -> None:
    assert variance_by_dot([1, 2, 3, 4, 5]) == 2


def test_内積の平均と分散は統計の公式と一致する() -> None:
    for xs in ([1, 2, 3, 4, 5], [2.5, -1, 0.3, 8], [10, 10, 10], [0.2, 0.9]):
        assert mean_by_dot(xs) == pytest.approx(float(np.mean(xs)))
        assert variance_by_dot(xs) == pytest.approx(float(np.var(xs)))
        assert math.sqrt(variance_by_dot(xs)) == pytest.approx(float(np.std(xs)))


def test_空のデータの平均と分散は決まらない() -> None:
    with pytest.raises(ValueError):
        mean_by_dot([])
    with pytest.raises(ValueError):
        variance_by_dot([])


def test_1つだけの値の平均はその値で分散は0() -> None:
    assert mean_by_dot([7]) == 7
    assert variance_by_dot([7]) == 0


def test_2点を通る直線の法線ベクトルと定数() -> None:
    assert line_normal_form([30, 0], [0, 20]) == ([20, 30], 600)


def test_直線上の点は法線ベクトルとの内積が定数() -> None:
    pairs: list[tuple[list[float], list[float]]] = [
        ([30, 0], [0, 20]),
        ([1, 5], [4, -1]),
        ([0.5, 0.5], [2, 3.5]),
    ]
    for p, q in pairs:
        normal, constant = line_normal_form(p, q)
        middle = [(a + b) / 2 for a, b in zip(p, q, strict=True)]
        for point in (p, q, middle):
            assert vector_dot(normal, point) == pytest.approx(constant)
        direction = [b - a for a, b in zip(p, q, strict=True)]
        assert vector_dot(normal, direction) == pytest.approx(0)


def test_縦の直線と横の直線の法線ベクトル() -> None:
    assert line_normal_form([5, 0], [5, 10]) == ([10, 0], 50)
    assert line_normal_form([0, 2], [4, 2]) == ([0, -4], -8)


def test_同じ2点では直線が決まらない() -> None:
    with pytest.raises(ValueError):
        line_normal_form([1, 2], [1, 2])
