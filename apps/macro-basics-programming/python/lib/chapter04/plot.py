"""45 度線と総需要、乗数の図。"""

from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter04.multiplier import aggregate_demand, equilibrium_income


def plot_keynesian_cross(
    mpc: float,
    autonomous_consumption: float,
    investment: float,
    government: float,
    net_exports: float,
    income_max: float,
    tax: float = 0,
) -> Figure:
    """45 度線（総供給 Y）と総需要の線を描き、交点（均衡）に印を付ける。"""
    spec = (mpc, autonomous_consumption, investment, government, net_exports)
    incomes = [0, income_max]
    demand = [aggregate_demand(y, *spec, tax=tax) for y in incomes]
    y_star = equilibrium_income(*spec, tax=tax)
    fig, ax = plt.subplots()
    ax.plot(incomes, incomes, label="45-degree line (Y)")
    ax.plot(incomes, demand, label="Aggregate demand")
    ax.plot([y_star], [y_star], "o", label="Equilibrium")
    ax.set_xlabel("Income Y")
    ax.set_ylabel("Demand / Supply")
    ax.legend()
    plt.close(fig)
    return fig


def plot_multiplier_slopes(
    mpcs: Sequence[float], autonomous: float, income_max: float
) -> Figure:
    """限界消費性向ごとの総需要の線。c が大きいほど傾きが急で、乗数が大きい。"""
    fig, ax = plt.subplots()
    ax.plot([0, income_max], [0, income_max], label="45-degree line (Y)")
    for mpc in mpcs:
        ax.plot(
            [0, income_max],
            [autonomous, autonomous + mpc * income_max],
            label=f"c = {mpc}",
        )
    ax.set_xlabel("Income Y")
    ax.set_ylabel("Aggregate demand")
    ax.legend()
    plt.close(fig)
    return fig
