"""45 度線分析（ケインズの交差図）。横軸が所得、縦軸が総支出。"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter09.linear import income_determination


def plot_keynesian_cross(
    autonomous_consumption: float,
    mpc: float,
    investment: float,
    new_investment: float | None = None,
) -> Figure:
    """45 度線と総支出 C0 + cY + I の線、その交点（均衡所得）を描いた図を返す。

    new_investment を渡すと、投資が変わった後の総支出の線と均衡点も重ねて描く。
    """
    income, _ = income_determination(autonomous_consumption, mpc, investment)
    new_income = income
    if new_investment is not None:
        new_income, _ = income_determination(
            autonomous_consumption, mpc, new_investment
        )
    x_max = 1.5 * max(income, new_income)

    fig, ax = plt.subplots()
    ax.plot([0, x_max], [0, x_max], label="45-degree line")
    ax.plot(
        [0, x_max],
        [
            autonomous_consumption + investment,
            autonomous_consumption + investment + mpc * x_max,
        ],
        label="Expenditure",
    )
    ax.plot([income], [income], "o", color="black", label="Equilibrium")
    if new_investment is not None:
        base = autonomous_consumption + new_investment
        ax.plot([0, x_max], [base, base + mpc * x_max], label="Expenditure (after)")
        ax.plot(
            [new_income], [new_income], "s", color="black", label="Equilibrium (after)"
        )
    ax.set_xlabel("Income Y")
    ax.set_ylabel("Expenditure")
    ax.set_xlim(0, x_max)
    ax.set_ylim(0, x_max)
    ax.legend()
    plt.close(fig)
    return fig
