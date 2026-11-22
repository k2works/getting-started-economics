"""ソロー・モデルのアニメーション（第 5 章）。"""

from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from lib.animations.common import linear_values, make_animation
from lib.chapter05.solow import solow_path, steady_state_capital


@dataclass(frozen=True)
class SolowFrame:
    saving_rate: float
    steady: float
    path: list[float]


def solow_frames(
    saving_start: float,
    saving_end: float,
    depreciation: float,
    alpha: float,
    capital0: float,
    periods: int,
    frames: int,
) -> list[SolowFrame]:
    """貯蓄率を動かしたときの、資本の経路と、定常状態の資本。"""
    return [
        SolowFrame(
            s,
            steady_state_capital(s, depreciation, alpha),
            solow_path(capital0, s, depreciation, alpha, periods),
        )
        for s in linear_values(saving_start, saving_end, frames)
    ]


def animate_solow_saving(
    saving_start: float = 0.1,
    saving_end: float = 0.4,
    depreciation: float = 0.05,
    alpha: float = 0.5,
    capital0: float = 2.0,
    periods: int = 100,
    frames: int = 16,
) -> FuncAnimation:
    """貯蓄率を上げると、定常状態の資本が高くなり、資本の経路も高い水準へ向かう。"""
    data = solow_frames(
        saving_start, saving_end, depreciation, alpha, capital0, periods, frames
    )
    fig, ax = plt.subplots()
    (steady_line,) = ax.plot([], [], "--", color="gray", label="Steady state k*")
    (path_line,) = ax.plot([], [], label="Capital k(t)")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.set_xlim(0, periods)
    ax.set_ylim(0, 1.1 * max(f.steady for f in data))
    ax.set_xlabel("Period t")
    ax.set_ylabel("Capital k")
    ax.legend(fontsize="x-small", loc="lower right")

    def update(i: int) -> None:
        frame = data[i]
        steady_line.set_data([0, periods], [frame.steady, frame.steady])
        path_line.set_data(range(len(frame.path)), frame.path)
        label.set_text(f"s = {frame.saving_rate:.2f}, k* = {frame.steady:.1f}")

    plt.close(fig)
    return make_animation(fig, update, frames)
