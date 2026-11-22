"""第 11 章のアニメーション: 区分求積（中点法）の分割数を増やす。"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle

from lib.animations.common import make_animation
from lib.chapter11.integral import midpoint_rule_integral


@dataclass(frozen=True)
class RiemannFrame:
    """1 フレームの区分求積: 分割数、長方形の中点と高さ、幅、面積の和、誤差。"""

    pieces: int
    midpoints: list[float]
    heights: list[float]
    width: float
    area: float
    error: float


def riemann_sum_frames(
    func: Callable[[float], float],
    low: float,
    high: float,
    exact: float,
    pieces: Sequence[int],
) -> list[RiemannFrame]:
    """分割数ごとの、中点法の長方形と面積の和（第 11 章の midpoint_rule_integral）。"""
    if not pieces:
        raise ValueError("分割数を、1 つ以上与えてください")
    frames = []
    for n in pieces:
        width = (high - low) / n
        midpoints = [low + (i + 0.5) * width for i in range(n)]
        area = midpoint_rule_integral(func, low, high, n)
        frames.append(
            RiemannFrame(
                n,
                midpoints,
                [func(m) for m in midpoints],
                width,
                area,
                abs(area - exact),
            )
        )
    return frames


def _square(x: float) -> float:
    return x**2


def animate_riemann_sum(max_pieces: int = 50) -> FuncAnimation:
    """y = x² の 0 から 1 までの面積を、長方形 n 本（n = 1 → max_pieces）で近似する。"""
    data = riemann_sum_frames(_square, 0, 1, 1 / 3, range(1, max_pieces + 1))
    xs = np.linspace(0, 1, 201).tolist()
    fig, ax = plt.subplots()
    ax.plot(xs, [_square(x) for x in xs], color="tab:blue", label="y = x^2")
    ax.plot([], [], "s", color="tab:orange", alpha=0.5, label="Midpoint rectangles")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.15)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend(fontsize="small", loc="center left")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    bars: list[Rectangle] = []

    def update(i: int) -> None:
        frame = data[i]
        for bar in bars:
            bar.remove()
        bars.clear()
        for m, h in zip(frame.midpoints, frame.heights, strict=True):
            bar = Rectangle(
                (m - frame.width / 2, 0),
                frame.width,
                h,
                facecolor="tab:orange",
                edgecolor="tab:brown",
                alpha=0.5,
            )
            ax.add_patch(bar)
            bars.append(bar)
        label.set_text(
            f"n = {frame.pieces}: sum = {frame.area:.5f}, "
            f"exact = 0.33333, error = {frame.error:.1e}"
        )

    plt.close(fig)
    return make_animation(fig, update, len(data))


ANIMATIONS: dict[str, Callable[[], FuncAnimation]] = {
    "ch11-riemann-sum": animate_riemann_sum
}
