"""第 8 章のアニメーション（所得が増えると、予算線と最適点が動く）のテスト。"""

import pytest
from matplotlib.animation import FuncAnimation

from lib.animations.ch08 import animate_budget_moves, budget_moves_frames
from lib.chapter07.budget import budget_intercepts
from lib.chapter08.utility import cobb_douglas_demand, cobb_douglas_utility


def test_端のフレームは所得の両端の最適点() -> None:
    data = budget_moves_frames([1, 2], 0.5, 8, 40, 5)
    assert [f.income for f in data] == [8, 16, 24, 32, 40]
    assert data[0].bundle == cobb_douglas_demand([1, 2], 8, 0.5)
    assert data[-1].bundle == pytest.approx((20, 10))
    assert data[-1].intercepts == tuple(budget_intercepts([1, 2], 40))
    assert data[-1].level == pytest.approx(cobb_douglas_utility(20, 10, 0.5))


def test_所得が増えると最適点も効用も増え原点を通る直線の上を動く() -> None:
    data = budget_moves_frames([3, 4], 0.3, 60, 180, 7)
    xs = [f.bundle[0] for f in data]
    levels = [f.level for f in data]
    assert xs == sorted(xs)
    assert levels == sorted(levels)
    # コブ・ダグラス型では、y ÷ x が所得によらず一定（所得拡張経路は原点を通る直線）
    ratios = [f.bundle[1] / f.bundle[0] for f in data]
    assert ratios == pytest.approx([ratios[0]] * len(data))


def test_フレームは2つ以上() -> None:
    with pytest.raises(ValueError):
        budget_moves_frames([1, 2], 0.5, 8, 40, 1)


def test_アニメーションはすべてのフレームを描ける() -> None:
    anim = animate_budget_moves(frames=4)
    assert isinstance(anim, FuncAnimation)
    for i in range(4):
        anim._func(i)  # type: ignore[attr-defined]
