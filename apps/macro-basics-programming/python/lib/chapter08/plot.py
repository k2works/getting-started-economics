"""IS 曲線と IS-LM の均衡の図。"""

from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter07.money_market import lm_interest
from lib.chapter08.is_lm import is_income, is_interest, solve_is_lm


def plot_is_curves(
    mpc: float, intercept: float, bs: Sequence[float], interest_max: float
) -> Figure:
    """投資の利子感応度 b ごとの IS 曲線。b が大きいほど緩やか。"""
    fig, ax = plt.subplots()
    interests = [0, interest_max]
    for b in bs:
        incomes = [is_income(r, intercept, mpc, b) for r in interests]
        ax.plot(incomes, interests, label=f"b = {b}")
    ax.set_xlabel("Income Y")
    ax.set_ylabel("Interest rate r")
    ax.legend()
    plt.close(fig)
    return fig


def plot_is_lm_equilibrium(
    mpc: float,
    b: float,
    intercept: float,
    k: float,
    h: float,
    real_money: float,
    income_min: float,
    income_max: float,
) -> Figure:
    """IS 曲線と LM 曲線を描き、交点（均衡）に印を付ける。"""
    incomes = [income_min, income_max]
    y_star, r_star = solve_is_lm(mpc, b, intercept, k, h, real_money)
    fig, ax = plt.subplots()
    ax.plot(incomes, [is_interest(y, intercept, mpc, b) for y in incomes], label="IS")
    ax.plot(incomes, [lm_interest(y, real_money, k, h) for y in incomes], label="LM")
    ax.plot([y_star], [r_star], "o", label="Equilibrium")
    ax.set_xlabel("Income Y")
    ax.set_ylabel("Interest rate r")
    ax.set_ylim(bottom=0)
    ax.legend()
    plt.close(fig)
    return fig
