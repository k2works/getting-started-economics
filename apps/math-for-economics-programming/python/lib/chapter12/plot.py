"""資本の収束と、貯蓄率と定常状態の消費（黄金律）の図。"""

from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter12.solow import (
    solow_capital_path,
    solow_steady_state_capital,
    solow_steady_state_consumption,
)


def plot_solow_convergence(
    starts: Sequence[float],
    saving: float,
    alpha: float,
    depreciation: float,
    periods: int,
) -> Figure:
    """初期値ごとの資本の経路と、定常状態（水平の点線）を描く。"""
    if not starts:
        raise ValueError("初期値が 1 つ以上必要です")
    steady = solow_steady_state_capital(saving, alpha, depreciation)
    fig, ax = plt.subplots()
    for start in starts:
        path = solow_capital_path(start, saving, alpha, depreciation, periods)
        ax.plot(range(periods + 1), path, label=f"k(0) = {start:g}")
    ax.plot([0, periods], [steady, steady], ":", color="black", label="Steady state")
    ax.set_xlabel("Period t")
    ax.set_ylabel("Capital per worker k")
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig


def plot_golden_rule(
    alpha: float, depreciation: float, savings: Sequence[float]
) -> Figure:
    """貯蓄率（横軸）ごとの定常状態の消費と、黄金律 s = α の点を描く。"""
    if not savings:
        raise ValueError("貯蓄率が 1 つ以上必要です")
    fig, ax = plt.subplots()
    consumption = [
        solow_steady_state_consumption(s, alpha, depreciation) for s in savings
    ]
    ax.plot(savings, consumption, label="Steady-state consumption")
    best = solow_steady_state_consumption(alpha, alpha, depreciation)
    ax.plot([alpha], [best], "ko", label="Golden rule (s = alpha)")
    ax.set_xlabel("Saving rate s")
    ax.set_ylabel("Steady-state consumption c*")
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig
