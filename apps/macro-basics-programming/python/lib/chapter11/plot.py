"""フィリップス曲線とオークンの法則の図。"""

from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter11.okun import OkunFit
from lib.chapter11.phillips import short_run_inflation


def plot_phillips(
    natural_rate: float,
    expected_inflations: Sequence[float],
    beta: float,
    u_min: float,
    u_max: float,
) -> Figure:
    """短期のフィリップス曲線（期待インフレ率ごと）と、長期の垂直線。"""
    fig, ax = plt.subplots()
    unemployments = [u_min, u_max]
    all_rates: list[float] = []
    for expected in expected_inflations:
        rates = [
            short_run_inflation(u, natural_rate, expected, beta) for u in unemployments
        ]
        all_rates += rates
        ax.plot(
            unemployments, rates, label=f"Short run (expected inflation {expected})"
        )
    ax.plot(
        [natural_rate, natural_rate],
        [min(all_rates), max(all_rates)],
        label="Long run",
    )
    ax.set_xlabel("Unemployment rate (%)")
    ax.set_ylabel("Inflation rate (%)")
    ax.legend()
    plt.close(fig)
    return fig


def plot_okun(
    growth: Sequence[float], unemployment_change: Sequence[float], fit: OkunFit
) -> Figure:
    """成長率と失業率の変化の散布図と、回帰直線。"""
    fig, ax = plt.subplots()
    ax.plot(growth, unemployment_change, "o", label="Quarterly data")
    ends = [min(growth), max(growth)]
    ax.plot(ends, [fit.intercept + fit.slope * g for g in ends], label="Fitted line")
    ax.set_xlabel("Growth rate (%)")
    ax.set_ylabel("Change in unemployment rate (points)")
    ax.legend()
    plt.close(fig)
    return fig
