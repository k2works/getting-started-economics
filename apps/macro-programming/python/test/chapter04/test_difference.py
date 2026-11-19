"""第 4 章: 1 階差分方程式のテスト。

x(t+1) = a·x(t) + b。a = 0.5、b = 1、x(0) = 0 なら、x は 0、1、1.5、1.75、… と 2 に近づく。
"""

import pytest

from lib.chapter04.difference import (
    closed_form,
    cobweb_coefficients,
    income_adjustment,
    is_stable,
    iterate,
    linear_path,
    steady_state,
)


def test_写像を繰り返し適用した値を並べる() -> None:
    assert iterate(lambda x: 2 * x, 1, 3) == [1, 2, 4, 8]


def test_0回の繰り返しは初期値だけ() -> None:
    assert iterate(lambda x: x + 1, 5, 0) == [5]


def test_繰り返しの回数は負にできない() -> None:
    with pytest.raises(ValueError, match="回数"):
        iterate(lambda x: x, 1, -1)


def test_a0_5_b1_x0が0の経路() -> None:
    assert linear_path(0.5, 1, 0, 3) == pytest.approx([0, 1, 1.5, 1.75])


def test_定常状態はb割る1引くa() -> None:
    assert steady_state(0.5, 1) == pytest.approx(2)


def test_aが1なら定常状態は求められない() -> None:
    with pytest.raises(ValueError, match="1"):
        steady_state(1, 1)


def test_定常状態から出発すれば動かない() -> None:
    assert linear_path(0.5, 1, 2, 5) == pytest.approx([2] * 6)


@pytest.mark.parametrize(("a", "expected"), [(0.5, True), (-0.8, True), (1.1, False)])
def test_aの絶対値が1より小さければ安定(a: float, expected: bool) -> None:
    assert is_stable(a) is expected


def test_aの絶対値がちょうど1なら安定ではない() -> None:
    assert not is_stable(1)
    assert not is_stable(-1)


def test_閉じた形は繰り返しの結果と一致する() -> None:
    path = linear_path(0.5, 1, 0, 10)
    for t, value in enumerate(path):
        assert closed_form(0.5, 1, 0, t) == pytest.approx(value)


def test_閉じた形はt3で1_75() -> None:
    # a^t·(x0 − x*) + x* = 0.125·(0 − 2) + 2
    assert closed_form(0.5, 1, 0, 3) == pytest.approx(1.75)


def test_aが負なら経路は定常状態の上下を往復する() -> None:
    path = linear_path(-0.8, 1, 0, 6)
    steady = steady_state(-0.8, 1)
    signs = [value > steady for value in path]
    assert all(signs[i] != signs[i + 1] for i in range(len(signs) - 1))


def test_aが1より大きければ定常状態から離れていく() -> None:
    path = linear_path(1.1, 1, 0, 5)
    steady = steady_state(1.1, 1)
    gaps = [abs(value - steady) for value in path]
    assert gaps == sorted(gaps)
    assert gaps[-1] > gaps[0]


def test_45度線モデルの所得は定常状態250に近づく() -> None:
    # Y(t+1) = C0 + c·Y(t) + I = 20 + 0.8·Y(t) + 30。定常状態 50 ÷ (1 − 0.8) = 250
    path = income_adjustment(
        autonomous_consumption=20, mpc=0.8, investment=30, initial_income=0, periods=60
    )
    assert path[-1] == pytest.approx(250, abs=0.01)
    assert path[1] == pytest.approx(50)


def test_45度線モデルの調整経路の定常状態は乗数を使った国民所得と同じ() -> None:
    steady = steady_state(0.8, 20 + 30)
    assert steady == pytest.approx((20 + 30) * (1 / (1 - 0.8)))


def test_蜘蛛の巣モデルの係数() -> None:
    # 需要 Q = 100 − 3P、供給（前期の価格）Q = 2P(t−1)。P(t) = 100/3 − (2/3)·P(t−1)
    a, b = cobweb_coefficients(100, 3, 0, 2)
    assert a == pytest.approx(-2 / 3)
    assert b == pytest.approx(100 / 3)


def test_蜘蛛の巣モデルの定常状態は需要と供給の均衡価格() -> None:
    a, b = cobweb_coefficients(100, 3, 0, 2)
    assert steady_state(a, b) == pytest.approx(100 / (3 + 2))


def test_供給の傾きが需要の傾きより小さければ蜘蛛の巣は収束する() -> None:
    a, _ = cobweb_coefficients(100, 3, 0, 2)
    assert is_stable(a)


def test_供給の傾きが需要の傾きより大きければ蜘蛛の巣は発散する() -> None:
    # 需要 Q = 100 − 2P、供給 Q = 3P(t−1)。傾きの比 −3/2
    a, _ = cobweb_coefficients(100, 2, 0, 3)
    assert a == pytest.approx(-1.5)
    assert not is_stable(a)


def test_蜘蛛の巣モデルでは需要曲線の傾きは正でなければならない() -> None:
    with pytest.raises(ValueError, match="傾き"):
        cobweb_coefficients(100, 0, 0, 2)
