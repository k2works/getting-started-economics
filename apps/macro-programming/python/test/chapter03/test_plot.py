"""第 3 章: 回帰の図のテスト。"""

from typing import Any

import numpy as np
import pandas as pd
import pytest
from matplotlib.lines import Line2D

from lib.chapter01.accounting import load_countries
from lib.chapter03.plot import plot_regression
from lib.chapter03.regression import fit_ols


def xy(line: Line2D) -> list[tuple[float, float]]:
    data: Any = line.get_xydata()
    return [(float(x), float(y)) for x, y in data]


def data() -> tuple[pd.Series, pd.Series]:
    df = load_countries()
    return np.log(df["k"]), np.log(df["y"])


def test_回帰の図は点と回帰直線の2本() -> None:
    x, y = data()
    ax = plot_regression(x, y).axes[0]
    assert [line.get_label() for line in ax.lines] == ["Countries", "OLS line"]


def test_点はxとyの組() -> None:
    x, y = data()
    ax = plot_regression(x, y).axes[0]
    points = xy(ax.lines[0])
    assert len(points) == 24
    assert points[0] == pytest.approx((x.iloc[0], y.iloc[0]))


def test_回帰直線の傾きは最小二乗法の傾き() -> None:
    x, y = data()
    ax = plot_regression(x, y).axes[0]
    (x0, y0), (x1, y1) = xy(ax.lines[1])
    result = fit_ols(y, pd.DataFrame({"x": x}))
    assert (y1 - y0) / (x1 - x0) == pytest.approx(result.coefficients["x"])
    assert y0 == pytest.approx(
        result.coefficients["const"] + result.coefficients["x"] * x0
    )


def test_点の名前を指定できる() -> None:
    x, y = data()
    ax = plot_regression(x, y, label="Quarters").axes[0]
    assert ax.lines[0].get_label() == "Quarters"


def test_軸の名前を指定できる() -> None:
    x, y = data()
    ax = plot_regression(x, y, xlabel="ln k", ylabel="ln y").axes[0]
    assert ax.get_xlabel() == "ln k"
    assert ax.get_ylabel() == "ln y"
