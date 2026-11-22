"""対数線形近似の誤差のアニメーション（第 17 章）。"""

from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation

from lib.animations.common import linear_values, make_animation
from lib.chapter16.solow_stochastic import SolowParameters
from lib.chapter17.loglinear import capital_paths


@dataclass(frozen=True)
class LoglinearFrame:
    deviation: float
    paths: pd.DataFrame


def loglinear_frames(
    max_deviation: float, periods: int, frames: int
) -> list[LoglinearFrame]:
    """初期の乖離を動かしたときの、厳密な経路と線形近似の経路。"""
    params = SolowParameters()
    return [
        LoglinearFrame(d, capital_paths(params, d, periods))
        for d in linear_values(max_deviation / frames, max_deviation, frames)
    ]


def animate_loglinear_error(
    max_deviation: float = 1.0, periods: int = 60, frames: int = 20
) -> FuncAnimation:
    """初期の乖離が大きいほど、厳密な経路と線形近似の経路が離れる。小さければ、ほぼ重なる。"""
    data = loglinear_frames(max_deviation, periods, frames)
    fig, ax = plt.subplots()
    (exact_line,) = ax.plot([], [], label="Exact")
    (linear_line,) = ax.plot([], [], "--", label="Linear approximation")
    label = ax.text(0.98, 0.05, "", transform=ax.transAxes, ha="right", va="bottom")
    ax.set_xlim(0, periods)
    ax.set_ylim(0, 100 * max_deviation * 1.1)
    ax.set_xlabel("Period t")
    ax.set_ylabel("Capital deviation (%)")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        frame = data[i]
        x = range(len(frame.paths))
        exact_line.set_data(x, frame.paths["exact"].to_numpy())
        linear_line.set_data(x, frame.paths["linear"].to_numpy())
        label.set_text(f"initial deviation = {100 * frame.deviation:.0f}%")

    plt.close(fig)
    return make_animation(fig, update, frames)
