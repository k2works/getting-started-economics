"""第 16 章: 要素分解とシミュレーションの図のテスト。"""

from typing import Any

import numpy as np
import pandas as pd
import pytest
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from lib.chapter16.plot import plot_decomposition, plot_solow_simulation
from lib.chapter16.solow_stochastic import (
    SolowParameters,
    log_deviations,
    stochastic_solow,
)


def data(line: Line2D) -> tuple[list[float], list[float]]:
    xs: Any = line.get_xdata()
    ys: Any = line.get_ydata()
    return [float(x) for x in xs], [float(y) for y in ys]


def test_要素分解の図は3本の棒() -> None:
    shares = pd.Series({"tfp": 0.58, "capital": -0.003, "labour": 0.42})
    ax = plot_decomposition(shares).axes[0]
    heights = [p.get_height() for p in ax.patches if isinstance(p, Rectangle)]
    assert heights == pytest.approx([0.58, -0.003, 0.42])
    assert [t.get_text() for t in ax.get_xticklabels()] == ["tfp", "capital", "labour"]


def test_要素分解の図の縦軸の名前() -> None:
    shares = pd.Series({"tfp": 0.5, "capital": 0.1, "labour": 0.4})
    ax = plot_decomposition(shares).axes[0]
    assert ax.get_ylabel() == "Share of GDP variance"


def test_シミュレーションの図は3つの変数と0の線() -> None:
    params = SolowParameters()
    dev = log_deviations(stochastic_solow(params, 30, np.random.default_rng(0)), params)
    ax = plot_solow_simulation(dev).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "TFP (a)",
        "Output (y)",
        "Capital (k)",
        "Zero",
    ]
    assert data(ax.lines[1])[1] == pytest.approx(dev["y"].tolist())
    assert data(ax.lines[3]) == ([0, 29], [0, 0])


def test_シミュレーションの図の軸の名前() -> None:
    params = SolowParameters()
    dev = log_deviations(stochastic_solow(params, 10, np.random.default_rng(0)), params)
    ax = plot_solow_simulation(dev).axes[0]
    assert ax.get_xlabel() == "Period"
    assert ax.get_ylabel() == "Deviation from steady state (%)"


def test_要素分解の図は0の線を引く() -> None:
    shares = pd.Series({"tfp": 0.5, "capital": 0.1, "labour": 0.4})
    ax = plot_decomposition(shares).axes[0]
    assert len(ax.lines) == 1
    ys: Any = ax.lines[0].get_ydata()
    assert [float(y) for y in ys] == [0, 0]
