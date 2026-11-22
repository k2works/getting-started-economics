"""第 11 章のアニメーション（区分求積）のテスト。"""

import pytest
from matplotlib.animation import FuncAnimation

from lib.animations.ch11 import animate_riemann_sum, riemann_sum_frames
from lib.chapter11.integral import midpoint_rule_integral


def _square(x: float) -> float:
    return x**2


def test_各フレームの面積は中点法の値で長方形の和に一致する() -> None:
    data = riemann_sum_frames(_square, 0, 1, 1 / 3, [1, 2, 4, 50])
    assert [f.pieces for f in data] == [1, 2, 4, 50]
    assert data[0].area == pytest.approx(0.25)
    assert data[2].area == pytest.approx(0.328125)
    for frame in data:
        assert frame.area == pytest.approx(
            midpoint_rule_integral(_square, 0, 1, frame.pieces)
        )
        assert len(frame.midpoints) == len(frame.heights) == frame.pieces
        assert frame.width == pytest.approx(1 / frame.pieces)
        assert sum(frame.heights) * frame.width == pytest.approx(frame.area)
        assert frame.error == pytest.approx(abs(frame.area - 1 / 3))
    assert data[2].midpoints == pytest.approx([0.125, 0.375, 0.625, 0.875])


def test_分割を細かくするほど誤差が小さくなる() -> None:
    data = riemann_sum_frames(_square, 0, 1, 1 / 3, list(range(1, 51)))
    errors = [f.error for f in data]
    assert errors == sorted(errors, reverse=True)
    # 誤差は 1/(12n²)。n = 50 で 1/30000
    assert errors[-1] == pytest.approx(1 / 30000)


def test_分割数は1つ以上() -> None:
    with pytest.raises(ValueError):
        riemann_sum_frames(_square, 0, 1, 1 / 3, [])


def test_アニメーションはすべてのフレームを描ける() -> None:
    anim = animate_riemann_sum()
    assert isinstance(anim, FuncAnimation)
    for i in (0, 3, 49):
        anim._func(i)  # type: ignore[attr-defined]
    ax = anim._fig.axes[0]  # type: ignore[attr-defined]
    # 最後に描いたフレーム（n = 50）の長方形が、50 本ある
    assert len(ax.patches) == 50
