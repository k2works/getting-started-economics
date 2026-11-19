"""第 10 章: オークンの法則とフィリップス曲線のテスト。

オークンの法則: 失業率の循環 = c + β × GDP の循環（β < 0）。
フィリップス曲線: 物価上昇率 = c + β × 失業率の循環（β < 0）。
"""

import numpy as np
import pandas as pd
import pytest

from lib.chapter09.cycles import load_quarterly
from lib.chapter10.okun_phillips import (
    okun_regression,
    okun_regression_from_data,
    phillips_by_period,
    phillips_regression,
    phillips_regression_from_data,
    rolling_slope,
)


def exact_series(slope: float, intercept: float = 0.0) -> tuple[pd.Series, pd.Series]:
    x = pd.Series([-2.0, -1.0, 0.0, 1.0, 2.0, 1.5, -0.5, 0.5])
    return intercept + slope * x, x


def test_ちょうどの関係を満たすデータでオークンの係数を復元できる() -> None:
    u, g = exact_series(-0.5)
    result = okun_regression(u, g)
    assert result.coefficients["output_cycle"] == pytest.approx(-0.5)
    assert result.coefficients["const"] == pytest.approx(0)
    assert result.r_squared == pytest.approx(1)


def test_ちょうどの関係を満たすデータでフィリップス曲線の傾きを復元できる() -> None:
    pi, gap = exact_series(-0.4, intercept=2.0)
    result = phillips_regression(pi, gap)
    assert result.coefficients["unemployment_gap"] == pytest.approx(-0.4)
    assert result.coefficients["const"] == pytest.approx(2.0)


def test_同梱のデータのオークンの係数は負() -> None:
    result = okun_regression_from_data(load_quarterly())
    assert result.coefficients["output_cycle"] < -0.4
    assert result.t_values()["output_cycle"] < -20


def test_同梱のデータのオークンの係数の値() -> None:
    result = okun_regression_from_data(load_quarterly())
    assert result.coefficients["output_cycle"] == pytest.approx(-0.496, abs=0.002)
    assert result.r_squared == pytest.approx(0.927, abs=0.005)
    assert result.n_obs == 160


def test_同梱のデータのフィリップス曲線の傾きは負() -> None:
    result = phillips_regression_from_data(load_quarterly())
    assert result.coefficients["unemployment_gap"] < 0
    assert result.t_values()["unemployment_gap"] < -3


def test_期間を分けるとフィリップス曲線は後半で平らになる() -> None:
    parts = phillips_by_period(load_quarterly(), split_year=2000)
    before = parts["before"].coefficients["unemployment_gap"]
    after = parts["after"].coefficients["unemployment_gap"]
    assert before < after < 0
    assert abs(before) > 2 * abs(after) * 0.8


def test_期間を分けたフィリップス曲線の傾きの値() -> None:
    parts = phillips_by_period(load_quarterly(), split_year=2000)
    assert parts["before"].coefficients["unemployment_gap"] == pytest.approx(
        -0.571, abs=0.005
    )
    assert parts["after"].coefficients["unemployment_gap"] == pytest.approx(
        -0.161, abs=0.005
    )


def test_期間を分ける年は範囲の内側でなければならない() -> None:
    with pytest.raises(ValueError, match="年"):
        phillips_by_period(load_quarterly(), split_year=1980)
    with pytest.raises(ValueError, match="年"):
        phillips_by_period(load_quarterly(), split_year=2030)


def test_期間を分けた観測数の合計は全体と等しい() -> None:
    df = load_quarterly()
    parts = phillips_by_period(df, split_year=2000)
    assert parts["before"].n_obs + parts["after"].n_obs == len(df)


def test_窓をずらした傾きの数は系列の長さ引く窓の幅足す1() -> None:
    u, g = exact_series(-0.5)
    slopes = rolling_slope(g, u, window=4)
    assert len(slopes) == 8 - 4 + 1


def test_窓をずらした傾きはちょうどの関係なら常に同じ() -> None:
    u, g = exact_series(-0.5)
    assert rolling_slope(g, u, window=4).to_numpy() == pytest.approx(-0.5)


def test_最初の窓の傾きは直接回帰した傾きと一致する() -> None:
    rng = np.random.default_rng(0)
    x = pd.Series(rng.normal(size=30))
    y = pd.Series(-0.3 * x + rng.normal(0, 0.1, 30))
    first = rolling_slope(x, y, window=10).iloc[0]
    direct = okun_regression(
        y.iloc[:10].reset_index(drop=True), x.iloc[:10].reset_index(drop=True)
    )
    assert first == pytest.approx(direct.coefficients["output_cycle"])


def test_窓の幅は3以上で系列の長さ以下でなければならない() -> None:
    u, g = exact_series(-0.5)
    with pytest.raises(ValueError, match="窓"):
        rolling_slope(g, u, window=2)
    with pytest.raises(ValueError, match="窓"):
        rolling_slope(g, u, window=9)


def test_窓をずらした傾きの行の名前は窓の最後の時点() -> None:
    df = load_quarterly()
    slopes = rolling_slope(
        pd.Series(df["unemployment"]), pd.Series(df["inflation"]), window=40
    )
    assert str(slopes.index[0]) == "1989Q4"
    assert str(slopes.index[-1]) == "2019Q4"


def test_最後の年で分けても後半は4四半期だけで回帰できる() -> None:
    parts = phillips_by_period(load_quarterly(), split_year=2019)
    assert parts["after"].n_obs == 4


def test_窓の幅が系列の長さと同じなら傾きは1つ() -> None:
    u, g = exact_series(-0.5)
    assert len(rolling_slope(g, u, window=8)) == 1
