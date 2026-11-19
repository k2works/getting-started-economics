"""第 14 章: インパルス反応とシミュレーションの図のテスト。"""

from typing import Any

import numpy as np
import pytest
from matplotlib.lines import Line2D

from lib.chapter13.adas import AdasParameters
from lib.chapter14.plot import plot_impulse_response, plot_simulation
from lib.chapter14.simulation import impulse_response, simulate

PARAMS = AdasParameters(a=0.8, c=0.3, sigma_u=1.5, sigma_v=1.2)


def ys(line: Line2D) -> list[float]:
    data: Any = line.get_ydata()
    return [float(v) for v in data]


def test_インパルス反応の図は産出量と物価と0の線() -> None:
    df = impulse_response(PARAMS, u=1.0)
    ax = plot_impulse_response(df).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Output (y)",
        "Price (p)",
        "Zero",
    ]
    assert ys(ax.lines[0]) == pytest.approx(df["y"].tolist())
    assert ys(ax.lines[1]) == pytest.approx(df["p"].tolist())


def test_0の線は横軸の全体にわたる() -> None:
    df = impulse_response(PARAMS, v=1.0)
    ax = plot_impulse_response(df).axes[0]
    assert ys(ax.lines[2]) == [0, 0]


def test_シミュレーションの図は産出量と物価と0の線() -> None:
    df = simulate(PARAMS, 40, np.random.default_rng(0))
    ax = plot_simulation(df).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Output (y)",
        "Price (p)",
        "Zero",
    ]
    assert ys(ax.lines[0]) == pytest.approx(df["y"].tolist())


def test_0の線は最初の期から最後の期まで() -> None:
    df = impulse_response(PARAMS, v=1.0)
    ax = plot_impulse_response(df).axes[0]
    xs: Any = ax.lines[2].get_xdata()
    assert [float(x) for x in xs] == [0, len(df) - 1]


def test_インパルス反応の図はショックの期を横軸に示す() -> None:
    ax = plot_impulse_response(impulse_response(PARAMS, u=1.0)).axes[0]
    assert ax.get_xlabel() == "Period (shock at period 3)"
