"""付録 A: 回帰分析（最小二乗法）のテスト。"""

import random

import pytest

from lib.appendix_a.regression import fit_line, r_squared
from lib.chapter08.simulation import simulate_demand


def test_直線上の点なら切片と傾きがそのまま求まる() -> None:
    x = [0.0, 1.0, 2.0, 3.0]
    y = [3 + 2 * v for v in x]
    intercept, slope = fit_line(x, y)
    assert intercept == pytest.approx(3)
    assert slope == pytest.approx(2)


def test_直線上の点なら決定係数は1() -> None:
    x = [0.0, 1.0, 2.0, 3.0]
    y = [3 + 2 * v for v in x]
    assert r_squared(x, y) == pytest.approx(1)


def test_手計算できる3点の回帰直線() -> None:
    # 点 (0, 1)、(1, 3)、(2, 2): 平均は x = 1、y = 2。傾き = (−1×−1 + 0 + 1×0) ÷ 2 = 0.5
    intercept, slope = fit_line([0.0, 1.0, 2.0], [1.0, 3.0, 2.0])
    assert slope == pytest.approx(0.5)
    assert intercept == pytest.approx(1.5)


def test_すべて同じ値のxでは傾きは求められない() -> None:
    with pytest.raises(ValueError):
        fit_line([1.0, 1.0, 1.0], [1.0, 2.0, 3.0])


def test_点の数が合わなければ求められない() -> None:
    with pytest.raises(ValueError):
        fit_line([1.0, 2.0], [1.0])


def test_第8章のシミュレーションで作った需要データから需要曲線を推定できる() -> None:
    rng = random.Random(0)
    prices: list[float] = []
    quantities: list[float] = []
    for price in range(5, 21):
        observations = simulate_demand(price, 100, 2, 10, 50, rng)
        prices.extend([float(price)] * len(observations))
        quantities.extend(observations)
    intercept, slope = fit_line(prices, quantities)
    # 真の需要曲線は Q = 100 - 2P。標準誤差は、傾きが約 0.08、切片が約 1
    assert slope == pytest.approx(-2, abs=0.4)
    assert intercept == pytest.approx(100, abs=5)


def test_ばらつきが大きいほど決定係数は小さい() -> None:
    def fit_r2(sigma: float) -> float:
        rng = random.Random(0)
        prices: list[float] = []
        quantities: list[float] = []
        for price in range(5, 21):
            observations = simulate_demand(price, 100, 2, sigma, 50, rng)
            prices.extend([float(price)] * len(observations))
            quantities.extend(observations)
        return r_squared(prices, quantities)

    assert fit_r2(5) > fit_r2(10) > fit_r2(30)
