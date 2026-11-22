"""需要・供給・余剰の図。価格を縦軸、数量を横軸にする。"""

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from lib.chapter01.market import equilibrium


def _demand_line(a: float, b: float) -> tuple[list[float], list[float]]:
    """需要曲線の両端: 数量 0（価格 a/b）から、価格 0（数量 a）まで。"""
    return [0, a], [a / b, 0]


def _supply_line(c: float, d: float, q_max: float) -> tuple[list[float], list[float]]:
    """供給曲線: 価格 0 以上の部分を、数量 q_max まで。"""
    q_start = max(c, 0)
    return [q_start, q_max], [max(-c / d, 0), (q_max - c) / d]


def _style(ax: Axes) -> None:
    ax.set_xlabel("Quantity")
    ax.set_ylabel("Price")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend(fontsize="x-small")


def plot_market(a: float, b: float, c: float, d: float) -> Figure:
    """需要・供給・均衡の点と、消費者余剰・生産者余剰を描く。"""
    eq = equilibrium(a, b, c, d)
    fig, ax = plt.subplots()
    q_max = a
    ax.plot(*_demand_line(a, b), label="Demand")
    ax.plot(*_supply_line(c, d, q_max), label="Supply")
    ax.plot([eq.quantity], [eq.price], "ko", label="Equilibrium")
    supply_q, supply_p = _supply_line(c, d, q_max)
    ax.fill(
        [0, eq.quantity, 0],
        [a / b, eq.price, eq.price],
        alpha=0.3,
        color="tab:blue",
        label="Consumer surplus",
    )
    ax.fill(
        [supply_q[0], eq.quantity, 0, 0],
        [supply_p[0], eq.price, eq.price, supply_p[0]],
        alpha=0.3,
        color="tab:green",
        label="Producer surplus",
    )
    _style(ax)
    plt.close(fig)
    return fig


def plot_harvest_paradox(
    a: float, b: float, c: float, d: float, c_after: float
) -> Figure:
    """供給が増える（切片が c から c_after に増える）前後の均衡を、並べて描く。"""
    before = equilibrium(a, b, c, d)
    after = equilibrium(a, b, c_after, d)
    fig, ax = plt.subplots()
    q_max = a
    ax.plot(*_demand_line(a, b), label="Demand")
    ax.plot(*_supply_line(c, d, q_max), label="Supply before")
    ax.plot(*_supply_line(c_after, d, q_max), "--", label="Supply after")
    ax.plot([before.quantity], [before.price], "ko", label="Equilibrium before")
    ax.plot([after.quantity], [after.price], "ro", label="Equilibrium after")
    _style(ax)
    plt.close(fig)
    return fig
