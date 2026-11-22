"""IS-MP-PC モデルのインパルス反応のアニメーション（第 15 章）。"""

from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation

from lib.animations.common import linear_values, make_animation
from lib.chapter15.ismppc import IsMpPcParameters, impulse_response


@dataclass(frozen=True)
class IsMpPcFrame:
    c: float
    phi: float
    response: pd.DataFrame


def ismppc_frames(c_start: float, c_end: float, frames: int) -> list[IsMpPcFrame]:
    """MP 曲線のインフレへの反応 c を動かしたときの、物価ショック（e = 1）への反応。"""
    result = []
    for c in linear_values(c_start, c_end, frames):
        params = IsMpPcParameters(c=c)
        result.append(
            IsMpPcFrame(c, params.phi, impulse_response(params, shock_pc=1.0))
        )
    return result


def animate_ismppc_impulse(
    c_start: float = 0.0, c_end: float = 3.0, frames: int = 16
) -> FuncAnimation:
    """c が大きい（インフレに強く反応する）ほど、インフレ率は、速く元に戻る。"""
    data = ismppc_frames(c_start, c_end, frames)
    steady = IsMpPcParameters()
    n = len(data[0].response)
    pi_gap = [f.response["pi"] - steady.pi_star for f in data]
    y_gap = [f.response["y"] - steady.y_star for f in data]
    low = 1.1 * min(min(s.min() for s in pi_gap), min(s.min() for s in y_gap))
    high = 1.1 * max(max(s.max() for s in pi_gap), max(s.max() for s in y_gap))
    fig, ax = plt.subplots()
    ax.plot([0, n - 1], [0, 0], "--", color="gray", label="Zero")
    (pi_line,) = ax.plot([], [], "o-", label="Inflation gap")
    (y_line,) = ax.plot([], [], "o-", label="Output gap")
    label = ax.text(0.98, 0.05, "", transform=ax.transAxes, ha="right", va="bottom")
    ax.set_xlim(0, n - 1)
    ax.set_ylim(low, high)
    ax.set_xlabel("Period (shock at period 3)")
    ax.set_ylabel("Deviation from steady state")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        pi_line.set_data(range(n), pi_gap[i].to_numpy())
        y_line.set_data(range(n), y_gap[i].to_numpy())
        label.set_text(f"c = {data[i].c:.2f}, phi = {data[i].phi:.2f}")

    plt.close(fig)
    return make_animation(fig, update, frames)
