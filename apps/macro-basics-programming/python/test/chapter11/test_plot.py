"""第 11 章: フィリップス曲線とオークンの法則の図のテスト。"""

import numpy as np
import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from lib.chapter11.okun import OkunFit
from lib.chapter11.plot import plot_okun, plot_phillips


def line(ax: Axes, label: str) -> Line2D:
    (found,) = [ln for ln in ax.get_lines() if ln.get_label() == label]
    return found


def xs(ln: Line2D) -> list[float]:
    return [float(v) for v in np.asarray(ln.get_xdata(), dtype=float)]


def ys(ln: Line2D) -> list[float]:
    return [float(v) for v in np.asarray(ln.get_ydata(), dtype=float)]


def phillips() -> Axes:
    return plot_phillips(
        natural_rate=5, expected_inflations=[2, 4], beta=0.5, u_min=3, u_max=7
    ).axes[0]


def test_短期の曲線は右下がりで自然失業率では期待インフレ率() -> None:
    ax = phillips()
    curve = line(ax, "Short run (expected inflation 2)")
    assert xs(curve) == [3, 7]
    assert ys(curve) == pytest.approx([3.0, 1.0])


def test_期待インフレ率が高い曲線は上にある() -> None:
    ax = phillips()
    low = ys(line(ax, "Short run (expected inflation 2)"))
    high = ys(line(ax, "Short run (expected inflation 4)"))
    assert high == pytest.approx([5.0, 3.0])
    assert all(h > lo for h, lo in zip(high, low, strict=True))


def test_長期の曲線は自然失業率で垂直() -> None:
    ax = phillips()
    vertical = line(ax, "Long run")
    assert xs(vertical) == [5, 5]
    assert ys(vertical) == pytest.approx([1.0, 5.0])


def test_フィリップス曲線の図の軸の名前() -> None:
    ax = phillips()
    assert ax.get_xlabel() == "Unemployment rate (%)"
    assert ax.get_ylabel() == "Inflation rate (%)"


GROWTH = [0.0, 2.0, 4.0]
CHANGE = [1.2, 0.4, -0.4]


def okun() -> Axes:
    fit = OkunFit(slope=-0.4, intercept=1.2)
    return plot_okun(GROWTH, CHANGE, fit).axes[0]


def test_オークンの図は散布図と回帰直線() -> None:
    ax = okun()
    points = line(ax, "Quarterly data")
    assert xs(points) == GROWTH
    assert ys(points) == pytest.approx(CHANGE)
    fitted = line(ax, "Fitted line")
    assert xs(fitted) == [0.0, 4.0]
    assert ys(fitted) == pytest.approx([1.2, -0.4])


def test_オークンの図の軸の名前() -> None:
    ax = okun()
    assert ax.get_xlabel() == "Growth rate (%)"
    assert ax.get_ylabel() == "Change in unemployment rate (points)"
