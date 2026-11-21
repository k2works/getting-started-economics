"""貨幣市場の均衡と LM 曲線の図。"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter07.liquidity import lm_interest_with_trap
from lib.chapter07.money_market import lm_interest, money_demand


def plot_money_market(
    income: float,
    income_after: float,
    real_money: float,
    k: float,
    h: float,
    interest_max: float,
) -> Figure:
    """貨幣市場の均衡。貨幣供給は垂直、貨幣需要は右下がり（所得が増えると右へ）。"""
    fig, ax = plt.subplots()
    for y in (income, income_after):
        demand = [money_demand(y, r, k, h) for r in (0, interest_max)]
        ax.plot(demand, [0, interest_max], label=f"Money demand (Y = {y:g})")
    ax.plot([real_money, real_money], [0, interest_max], label="Money supply (M/P)")
    ax.plot(
        [real_money], [lm_interest(income, real_money, k, h)], "o", label="Equilibrium"
    )
    ax.set_xlabel("Real money balances")
    ax.set_ylabel("Interest rate r")
    ax.legend()
    plt.close(fig)
    return fig


def plot_lm_curves(
    incomes: list[float],
    real_money: float,
    real_money_after: float,
    k: float,
    h: float,
    floor: float,
) -> Figure:
    """LM 曲線と、実質貨幣供給が増えたあとの LM 曲線、流動性のわなのある LM 曲線。"""
    fig, ax = plt.subplots()
    ax.plot(incomes, [lm_interest(y, real_money, k, h) for y in incomes], label="LM")
    ax.plot(
        incomes,
        [lm_interest(y, real_money_after, k, h) for y in incomes],
        label="LM (M/P increased)",
    )
    ax.plot(
        incomes,
        [lm_interest_with_trap(y, real_money, k, h, floor) for y in incomes],
        "--",
        label="LM with liquidity trap",
    )
    ax.set_xlabel("Income Y")
    ax.set_ylabel("Interest rate r")
    ax.legend()
    plt.close(fig)
    return fig
