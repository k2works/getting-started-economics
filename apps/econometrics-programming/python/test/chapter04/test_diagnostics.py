"""第 4 章: 残差診断（標準化残差・てこ比・クックの距離・Q-Q）のテスト。"""

import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.outliers_influence import OLSInfluence

from lib.chapter01.statistics import sample_correlation, sample_variance
from lib.chapter02.simple import fit_simple
from lib.chapter03.multiple import fit_ols, leverage
from lib.chapter04.diagnostics import (
    cooks_distance,
    match_moments,
    qq_points,
    same_summary_datasets,
    standardized_residuals,
    studentized_residuals,
)

X = [1, 2, 3, 4]
Y = [2, 4, 5, 9]


def random_data(n: int = 40, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    x1 = rng.standard_normal(n)
    x2 = 0.5 * x1 + rng.standard_normal(n)
    y = 1 + 2 * x1 - x2 + rng.standard_normal(n)
    return pd.DataFrame({"y": y, "x1": x1, "x2": x2})


def test_標準化残差は残差を誤差の標準偏差の推定値で割る() -> None:
    result = fit_ols(Y, X)
    z = standardized_residuals(result)
    assert z == pytest.approx(np.array([0.3, 0.1, -1.1, 0.7]) / 0.9**0.5)


def test_手計算の例のてこ比() -> None:
    assert leverage(X) == pytest.approx([0.7, 0.3, 0.3, 0.7])


def test_手計算の例のスチューデント化残差とクックの距離() -> None:
    result = fit_ols(Y, X)
    h = leverage(X)
    r = studentized_residuals(result, h)
    assert r[0] == pytest.approx(0.3 / (0.9**0.5 * 0.3**0.5))
    assert cooks_distance(result, h)[0] == pytest.approx(r[0] ** 2 / 2 * 0.7 / 0.3)


def test_スチューデント化残差とクックの距離はstatsmodelsと一致する() -> None:
    df = random_data()
    x = df[["x1", "x2"]]
    result = fit_ols(df["y"], x)
    h = leverage(x)
    influence = OLSInfluence(sm.OLS(df["y"], sm.add_constant(x)).fit())
    assert studentized_residuals(result, h) == pytest.approx(
        influence.resid_studentized_internal
    )
    assert cooks_distance(result, h) == pytest.approx(influence.cooks_distance[0])


def test_Q_Qの点は小さい順で理論分位点と対応する() -> None:
    values = [3.0, -1.0, 0.5, 2.0]
    theoretical, ordered = qq_points(values)
    assert ordered.tolist() == sorted(
        (np.asarray(values) - np.mean(values)) / np.std(values, ddof=1)
    )
    assert theoretical == pytest.approx(stats.norm.ppf([0.125, 0.375, 0.625, 0.875]))


def test_正規乱数のQ_Q点はほぼ1本の直線上にある() -> None:
    values = np.random.default_rng(0).standard_normal(500)
    theoretical, ordered = qq_points(values)
    assert sample_correlation(theoretical, ordered) > 0.99
    assert fit_simple(theoretical, ordered).slope == pytest.approx(1, abs=0.05)


def test_モーメントをそろえると平均と標準偏差と相関が指定どおり() -> None:
    x, y = match_moments(
        np.arange(6.0), [1.0, 3.0, 2.0, 5.0, 4.0, 4.5], (9, 7.5), (3.3, 2.0), 0.8
    )
    assert np.mean(x) == pytest.approx(9)
    assert np.mean(y) == pytest.approx(7.5)
    assert sample_variance(x) ** 0.5 == pytest.approx(3.3)
    assert sample_variance(y) ** 0.5 == pytest.approx(2.0)
    assert sample_correlation(x, y) == pytest.approx(0.8)


def test_形が説明変数と完全に比例していると相関を指定できない() -> None:
    with pytest.raises(ValueError, match="比例"):
        match_moments([1.0, 2.0, 3.0], [2.0, 4.0, 6.0], (0, 0), (1, 1), 0.5)


def test_4組のデータは要約統計量がすべて同じ() -> None:
    datasets = same_summary_datasets()
    assert list(datasets) == ["linear", "curved", "outlier", "clustered"]
    for x, y in datasets.values():
        assert len(x) == len(y) == 11
        assert np.mean(x) == pytest.approx(9)
        assert np.mean(y) == pytest.approx(7.5)
        assert sample_variance(x) ** 0.5 == pytest.approx(3.3)
        assert sample_variance(y) ** 0.5 == pytest.approx(2.0)
        assert sample_correlation(x, y) == pytest.approx(0.8)
        fit = fit_simple(x, y)
        assert fit.slope == pytest.approx(0.8 * 2.0 / 3.3)
        assert fit.intercept == pytest.approx(7.5 - 0.8 * 2.0 / 3.3 * 9)


def test_4組のデータは要約統計量が同じでもクックの距離が違う() -> None:
    maxima = {}
    for name, (x, y) in same_summary_datasets().items():
        result = fit_ols(y, x)
        maxima[name] = cooks_distance(result, leverage(x)).max()
    assert maxima["outlier"] > 5 * maxima["linear"]
    assert maxima["outlier"] > 1
