"""第 9 章: トレンドと景気循環のテスト。

HP フィルターは、直線のトレンドを、そのまま残す（循環は 0）。
log_cycle は、対数のトレンドからの乖離（%）で、毎期同じ率で伸びる系列なら 0。
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm

from lib.chapter09.cycles import (
    cross_correlation,
    cycle,
    cycle_statistics,
    hp_trend,
    load_quarterly,
    log_cycle,
    relative_volatility,
    volatility,
)


def series(values: list[float]) -> pd.Series:
    return pd.Series(values, dtype=float)


def test_直線の系列のHPトレンドは系列そのもの() -> None:
    x = series([1.0 + 2 * t for t in range(20)])
    assert hp_trend(x).to_numpy() == pytest.approx(x.to_numpy())


def test_定数の系列のトレンドは定数() -> None:
    x = series([5.0] * 10)
    assert hp_trend(x).to_numpy() == pytest.approx(5.0)


def test_HPフィルターはstatsmodelsの結果と一致する() -> None:
    rng = np.random.default_rng(0)
    x = pd.Series(np.cumsum(rng.normal(0.5, 1.0, 120)))
    theirs_cycle, theirs_trend = sm.tsa.filters.hpfilter(x, lamb=1600)
    assert hp_trend(x, 1600).to_numpy() == pytest.approx(theirs_trend.to_numpy())
    assert cycle(x, 1600).to_numpy() == pytest.approx(theirs_cycle.to_numpy())


def test_循環の平均は0() -> None:
    rng = np.random.default_rng(1)
    x = pd.Series(np.cumsum(rng.normal(0.5, 1.0, 80)))
    assert cycle(x).mean() == pytest.approx(0, abs=1e-9)


def test_平滑化の強さを大きくするとトレンドは直線に近づく() -> None:
    rng = np.random.default_rng(2)
    x = pd.Series(np.cumsum(rng.normal(0.5, 1.0, 60)))
    t = np.arange(60)
    slope, intercept = np.polyfit(t, x.to_numpy(), 1)
    line = intercept + slope * t
    smooth = hp_trend(x, 1e9).to_numpy()
    rough = hp_trend(x, 1.0).to_numpy()
    assert np.abs(smooth - line).max() < np.abs(rough - line).max()
    assert smooth == pytest.approx(line, abs=0.01)


def test_系列の長さが3未満ならトレンドは求められない() -> None:
    with pytest.raises(ValueError, match="長さ"):
        hp_trend(series([1.0, 2.0]))


def test_平滑化の強さは正でなければならない() -> None:
    with pytest.raises(ValueError, match="平滑化"):
        hp_trend(series([1.0, 2.0, 3.0]), 0)


def test_行の名前はそのまま引き継ぐ() -> None:
    x = pd.Series([1.0, 2.0, 3.0, 4.0], index=list("abcd"))
    assert list(hp_trend(x).index) == list("abcd")


def test_毎期同じ率で伸びる系列の対数の循環は0() -> None:
    x = series([100 * 1.01**t for t in range(40)])
    assert log_cycle(x).to_numpy() == pytest.approx(0, abs=1e-9)


def test_対数の循環は対数のトレンドからの乖離のパーセント() -> None:
    x = series([100 * 1.01**t for t in range(40)])
    x.iloc[20] *= 1.05
    result = log_cycle(x)
    assert result.iloc[20] > 3.5
    assert result.iloc[20] == result.max()


def test_標準偏差を手計算と比べる() -> None:
    # 1、2、3、4 の標本の標準偏差 = √(5 ÷ 3)
    assert volatility(series([1, 2, 3, 4])) == pytest.approx(np.sqrt(5 / 3))


def test_相対的な変動の大きさ() -> None:
    x = series([1, 2, 3, 4])
    assert relative_volatility(3 * x, x) == pytest.approx(3)


def test_同じ系列の相関は1で逆向きの系列は負1() -> None:
    x = series([1, 3, 2, 5, 4, 6])
    assert cross_correlation(x, x) == pytest.approx(1)
    assert cross_correlation(x, -x) == pytest.approx(-1)


def test_ラグを指定すると系列をずらして相関を求める() -> None:
    x = series([0, 1, 0, -1, 0, 1, 0, -1])
    y = x.shift(1)  # y(t) = x(t−1)
    assert cross_correlation(x, y, lag=-1) == pytest.approx(1)
    assert cross_correlation(x, y, lag=0) == pytest.approx(0, abs=1e-9)


def test_CSVを読むと四半期の期間が行の名前になる(tmp_path: Path) -> None:
    path = tmp_path / "q.csv"
    path.write_text(
        "year,quarter,gdp,consumption,investment,unemployment,inflation\n"
        "2000,1,100,60,20,4.0,2.0\n2000,2,101,61,21,4.1,2.1\n",
        encoding="utf-8",
    )
    df = load_quarterly(path)
    assert str(df.index[0]) == "2000Q1"
    assert str(df.index[1]) == "2000Q2"
    assert list(df.columns) == [
        "gdp",
        "consumption",
        "investment",
        "unemployment",
        "inflation",
    ]


def test_同梱のデータは1980年から2019年までの160四半期() -> None:
    df = load_quarterly()
    assert len(df) == 160
    assert str(df.index[0]) == "1980Q1"
    assert str(df.index[-1]) == "2019Q4"


def test_循環の統計は変数ごとの行() -> None:
    stats = cycle_statistics(load_quarterly())
    assert list(stats.index) == [
        "gdp",
        "consumption",
        "investment",
        "unemployment",
        "inflation",
    ]
    assert list(stats.columns) == [
        "volatility",
        "relative_to_gdp",
        "correlation_with_gdp",
        "autocorrelation",
    ]


def test_GDP自身の相対的な変動は1で相関は1() -> None:
    stats = cycle_statistics(load_quarterly())
    assert stats.loc["gdp", "relative_to_gdp"] == pytest.approx(1)
    assert stats.loc["gdp", "correlation_with_gdp"] == pytest.approx(1)


def test_投資は消費より変動が大きい() -> None:
    stats = cycle_statistics(load_quarterly())
    relative = stats["relative_to_gdp"]
    assert float(relative["investment"]) > float(relative["consumption"])


def test_失業率の循環はGDPの循環と逆に動く() -> None:
    stats = cycle_statistics(load_quarterly())
    assert float(stats["correlation_with_gdp"]["unemployment"]) < -0.9


def test_同梱のデータの循環の統計の値() -> None:
    stats = cycle_statistics(load_quarterly())
    assert stats["volatility"]["gdp"] == pytest.approx(1.008, abs=0.001)
    assert stats["relative_to_gdp"]["investment"] == pytest.approx(3.686, abs=0.001)
    assert stats["relative_to_gdp"]["consumption"] == pytest.approx(0.761, abs=0.001)
    assert stats["correlation_with_gdp"]["unemployment"] == pytest.approx(
        -0.963, abs=0.001
    )
    assert stats["autocorrelation"]["gdp"] == pytest.approx(0.623, abs=0.001)
