"""第 8 章: 確率過程（ホワイト・ノイズと AR(1)）のテスト。

手計算の例: x = [1, 2, 3, 4]。平均 2.5、変動の合計 5。ラグ 1 の自己共分散は、
((−1.5)(−0.5) + (−0.5)(0.5) + (0.5)(1.5)) ÷ 4 = 0.3125、自己相関は 0.3125 ÷ 1.25 = 0.25。
"""

import numpy as np
import pytest

from lib.chapter04.difference import linear_path
from lib.chapter08.stochastic import (
    ar1_autocorrelation,
    ar1_impulse_response,
    ar1_series,
    ar1_variance,
    autocorrelation_function,
    sample_autocorrelation,
    sample_autocovariance,
    shock_half_life,
    white_noise,
)

X = [1.0, 2.0, 3.0, 4.0]


def test_ホワイトノイズの平均は0で標準偏差は指定した値に近い() -> None:
    x = white_noise(100_000, 2.0, np.random.default_rng(0))
    assert x.mean() == pytest.approx(0, abs=0.03)
    assert x.std() == pytest.approx(2.0, abs=0.03)


def test_種が同じなら同じ系列() -> None:
    a = white_noise(10, 1.0, np.random.default_rng(5))
    b = white_noise(10, 1.0, np.random.default_rng(5))
    assert a.tolist() == b.tolist()


def test_ホワイトノイズの自己相関は0に近い() -> None:
    x = white_noise(100_000, 1.0, np.random.default_rng(1))
    assert sample_autocorrelation(x, 1) == pytest.approx(0, abs=0.02)
    assert sample_autocorrelation(x, 5) == pytest.approx(0, abs=0.02)


def test_系列の長さは正でなければならない() -> None:
    with pytest.raises(ValueError, match="長さ"):
        white_noise(0, 1.0, np.random.default_rng(0))


def test_標準偏差は負にできない() -> None:
    with pytest.raises(ValueError, match="標準偏差"):
        white_noise(10, -1.0, np.random.default_rng(0))


def test_AR1の分散は理論値4_3に近い() -> None:
    x = ar1_series(0.5, 1.0, 100_000, np.random.default_rng(2))
    assert x.var() == pytest.approx(4 / 3, abs=0.05)


def test_AR1の自己相関はラグkでrhoのk乗に近い() -> None:
    x = ar1_series(0.5, 1.0, 100_000, np.random.default_rng(2))
    assert sample_autocorrelation(x, 1) == pytest.approx(0.5, abs=0.01)
    assert sample_autocorrelation(x, 2) == pytest.approx(0.25, abs=0.01)


def test_rhoが負なら自己相関も負() -> None:
    x = ar1_series(-0.7, 1.0, 100_000, np.random.default_rng(3))
    assert sample_autocorrelation(x, 1) == pytest.approx(-0.7, abs=0.01)


def test_AR1の長さは指定どおり() -> None:
    assert len(ar1_series(0.9, 1.0, 50, np.random.default_rng(0))) == 50


@pytest.mark.parametrize("rho", [1.0, -1.0, 1.5])
def test_rhoの絶対値が1以上なら定常ではない(rho: float) -> None:
    with pytest.raises(ValueError, match="定常"):
        ar1_series(rho, 1.0, 10, np.random.default_rng(0))


def test_自己共分散を手計算と比べる() -> None:
    assert sample_autocovariance(X, 0) == pytest.approx(1.25)
    assert sample_autocovariance(X, 1) == pytest.approx(0.3125)


def test_自己相関を手計算と比べる() -> None:
    assert sample_autocorrelation(X, 0) == pytest.approx(1)
    assert sample_autocorrelation(X, 1) == pytest.approx(0.25)


def test_自己相関関数はラグ0から並べる() -> None:
    assert autocorrelation_function(X, 2) == pytest.approx([1, 0.25, -0.3])


@pytest.mark.parametrize("lag", [-1, 4, 10])
def test_ラグは0以上で系列の長さより短くなければならない(lag: int) -> None:
    with pytest.raises(ValueError, match="ラグ"):
        sample_autocovariance(X, lag)


def test_定数の系列では自己相関は求められない() -> None:
    with pytest.raises(ValueError, match="変動"):
        sample_autocorrelation([2.0, 2.0, 2.0], 1)


def test_AR1の分散の理論値() -> None:
    # σ² ÷ (1 − ρ²) = 1 ÷ 0.75
    assert ar1_variance(0.5, 1.0) == pytest.approx(4 / 3)


def test_rhoが1なら分散は求められない() -> None:
    with pytest.raises(ValueError, match="定常"):
        ar1_variance(1.0, 1.0)


def test_AR1の自己相関の理論値はrhoのk乗() -> None:
    assert ar1_autocorrelation(0.5, 3) == pytest.approx(0.125)
    assert ar1_autocorrelation(-0.5, 3) == pytest.approx(-0.125)


def test_ショックの半減期() -> None:
    assert shock_half_life(0.5) == pytest.approx(1)
    assert shock_half_life(0.9) == pytest.approx(np.log(0.5) / np.log(0.9))


@pytest.mark.parametrize("rho", [0, 1, -1, 1.2])
def test_半減期はrhoの絶対値が0より大きく1より小さいときだけ(rho: float) -> None:
    with pytest.raises(ValueError, match="rho"):
        shock_half_life(rho)


def test_インパルス反応は毎期rho倍() -> None:
    assert ar1_impulse_response(0.8, 2) == pytest.approx([1, 0.8, 0.64])


def test_インパルス反応は第4章の差分方程式の経路と同じ() -> None:
    assert ar1_impulse_response(0.8, 10, shock=2.0) == pytest.approx(
        linear_path(0.8, 0, 2.0, 10)
    )


def test_標準偏差が0ならすべて0の系列() -> None:
    assert white_noise(5, 0.0, np.random.default_rng(0)).tolist() == [0.0] * 5
