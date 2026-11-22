"""アニメーションの共通部分。"""

from collections.abc import Callable

import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.figure import Figure
from numpy.typing import ArrayLike, NDArray

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


def histogram_heights(values: ArrayLike, edges: NDArray[np.float64]) -> list[float]:
    """値を、区間 edges で数えて、全体に対する割合（棒の高さ）にする。"""
    data = np.asarray(values, dtype=float)
    counts, _ = np.histogram(data, bins=edges)
    return [float(c) / data.size for c in counts]
