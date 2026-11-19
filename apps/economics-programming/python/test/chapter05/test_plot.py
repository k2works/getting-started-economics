"""第 5 章: 価格の調整経路の図のテスト。"""

from typing import Any

import pytest
from matplotlib.lines import Line2D

from lib.chapter05.adjustment import walras_path
from lib.chapter05.plot import plot_price_paths


def xy(line: Line2D) -> list[tuple[float, float]]:
    data: Any = line.get_xydata()
    return [(float(x), float(y)) for x, y in data]


def demand(price: float) -> float:
    return 100 - 2 * price


def supply(price: float) -> float:
    return 3 * price


def test_調整経路の図には経路ごとの線と均衡価格の線がある() -> None:
    paths = {
        "step 0.1": walras_path(demand, supply, initial_price=0, step=0.1),
        "step 0.3": walras_path(demand, supply, initial_price=0, step=0.3),
    }
    ax = plot_price_paths(paths, equilibrium_price=20).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "step 0.1",
        "step 0.3",
        "Equilibrium",
    ]


def test_経路の点は繰り返しの回数と価格の組() -> None:
    path = walras_path(demand, supply, initial_price=0, step=0.1)
    ax = plot_price_paths({"a": path}, equilibrium_price=20).axes[0]
    points = xy(ax.lines[0])
    assert [x for x, _ in points] == list(range(len(path)))
    assert [y for _, y in points] == pytest.approx(path)


def test_均衡価格の線は全ステップで同じ高さ() -> None:
    path = walras_path(demand, supply, initial_price=0, step=0.1)
    ax = plot_price_paths({"a": path}, equilibrium_price=20).axes[0]
    points = xy(ax.lines[1])
    assert all(y == 20 for _, y in points)
    assert points[0][0] == 0
    assert points[-1][0] == len(path) - 1
