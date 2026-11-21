"""需要曲線と所得消費曲線の図。"""

from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter03.demand import demand_curve, income_consumption_curve


def plot_demand_curve(
    incomes: Sequence[float], prices: Sequence[float], py: float
) -> Figure:
    """需要曲線を、所得ごとに描く（横軸が数量、縦軸が価格）。所得が増えると、右へ動く。"""
    fig, ax = plt.subplots()
    for income in incomes:
        points = demand_curve(income, prices, py)
        ax.plot(
            [q for _, q in points], [p for p, _ in points], label=f"Income = {income}"
        )
    ax.set_xlabel("Quantity of good x")
    ax.set_ylabel("Price of good x")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig


def plot_income_consumption(incomes: Sequence[float], px: float, py: float) -> Figure:
    """所得消費曲線。所得を動かしたときの、最適消費点をつなぐ。"""
    bundles = income_consumption_curve(incomes, px, py)
    fig, ax = plt.subplots()
    ax.plot(
        [x for x, _ in bundles],
        [y for _, y in bundles],
        "o-",
        label="Income-consumption curve",
    )
    ax.set_xlabel("Good x")
    ax.set_ylabel("Good y")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig
