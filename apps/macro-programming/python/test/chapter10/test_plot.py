"""第 10 章: オークンの法則とフィリップス曲線の図のテスト。"""

from typing import Any

import pandas as pd
import pytest

from lib.chapter10.plot import plot_rolling_slope


def test_傾きの推移の図は傾きの線と0の線() -> None:
    slopes = pd.Series([-0.5, -0.4, -0.2], index=pd.period_range("2000Q1", periods=3))
    ax = plot_rolling_slope(slopes).axes[0]
    assert [line.get_label() for line in ax.lines] == ["Slope", "Zero"]


def test_傾きの点は窓の順番と傾き() -> None:
    slopes = pd.Series([-0.5, -0.4, -0.2], index=pd.period_range("2000Q1", periods=3))
    ax = plot_rolling_slope(slopes).axes[0]
    ydata: Any = ax.lines[0].get_ydata()
    assert [float(y) for y in ydata] == pytest.approx([-0.5, -0.4, -0.2])


def test_0の線は高さ0() -> None:
    slopes = pd.Series([-0.5, -0.4, -0.2], index=pd.period_range("2000Q1", periods=3))
    ax = plot_rolling_slope(slopes).axes[0]
    ydata: Any = ax.lines[1].get_ydata()
    assert [float(y) for y in ydata] == [0.0, 0.0]
