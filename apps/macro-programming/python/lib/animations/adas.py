"""動的 AD-AS モデルのインパルス反応のアニメーション（第 14 章）。"""

from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation

from lib.animations.common import linear_values, make_animation
from lib.chapter13.adas import AdasParameters
from lib.chapter14.simulation import impulse_response


@dataclass(frozen=True)
class AdasFrame:
    a: float
    h: float
    response: pd.DataFrame


def adas_frames(
    a_start: float, a_end: float, c: float, u: float, frames: int
) -> list[AdasFrame]:
    """AS 曲線の傾き a を動かしたときの、需要ショック u への反応。"""
    result = []
    for a in linear_values(a_start, a_end, frames):
        params = AdasParameters(a, c, 0.0, 0.0)
        result.append(AdasFrame(a, params.h, impulse_response(params, u=u)))
    return result


def animate_adas_impulse(
    a_start: float = 0.5,
    a_end: float = 4.0,
    c: float = 0.3,
    u: float = 1.0,
    frames: int = 15,
) -> FuncAnimation:
    """a が大きいほど h が小さくなり、物価の乖離は、速く元に戻る。"""
    data = adas_frames(a_start, a_end, c, u, frames)
    n = len(data[0].response)
    values = pd.concat([f.response[["y", "p"]] for f in data])
    fig, ax = plt.subplots()
    ax.plot([0, n - 1], [0, 0], "--", color="gray", label="Zero")
    (y_line,) = ax.plot([], [], "o-", label="Output (y)")
    (p_line,) = ax.plot([], [], "o-", label="Price (p)")
    label = ax.text(0.98, 0.05, "", transform=ax.transAxes, ha="right", va="bottom")
    ax.set_xlim(0, n - 1)
    ax.set_ylim(1.1 * values.min().min(), 1.1 * values.max().max())
    ax.set_xlabel("Period (shock at period 3)")
    ax.set_ylabel("Deviation from trend (%)")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        frame = data[i]
        y_line.set_data(range(n), frame.response["y"].to_numpy())
        p_line.set_data(range(n), frame.response["p"].to_numpy())
        label.set_text(f"a = {frame.a:.2f}, h = {frame.h:.2f}")

    plt.close(fig)
    return make_animation(fig, update, frames)
