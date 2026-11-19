"""第 17 章: 厳密な経路と線形近似の図のテスト。"""

from typing import Any

import pytest
from matplotlib.lines import Line2D

from lib.chapter16.solow_stochastic import SolowParameters
from lib.chapter17.loglinear import capital_paths
from lib.chapter17.plot import plot_exact_vs_linear


def values(line: Line2D) -> tuple[list[float], list[float]]:
    xs: Any = line.get_xdata()
    ys: Any = line.get_ydata()
    return [float(x) for x in xs], [float(y) for y in ys]


def test_図は厳密な経路と近似の経路と0の線() -> None:
    df = capital_paths(SolowParameters(), initial_deviation=0.5, periods=20)
    ax = plot_exact_vs_linear(df).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Exact",
        "Linear approximation",
        "Zero",
    ]
    assert values(ax.lines[0])[1] == pytest.approx(df["exact"].tolist())
    assert values(ax.lines[1])[1] == pytest.approx(df["linear"].tolist())
    assert values(ax.lines[2]) == ([0, 20], [0, 0])


def test_近似の経路は点線で描く() -> None:
    df = capital_paths(SolowParameters(), initial_deviation=0.5, periods=5)
    ax = plot_exact_vs_linear(df).axes[0]
    assert [line.get_linestyle() for line in ax.lines] == ["-", ":", "--"]


def test_図の軸の名前() -> None:
    df = capital_paths(SolowParameters(), initial_deviation=0.5, periods=5)
    ax = plot_exact_vs_linear(df).axes[0]
    assert ax.get_xlabel() == "Period"
    assert ax.get_ylabel() == "Capital, deviation from steady state (%)"
