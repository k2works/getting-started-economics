"""第 16 章: 標本選択と、OLS・ヘックマンの直線の図のテスト。"""

from typing import Any

import numpy as np
import pytest

from lib.chapter03.multiple import fit_ols
from lib.chapter16.heckit import draw_selection_sample, heckit_two_step
from lib.chapter16.plot import plot_selection


def xs(line: Any) -> list[float]:
    values: Any = line.get_xdata()
    return [float(v) for v in values]


def ys(line: Any) -> list[float]:
    values: Any = line.get_ydata()
    return [float(v) for v in values]


def slope(line: Any) -> float:
    x, y = xs(line), ys(line)
    return (y[1] - y[0]) / (x[1] - x[0])


def test_選択されたデータと3本の直線() -> None:
    df = draw_selection_sample(3000, 0.7, np.random.default_rng(0))
    ax = plot_selection(df).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Selected",
        "True line",
        "OLS (selected)",
        "Heckit",
    ]
    chosen = df[df["selected"] == 1]
    assert len(xs(ax.lines[0])) == len(chosen)


def test_直線の傾き() -> None:
    df = draw_selection_sample(3000, 0.7, np.random.default_rng(0))
    ax = plot_selection(df).axes[0]
    chosen = df[df["selected"] == 1]
    assert slope(ax.lines[1]) == pytest.approx(2)
    assert slope(ax.lines[2]) == pytest.approx(
        fit_ols(chosen["y"], chosen[["x"]]).coefficients["x"]
    )
    assert slope(ax.lines[3]) == pytest.approx(
        heckit_two_step(df, ["x"], ["x", "z"]).coefficients["x"]
    )
    assert slope(ax.lines[2]) < slope(ax.lines[3])


def test_軸の名前() -> None:
    df = draw_selection_sample(500, 0.7, np.random.default_rng(0))
    ax = plot_selection(df).axes[0]
    assert ax.get_xlabel() == "x"
    assert ax.get_ylabel() == "y (observed only if selected)"
