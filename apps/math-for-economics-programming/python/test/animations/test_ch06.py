import math
from pathlib import Path

import pytest
from matplotlib.animation import FuncAnimation

from lib.animations.ch06 import animate_taylor_order, taylor_order_frames
from lib.chapter06.growth import taylor_exp_approximation


def test_テイラー近似の各フレームは次数ごとの近似の値() -> None:
    data = taylor_order_frames(-2, 2, 6, 1.0, 5)
    assert [f.order for f in data] == list(range(7))
    assert data[0].xs == [-2, -1, 0, 1, 2]
    assert data[0].approximations == [1, 1, 1, 1, 1]  # 0 次は定数 1
    assert data[2].approximations == pytest.approx(
        [taylor_exp_approximation(x, 2) for x in data[2].xs]
    )
    assert data[6].error_at_point == pytest.approx(
        abs(taylor_exp_approximation(1, 6) - math.e)
    )


def test_次数を上げるほど誤差が減る() -> None:
    errors = [f.error_at_point for f in taylor_order_frames(-2, 2, 6, 1.0, 5)]
    assert errors == sorted(errors, reverse=True)
    assert errors[0] == pytest.approx(math.e - 1)


def test_次数の上限は0以上() -> None:
    assert len(taylor_order_frames(-1, 1, 0, 0.5, 3)) == 1
    with pytest.raises(ValueError, match="次数"):
        taylor_order_frames(-1, 1, -1, 0.5, 3)


def test_アニメーションは次数ごとに同じフレームを繰り返す(tmp_path: Path) -> None:
    animation = animate_taylor_order(max_order=2, hold=2, points=5)
    assert isinstance(animation, FuncAnimation)
    for i in range(6):
        animation._func(i)  # type: ignore[attr-defined]
    path = tmp_path / "taylor.gif"
    animation.save(path, writer="pillow", fps=5, dpi=30)
    assert path.read_bytes()[:6] == b"GIF89a"
