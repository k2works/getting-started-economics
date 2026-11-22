import pytest

from lib.chapter02.quadratic import (
    argmax_on_grid,
    complete_the_square,
    parabola_vertex,
    quadratic_discriminant,
    quadratic_roots,
)


def test_平方完成すると頂点の形になる() -> None:
    # 2x² − 8x + 6 = 2(x − 2)² − 2
    assert complete_the_square(2, -8, 6) == (2, 2, -2)


def test_平方完成した式は元の式と同じ値になる() -> None:
    a, h, k = complete_the_square(2, -8, 6)
    for x in [-1, 0, 0.5, 3, 10]:
        assert a * (x - h) ** 2 + k == pytest.approx(2 * x**2 - 8 * x + 6)


def test_上に凸の放物線の頂点は最大値() -> None:
    # −x² + 80x = −(x − 40)² + 1600
    assert parabola_vertex(-1, 80, 0) == (40, 1600)


def test_2乗の係数が0なら2次関数ではない() -> None:
    with pytest.raises(ValueError):
        complete_the_square(0, 2, 1)
    with pytest.raises(ValueError):
        parabola_vertex(0, 2, 1)
    with pytest.raises(ValueError):
        quadratic_roots(0, 2, 1)


def test_判別式は_b2乗引く_4ac() -> None:
    assert quadratic_discriminant(2, -8, 6) == 16
    assert quadratic_discriminant(1, -4, 4) == 0
    assert quadratic_discriminant(1, 2, 5) == -16


def test_実数解の個数は判別式の符号で決まる() -> None:
    assert quadratic_roots(2, -8, 6) == (1, 3)  # D > 0: 2 つ
    assert quadratic_roots(1, -4, 4) == (2,)  # D = 0: 1 つ
    assert quadratic_roots(2, -8, 8) == (2,)  # D = 0、2 乗の係数が 1 でない
    assert quadratic_roots(1, 2, 5) == ()  # D < 0: なし


def test_解を代入すると0になる() -> None:
    for x in quadratic_roots(3, -5, -7):
        assert 3 * x**2 - 5 * x - 7 == pytest.approx(0)


def test_格子の上で最大値をとる点を探す() -> None:
    best = argmax_on_grid(lambda x: -((x - 40) ** 2) + 1600, 0, 100, 201)
    assert best == 40


def test_格子探索の答えは頂点の近くにある() -> None:
    def f(x: float) -> float:
        return -2 * x**2 + 7 * x + 1

    h, _ = parabola_vertex(-2, 7, 1)
    best = argmax_on_grid(f, 0, 10, 1001)
    assert best == pytest.approx(h, abs=0.01)


def test_格子の点が2つ未満ならエラー() -> None:
    with pytest.raises(ValueError):
        argmax_on_grid(lambda x: x, 0, 1, 1)


def test_格子の点が2つだけでも下限が0でなくても探せる() -> None:
    assert argmax_on_grid(lambda x: -x, 0, 1, 2) == 0
    assert argmax_on_grid(lambda x: x, 0, 1, 2) == 1
    assert argmax_on_grid(lambda x: -((x - 40) ** 2), 15, 55, 41) == 40
