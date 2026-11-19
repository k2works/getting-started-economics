"""第 6 章: 収斂の図のテスト。"""

from typing import Any

import pandas as pd
import pytest
from matplotlib.lines import Line2D

from lib.chapter06.plot import plot_beta_over_time


def xy(line: Line2D) -> list[tuple[float, float]]:
    data: Any = line.get_xydata()
    return [(float(x), float(y)) for x, y in data]


def series() -> pd.Series:
    return pd.Series([-0.5, -0.8, -1.0], index=[1990, 1991, 1992])


def test_傾きの推移の図は傾きの線と0の線() -> None:
    ax = plot_beta_over_time(series()).axes[0]
    assert [line.get_label() for line in ax.lines] == ["Beta", "Zero"]


def test_傾きの点は開始年と傾きの組() -> None:
    ax = plot_beta_over_time(series()).axes[0]
    assert xy(ax.lines[0]) == [
        pytest.approx((1990, -0.5)),
        pytest.approx((1991, -0.8)),
        pytest.approx((1992, -1.0)),
    ]


def test_0の線は開始年の端から端まで() -> None:
    ax = plot_beta_over_time(series()).axes[0]
    assert xy(ax.lines[1]) == [(1990, 0), (1992, 0)]
