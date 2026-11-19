"""第 1 章: 統計学の復習（標本の特徴を表す数値と、確率分布）のテスト。"""

import numpy as np
import pytest
from scipy import stats

from lib.chapter01.statistics import (
    critical_value,
    normal_cdf,
    sample_correlation,
    sample_covariance,
    sample_variance,
    sampling_distribution_of_mean,
    standard_error_of_mean,
    standardize,
)

X = [1, 2, 3, 4, 5]


def test_不偏分散は分母がn引く1() -> None:
    assert sample_variance(X) == pytest.approx(2.5)


def test_分母をnにすると標本分散() -> None:
    assert sample_variance(X, ddof=0) == pytest.approx(2.0)


def test_定数の分散は0() -> None:
    assert sample_variance([7, 7, 7]) == 0


def test_観測値が足りないと分散は計算できない() -> None:
    with pytest.raises(ValueError, match="観測値の数"):
        sample_variance([1])
    with pytest.raises(ValueError, match="観測値の数"):
        sample_variance([1, 2], ddof=2)


def test_共分散() -> None:
    assert sample_covariance([1, 2, 3], [2, 4, 5]) == pytest.approx(1.5)


def test_自分自身との共分散は分散() -> None:
    assert sample_covariance(X, X) == pytest.approx(sample_variance(X))


def test_共分散は順序を入れ替えても同じ() -> None:
    x, y = [1, 2, 3, 4], [2, 4, 5, 9]
    assert sample_covariance(x, y) == pytest.approx(sample_covariance(y, x))


def test_長さが違うと共分散は計算できない() -> None:
    with pytest.raises(ValueError, match="長さ"):
        sample_covariance([1, 2, 3], [1, 2])
    with pytest.raises(ValueError, match="長さ"):
        sample_covariance([1, 2], [1, 2, 3])


def test_観測値が1個だと共分散は計算できない() -> None:
    with pytest.raises(ValueError, match="観測値の数"):
        sample_covariance([1], [2])


def test_直線上のデータの相関は1と負の1() -> None:
    assert sample_correlation(X, [2 * v + 1 for v in X]) == pytest.approx(1)
    assert sample_correlation(X, [-3 * v for v in X]) == pytest.approx(-1)


def test_相関は単位を変えても変わらない() -> None:
    x, y = [1, 2, 3, 4], [2, 4, 5, 9]
    scaled = [100 * v for v in x]
    assert sample_correlation(scaled, y) == pytest.approx(sample_correlation(x, y))


def test_共分散の例の相関はNumPyと一致する() -> None:
    x, y = [1, 2, 3, 4], [2, 4, 5, 9]
    assert sample_correlation(x, y) == pytest.approx(np.corrcoef(x, y)[0, 1])


def test_ばらつきのない変数の相関は計算できない() -> None:
    with pytest.raises(ValueError, match="分散が 0"):
        sample_correlation([1, 1, 1], [1, 2, 3])


def test_標準化すると平均0分散1() -> None:
    z = standardize([1, 2, 3, 4, 10])
    assert np.mean(z) == pytest.approx(0, abs=1e-12)
    assert sample_variance(z) == pytest.approx(1)


def test_標本平均の標準誤差() -> None:
    assert standard_error_of_mean(X) == pytest.approx((2.5 / 5) ** 0.5)


def test_標準正規の分布関数() -> None:
    assert normal_cdf(0) == pytest.approx(0.5)
    assert normal_cdf(1.96) == pytest.approx(0.9750021, abs=1e-6)
    assert normal_cdf(-1.96) == pytest.approx(1 - normal_cdf(1.96))


def test_標準正規の分布関数はSciPyと一致する() -> None:
    for z in (-3.0, -0.5, 0.3, 2.2):
        assert normal_cdf(z) == pytest.approx(stats.norm.cdf(z))


def test_正規分布の臨界値() -> None:
    assert critical_value("normal", 0.975) == pytest.approx(1.959964, abs=1e-6)


def test_t分布の臨界値は正規分布より大きい() -> None:
    assert critical_value("t", 0.975, 2) == pytest.approx(4.302653, abs=1e-6)
    assert critical_value("t", 0.975, 30) > critical_value("normal", 0.975)


def test_自由度が大きいとt分布は正規分布に近づく() -> None:
    assert critical_value("t", 0.975, 100000) == pytest.approx(
        critical_value("normal", 0.975), abs=1e-4
    )


def test_tの2乗はFの1つめの自由度が1の場合に等しい() -> None:
    t = critical_value("t", 0.975, 2)
    assert t**2 == pytest.approx(critical_value("f", 0.95, 1, 2))
    assert critical_value("f", 0.95, 1, 2) == pytest.approx(18.5128, abs=1e-4)


def test_標準正規の2乗はカイ2乗の自由度1に等しい() -> None:
    z = critical_value("normal", 0.975)
    assert z**2 == pytest.approx(critical_value("chi2", 0.95, 1))


def test_知らない分布は受け付けない() -> None:
    with pytest.raises(ValueError, match="分布"):
        critical_value("gamma", 0.95)


def test_確率は0と1の間でなければならない() -> None:
    for p in (0, 1, -0.1, 1.5):
        with pytest.raises(ValueError, match="確率"):
            critical_value("normal", p)


def test_標本平均の標準偏差は1をnの平方根で割った値に近づく() -> None:
    means = sampling_distribution_of_mean(
        n=25, repetitions=2000, rng=np.random.default_rng(0)
    )
    assert means.shape == (2000,)
    assert np.mean(means) == pytest.approx(0, abs=4 * 0.2 / 2000**0.5)
    assert np.std(means, ddof=1) == pytest.approx(0.2, rel=0.1)


def test_同じ種なら同じ標本平均になる() -> None:
    a = sampling_distribution_of_mean(5, 10, np.random.default_rng(1))
    b = sampling_distribution_of_mean(5, 10, np.random.default_rng(1))
    assert np.array_equal(a, b)
