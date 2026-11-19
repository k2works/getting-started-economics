"""第 6 章: 大標本特性（一致性・t 値の分布・正規性の検定・LM 検定）のテスト。"""

import math

import numpy as np
import pandas as pd
import pytest
from scipy import stats
from statsmodels.stats.stattools import jarque_bera as reference_jarque_bera

from lib.chapter03.multiple import fit_ols
from lib.chapter05.inference import TestResult
from lib.chapter06.asymptotics import (
    consistency_experiment,
    draw_skewed_sample,
    jarque_bera,
    jarque_bera_rejection_rate,
    kurtosis,
    lm_test,
    skewness,
    t_value_distribution,
)

SKEWED = [0, 0, 0, 4]


def test_歪度は左右対称なら0で裾が長い側が正() -> None:
    assert skewness([1, 2, 3, 4, 5]) == pytest.approx(0)
    assert skewness(SKEWED) == pytest.approx(2 / 3**0.5)
    assert skewness([4, 4, 4, 0]) == pytest.approx(-2 / 3**0.5)


def test_尖度() -> None:
    assert kurtosis([-1, 1]) == pytest.approx(1)
    assert kurtosis(SKEWED) == pytest.approx(21 / 9)


def test_正規乱数の歪度は0で尖度は3に近い() -> None:
    x = np.random.default_rng(3).standard_normal(100000)
    assert skewness(x) == pytest.approx(0, abs=0.03)
    assert kurtosis(x) == pytest.approx(3, abs=0.1)


def test_手計算の例のJB統計量とp値() -> None:
    test = jarque_bera(SKEWED)
    assert test.statistic == pytest.approx(4 / 6 * (4 / 3 + 1 / 9))
    assert test.p_value == pytest.approx(math.exp(-test.statistic / 2))


def test_JB検定はstatsmodelsと一致する() -> None:
    x = np.random.default_rng(0).exponential(1.0, 50)
    test = jarque_bera(x)
    statistic, p, _, _ = reference_jarque_bera(x)
    assert isinstance(test, TestResult)
    assert test.statistic == pytest.approx(statistic)
    assert test.p_value == pytest.approx(p)


def random_data(n: int = 60, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    x1 = rng.standard_normal(n)
    x2 = rng.standard_normal(n)
    y = 1 + 2 * x1 + 0.3 * x2 + rng.standard_normal(n)
    return pd.DataFrame({"y": y, "x1": x1, "x2": x2})


def test_LM統計量は残差平方和の比から決まる() -> None:
    df = random_data()
    test = lm_test(df["y"], df[["x1"]], df[["x2"]])
    rss_restricted = float(np.sum(fit_ols(df["y"], df[["x1"]]).residuals ** 2))
    rss_full = float(np.sum(fit_ols(df["y"], df[["x1", "x2"]]).residuals ** 2))
    assert test.statistic == pytest.approx(60 * (1 - rss_full / rss_restricted))
    assert test.p_value == pytest.approx(stats.chi2.sf(test.statistic, 1))


def test_LM検定は関係のある変数を棄却し関係のない変数を棄却しない() -> None:
    df = random_data(200)
    noise = pd.DataFrame({"noise": np.random.default_rng(9).standard_normal(200)})
    relevant = lm_test(df["y"], df[["x2"]], df[["x1"]])
    irrelevant = lm_test(df["y"], df[["x1"]], noise)
    assert relevant.p_value < 0.001
    # 種を固定した 1 標本の例示。帰無仮説が正しくても、種を変えれば、約 5% で p < 0.05 になる
    assert irrelevant.p_value > 0.05


def test_LM検定は複数の変数を同時に検定できる() -> None:
    df = random_data()
    test = lm_test(df["y"], df[["x1"]], df[["x2"]].assign(x3=df["x2"] ** 2))
    assert test.p_value == pytest.approx(stats.chi2.sf(test.statistic, 2))


def test_歪んだ誤差は平均0で歪度が2に近い() -> None:
    x, y = draw_skewed_sample(100000, 1.0, 0.5, 1.0, np.random.default_rng(0))
    u = y - 1.0 - 0.5 * x
    assert np.mean(u) == pytest.approx(0, abs=0.02)
    assert skewness(u) == pytest.approx(2, abs=0.15)
    assert np.std(u) == pytest.approx(1, abs=0.02)


def test_誤差の大きさで歪んだ誤差も比例する() -> None:
    _, y1 = draw_skewed_sample(1000, 0.0, 0.0, 1.0, np.random.default_rng(1))
    _, y3 = draw_skewed_sample(1000, 0.0, 0.0, 3.0, np.random.default_rng(1))
    assert y3 == pytest.approx(3 * y1)


def test_標本が大きいほど傾きの推定値は真の値に集まる() -> None:
    estimates = consistency_experiment(
        [30, 100, 250, 500], 1000, np.random.default_rng(0)
    )
    assert list(estimates) == [30, 100, 250, 500]
    sds = []
    for n, slopes in estimates.items():
        assert len(slopes) == 1000
        assert slopes.mean() == pytest.approx(0.5, abs=4 * slopes.std() / 1000**0.5)
        assert slopes.std(ddof=1) == pytest.approx(1 / (n - 3) ** 0.5, rel=0.1)
        sds.append(slopes.std(ddof=1))
    assert sds == sorted(sds, reverse=True)


def test_誤差が正規分布ならt値の標準偏差はt分布の理論値に近い() -> None:
    t = t_value_distribution(30, 2000, False, np.random.default_rng(1))
    assert t.mean() == pytest.approx(0, abs=0.1)
    assert t.std() == pytest.approx((28 / 26) ** 0.5, rel=0.05)


def test_標本が大きければ誤差が歪んでいてもt値は標準正規に近い() -> None:
    t = t_value_distribution(500, 2000, True, np.random.default_rng(1))
    assert t.std() == pytest.approx(1, abs=0.05)
    assert np.mean(np.abs(t) > 1.96) == pytest.approx(
        0.05, abs=4 * (0.05 * 0.95 / 2000) ** 0.5
    )


def test_小標本で臨界値1_96を使うと棄却率が超えるがt分布の臨界値なら5パーセントに近い() -> (
    None
):
    critical = stats.t.ppf(0.975, 8)
    for skewed in (False, True):
        t = t_value_distribution(10, 2000, skewed, np.random.default_rng(1))
        assert np.mean(np.abs(t) > 1.96) > 0.07
        assert np.mean(np.abs(t) > critical) == pytest.approx(
            0.05, abs=4 * (0.05 * 0.95 / 2000) ** 0.5
        )


def test_JB検定は歪んだ誤差を棄却し正規の誤差をほとんど棄却しない() -> None:
    skewed = jarque_bera_rejection_rate(100, 500, True, np.random.default_rng(2))
    normal = jarque_bera_rejection_rate(100, 500, False, np.random.default_rng(2))
    assert skewed > 0.95
    assert normal < 0.08


def test_ばらつきのない列では歪度も尖度も計算できない() -> None:
    for function in (skewness, kurtosis):
        with pytest.raises(ValueError, match="ばらつき"):
            function([3.0, 3.0, 3.0])
