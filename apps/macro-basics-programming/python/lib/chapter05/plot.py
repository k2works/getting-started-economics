"""ギャップとビルトイン・スタビライザーの図。"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter05.stabilization import income_swing


def plot_gap(
    mpc: float,
    autonomous: float,
    full_employment_income: float,
    income_max: float,
) -> Figure:
    """45 度線・総需要・完全雇用所得を描く。

    完全雇用所得の上の線分は、総需要と 45 度線の縦の差で、ギャップを埋めるのに
    必要な支出の大きさ（デフレギャップでは総需要が下、インフレギャップでは上）。
    """
    incomes = [0, income_max]
    demand = [autonomous + mpc * y for y in incomes]
    y_star = autonomous / (1 - mpc)
    y_full = full_employment_income
    fig, ax = plt.subplots()
    ax.plot(incomes, incomes, label="45-degree line (Y)")
    ax.plot(incomes, demand, label="Aggregate demand")
    ax.plot([y_full, y_full], [0, income_max], "--", label="Full-employment income")
    ax.plot([y_star], [y_star], "o", label="Equilibrium")
    ax.plot([y_full, y_full], [autonomous + mpc * y_full, y_full], label="Gap")
    ax.set_xlabel("Income Y")
    ax.set_ylabel("Demand / Supply")
    ax.legend()
    plt.close(fig)
    return fig


def plot_income_swing(mpc: float, tax_rate: float, shock: float) -> Figure:
    """独立支出が shock だけ変動したときの、所得の変動を、比例税の有無で比べる。"""
    fig, ax = plt.subplots()
    ax.bar(
        ["No tax", "Proportional tax"],
        [income_swing(mpc, 0, shock), income_swing(mpc, tax_rate, shock)],
    )
    ax.set_ylabel("Change in income")
    plt.close(fig)
    return fig
