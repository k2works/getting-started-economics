"""価格の調整と従量税のアニメーション（第 5・7 章）。"""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.axes import Axes
from matplotlib.patches import Polygon

from lib.animations.common import linear_values, make_animation
from lib.chapter05.adjustment import walras_path
from lib.chapter07.surplus import (
    TaxEquilibrium,
    equilibrium,
    equilibrium_with_tax,
    inverse_demand,
)

_ALPHA = 0.4
_QUANTITIES = [float(q) for q in range(0, 101)]


def _patch(label: str, color: str) -> Polygon:
    return Polygon([(0, 0)], closed=True, alpha=_ALPHA, label=label, facecolor=color)


def _draw_market(
    ax: Axes,
    demand_intercept: float,
    demand_slope: float,
    supply_intercept: float,
    supply_slope: float,
) -> None:
    ax.plot(
        _QUANTITIES,
        [inverse_demand(q, demand_intercept, demand_slope) for q in _QUANTITIES],
        label="Demand",
    )
    ax.plot(
        _QUANTITIES,
        [(q - supply_intercept) / supply_slope for q in _QUANTITIES],
        label="Supply",
    )
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 50)
    ax.set_xlabel("Quantity")
    ax.set_ylabel("Price")


def walras_frames(
    demand_intercept: float,
    demand_slope: float,
    supply_intercept: float,
    supply_slope: float,
    initial_price: float,
    step: float,
) -> list[float]:
    """ワルラス調整の価格の推移。各フレームが、調整の 1 回分。"""
    return walras_path(
        lambda p: demand_intercept - demand_slope * p,
        lambda p: supply_intercept + supply_slope * p,
        initial_price,
        step,
    )


def animate_walras(
    demand_intercept: float = 100,
    demand_slope: float = 2,
    supply_intercept: float = 0,
    supply_slope: float = 3,
    initial_price: float = 40,
    step: float = 0.3,
) -> FuncAnimation:
    """価格が、超過需要に応じて上下に揺れながら、均衡価格へ近づく。"""
    path = walras_frames(
        demand_intercept,
        demand_slope,
        supply_intercept,
        supply_slope,
        initial_price,
        step,
    )
    fig, ax = plt.subplots()
    _draw_market(ax, demand_intercept, demand_slope, supply_intercept, supply_slope)
    price, _ = equilibrium(
        demand_intercept, demand_slope, supply_intercept, supply_slope
    )
    ax.plot([0, 100], [price, price], linestyle=":", color="gray", label="Equilibrium")
    (level,) = ax.plot([], [], linestyle="--", color="tab:green", label="Price")
    (gap,) = ax.plot([], [], color="tab:red", label="Excess demand")
    (demanded,) = ax.plot([], [], "o", color="tab:blue")
    (supplied,) = ax.plot([], [], "o", color="tab:orange")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        p = path[i]
        qd = demand_intercept - demand_slope * p
        qs = supply_intercept + supply_slope * p
        level.set_data([0, 100], [p, p])
        gap.set_data([qs, qd], [p, p])
        demanded.set_data([qd], [p])
        supplied.set_data([qs], [p])
        state = "excess supply" if qd < qs else "excess demand"
        label.set_text(f"Step {i}: P = {p:.1f} ({state})")

    plt.close(fig)
    return make_animation(fig, update, len(path))


def tax_frames(
    demand_intercept: float,
    demand_slope: float,
    supply_intercept: float,
    supply_slope: float,
    max_tax: float,
    frames: int,
) -> list[TaxEquilibrium]:
    """税額を 0 から max_tax へ動かしたときの、各フレームの均衡。"""
    return [
        equilibrium_with_tax(
            demand_intercept, demand_slope, supply_intercept, supply_slope, tax
        )
        for tax in linear_values(0.0, max_tax, frames)
    ]


def animate_tax_wedge(
    demand_intercept: float = 100,
    demand_slope: float = 2,
    supply_intercept: float = 0,
    supply_slope: float = 3,
    max_tax: float = 15,
    frames: int = 30,
) -> FuncAnimation:
    """税額が増えると、供給曲線が上へ動き、税収の長方形と死荷重の三角形が現れる。"""
    taxes = linear_values(0.0, max_tax, frames)
    data = tax_frames(
        demand_intercept, demand_slope, supply_intercept, supply_slope, max_tax, frames
    )
    price, quantity = equilibrium(
        demand_intercept, demand_slope, supply_intercept, supply_slope
    )
    fig, ax = plt.subplots()
    _draw_market(ax, demand_intercept, demand_slope, supply_intercept, supply_slope)
    (shifted,) = ax.plot([], [], linestyle="--", label="Supply + tax")
    revenue = _patch("Tax revenue", "tab:green")
    loss = _patch("Deadweight loss", "tab:red")
    ax.add_patch(revenue)
    ax.add_patch(loss)
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        tax, frame = taxes[i], data[i]
        shifted.set_data(
            _QUANTITIES,
            [(q - supply_intercept) / supply_slope + tax for q in _QUANTITIES],
        )
        q, pc, pp = frame.quantity, frame.consumer_price, frame.producer_price
        revenue.set_xy([(0, pp), (q, pp), (q, pc), (0, pc)])
        loss.set_xy([(q, pp), (quantity, price), (q, pc)])
        label.set_text(
            f"Tax = {tax:.1f}, revenue = {frame.tax_revenue:.1f}, "
            f"loss = {frame.deadweight_loss:.1f}"
        )

    plt.close(fig)
    return make_animation(fig, update, frames)
