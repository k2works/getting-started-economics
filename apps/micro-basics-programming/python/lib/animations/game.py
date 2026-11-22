"""割引因子を上げると、協調を続ける価値が、裏切る価値を上回る（第 13 章）。"""

from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from lib.animations.common import linear_values, make_animation
from lib.chapter13.repeated import (
    cooperation_threshold,
    cooperation_value,
    deviation_value,
    trigger_sustains_cooperation,
)


@dataclass(frozen=True)
class DeltaFrame:
    """ある割引因子のもとの、協調の価値・裏切りの価値・協調が続くか。"""

    delta: float
    cooperate: float
    defect: float
    sustained: bool


def threshold_frames(
    temptation: float,
    reward: float,
    punishment: float,
    delta_max: float,
    frames: int,
) -> list[DeltaFrame]:
    """割引因子を 0 から delta_max へ上げたときの、各フレームのデータ。"""
    return [
        DeltaFrame(
            d,
            cooperation_value(reward, d),
            deviation_value(temptation, punishment, d),
            trigger_sustains_cooperation(temptation, reward, punishment, d),
        )
        for d in linear_values(0.0, delta_max, frames)
    ]


def animate_trigger_threshold(
    temptation: float = 5.0,
    reward: float = 3.0,
    punishment: float = 1.0,
    delta_max: float = 0.95,
    frames: int = 40,
) -> FuncAnimation:
    """割引因子を上げながら、2 つの価値を描き、閾値で協調が続く様子を見せる。"""
    data = threshold_frames(temptation, reward, punishment, delta_max, frames)
    threshold = cooperation_threshold(temptation, reward, punishment)
    fig, ax = plt.subplots()
    (coop,) = ax.plot([], [], label="Cooperate forever")
    (defect,) = ax.plot([], [], label="Defect once")
    (now,) = ax.plot([], [], "o", label="Now")
    ax.plot([threshold, threshold], [0, 65], linestyle=":", label="Threshold")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 65)
    ax.set_xlabel("Discount factor")
    ax.set_ylabel("Present value")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        so_far = data[: i + 1]
        coop.set_data([f.delta for f in so_far], [f.cooperate for f in so_far])
        defect.set_data([f.delta for f in so_far], [f.defect for f in so_far])
        frame = data[i]
        now.set_data([frame.delta], [frame.cooperate])
        state = "cooperation holds" if frame.sustained else "defection pays"
        label.set_text(f"delta = {frame.delta:.2f}: {state}")

    plt.close(fig)
    return make_animation(fig, update, frames)
