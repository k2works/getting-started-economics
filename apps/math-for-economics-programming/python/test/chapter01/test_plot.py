import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.axes import Axes
from matplotlib.patches import Polygon

from lib.chapter01.market import consumer_surplus, equilibrium, producer_surplus
from lib.chapter01.plot import plot_harvest_paradox, plot_market


def _line(ax: Axes, label: str) -> tuple[list[float], list[float]]:
    line = next(x for x in ax.lines if x.get_label() == label)
    xs = np.asarray(line.get_xdata(), dtype=float).tolist()
    ys = np.asarray(line.get_ydata(), dtype=float).tolist()
    return xs, ys


def test_需要曲線は右下がりで価格軸の切片は上限の価格() -> None:
    ax = plot_market(120, 2, 0, 1).axes[0]
    xs, ys = _line(ax, "Demand")
    assert (xs[0], ys[0]) == (0, 60)
    assert (xs[-1], ys[-1]) == (120, 0)
    assert all(y1 > y2 for y1, y2 in zip(ys, ys[1:], strict=False))


def test_供給曲線は右上がりで原点を通る() -> None:
    ax = plot_market(120, 2, 0, 1).axes[0]
    xs, ys = _line(ax, "Supply")
    assert (xs[0], ys[0]) == (0, 0)
    assert all(y1 < y2 for y1, y2 in zip(ys, ys[1:], strict=False))


def test_均衡の点は需要曲線と供給曲線の交点() -> None:
    ax = plot_market(120, 2, 0, 1).axes[0]
    xs, ys = _line(ax, "Equilibrium")
    assert (xs, ys) == ([40], [40])


def test_切片のある供給は価格軸の正の値から始まる() -> None:
    ax = plot_market(100, 2, -10, 1).axes[0]
    xs, ys = _line(ax, "Supply")
    assert (xs[0], ys[0]) == (0, 10)


def _area(ax: Axes, label: str) -> float:
    """塗った多角形の面積（靴ひも公式）。"""
    patch = next(x for x in ax.patches if x.get_label() == label)
    assert isinstance(patch, Polygon)
    points = patch.get_xy()[:-1]
    n = len(points)
    total = sum(
        points[i][0] * points[(i + 1) % n][1] - points[(i + 1) % n][0] * points[i][1]
        for i in range(n)
    )
    return float(abs(total)) / 2


def test_余剰の領域が2つ塗られている() -> None:
    ax = plot_market(120, 2, 0, 1).axes[0]
    assert {p.get_label() for p in ax.patches} == {
        "Consumer surplus",
        "Producer surplus",
    }


@pytest.mark.parametrize("params", [(120, 2, 0, 1), (100, 2, 10, 1), (100, 2, -10, 1)])
def test_塗った面積は余剰の値に等しい(
    params: tuple[float, float, float, float],
) -> None:
    a, b, c, d = params
    price = equilibrium(a, b, c, d).price
    ax = plot_market(*params).axes[0]
    assert _area(ax, "Consumer surplus") == pytest.approx(consumer_surplus(price, a, b))
    assert _area(ax, "Producer surplus") == pytest.approx(producer_surplus(price, c, d))


def test_軸と凡例がある() -> None:
    ax = plot_market(120, 2, 0, 1).axes[0]
    assert ax.get_xlabel() == "Quantity"
    assert ax.get_ylabel() == "Price"
    assert ax.get_legend() is not None
    plt.close("all")


def test_豊作貧乏の図は供給が右に動いた後の曲線を点線で描く() -> None:
    ax = plot_harvest_paradox(100, 0.5, 10, 1, 40).axes[0]
    xs, ys = _line(ax, "Supply after")
    assert (xs[0], ys[0]) == (40, 0)
    assert _line(ax, "Supply before")[0][0] == 10
    line = next(x for x in ax.lines if x.get_label() == "Supply after")
    assert line.get_linestyle() == "--"


def test_豊作貧乏の図の均衡の点は前と後の2つ() -> None:
    ax = plot_harvest_paradox(100, 0.5, 10, 1, 40).axes[0]
    assert _line(ax, "Equilibrium before") == ([70], [60])
    assert _line(ax, "Equilibrium after") == ([80], [40])


def test_需要の切片より供給が大きくなる設定でも描ける() -> None:
    fig = plot_harvest_paradox(120, 2, 0, 1, 20)
    assert fig.axes[0].get_legend() is not None


@pytest.mark.parametrize("args", [(10, 1, 20, 1)])
def test_均衡のない設定の図はエラー(args: tuple[float, float, float, float]) -> None:
    with pytest.raises(ValueError):
        plot_market(*args)


def test_供給曲線の終点は数量の上限での価格() -> None:
    ax = plot_market(100, 2, -10, 2).axes[0]
    xs, ys = _line(ax, "Supply")
    assert (xs[0], ys[0]) == (0, 5)
    assert (xs[-1], ys[-1]) == (100, 55)


def test_軸は数量も価格も0から始まる() -> None:
    ax = plot_market(120, 2, 0, 1).axes[0]
    assert ax.get_xlim()[0] == 0
    assert ax.get_ylim()[0] == 0


def test_消費者余剰の領域は価格軸の上限から始まり透けて見える() -> None:
    ax = plot_market(120, 2, 0, 1).axes[0]
    patch = next(x for x in ax.patches if x.get_label() == "Consumer surplus")
    assert isinstance(patch, Polygon)
    assert tuple(patch.get_xy()[0]) == (0, 60)
    alpha = patch.get_alpha()
    assert alpha is not None and 0 < alpha < 1
