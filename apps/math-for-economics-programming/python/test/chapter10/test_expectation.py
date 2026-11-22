from fractions import Fraction

import pytest

from lib.chapter10.expectation import (
    discrete_expected_value,
    discrete_variance,
    random_variable_distribution,
)
from lib.chapter10.probability import dice_sample_space

HALF = Fraction(1, 2)


def test_目の和の分布は和ごとの確率() -> None:
    sums = random_variable_distribution(dice_sample_space(), sum)
    assert sums[7] == Fraction(1, 6)
    assert sums[2] == sums[12] == Fraction(1, 36)
    assert sorted(sums) == list(range(2, 13))
    assert sum(sums.values()) == 1


def test_期待値は値かける確率の和() -> None:
    one_die = random_variable_distribution(dice_sample_space(1), sum)
    assert discrete_expected_value(one_die) == Fraction(7, 2)
    two_dice = random_variable_distribution(dice_sample_space(), sum)
    assert discrete_expected_value(two_dice) == 7
    assert discrete_expected_value({0: HALF, 100: HALF}) == 50
    assert discrete_expected_value({16: HALF, 100: HALF}) == 58
    assert discrete_expected_value({0: Fraction(3, 4), 40: Fraction(1, 4)}) == 10


def test_分散は期待値からのずれの2乗の期待値() -> None:
    one_die = random_variable_distribution(dice_sample_space(1), sum)
    assert discrete_variance(one_die) == Fraction(35, 12)
    two_dice = random_variable_distribution(dice_sample_space(), sum)
    # 独立な 2 個の和の分散は、1 個の分散の 2 倍
    assert discrete_variance(two_dice) == Fraction(35, 6)
    assert discrete_variance({0: HALF, 100: HALF}) == 2500
    assert discrete_variance({0: Fraction(3, 4), 40: Fraction(1, 4)}) == 300


def test_値を3倍して2を足すと期待値も3倍して2を足し分散は9倍() -> None:
    space = dice_sample_space()
    scaled = random_variable_distribution(space, lambda o: 3 * sum(o) + 2)
    assert discrete_expected_value(scaled) == 3 * 7 + 2
    assert discrete_variance(scaled) == 9 * Fraction(35, 6)
    halved = random_variable_distribution(space, lambda o: Fraction(sum(o), 2))
    assert discrete_expected_value(halved) == Fraction(7, 2)
    assert discrete_variance(halved) == Fraction(35, 24)


def test_確率1の値だけなら期待値はその値で分散は0() -> None:
    assert discrete_expected_value({40: Fraction(1)}) == 40
    assert discrete_variance({40: Fraction(1)}) == 0
    # 確率 0 の値は、期待値にも分散にも効かない
    assert discrete_expected_value({40: Fraction(1), 1000: Fraction(0)}) == 40
    assert discrete_variance({-5: Fraction(0), 40: Fraction(1)}) == 0


def test_分布の確率は0以上1以下で合計は1() -> None:
    bad_distributions: list[dict[int, Fraction]] = [
        {},
        {0: HALF, 100: Fraction(1, 4)},
        {0: Fraction(3, 2), 100: -HALF},
        {0: HALF, 100: HALF, 200: Fraction(1, 100)},
    ]
    for bad in bad_distributions:
        with pytest.raises(ValueError):
            discrete_expected_value(bad)
        with pytest.raises(ValueError):
            discrete_variance(bad)
