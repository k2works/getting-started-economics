"""マンデル・フレミング・モデルの図。"""

from dataclasses import replace

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from lib.chapter07.money_market import lm_interest
from lib.chapter08.is_lm import is_interest
from lib.chapter14.mundell_fleming import (
    SmallOpenEconomy,
    fixed_rate_equilibrium,
    floating_rate_equilibrium,
    policy_effects_table,
)

BAR_LABELS = [
    "Fixed\nfiscal",
    "Fixed\nmonetary",
    "Floating\nfiscal",
    "Floating\nmonetary",
]


def _style(ax: Axes, title: str) -> None:
    ax.set_title(title)
    ax.set_xlabel("Income Y")
    ax.set_ylabel("Interest rate r")
    ax.set_ylim(bottom=0)
    ax.legend(fontsize="x-small")


def _spending(economy: SmallOpenEconomy) -> float:
    """為替レートも含めた IS の右辺 A + n·e。"""
    return economy.intercept + economy.n * economy.exchange_rate


def _is_line(economy: SmallOpenEconomy, incomes: list[float]) -> list[float]:
    return [is_interest(y, _spending(economy), economy.mpc, economy.b) for y in incomes]


def _lm_line(
    economy: SmallOpenEconomy, real_money: float, incomes: list[float]
) -> list[float]:
    return [lm_interest(y, real_money, economy.k, economy.h) for y in incomes]


def _fixed_panel(
    ax: Axes, economy: SmallOpenEconomy, fiscal: SmallOpenEconomy, incomes: list[float]
) -> None:
    before = fixed_rate_equilibrium(economy)
    after = fixed_rate_equilibrium(fiscal)
    ax.plot(incomes, _is_line(economy, incomes), label="IS")
    ax.plot(incomes, _is_line(fiscal, incomes), "--", label="IS after fiscal policy")
    ax.plot(incomes, _lm_line(economy, before.real_money, incomes), label="LM")
    ax.plot(
        incomes,
        _lm_line(economy, after.real_money, incomes),
        "--",
        label="LM after fiscal policy",
    )
    ax.plot(incomes, [economy.world_rate] * 2, label="BP")
    ax.plot([before.income], [before.interest], "o", label="Equilibrium before")
    ax.plot([after.income], [after.interest], "s", label="Equilibrium after")
    _style(ax, "Fixed rate")


def _floating_panel(
    ax: Axes, economy: SmallOpenEconomy, fiscal: SmallOpenEconomy, incomes: list[float]
) -> None:
    before = floating_rate_equilibrium(economy)
    after = floating_rate_equilibrium(fiscal)
    adjusted = replace(fiscal, exchange_rate=after.exchange_rate)
    ax.plot(incomes, _is_line(economy, incomes), label="IS")
    ax.plot(incomes, _is_line(fiscal, incomes), "--", label="IS after fiscal policy")
    ax.plot(
        incomes,
        _is_line(adjusted, incomes),
        ":",
        label="IS after exchange rate adjustment",
    )
    ax.plot(incomes, _lm_line(economy, before.real_money, incomes), label="LM")
    ax.plot(incomes, [economy.world_rate] * 2, label="BP")
    ax.plot([after.income], [after.interest], "o", label="Equilibrium")
    _style(ax, "Floating rate")


def plot_fiscal_policy_by_regime(
    economy: SmallOpenEconomy,
    delta_government: float,
    income_min: float,
    income_max: float,
) -> Figure:
    """財政政策の効果。左: 固定相場（BP の上を右へ）、右: 変動相場（動かない）。"""
    incomes = [income_min, income_max]
    fiscal = replace(economy, intercept=economy.intercept + delta_government)
    fig, (left, right) = plt.subplots(1, 2, sharey=True)
    _fixed_panel(left, economy, fiscal, incomes)
    _floating_panel(right, economy, fiscal, incomes)
    plt.close(fig)
    return fig


def plot_policy_effects(
    economy: SmallOpenEconomy, delta_government: float, delta_real_money: float
) -> Figure:
    """固定・変動 × 財政・金融の 4 通りの所得の変化（棒グラフ）。"""
    rows = policy_effects_table(economy, delta_government, delta_real_money)
    fig, ax = plt.subplots()
    ax.bar(BAR_LABELS, [r.income_change for r in rows])
    ax.set_ylabel("Change in income Y")
    plt.close(fig)
    return fig
