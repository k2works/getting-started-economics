"""RBC モデルのインパルス反応のアニメーション（第 18 章）。"""

from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation

from lib.animations.common import linear_values, make_animation
from lib.chapter18.rbc import RbcParameters, impulse_response, solve_rbc

_VARIABLES = {"y": "Output", "c": "Consumption", "i": "Investment", "k": "Capital"}


@dataclass(frozen=True)
class RbcFrame:
    rho: float
    response: pd.DataFrame


def rbc_frames(rho_start: float, rho_end: float, frames: int) -> list[RbcFrame]:
    """TFP のショックの持続性 ρ を動かしたときの、1% の TFP ショックへの反応。"""
    return [
        RbcFrame(rho, impulse_response(solve_rbc(RbcParameters(rho=rho)), shock=0.01))
        for rho in linear_values(rho_start, rho_end, frames)
    ]


def animate_rbc_impulse(
    rho_start: float = 0.1, rho_end: float = 0.95, frames: int = 15
) -> FuncAnimation:
    """ρ が大きいほど、反応は長く続き、資本のピークは遅れる。"""
    data = rbc_frames(rho_start, rho_end, frames)
    n = len(data[0].response)
    values = pd.concat([f.response[list(_VARIABLES)] for f in data])
    fig, ax = plt.subplots()
    ax.plot([0, n - 1], [0, 0], "--", color="gray", label="Zero")
    lines = {
        column: ax.plot([], [], label=name)[0] for column, name in _VARIABLES.items()
    }
    label = ax.text(0.98, 0.55, "", transform=ax.transAxes, ha="right")
    ax.set_xlim(0, n - 1)
    ax.set_ylim(1.1 * values.min().min(), 1.1 * values.max().max())
    ax.set_xlabel("Period (shock at period 3)")
    ax.set_ylabel("Deviation from steady state (%)")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        frame = data[i]
        for column, line in lines.items():
            line.set_data(range(n), frame.response[column].to_numpy())
        label.set_text(f"rho = {frame.rho:.2f}")

    plt.close(fig)
    return make_animation(fig, update, frames)
