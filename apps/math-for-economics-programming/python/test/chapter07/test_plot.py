import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.axes import Axes

from lib.chapter07.budget import budget_intercepts, consumption_given_leisure
from lib.chapter07.plot import plot_budget_set, plot_labor_leisure
from lib.chapter07.vectors import vector_angle_degrees, vector_dot, vector_length


def _series(ax: Axes, label: str) -> tuple[list[float], list[float]]:
    line = next(x for x in ax.lines if x.get_label() == label)
    xs = np.asarray(line.get_xdata(), dtype=float).tolist()
    ys = np.asarray(line.get_ydata(), dtype=float).tolist()
    return xs, ys


def test_予算線は2つの切片を結ぶ() -> None:
    ax = plot_budget_set([3, 4], 120, []).axes[0]
    xs, ys = _series(ax, "Budget line")
    assert xs == pytest.approx([0, 40])
    assert ys == pytest.approx([30, 0])
    assert budget_intercepts([3, 4], 120) == [40, 30]


def test_価格ベクトルの矢印は予算線と直交し価格と同じ向き() -> None:
    prices = [3, 4]
    ax = plot_budget_set(prices, 120, []).axes[0]
    xs, ys = _series(ax, "Price vector (normal)")
    arrow = [xs[1] - xs[0], ys[1] - ys[0]]
    assert vector_dot(arrow, [40, -30]) == pytest.approx(0)
    assert vector_angle_degrees(arrow, prices) == pytest.approx(0, abs=1e-5)
    # 矢印は、予算線の中点から出る
    assert (xs[0], ys[0]) == pytest.approx((20, 15))


def test_価格ベクトルの矢印の長さは小さい切片の4分の1() -> None:
    xs, ys = _series(plot_budget_set([3, 4], 120, []).axes[0], "Price vector (normal)")
    assert vector_length([xs[1] - xs[0], ys[1] - ys[0]]) == pytest.approx(30 / 4)
    xs, ys = _series(plot_budget_set([2, 3], 60, []).axes[0], "Price vector (normal)")
    assert vector_length([xs[1] - xs[0], ys[1] - ys[0]]) == pytest.approx(20 / 4)


def test_財の組合せは予算内と予算線上と予算外に分けて描く() -> None:
    bundles = [[12, 12], [20, 15], [28, 18], [4, 3]]
    ax = plot_budget_set([3, 4], 120, bundles).axes[0]
    assert _series(ax, "Inside") == ([12, 4], [12, 3])
    assert _series(ax, "On the line") == ([20], [15])
    assert _series(ax, "Outside") == ([28], [18])


def test_組合せがない分類は凡例に載せない() -> None:
    ax = plot_budget_set([3, 4], 120, [[1, 1]]).axes[0]
    labels = {x.get_label() for x in ax.lines}
    assert "Inside" in labels
    assert not {"On the line", "Outside"} & labels


def test_予算内の領域は予算線の下を塗る() -> None:
    ax = plot_budget_set([2, 3], 60, []).axes[0]
    area = next(c for c in ax.collections if c.get_label() == "Affordable set")
    vertices = np.asarray(area.get_paths()[0].vertices, dtype=float).tolist()
    # 原点と 2 つの切片を頂点とする三角形
    assert {(x, y) for x, y in vertices} == {(0, 0), (0, 20), (30, 0)}


def test_予算の図の軸と凡例() -> None:
    ax = plot_budget_set([2, 3], 60, [[1, 1]]).axes[0]
    assert ax.get_xlabel() == "Good 1"
    assert ax.get_ylabel() == "Good 2"
    assert ax.get_legend() is not None
    assert ax.get_aspect() == 1
    plt.close("all")


def test_3財の予算は図にしない() -> None:
    with pytest.raises(ValueError):
        plot_budget_set([1, 2, 3], 60, [])


def test_労働と余暇の予算線は余暇0から総時間まで() -> None:
    ax = plot_labor_leisure(8, 12, 24, 40).axes[0]
    xs, ys = _series(ax, "Budget (wage 8)")
    assert (xs[0], xs[-1]) == (0, 24)
    assert ys == pytest.approx([consumption_given_leisure(x, 8, 24, 40) for x in xs])


def test_賃金が上がった後の予算線は点線で余暇24時間の点で交わる() -> None:
    ax = plot_labor_leisure(8, 12, 24, 40).axes[0]
    line = next(
        x for x in ax.lines if x.get_label() == "Budget after wage rise (wage 12)"
    )
    xs, ys = _series(ax, "Budget after wage rise (wage 12)")
    assert line.get_linestyle() == "--"
    assert ys[0] == pytest.approx(12 * 24 + 40)
    assert (xs[-1], ys[-1]) == pytest.approx((24, 40))


def test_労働と余暇の図の軸と凡例() -> None:
    ax = plot_labor_leisure(8, 12, 24, 40).axes[0]
    assert ax.get_xlabel() == "Leisure (hours)"
    assert ax.get_ylim()[0] == 0
    assert ax.get_ylabel() == "Consumption"
    assert ax.get_legend() is not None
    plt.close("all")
