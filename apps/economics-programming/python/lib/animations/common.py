"""アニメーションの共通部分。"""

from collections.abc import Callable

from matplotlib.animation import FuncAnimation
from matplotlib.figure import Figure

_INTERVAL_MS = 100


def linear_values(start: float, end: float, frames: int) -> list[float]:
    """start から end まで、等間隔に frames 個の値（両端を含む）。"""
    if frames < 2:
        raise ValueError("フレーム数は、2 以上にする")
    return [start + (end - start) * i / (frames - 1) for i in range(frames)]


def make_animation(
    fig: Figure, update: Callable[[int], None], frames: int
) -> FuncAnimation:
    """図と、フレームごとの更新の関数から、アニメーションを作る。"""
    return FuncAnimation(
        fig, update, frames=frames, interval=_INTERVAL_MS, repeat=True, blit=False
    )
