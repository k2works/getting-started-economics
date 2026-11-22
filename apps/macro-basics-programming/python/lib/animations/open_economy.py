"""財政政策の効果は、為替制度で変わる（第 14 章）。"""

from dataclasses import dataclass, replace

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from lib.animations.common import linear_values, make_animation
from lib.chapter14.mundell_fleming import (
    SmallOpenEconomy,
    fixed_rate_equilibrium,
    floating_rate_equilibrium,
)

_ECONOMY = SmallOpenEconomy(
    mpc=0.6,
    b=20,
    intercept=400,
    n=50,
    k=0.5,
    h=100,
    real_money=250,
    world_rate=2.5,
    exchange_rate=1,
)


@dataclass(frozen=True)
class RegimeFrame:
    """政府支出の増加のもとの、固定相場と変動相場の均衡所得。"""

    delta_government: float
    fixed_income: float
    floating_income: float
    exchange_rate: float


def regime_frames(
    economy: SmallOpenEconomy, max_delta_government: float, frames: int
) -> list[RegimeFrame]:
    """政府支出を 0 から増やしたときの、各フレームのデータ。"""
    data = []
    for dg in linear_values(0.0, max_delta_government, frames):
        moved = replace(economy, intercept=economy.intercept + dg)
        floating = floating_rate_equilibrium(moved)
        data.append(
            RegimeFrame(
                dg,
                fixed_rate_equilibrium(moved).income,
                floating.income,
                floating.exchange_rate,
            )
        )
    return data


def animate_regimes(
    economy: SmallOpenEconomy = _ECONOMY,
    max_delta_government: float = 20.0,
    frames: int = 30,
) -> FuncAnimation:
    """政府支出を増やすと、固定相場では所得が増え、変動相場では為替が動いて相殺する。"""
    data = regime_frames(economy, max_delta_government, frames)
    fig, ax = plt.subplots()
    (fixed,) = ax.plot([], [], label="Fixed rate")
    (floating,) = ax.plot([], [], label="Floating rate")
    (fixed_point,) = ax.plot([], [], "o")
    (floating_point,) = ax.plot([], [], "o")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.set_xlim(0, max_delta_government)
    ax.set_ylim(data[0].floating_income - 20, max(f.fixed_income for f in data) + 20)
    ax.set_xlabel("Delta G")
    ax.set_ylabel("Equilibrium income Y")
    ax.legend(fontsize="x-small", loc="center left")

    def update(i: int) -> None:
        shown = data[: i + 1]
        xs = [f.delta_government for f in shown]
        fixed.set_data(xs, [f.fixed_income for f in shown])
        floating.set_data(xs, [f.floating_income for f in shown])
        fixed_point.set_data([xs[-1]], [shown[-1].fixed_income])
        floating_point.set_data([xs[-1]], [shown[-1].floating_income])
        label.set_text(
            f"Delta G = {xs[-1]:.0f}, exchange rate e = {shown[-1].exchange_rate:.2f}"
        )

    plt.close(fig)
    return make_animation(fig, update, frames)
