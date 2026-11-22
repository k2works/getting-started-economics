import math

import pytest

from lib.chapter03.interest import years_to_multiply
from lib.chapter04.sequence import affine_fixed_point, iterate_map
from lib.chapter12.recurrence import (
    classify_linear_recurrence,
    recurrence_closed_form,
    recurrence_half_life,
)


def test_閉じた解は不動点からの差を毎期a倍する() -> None:
    # x(t + 1) = 0.5·x(t) + 6、x(0) = 20。不動点 12、差 8 が 4、2、1 と半分になる
    assert [recurrence_closed_form(0.5, 6, 20, t) for t in range(4)] == [20, 16, 14, 13]


@pytest.mark.parametrize(
    ("a", "b", "start"),
    [(0.5, 6, 20), (0.9, 1, 0), (-0.5, 6, 0), (1.1, -2, 3), (-1.5, 4, 0.25)],
)
def test_閉じた解は反復と一致する(a: float, b: float, start: float) -> None:
    path = iterate_map(a, b, start, 12)
    closed = [recurrence_closed_form(a, b, start, t) for t in range(13)]
    assert closed == pytest.approx(path)


def test_aが1なら閉じた解は公差bの等差数列() -> None:
    assert [recurrence_closed_form(1, 3, 2, t) for t in range(4)] == [2, 5, 8, 11]
    assert recurrence_closed_form(1, -0.5, 4, 10) == pytest.approx(-1)
    assert recurrence_closed_form(1, 3, 2, 7) == pytest.approx(
        iterate_map(1, 3, 2, 7)[-1]
    )


def test_不動点から始めると動かない() -> None:
    fixed = affine_fixed_point(0.9, 1)
    assert recurrence_closed_form(0.9, 1, fixed, 25) == pytest.approx(fixed)


@pytest.mark.parametrize(
    ("a", "kind"),
    [
        (0.5, "converges"),
        (0.9, "converges"),
        (0, "converges"),
        (-0.5, "converges with oscillation"),
        (1.1, "diverges"),
        (-1.5, "diverges with oscillation"),
        (1, "arithmetic"),
        (-1, "two-cycle"),
    ],
)
def test_aの大きさと符号でふるまいを分ける(a: float, kind: str) -> None:
    assert classify_linear_recurrence(a) == kind


def test_aが負なら不動点の上下を行き来する() -> None:
    # x(t + 1) = −0.5·x(t) + 6 の不動点は 4。差 −4 が 2、−1、0.5 と符号を変える
    gaps = [recurrence_closed_form(-0.5, 6, 0, t) - 4 for t in range(5)]
    assert gaps == pytest.approx([-4, 2, -1, 0.5, -0.25])


def test_差が半分になる期数は対数で求まる() -> None:
    assert recurrence_half_life(0.5) == pytest.approx(1)
    assert recurrence_half_life(0.25) == pytest.approx(0.5)
    assert recurrence_half_life(0.9) == pytest.approx(math.log(2) / -math.log(0.9))
    assert 0.9 ** recurrence_half_life(0.9) == pytest.approx(0.5)


def test_半減期は割引の逆で第3章の倍になる年数と同じ形() -> None:
    assert recurrence_half_life(1 / 1.05) == pytest.approx(years_to_multiply(0.05, 2))


def test_負の期の閉じた解は求めない() -> None:
    with pytest.raises(ValueError):
        recurrence_closed_form(0.5, 6, 20, -1)


def test_0期の閉じた解は初期値() -> None:
    assert recurrence_closed_form(1.1, -2, 3, 0) == 3
    assert recurrence_closed_form(1, 3, 2, 0) == 2


def test_aが負でも半減期は差の大きさで測る() -> None:
    assert recurrence_half_life(-0.5) == pytest.approx(1)


@pytest.mark.parametrize("a", [0, 1, -1, 1.1, -2])
def test_収束しないかすぐ止まるaには半減期がない(a: float) -> None:
    # a = 0 は、対数の計算でなく、範囲の確かめで止める（メッセージで見分ける）
    with pytest.raises(ValueError, match="差が半分"):
        recurrence_half_life(a)
