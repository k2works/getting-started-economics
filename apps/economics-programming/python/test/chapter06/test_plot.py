"""第 6 章: 二分法の図のテスト。"""

from typing import Any

import pytest
from matplotlib.lines import Line2D

from lib.chapter06.bisection import make_excess_demand
from lib.chapter06.plot import bisection_midpoints, plot_bisection

EXCESS = make_excess_demand(100, 2, 0, 3)  # 均衡価格は 20


def xy(line: Line2D) -> list[tuple[float, float]]:
    data: Any = line.get_xydata()
    return [(float(x), float(y)) for x, y in data]


def test_中点は区間を半分ずつに絞った順に並ぶ() -> None:
    # 区間 [0, 100] の中点 50 は、超過需要が負なので、上限を 50 に。次は 25、12.5、18.75
    assert bisection_midpoints(EXCESS, 0, 100, 4) == pytest.approx(
        [50, 25, 12.5, 18.75]
    )


def test_中点は均衡価格に近づく() -> None:
    mids = bisection_midpoints(EXCESS, 0, 100, 10)
    assert abs(mids[-1] - 20) < 100 / 2**10


def test_二分法の図には超過需要の曲線とゼロの線と中点がある() -> None:
    ax = plot_bisection(EXCESS, 0, 100, steps=5).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Excess demand",
        "Zero",
        "Midpoints",
    ]


def test_中点の点は価格と超過需要の組() -> None:
    ax = plot_bisection(EXCESS, 0, 100, steps=3).axes[0]
    points = xy(ax.lines[2])
    assert [x for x, _ in points] == pytest.approx([50, 25, 12.5])
    assert [y for _, y in points] == pytest.approx([EXCESS(x) for x in (50, 25, 12.5)])


def test_超過需要の曲線は価格が上がると下がる() -> None:
    ax = plot_bisection(EXCESS, 0, 100, steps=3).axes[0]
    ys = [y for _, y in xy(ax.lines[0])]
    assert all(a >= b for a, b in zip(ys, ys[1:], strict=False))


def test_ゼロの線は区間の端から端まで高さ0() -> None:
    ax = plot_bisection(EXCESS, 0, 100, steps=3).axes[0]
    assert xy(ax.lines[1]) == [(0, 0), (100, 0)]
