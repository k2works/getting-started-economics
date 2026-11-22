from fractions import Fraction

import pytest

from lib.chapter10.probability import (
    are_independent_events,
    conditional_probability,
    dice_sample_space,
    equally_likely_probability,
    outcomes_where,
    require_probability,
)

SPACE = dice_sample_space()


def _sum_is(total: int) -> frozenset[tuple[int, ...]]:
    return outcomes_where(SPACE, lambda o: sum(o) == total)


def test_サイコロ2個の標本空間は36通り() -> None:
    assert len(SPACE) == 36
    assert (1, 6) in SPACE and (6, 1) in SPACE
    assert len(dice_sample_space(3)) == 216
    assert len(dice_sample_space(2, faces=4)) == 16
    assert dice_sample_space(1) == {(1,), (2,), (3,), (4,), (5,), (6,)}
    assert dice_sample_space(2, faces=1) == {(1, 1)}


def test_均等確率の確率は事象の数を標本の数で割る() -> None:
    assert equally_likely_probability(_sum_is(7), SPACE) == Fraction(1, 6)
    assert equally_likely_probability(_sum_is(2), SPACE) == Fraction(1, 36)
    assert equally_likely_probability(_sum_is(8), SPACE) == Fraction(5, 36)
    four = dice_sample_space(2, faces=4)
    five = outcomes_where(four, lambda o: sum(o) == 5)
    assert equally_likely_probability(five, four) == Fraction(4, 16)


def test_確率は0以上1以下で全事象は1で空事象は0() -> None:
    for total in range(1, 14):
        assert 0 <= equally_likely_probability(_sum_is(total), SPACE) <= 1
    assert equally_likely_probability(SPACE, SPACE) == 1
    assert equally_likely_probability(frozenset(), SPACE) == 0
    assert equally_likely_probability(_sum_is(13), SPACE) == 0


def test_余事象の確率は1から引く() -> None:
    seven = _sum_is(7)
    assert equally_likely_probability(SPACE - seven, SPACE) == Fraction(5, 6)
    at_least_one_six = outcomes_where(SPACE, lambda o: 6 in o)
    no_six = SPACE - at_least_one_six
    assert equally_likely_probability(no_six, SPACE) == Fraction(25, 36)
    assert equally_likely_probability(at_least_one_six, SPACE) == Fraction(11, 36)


def test_加法定理は重なりを1回引く() -> None:
    eight = _sum_is(8)
    doubles = outcomes_where(SPACE, lambda o: o[0] == o[1])
    union = equally_likely_probability(eight | doubles, SPACE)
    p_eight = equally_likely_probability(eight, SPACE)
    p_doubles = equally_likely_probability(doubles, SPACE)
    overlap = equally_likely_probability(eight & doubles, SPACE)
    assert union == p_eight + p_doubles - overlap == Fraction(5, 18)
    assert overlap == Fraction(1, 36)
    # 重ならない（排反な）事象なら、確率は足すだけ
    seven = _sum_is(7)
    assert equally_likely_probability(seven | doubles, SPACE) == Fraction(1, 3)


def test_標本空間は空でなく事象はその部分集合() -> None:
    with pytest.raises(ValueError):
        equally_likely_probability(frozenset(), frozenset())
    with pytest.raises(ValueError):
        equally_likely_probability(frozenset({(7, 7)}), SPACE)
    for dice, faces in [(0, 6), (2, 0), (-1, 6)]:
        with pytest.raises(ValueError):
            dice_sample_space(dice, faces)


def test_条件付き確率は重なりの確率をBの確率で割る() -> None:
    first_six = outcomes_where(SPACE, lambda o: o[0] == 6)
    assert conditional_probability(_sum_is(8), first_six, SPACE) == Fraction(1, 6)
    high = outcomes_where(SPACE, lambda o: sum(o) >= 10)
    assert conditional_probability(high, first_six, SPACE) == Fraction(1, 2)
    assert equally_likely_probability(high, SPACE) == Fraction(1, 6)
    # 条件付き確率は、向きを入れ替えると、一般に違う
    assert conditional_probability(_sum_is(12), first_six, SPACE) == Fraction(1, 6)
    assert conditional_probability(first_six, _sum_is(12), SPACE) == 1


def test_1個目が6でも和が7の確率は変わらず独立() -> None:
    first_six = outcomes_where(SPACE, lambda o: o[0] == 6)
    seven = _sum_is(7)
    assert conditional_probability(seven, first_six, SPACE) == Fraction(1, 6)
    assert are_independent_events(seven, first_six, SPACE)
    # 和が 8 は、1 個目が 6 だと確率が上がる（5/36 → 1/6）ので、独立でない
    assert not are_independent_events(_sum_is(8), first_six, SPACE)


def test_確率0の事象を条件にはできない() -> None:
    with pytest.raises(ValueError):
        conditional_probability(_sum_is(7), _sum_is(13), SPACE)
    assert conditional_probability(_sum_is(13), _sum_is(7), SPACE) == 0


def test_確率の値は0以上1以下だけを受け付ける() -> None:
    for ok in [Fraction(0), Fraction(1, 2), Fraction(1)]:
        require_probability(ok)
    for bad in [Fraction(-1, 100), Fraction(101, 100)]:
        with pytest.raises(ValueError):
            require_probability(bad)
