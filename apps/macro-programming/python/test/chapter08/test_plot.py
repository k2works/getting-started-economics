"""第 8 章: 確率過程の図のテスト。"""

from typing import Any

import numpy as np
import pytest
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from lib.chapter08.plot import plot_acf, plot_series
from lib.chapter08.stochastic import ar1_series


def xy(line: Line2D) -> list[tuple[float, float]]:
    data: Any = line.get_xydata()
    return [(float(x), float(y)) for x, y in data]


def test_系列の図は名前ごとの線() -> None:
    a = ar1_series(0.0, 1.0, 20, np.random.default_rng(0))
    b = ar1_series(0.9, 1.0, 20, np.random.default_rng(0))
    ax = plot_series({"rho = 0": a, "rho = 0.9": b}).axes[0]
    assert [line.get_label() for line in ax.lines] == ["rho = 0", "rho = 0.9"]


def test_線の点は時点と値の組() -> None:
    x = ar1_series(0.5, 1.0, 20, np.random.default_rng(0))
    ax = plot_series({"x": x}).axes[0]
    points = xy(ax.lines[0])
    assert [t for t, _ in points] == list(range(20))
    assert [v for _, v in points] == pytest.approx(x.tolist())


def test_自己相関の図は標本の棒と理論値の線() -> None:
    sample = [1.0, 0.5, 0.2, 0.1]
    theory = [1.0, 0.5, 0.25, 0.125]
    ax = plot_acf(sample, theory).axes[0]
    heights = [p.get_height() for p in ax.patches if isinstance(p, Rectangle)]
    assert heights == pytest.approx(sample)
    assert [line.get_label() for line in ax.lines] == ["Theory"]
    assert xy(ax.lines[0]) == [pytest.approx((i, v)) for i, v in enumerate(theory)]
