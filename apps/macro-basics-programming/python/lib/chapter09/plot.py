"""財政政策・金融政策の効果と、流動性のわなの図。"""

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from lib.chapter07.money_market import lm_interest
from lib.chapter08.is_lm import is_income, is_interest, solve_is_lm


def _style(ax: Axes) -> None:
    ax.set_xlabel("Income Y")
    ax.set_ylabel("Interest rate r")
    ax.set_ylim(bottom=0)
    ax.legend()


def plot_policy_shifts(
    mpc: float,
    b: float,
    intercept: float,
    k: float,
    h: float,
    real_money: float,
    delta_government: float,
    delta_real_money: float,
    income_min: float,
    income_max: float,
) -> Figure:
    """左: 財政政策（IS が右へ）、右: 金融政策（LM が右へ）。均衡の動きを見る。"""
    incomes = [income_min, income_max]
    fiscal_intercept = intercept + delta_government
    money_after = real_money + delta_real_money
    start = solve_is_lm(mpc, b, intercept, k, h, real_money)
    fiscal = solve_is_lm(mpc, b, fiscal_intercept, k, h, real_money)
    monetary = solve_is_lm(mpc, b, intercept, k, h, money_after)

    def is_line(a: float) -> list[float]:
        return [is_interest(y, a, mpc, b) for y in incomes]

    def lm_line(m: float) -> list[float]:
        return [lm_interest(y, m, k, h) for y in incomes]

    fig, (left, right) = plt.subplots(1, 2, sharey=True)
    left.plot(incomes, is_line(intercept), label="IS")
    left.plot(incomes, is_line(fiscal_intercept), "--", label="IS after fiscal policy")
    left.plot(incomes, lm_line(real_money), label="LM")
    left.plot([start[0]], [start[1]], "o", label="Equilibrium before")
    left.plot([fiscal[0]], [fiscal[1]], "s", label="Equilibrium after")
    right.plot(incomes, is_line(intercept), label="IS")
    right.plot(incomes, lm_line(real_money), label="LM")
    right.plot(incomes, lm_line(money_after), "--", label="LM after monetary policy")
    right.plot([start[0]], [start[1]], "o", label="Equilibrium before")
    right.plot([monetary[0]], [monetary[1]], "s", label="Equilibrium after")
    _style(left)
    _style(right)
    plt.close(fig)
    return fig


def plot_liquidity_trap(
    mpc: float,
    b: float,
    intercept: float,
    trap_interest: float,
    delta_government: float,
    income_min: float,
    income_max: float,
) -> Figure:
    """流動性のわな（LM が水平）。IS が右へ動くと、所得は単純な乗数の分だけ増える。

    LM が水平なので、貨幣供給を増やしても、LM は動かない（金融政策は無効）。
    """
    incomes = [income_min, income_max]
    after = intercept + delta_government
    fig, ax = plt.subplots()
    ax.plot(incomes, [is_interest(y, intercept, mpc, b) for y in incomes], label="IS")
    ax.plot(
        incomes,
        [is_interest(y, after, mpc, b) for y in incomes],
        "--",
        label="IS after fiscal policy",
    )
    ax.plot(incomes, [trap_interest, trap_interest], label="LM (liquidity trap)")
    before_income = is_income(trap_interest, intercept, mpc, b)
    after_income = is_income(trap_interest, after, mpc, b)
    ax.plot([before_income], [trap_interest], "o", label="Equilibrium before")
    ax.plot([after_income], [trap_interest], "s", label="Equilibrium after")
    _style(ax)
    plt.close(fig)
    return fig
