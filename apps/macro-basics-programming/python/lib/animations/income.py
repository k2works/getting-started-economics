"""限界消費性向を上げると、乗数が大きくなる（第 4 章）。"""

from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from lib.animations.common import linear_values, make_animation
from lib.chapter04.multiplier import (
    aggregate_demand,
    equilibrium_income,
    spending_multiplier,
)

_INCOMES = [0.0, 1000.0]


@dataclass(frozen=True)
class MpcFrame:
    """ある限界消費性向のもとの、均衡国民所得と乗数。"""

    mpc: float
    income: float
    multiplier: float


def mpc_frames(
    autonomous_consumption: float,
    investment: float,
    government: float,
    net_exports: float,
    mpc_start: float,
    mpc_end: float,
    frames: int,
) -> list[MpcFrame]:
    """限界消費性向を動かしたときの、各フレームのデータ。"""
    return [
        MpcFrame(
            c,
            equilibrium_income(
                c, autonomous_consumption, investment, government, net_exports
            ),
            spending_multiplier(c),
        )
        for c in linear_values(mpc_start, mpc_end, frames)
    ]


def animate_mpc_change(
    autonomous_consumption: float = 40.0,
    investment: float = 30.0,
    government: float = 30.0,
    net_exports: float = 0.0,
    mpc_start: float = 0.3,
    mpc_end: float = 0.9,
    frames: int = 30,
) -> FuncAnimation:
    """限界消費性向を上げると、総需要の線が急になり、均衡所得が大きく右へ動く。"""
    data = mpc_frames(
        autonomous_consumption,
        investment,
        government,
        net_exports,
        mpc_start,
        mpc_end,
        frames,
    )
    fig, ax = plt.subplots()
    ax.plot(_INCOMES, _INCOMES, label="45-degree line")
    (demand,) = ax.plot([], [], label="Aggregate demand D")
    (point,) = ax.plot([], [], "o", label="Equilibrium")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.set_xlim(*_INCOMES)
    ax.set_ylim(*_INCOMES)
    ax.set_xlabel("Income Y")
    ax.set_ylabel("Aggregate demand")
    ax.legend(fontsize="x-small", loc="lower right")

    def update(i: int) -> None:
        frame = data[i]
        demand.set_data(
            _INCOMES,
            [
                aggregate_demand(
                    y,
                    frame.mpc,
                    autonomous_consumption,
                    investment,
                    government,
                    net_exports,
                )
                for y in _INCOMES
            ],
        )
        point.set_data([frame.income], [frame.income])
        label.set_text(
            f"c = {frame.mpc:.2f}, multiplier = {frame.multiplier:.1f}, "
            f"Y = {frame.income:.0f}"
        )

    plt.close(fig)
    return make_animation(fig, update, frames)
