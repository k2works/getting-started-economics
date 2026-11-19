"""第 2 章: 単回帰分析（最小二乗法）のテスト。"""

import numpy as np
import pytest
import statsmodels.api as sm

from lib.chapter02.simple import (
    SimpleFit,
    draw_sample,
    fit_simple,
    fitted_values,
    r_squared,
    residuals,
    sampling_distribution,
    slope_standard_error,
)

X = [1, 2, 3, 4]
Y = [2, 4, 5, 9]


def test_手計算の例の傾きと切片() -> None:
    fit = fit_simple(X, Y)
    assert fit.slope == pytest.approx(2.2)
    assert fit.intercept == pytest.approx(-0.5)


def test_直線上のデータは傾きと切片を復元する() -> None:
    x = [0, 1, 2, 5]
    fit = fit_simple(x, [3 + 2 * v for v in x])
    assert isinstance(fit, SimpleFit)
    assert fit.intercept == pytest.approx(3)
    assert fit.slope == pytest.approx(2)


def test_当てはめ値と残差() -> None:
    fit = fit_simple(X, Y)
    assert fitted_values(fit, X) == pytest.approx([1.7, 3.9, 6.1, 8.3])
    assert residuals(fit, X, Y) == pytest.approx([0.3, 0.1, -1.1, 0.7])


def test_残差の和は0で説明変数と直交する() -> None:
    fit = fit_simple(X, Y)
    e = residuals(fit, X, Y)
    assert np.sum(e) == pytest.approx(0, abs=1e-12)
    assert np.sum(np.asarray(X) * e) == pytest.approx(0, abs=1e-12)


def test_残差平方和と決定係数() -> None:
    fit = fit_simple(X, Y)
    e = residuals(fit, X, Y)
    assert np.sum(e**2) == pytest.approx(1.8)
    assert r_squared(fit, X, Y) == pytest.approx(1 - 1.8 / 26)


def test_全平方和は説明される部分と残差平方和の和() -> None:
    fit = fit_simple(X, Y)
    y = np.asarray(Y, dtype=float)
    total = np.sum((y - y.mean()) ** 2)
    explained = np.sum((fitted_values(fit, X) - y.mean()) ** 2)
    unexplained = np.sum(residuals(fit, X, Y) ** 2)
    assert total == pytest.approx(explained + unexplained)


def test_直線上のデータの決定係数は1() -> None:
    fit = fit_simple(X, [1 + 3 * v for v in X])
    assert r_squared(fit, X, [1 + 3 * v for v in X]) == pytest.approx(1)


def test_傾きの標準誤差() -> None:
    fit = fit_simple(X, Y)
    assert slope_standard_error(fit, X, Y) == pytest.approx((0.9 / 5) ** 0.5)


def test_観測値が2個では標準誤差は計算できない() -> None:
    fit = fit_simple([1, 2], [1, 3])
    with pytest.raises(ValueError, match="自由度"):
        slope_standard_error(fit, [1, 2], [1, 3])


def test_説明変数にばらつきがないと推定できない() -> None:
    with pytest.raises(ValueError, match="分散が 0"):
        fit_simple([2, 2, 2], [1, 2, 3])


def test_statsmodelsと一致する() -> None:
    x, y = draw_sample(30, 1.0, 0.5, 1.0, np.random.default_rng(0))
    fit = fit_simple(x, y)
    reference = sm.OLS(y, sm.add_constant(x)).fit()
    assert [fit.intercept, fit.slope] == pytest.approx(reference.params)
    assert slope_standard_error(fit, x, y) == pytest.approx(reference.bse[1])
    assert r_squared(fit, x, y) == pytest.approx(reference.rsquared)


def test_標本は長さnで同じ種なら同じ() -> None:
    x1, y1 = draw_sample(10, 1.0, 2.0, 1.0, np.random.default_rng(3))
    x2, y2 = draw_sample(10, 1.0, 2.0, 1.0, np.random.default_rng(3))
    assert x1.shape == y1.shape == (10,)
    assert np.array_equal(x1, x2)
    assert np.array_equal(y1, y2)


def test_誤差が0なら母集団の式の上に乗る() -> None:
    x, y = draw_sample(10, 1.0, 2.0, 0.0, np.random.default_rng(0))
    assert y == pytest.approx(1.0 + 2.0 * x)


def test_標本分布の表の形() -> None:
    table = sampling_distribution(
        n=20,
        repetitions=50,
        intercept=1,
        slope=0.5,
        sigma=1,
        rng=np.random.default_rng(0),
    )
    assert list(table.columns) == ["intercept", "slope", "se"]
    assert len(table) == 50


def test_傾きの推定値は不偏() -> None:
    table = sampling_distribution(
        n=50,
        repetitions=2000,
        intercept=1,
        slope=0.5,
        sigma=1,
        rng=np.random.default_rng(0),
    )
    spread = 1 / (50 - 3) ** 0.5
    assert table["slope"].mean() == pytest.approx(0.5, abs=4 * spread / 2000**0.5)
    assert table["intercept"].mean() == pytest.approx(1.0, abs=0.02)


def test_傾きのばらつきは理論値に近く標準誤差の平均と一致する() -> None:
    table = sampling_distribution(
        n=50,
        repetitions=2000,
        intercept=1,
        slope=0.5,
        sigma=1,
        rng=np.random.default_rng(0),
    )
    assert table["slope"].std() == pytest.approx(1 / 47**0.5, rel=0.1)
    assert table["se"].mean() == pytest.approx(table["slope"].std(), rel=0.1)


def test_誤差が大きいほど傾きはばらつく() -> None:
    small = sampling_distribution(30, 500, 1, 0.5, 1, np.random.default_rng(1))
    large = sampling_distribution(30, 500, 1, 0.5, 3, np.random.default_rng(1))
    assert large["slope"].std() == pytest.approx(3 * small["slope"].std(), rel=1e-9)
