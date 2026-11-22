"""供給曲線の導出と、独占（限界費用の変化）のアニメーション（第 7・11 章）。"""

from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Polygon

from lib.animations.common import linear_values, make_animation
from lib.chapter05.cost import CostCurve, average_cost, marginal_cost
from lib.chapter07.supply import profit, profit_maximizing_output
from lib.chapter11.monopoly import (
    MarketOutcome,
    Monopoly,
    competitive_outcome,
    monopoly_outcome,
)

_CURVE = CostCurve(1, -6, 15, 32)
_QUANTITIES = [0.05 * i for i in range(1, 161)]
_ALPHA = 0.3


@dataclass(frozen=True)
class SupplyFrame:
    """ある価格のもとの、利潤最大の生産量と、利潤。"""

    price: float
    quantity: float
    profit: float


def supply_frames(curve: CostCurve, p_max: float, frames: int) -> list[SupplyFrame]:
    """価格を 0 から p_max へ上げたときの、各フレームのデータ。"""
    result = []
    for price in linear_values(0.0, p_max, frames):
        q = profit_maximizing_output(curve, price)
        result.append(SupplyFrame(price, q, profit(curve, price, q)))
    return result


def animate_supply_curve(
    curve: CostCurve = _CURVE, p_max: float = 40.0, frames: int = 40
) -> FuncAnimation:
    """価格が上がると、P = MC の点が動き、利潤の長方形が変わり、供給曲線ができる。"""
    data = supply_frames(curve, p_max, frames)
    fig, ax = plt.subplots()
    ax.plot(_QUANTITIES, [marginal_cost(curve, q) for q in _QUANTITIES], label="MC")
    ax.plot(_QUANTITIES, [average_cost(curve, q) for q in _QUANTITIES], label="AC")
    (trace,) = ax.plot([], [], label="Supply curve")
    (now,) = ax.plot([], [], "o", label="P = MC")
    area = Polygon(
        [(0, 0)], closed=True, alpha=_ALPHA, label="Profit", facecolor="tab:green"
    )
    ax.add_patch(area)
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.set_xlim(0, 8)
    ax.set_ylim(0, p_max)
    ax.set_xlabel("Quantity q")
    ax.set_ylabel("Price P")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        frame = data[i]
        so_far = data[: i + 1]
        trace.set_data([f.quantity for f in so_far], [f.price for f in so_far])
        now.set_data([frame.quantity], [frame.price])
        if frame.quantity > 0:
            cost = average_cost(curve, frame.quantity)
            area.set_xy(
                [
                    (0, cost),
                    (frame.quantity, cost),
                    (frame.quantity, frame.price),
                    (0, frame.price),
                ]
            )
        else:
            area.set_xy([(0, 0)])
        label.set_text(f"P = {frame.price:.1f}, profit = {frame.profit:.1f}")

    plt.close(fig)
    return make_animation(fig, update, frames)


@dataclass(frozen=True)
class MonopolyFrame:
    """ある限界費用のもとの、独占と完全競争の結果。"""

    cost: float
    monopoly: MarketOutcome
    competitive: MarketOutcome


def monopoly_frames(
    intercept: float, slope: float, max_cost: float, frames: int
) -> list[MonopolyFrame]:
    """限界費用を 0 から max_cost へ上げたときの、各フレームのデータ。"""
    result = []
    for cost in linear_values(0.0, max_cost, frames):
        demand = Monopoly(intercept, slope, cost)
        result.append(
            MonopolyFrame(cost, monopoly_outcome(demand), competitive_outcome(demand))
        )
    return result


def animate_monopoly_cost(
    intercept: float = 100.0,
    slope: float = 1.0,
    max_cost: float = 40.0,
    frames: int = 30,
) -> FuncAnimation:
    """限界費用が上がると、MR = MC の点が動き、利潤と死荷重が変わる。"""
    data = monopoly_frames(intercept, slope, max_cost, frames)
    fig, ax = plt.subplots()
    ax.plot([0, intercept / slope], [intercept, 0], label="Demand")
    ax.plot([0, intercept / (2 * slope)], [intercept, 0], label="Marginal revenue")
    (cost_line,) = ax.plot([], [], label="Marginal cost")
    (mono_point,) = ax.plot([], [], "o", label="Monopoly")
    (comp_point,) = ax.plot([], [], "o", label="Competition")
    profit_area = Polygon(
        [(0, 0)], closed=True, alpha=_ALPHA, label="Profit", facecolor="tab:green"
    )
    loss_area = Polygon(
        [(0, 0)],
        closed=True,
        alpha=_ALPHA,
        label="Deadweight loss",
        facecolor="tab:red",
    )
    ax.add_patch(profit_area)
    ax.add_patch(loss_area)
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.set_xlim(0, intercept / slope)
    ax.set_ylim(0, intercept)
    ax.set_xlabel("Quantity Q")
    ax.set_ylabel("Price P")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        frame = data[i]
        m, c, cost = frame.monopoly, frame.competitive, frame.cost
        cost_line.set_data([0, intercept / slope], [cost, cost])
        mono_point.set_data([m.quantity], [m.price])
        comp_point.set_data([c.quantity], [c.price])
        profit_area.set_xy(
            [(0, m.price), (m.quantity, m.price), (m.quantity, cost), (0, cost)]
        )
        loss_area.set_xy(
            [(m.quantity, m.price), (m.quantity, cost), (c.quantity, cost)]
        )
        label.set_text(f"MC = {cost:.1f}, P = {m.price:.1f}, Q = {m.quantity:.1f}")

    plt.close(fig)
    return make_animation(fig, update, frames)
