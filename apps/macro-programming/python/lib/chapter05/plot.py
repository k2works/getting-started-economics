"""ソロー・モデルの図。"""

from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter05.solow import (
    convergence_speed,
    log_linear_path,
    solow_path,
    steady_state_capital,
)


def plot_solow_diagram(
    saving_rate: float, depreciation: float, alpha: float, technology: float = 1
) -> Figure:
    """ソロー図: 貯蓄 s·A·k^α と減耗 δ·k。交点が定常状態。

    交点の左では、貯蓄が減耗より多く、資本が増える。右では、資本が減る。
    """
    k_star = steady_state_capital(saving_rate, depreciation, alpha, technology)
    ks = [2 * k_star * i / 50 for i in range(51)]
    fig, ax = plt.subplots()
    ax.plot(ks, [saving_rate * technology * k**alpha for k in ks], label="Saving")
    ax.plot(ks, [depreciation * k for k in ks], label="Depreciation")
    ax.plot(
        [k_star],
        [depreciation * k_star],
        "o",
        color="black",
        label="Steady state",
    )
    ax.set_xlabel("Capital per worker k")
    ax.set_ylabel("Saving and depreciation")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend()
    plt.close(fig)
    return fig


def plot_solow_convergence(
    starts: Sequence[float],
    saving_rate: float,
    depreciation: float,
    alpha: float,
    periods: int,
    technology: float = 1,
) -> Figure:
    """初期の資本ごとの経路と、最初の経路の対数線形近似（破線）を描く。"""
    k_star = steady_state_capital(saving_rate, depreciation, alpha, technology)
    fig, ax = plt.subplots()
    for start in starts:
        path = solow_path(start, saving_rate, depreciation, alpha, periods, technology)
        ax.plot(range(periods + 1), path, label=f"k0 = {start}")
    approx = log_linear_path(
        starts[0], k_star, convergence_speed(alpha, depreciation), periods
    )
    ax.plot(
        range(periods + 1),
        approx,
        "--",
        label=f"Log-linear (k0 = {starts[0]})",
    )
    ax.plot([0, periods], [k_star] * 2, ":", color="gray", label="Steady state")
    ax.set_xlabel("Period t")
    ax.set_ylabel("Capital per worker k")
    ax.legend()
    plt.close(fig)
    return fig
