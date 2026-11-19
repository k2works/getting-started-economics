"""第 5 章: 推論（t 検定・p 値・信頼区間・F 検定）のテスト。"""

import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm
from scipy import stats

from lib.chapter03.multiple import fit_ols
from lib.chapter05.inference import (
    TestResult,
    confidence_interval,
    coverage_rate,
    f_test,
    p_value,
    rejection_rate,
    slope_intervals,
    t_statistics,
)

X = [1, 2, 3, 4]
Y = [2, 4, 5, 9]


def random_data(n: int = 40, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    x1 = rng.standard_normal(n)
    x2 = 0.5 * x1 + rng.standard_normal(n)
    y = 1 + 2 * x1 - x2 + rng.standard_normal(n)
    return pd.DataFrame({"y": y, "x1": x1, "x2": x2})


def test_手計算の例のt値() -> None:
    t = t_statistics(fit_ols(Y, X))
    assert t["x1"] == pytest.approx(2.2 / 0.18**0.5)
    assert t["const"] == pytest.approx(-0.5 / 1.35**0.5)


def test_帰無仮説の値を変えるとt値が変わる() -> None:
    result = fit_ols(Y, X)
    t = t_statistics(result, null=2.0)
    assert t["x1"] == pytest.approx(0.2 / 0.18**0.5)


def test_p値は両側と片側で関係する() -> None:
    two = p_value(5.185, 2)
    assert two == pytest.approx(2 * stats.t.sf(5.185, 2))
    assert p_value(5.185, 2, "greater") == pytest.approx(two / 2)
    assert p_value(-5.185, 2, "less") == pytest.approx(two / 2)
    assert p_value(5.185, 2, "less") == pytest.approx(1 - two / 2)


def test_t値が0ならp値は1と半分() -> None:
    assert p_value(0, 10) == pytest.approx(1)
    assert p_value(0, 10, "greater") == pytest.approx(0.5)


def test_知らない対立仮説は受け付けない() -> None:
    with pytest.raises(ValueError, match="対立仮説"):
        p_value(1, 10, "bigger")


def test_手計算の例の信頼区間() -> None:
    interval = confidence_interval(fit_ols(Y, X))
    half = 4.302653 * 0.18**0.5
    assert interval.loc["x1", "lower"] == pytest.approx(2.2 - half, abs=1e-5)
    assert interval.loc["x1", "upper"] == pytest.approx(2.2 + half, abs=1e-5)


def test_信頼区間はstatsmodelsと一致する() -> None:
    df = random_data()
    x = df[["x1", "x2"]]
    interval = confidence_interval(fit_ols(df["y"], x), level=0.9)
    reference = sm.OLS(df["y"], sm.add_constant(x)).fit().conf_int(alpha=0.1)
    assert interval.to_numpy() == pytest.approx(reference.to_numpy())


def test_水準が高いほど区間は広い() -> None:
    result = fit_ols(Y, X)
    narrow = confidence_interval(result, 0.9).loc["x1"]
    wide = confidence_interval(result, 0.99).loc["x1"]
    assert wide["upper"] - wide["lower"] > narrow["upper"] - narrow["lower"]


def test_制約が1つならFはtの2乗でp値も一致する() -> None:
    result = fit_ols(Y, X)
    test = f_test(Y, pd.DataFrame({"x": X}), ["x"])
    t = t_statistics(result)["x1"]
    assert test.statistic == pytest.approx(t**2)
    assert test.statistic == pytest.approx(24.2 / 0.9)
    assert test.p_value == pytest.approx(p_value(t, 2))


def test_複数の制約のF検定はstatsmodelsと一致する() -> None:
    df = random_data()
    test = f_test(df["y"], df[["x1", "x2"]], ["x1", "x2"])
    full = sm.OLS(df["y"], sm.add_constant(df[["x1", "x2"]])).fit()
    assert test.statistic == pytest.approx(full.fvalue)
    assert test.p_value == pytest.approx(full.f_pvalue)


def test_一部の制約のF検定はstatsmodelsと一致する() -> None:
    df = random_data()
    test = f_test(df["y"], df[["x1", "x2"]], ["x2"])
    full = sm.OLS(df["y"], sm.add_constant(df[["x1", "x2"]])).fit()
    restricted = sm.OLS(df["y"], sm.add_constant(df[["x1"]])).fit()
    statistic, p, _ = full.compare_f_test(restricted)
    assert isinstance(test, TestResult)
    assert test.statistic == pytest.approx(statistic)
    assert test.p_value == pytest.approx(p)


def test_傾きの信頼区間を繰り返し作る() -> None:
    table = slope_intervals(30, 20, 0.95, np.random.default_rng(0))
    assert list(table.columns) == ["lower", "upper"]
    assert len(table) == 20
    assert (table["lower"] < table["upper"]).all()


def test_信頼区間の被覆率は区間の表から数えた割合と一致する() -> None:
    table = slope_intervals(30, 200, 0.95, np.random.default_rng(5))
    expected = ((table["lower"] <= 0.5) & (0.5 <= table["upper"])).mean()
    assert coverage_rate(30, 200, 0.95, np.random.default_rng(5)) == expected


def test_信頼区間の被覆率は水準に近い() -> None:
    rate = coverage_rate(30, 2000, 0.95, np.random.default_rng(0))
    assert rate == pytest.approx(0.95, abs=4 * (0.95 * 0.05 / 2000) ** 0.5)


def test_水準を下げると被覆率も下がる() -> None:
    rate = coverage_rate(30, 2000, 0.8, np.random.default_rng(0))
    assert rate == pytest.approx(0.8, abs=4 * (0.8 * 0.2 / 2000) ** 0.5)


def test_帰無仮説が正しいときの棄却率は有意水準に近い() -> None:
    rate = rejection_rate(30, 2000, 0.5, 0.5, 0.05, np.random.default_rng(0))
    assert rate == pytest.approx(0.05, abs=4 * (0.05 * 0.95 / 2000) ** 0.5)


def test_帰無仮説が誤っているほど棄却率は高い() -> None:
    near = rejection_rate(30, 1000, 0.5, 0.3, 0.05, np.random.default_rng(0))
    far = rejection_rate(30, 1000, 0.5, 0.0, 0.05, np.random.default_rng(0))
    assert far > near > 0.05
    assert far > 0.5


def test_検定する列がなければF検定はできない() -> None:
    x = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0, 6.0, 7.0]})
    with pytest.raises(ValueError, match="検定する列"):
        f_test([1.0, 3.0, 2.0, 5.0, 4.0, 7.0], x, [])
