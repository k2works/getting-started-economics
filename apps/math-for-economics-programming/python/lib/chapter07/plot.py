"""予算線と法線ベクトル（価格ベクトル）、労働と余暇の予算線の図。"""

from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from lib.chapter07.budget import (
    budget_intercepts,
    budget_status,
    consumption_given_leisure,
)
from lib.chapter07.vectors import vector_length

_STATUS_STYLES = {
    "inside": ("Inside", "o"),
    "on": ("On the line", "s"),
    "outside": ("Outside", "x"),
}


def _plot_price_vector(ax: Axes, prices: Sequence[float], income: float) -> None:
    """予算線の中点から、価格ベクトルの向きに矢印を描く（長さは、小さい切片の 1/4）。"""
    x_end, y_end = budget_intercepts(prices, income)
    start = (x_end / 2, y_end / 2)
    scale = min(x_end, y_end) / 4 / vector_length(prices)
    end = (start[0] + scale * prices[0], start[1] + scale * prices[1])
    ax.plot(
        [start[0], end[0]],
        [start[1], end[1]],
        color="C3",
        label="Price vector (normal)",
    )
    ax.annotate(
        "", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "color": "C3"}
    )


def plot_budget_set(
    prices: Sequence[float], income: float, bundles: Sequence[Sequence[float]]
) -> Figure:
    """2 財の予算線・予算内の領域・価格ベクトル（法線）と、財の組合せの点を描く。"""
    if len(prices) != 2:
        raise ValueError("予算の図は、2 財のときだけ描きます")
    x_end, y_end = budget_intercepts(prices, income)
    fig, ax = plt.subplots()
    ax.fill_between([0, x_end], [y_end, 0], alpha=0.2, label="Affordable set")
    ax.plot([0, x_end], [y_end, 0], color="C0", label="Budget line")
    _plot_price_vector(ax, prices, income)
    for status, (label, marker) in _STATUS_STYLES.items():
        group = [b for b in bundles if budget_status(prices, b, income) == status]
        if group:
            ax.plot([b[0] for b in group], [b[1] for b in group], marker, label=label)
    ax.set_aspect("equal")
    ax.set_xlabel("Good 1")
    ax.set_ylabel("Good 2")
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig


def plot_labor_leisure(
    wage: float, new_wage: float, total_hours: float, nonlabor_income: float
) -> Figure:
    """消費と余暇の予算線（賃金 wage）と、賃金が new_wage に上がった後の予算線。"""
    hours = [0, total_hours]
    fig, ax = plt.subplots()
    for w, style, label in [
        (wage, "-", f"Budget (wage {wage:g})"),
        (new_wage, "--", f"Budget after wage rise (wage {new_wage:g})"),
    ]:
        consumption = [
            consumption_given_leisure(h, w, total_hours, nonlabor_income) for h in hours
        ]
        ax.plot(hours, consumption, style, label=label)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Leisure (hours)")
    ax.set_ylabel("Consumption")
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig
