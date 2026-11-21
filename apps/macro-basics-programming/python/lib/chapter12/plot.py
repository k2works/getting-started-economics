"""消費の理論の比較と、加速度原理による投資の図。"""

from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter12.consumption import (
    consumption_from_absolute_income,
    permanent_consumption,
    ratchet_consumption,
)
from lib.chapter12.investment import accelerator_path


def plot_consumption_theories(
    incomes: Sequence[float], mpc: float, adjust: float
) -> Figure:
    """所得が一時的に増えたときの、3 つの仮説の消費の反応を、重ねて描く。"""
    periods = list(range(len(incomes)))
    absolute = [consumption_from_absolute_income(y, mpc) for y in incomes]
    fig, ax = plt.subplots()
    ax.plot(periods, incomes, linestyle="--", label="Income")
    ax.plot(periods, absolute, label="Absolute income")
    ax.plot(
        periods, permanent_consumption(incomes, mpc, adjust), label="Permanent income"
    )
    ax.plot(periods, ratchet_consumption(incomes, mpc), label="Ratchet")
    ax.set_xlabel("Period")
    ax.set_ylabel("Consumption")
    ax.legend()
    plt.close(fig)
    return fig


def plot_accelerator(capital_coefficient: float, incomes: Sequence[float]) -> Figure:
    """上に所得の線、下に、加速度原理による投資の棒を描く。

    所得の増加が小さくなると、所得はまだ増えているのに、投資は減る。
    """
    investment = accelerator_path(capital_coefficient, incomes)
    fig, (top, bottom) = plt.subplots(2, 1, sharex=True)
    top.plot(range(len(incomes)), incomes)
    top.set_ylabel("Income")
    bottom.bar(range(1, len(incomes)), investment)
    bottom.set_xlabel("Period")
    bottom.set_ylabel("Investment")
    plt.close(fig)
    return fig
