"""貨幣乗数と信用創造の図。"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter06.money_supply import credit_creation_path, money_multiplier


def plot_money_multiplier(
    cash_ratios: list[float], reserve_ratios: list[float]
) -> Figure:
    """現金預金比率 C/D を横軸に、準備預金比率 R/D ごとの貨幣乗数を描く。"""
    fig, ax = plt.subplots()
    for reserve_ratio in reserve_ratios:
        ax.plot(
            cash_ratios,
            [money_multiplier(c, reserve_ratio) for c in cash_ratios],
            label=f"R/D = {reserve_ratio}",
        )
    ax.set_xlabel("Cash-deposit ratio C/D")
    ax.set_ylabel("Money multiplier")
    ax.legend()
    plt.close(fig)
    return fig


def plot_credit_creation(
    base: float, cash_ratio: float, reserve_ratio: float, rounds: int
) -> Figure:
    """信用創造のラウンドごとのマネーストックが、上限（乗数 × H）に近づく様子。"""
    path = credit_creation_path(base, cash_ratio, reserve_ratio, rounds)
    limit = money_multiplier(cash_ratio, reserve_ratio) * base
    fig, ax = plt.subplots()
    ax.plot(range(1, rounds + 1), path, label="Money stock after each round")
    ax.plot([1, rounds], [limit, limit], "--", label="Limit (multiplier x H)")
    ax.set_xlabel("Round")
    ax.set_ylabel("Money stock")
    ax.legend()
    plt.close(fig)
    return fig
