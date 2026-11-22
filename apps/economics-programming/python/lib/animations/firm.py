"""利潤最大化・独占・クールノー競争のアニメーション（第 10・15 章）。"""

from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Polygon

from lib.animations.common import linear_values, make_animation
from lib.chapter01.demand import choke_price
from lib.chapter04.cost import average_cost, average_variable_cost, marginal_cost
from lib.chapter07.surplus import inverse_demand
from lib.chapter10.optimization import profit_maximizing_quantity
from lib.chapter15.monopoly import (
    MonopolyOutcome,
    competitive_quantity,
    marginal_revenue,
    monopoly_outcome,
)
from lib.chapter15.oligopoly import best_response

_ALPHA = 0.4


def _patch(label: str, color: str) -> Polygon:
    return Polygon([(0, 0)], closed=True, alpha=_ALPHA, label=label, facecolor=color)


@dataclass(frozen=True)
class ProfitFrame:
    """ある価格での、利潤を最大にする生産量と、そのときの利潤。"""

    price: float
    quantity: float
    profit: float


def profit_frames(
    start_price: float, end_price: float, frames: int
) -> list[ProfitFrame]:
    """価格を動かしたときの、各フレームの生産量と利潤。停止なら、どちらも 0。"""
    result = []
    for price in linear_values(start_price, end_price, frames):
        quantity = profit_maximizing_quantity(price)
        profit = (price - average_cost(quantity)) * quantity if quantity > 0 else 0.0
        result.append(ProfitFrame(price, quantity, profit))
    return result


def animate_profit_price(
    start_price: float = 4, end_price: float = 24, frames: int = 40
) -> FuncAnimation:
    """価格が AVC の最小を超えると、生産を始め、利潤が増える。"""
    data = profit_frames(start_price, end_price, frames)
    quantities = [6 * i / 60 for i in range(1, 61)]
    fig, ax = plt.subplots()
    ax.plot(quantities, [marginal_cost(q) for q in quantities], label="MC")
    ax.plot(quantities, [average_variable_cost(q) for q in quantities], label="AVC")
    ax.plot(quantities, [average_cost(q) for q in quantities], label="AC")
    (level,) = ax.plot([], [], linestyle="--", color="gray", label="Price")
    profit = _patch("Profit (green) / loss (red)", "tab:green")
    ax.add_patch(profit)
    (point,) = ax.plot([], [], "o", color="black", label="Optimum")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 30)
    ax.set_xlabel("Quantity")
    ax.set_ylabel("Cost per unit")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        frame = data[i]
        level.set_data([0, 6], [frame.price, frame.price])
        if frame.quantity > 0:
            cost = average_cost(frame.quantity)
            profit.set_xy(
                [
                    (0, cost),
                    (frame.quantity, cost),
                    (frame.quantity, frame.price),
                    (0, frame.price),
                ]
            )
            profit.set_facecolor("tab:red" if frame.profit < 0 else "tab:green")
            point.set_data([frame.quantity], [frame.price])
        else:
            profit.set_xy([(0, 0)])
            point.set_data([], [])
        label.set_text(
            f"P = {frame.price:.1f}, Q = {frame.quantity:.2f}, "
            f"profit = {frame.profit:.1f}"
        )

    plt.close(fig)
    return make_animation(fig, update, frames)


@dataclass(frozen=True)
class MonopolyFrame:
    """ある限界費用での、独占の結果と、完全競争の数量。"""

    cost: float
    outcome: MonopolyOutcome
    competitive: float


def monopoly_frames(
    demand_intercept: float, demand_slope: float, max_cost: float, frames: int
) -> list[MonopolyFrame]:
    """限界費用を 0 から max_cost へ動かしたときの、各フレームの結果。"""
    return [
        MonopolyFrame(
            cost,
            monopoly_outcome(demand_intercept, demand_slope, cost),
            competitive_quantity(demand_intercept, demand_slope, cost),
        )
        for cost in linear_values(0.0, max_cost, frames)
    ]


def animate_monopoly_cost(
    demand_intercept: float = 100,
    demand_slope: float = 2,
    max_cost: float = 40,
    frames: int = 30,
) -> FuncAnimation:
    """限界費用が上がると、MR = MC の点が動き、利潤の長方形と死荷重の三角形が変わる。"""
    data = monopoly_frames(demand_intercept, demand_slope, max_cost, frames)
    quantities = [float(q) for q in range(int(demand_intercept) + 1)]
    top = choke_price(demand_intercept, demand_slope)
    fig, ax = plt.subplots()
    ax.plot(
        quantities,
        [inverse_demand(q, demand_intercept, demand_slope) for q in quantities],
        label="Demand",
    )
    ax.plot(
        quantities,
        [marginal_revenue(q, demand_intercept, demand_slope) for q in quantities],
        label="MR",
    )
    (cost_line,) = ax.plot([], [], color="tab:red", label="MC")
    profit = _patch("Profit", "tab:green")
    loss = _patch("Deadweight loss", "tab:purple")
    ax.add_patch(profit)
    ax.add_patch(loss)
    (monopoly_point,) = ax.plot([], [], "o", color="black", label="Monopoly")
    (competitive_point,) = ax.plot([], [], "s", color="black", label="Competitive")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.set_xlim(0, demand_intercept)
    ax.set_ylim(0, top)
    ax.set_xlabel("Quantity")
    ax.set_ylabel("Price")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        frame = data[i]
        out, cost = frame.outcome, frame.cost
        cost_line.set_data([0, demand_intercept], [cost, cost])
        profit.set_xy(
            [(0, cost), (out.quantity, cost), (out.quantity, out.price), (0, out.price)]
        )
        loss.set_xy(
            [(out.quantity, out.price), (out.quantity, cost), (frame.competitive, cost)]
        )
        monopoly_point.set_data([out.quantity], [out.price])
        competitive_point.set_data([frame.competitive], [cost])
        label.set_text(
            f"MC = {cost:.1f}, P = {out.price:.1f}, "
            f"profit = {out.profit:.0f}, loss = {out.deadweight_loss:.0f}"
        )

    plt.close(fig)
    return make_animation(fig, update, frames)


def cournot_steps(
    demand_intercept: float,
    demand_slope: float,
    marginal_cost: float,
    rounds: int,
) -> list[tuple[float, float]]:
    """(0, 0) から、企業 1・企業 2 が交互に最適反応をとる、生産量の組の道すじ。"""
    q1, q2 = 0.0, 0.0
    path = [(q1, q2)]
    for _ in range(rounds):
        q1 = best_response(q2, demand_intercept, demand_slope, marginal_cost)
        path.append((q1, q2))
        q2 = best_response(q1, demand_intercept, demand_slope, marginal_cost)
        path.append((q1, q2))
    return path


def animate_cournot_steps(
    demand_intercept: float = 100,
    demand_slope: float = 2,
    cost: float = 10,
    rounds: int = 8,
) -> FuncAnimation:
    """2 社が交互に最適反応をとると、階段状に動いて、反応曲線の交点（均衡）に着く。"""
    path = cournot_steps(demand_intercept, demand_slope, cost, rounds)
    limit = competitive_quantity(demand_intercept, demand_slope, cost)
    others = [limit * i / 40 for i in range(41)]
    reaction = [best_response(q, demand_intercept, demand_slope, cost) for q in others]
    fig, ax = plt.subplots()
    ax.plot(reaction, others, label="Firm 1 best response")
    ax.plot(others, reaction, label="Firm 2 best response")
    (trail,) = ax.plot([], [], color="tab:green", label="Adjustment")
    (point,) = ax.plot([], [], "o", color="black")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.set_xlim(0, limit)
    ax.set_ylim(0, limit)
    ax.set_xlabel("Firm 1 quantity")
    ax.set_ylabel("Firm 2 quantity")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        trail.set_data([q1 for q1, _ in path[: i + 1]], [q2 for _, q2 in path[: i + 1]])
        point.set_data([path[i][0]], [path[i][1]])
        label.set_text(f"q1 = {path[i][0]:.1f}, q2 = {path[i][1]:.1f}")

    plt.close(fig)
    return make_animation(fig, update, len(path))
