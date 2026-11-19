"""第 4 章: 差分方程式の図のテスト。"""

from typing import Any

import pytest
from matplotlib.lines import Line2D

from lib.chapter04.difference import linear_path
from lib.chapter04.plot import plot_cobweb, plot_paths


def xy(line: Line2D) -> list[tuple[float, float]]:
    data: Any = line.get_xydata()
    return [(float(x), float(y)) for x, y in data]


def test_経路の図は経路ごとの線と定常状態の線() -> None:
    paths = {
        "a = 0.5": linear_path(0.5, 1, 0, 10),
        "a = -0.8": linear_path(-0.8, 1, 0, 10),
    }
    ax = plot_paths(paths, steady_state=2).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "a = 0.5",
        "a = -0.8",
        "Steady state",
    ]


def test_経路の点は時点と値の組() -> None:
    path = linear_path(0.5, 1, 0, 10)
    ax = plot_paths({"p": path}, steady_state=2).axes[0]
    points = xy(ax.lines[0])
    assert [x for x, _ in points] == list(range(11))
    assert [y for _, y in points] == pytest.approx(path)


def test_定常状態の線は全時点で同じ高さ() -> None:
    path = linear_path(0.5, 1, 0, 10)
    ax = plot_paths({"p": path}, steady_state=2).axes[0]
    points = xy(ax.lines[1])
    assert all(y == 2 for _, y in points)
    assert points[-1][0] == 10


def test_蜘蛛の巣の図は需要曲線_供給曲線_階段の3本() -> None:
    ax = plot_cobweb(100, 3, 0, 2, initial_price=10, periods=4).axes[0]
    assert [line.get_label() for line in ax.lines] == ["Demand", "Supply", "Path"]


def test_蜘蛛の巣の階段は価格に応じた数量と次の価格をたどる() -> None:
    ax = plot_cobweb(100, 3, 0, 2, initial_price=10, periods=2).axes[0]
    path = xy(ax.lines[2])
    # 最初の価格 10 のときの供給量 2·10 = 20。その数量で需要が決める次の価格 (100 − 20) ÷ 3
    assert path[0] == pytest.approx((20, 10))
    assert path[1] == pytest.approx((20, 80 / 3))
    assert path[2] == pytest.approx((2 * 80 / 3, 80 / 3))
