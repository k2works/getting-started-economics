import math

import pytest

from lib.chapter10.expectation import random_variable_distribution
from lib.chapter10.probability import dice_sample_space
from lib.chapter10.simulation import simulate_dice_sum_frequencies


def test_6万回投げると和が7の相対頻度は6分の1に近い() -> None:
    frequencies = simulate_dice_sum_frequencies(60_000, seed=1)
    # 標準誤差は √(1/6 × 5/6 ÷ 60000) ≈ 0.0015。その 6 倍ほどの幅で比べる
    assert frequencies[7] == pytest.approx(1 / 6, abs=0.01)
    assert frequencies[2] == pytest.approx(1 / 36, abs=0.005)


def test_どの和の相対頻度も分数で求めた確率に近い() -> None:
    exact = random_variable_distribution(dice_sample_space(), sum)
    frequencies = simulate_dice_sum_frequencies(60_000, seed=4)
    for total, p in exact.items():
        assert frequencies[int(total)] == pytest.approx(float(p), abs=0.01)


def test_相対頻度はとりうる和ごとに並び合計は1() -> None:
    frequencies = simulate_dice_sum_frequencies(1_000, seed=2)
    assert list(frequencies) == list(range(2, 13))
    assert sum(frequencies.values()) == pytest.approx(1)
    three = simulate_dice_sum_frequencies(500, seed=2, dice=3, faces=4)
    assert list(three) == list(range(3, 13))


def test_回数を増やすほど相対頻度と確率のずれの許容幅が狭まる() -> None:
    exact = {7: 1 / 6, 2: 1 / 36, 12: 1 / 36}
    for trials in (100, 10_000, 100_000):
        frequencies = simulate_dice_sum_frequencies(trials, seed=3)
        for total, p in exact.items():
            # 標準誤差 √(p(1 − p) ÷ n) の 4 倍以内。回数を 100 倍にすると幅は 1/10
            standard_error = math.sqrt(p * (1 - p) / trials)
            assert abs(frequencies[total] - p) < 4 * standard_error
    assert abs(frequencies[7] - 1 / 6) < 0.005


def test_種が同じなら結果も同じ() -> None:
    first = simulate_dice_sum_frequencies(200, seed=7)
    assert first == simulate_dice_sum_frequencies(200, seed=7)
    assert first != simulate_dice_sum_frequencies(200, seed=8)


def test_投げる回数は1以上() -> None:
    for trials in (0, -5):
        with pytest.raises(ValueError):
            simulate_dice_sum_frequencies(trials, seed=1)
    # 1 回だけなら、出た和の相対頻度が 1 で、ほかは 0
    once = simulate_dice_sum_frequencies(1, seed=1)
    assert sorted(once.values()) == [0] * 10 + [1]
