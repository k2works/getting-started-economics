"""第 12 章のアニメーション（ソロー・モデルの蜘蛛の巣図）のテスト。"""

import pytest
from matplotlib.animation import FuncAnimation

from lib.animations.ch12 import (
    animate_solow_cobweb,
    cobweb_points,
    solow_cobweb_frames,
)
from lib.chapter12.solow import (
    solow_capital_path,
    solow_next_capital,
    solow_steady_state_capital,
)

ALPHA = 1 / 3


def test_フレームは各初期値の資本の経路を1期ずつ伸ばす() -> None:
    data = solow_cobweb_frames([1, 12], 0.3, ALPHA, 0.1, 5)
    assert [f.period for f in data] == [0, 1, 2, 3, 4, 5]
    assert data[0].paths == ([1], [12])
    full = (
        solow_capital_path(1, 0.3, ALPHA, 0.1, 5),
        solow_capital_path(12, 0.3, ALPHA, 0.1, 5),
    )
    assert data[-1].paths == full
    assert data[2].paths == (full[0][:3], full[1][:3])


def test_フレームが進むと資本は下からも上からも定常状態に近づく() -> None:
    steady = solow_steady_state_capital(0.3, ALPHA, 0.1)
    data = solow_cobweb_frames([1, 12], 0.3, ALPHA, 0.1, 40)
    lows = [f.paths[0][-1] for f in data]
    highs = [f.paths[1][-1] for f in data]
    assert lows == sorted(lows) and lows[-1] < steady
    assert highs == sorted(highs, reverse=True) and highs[-1] > steady
    assert abs(lows[-1] - steady) < 0.1 * abs(1 - steady)


def test_階段の点は45度線と曲線を交互に結ぶ() -> None:
    xs, ys = cobweb_points([1, 1.2, 1.4])
    assert xs == [1, 1, 1.2, 1.2, 1.4]
    assert ys == [1, 1.2, 1.2, 1.4, 1.4]
    assert cobweb_points([5]) == ([5], [5])


def test_階段の縦の線の先は来期の資本の曲線の上にある() -> None:
    path = solow_capital_path(1, 0.3, ALPHA, 0.1, 3)
    xs, ys = cobweb_points(path)
    for i in range(1, len(xs), 2):
        assert ys[i] == pytest.approx(solow_next_capital(xs[i], 0.3, ALPHA, 0.1))


def test_初期値と期数は1つ以上() -> None:
    with pytest.raises(ValueError):
        solow_cobweb_frames([], 0.3, ALPHA, 0.1, 5)
    with pytest.raises(ValueError):
        solow_cobweb_frames([1], 0.3, ALPHA, 0.1, 0)


def test_蜘蛛の巣図のアニメーションは全フレームを描ける() -> None:
    anim = animate_solow_cobweb(frames=6)
    assert isinstance(anim, FuncAnimation)
    for i in range(6):
        anim._func(i)  # type: ignore[attr-defined]
