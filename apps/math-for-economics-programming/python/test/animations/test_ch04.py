from pathlib import Path

import pytest
from matplotlib.animation import FuncAnimation

from lib.animations.ch04 import ANIMATIONS, animate_series_converge, series_frames
from lib.chapter04.sequence import geometric_partial_sum, geometric_series_limit


def test_各フレームは項数ごとの部分和と無限級数との差() -> None:
    data = series_frames(2, 0.6, 4)
    assert [f.terms for f in data] == [1, 2, 3, 4]
    assert data[0].partial_sum == pytest.approx(2)
    assert data[-1].partial_sum == pytest.approx(geometric_partial_sum(2, 0.6, 4))
    limit = geometric_series_limit(2, 0.6)
    assert all(f.gap == pytest.approx(limit - f.partial_sum) for f in data)


def test_公比が正なら差は毎フレーム小さくなる() -> None:
    gaps = [f.gap for f in series_frames(2, 0.6, 10)]
    assert all(g1 > g2 > 0 for g1, g2 in zip(gaps, gaps[1:], strict=False))


def test_公比が負なら差の符号が入れ替わる() -> None:
    gaps = [f.gap for f in series_frames(1, -0.5, 4)]
    assert [g > 0 for g in gaps] == [False, True, False, True]


def test_収束しない公比ではフレームを作らない() -> None:
    with pytest.raises(ValueError):
        series_frames(1, 1.2, 5)


def test_アニメーションは項を1つずつ足す(tmp_path: Path) -> None:
    animation = animate_series_converge(first=1, ratio=-0.5, terms=4)
    assert isinstance(animation, FuncAnimation)
    path = tmp_path / "series.gif"
    animation.save(path, writer="pillow", fps=5, dpi=30)
    assert path.read_bytes()[:6] == b"GIF89a"


def test_登録したアニメーションの名前() -> None:
    assert sorted(ANIMATIONS) == ["ch04-series-converge"]
    assert isinstance(ANIMATIONS["ch04-series-converge"](), FuncAnimation)
