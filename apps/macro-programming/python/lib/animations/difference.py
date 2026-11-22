"""差分方程式のアニメーション（第 4 章）。"""

from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from lib.animations.common import linear_values, make_animation
from lib.chapter04.difference import linear_path


@dataclass(frozen=True)
class DifferenceFrame:
    a: float
    path: list[float]


def difference_frames(
    steady: float,
    initial: float,
    periods: int,
    a_start: float,
    a_end: float,
    frames: int,
) -> list[DifferenceFrame]:
    """係数 a を動かしたときの経路（b は、定常状態が steady になる値）。"""
    return [
        DifferenceFrame(a, linear_path(a, steady * (1 - a), initial, periods))
        for a in linear_values(a_start, a_end, frames)
    ]


def animate_difference(
    steady: float = 2.0,
    initial: float = 0.0,
    periods: int = 12,
    a_start: float = -1.2,
    a_end: float = 1.2,
    frames: int = 25,
) -> FuncAnimation:
    """係数 a を動かす。収束・往復（a < 0）・発散（|a| > 1）が、順に現れる。"""
    data = difference_frames(steady, initial, periods, a_start, a_end, frames)
    fig, ax = plt.subplots()
    ax.plot([0, periods], [steady, steady], "--", color="gray", label="Steady state")
    (line,) = ax.plot([], [], "o-", label="x(t)")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.set_xlim(0, periods)
    ax.set_ylim(-6, 8)
    ax.set_xlabel("Period t")
    ax.set_ylabel("x(t)")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        frame = data[i]
        line.set_data(range(len(frame.path)), frame.path)
        kind = "stable" if abs(frame.a) < 1 else "unstable"
        label.set_text(f"a = {frame.a:.2f} ({kind})")

    plt.close(fig)
    return make_animation(fig, update, frames)
