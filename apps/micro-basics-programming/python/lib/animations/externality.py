"""外部費用が大きくなると、市場と最適な数量の差（死荷重）が広がる（第 14 章）。"""

from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Polygon

from lib.animations.common import linear_values, make_animation
from lib.chapter14.externality import (
    ExternalityMarket,
    externality_deadweight_loss,
    market_quantity,
    socially_optimal_quantity,
)

_ALPHA = 0.3


@dataclass(frozen=True)
class ExternalityFrame:
    """ある外部費用のもとの、市場の数量・最適な数量・死荷重。"""

    external_cost: float
    market: float
    optimal: float
    loss: float


def externality_frames(
    demand: tuple[float, float],
    cost: tuple[float, float],
    max_external: float,
    frames: int,
) -> list[ExternalityFrame]:
    """外部費用を 0 から max_external へ上げたときの、各フレームのデータ。

    demand は逆需要の (切片 a, 傾き b)、cost は私的限界費用の (切片 c, 傾き d)。
    """
    result = []
    for e in linear_values(0.0, max_external, frames):
        market = ExternalityMarket(demand[0], demand[1], cost[0], cost[1], e)
        result.append(
            ExternalityFrame(
                e,
                market_quantity(market),
                socially_optimal_quantity(market),
                externality_deadweight_loss(market),
            )
        )
    return result


def animate_externality(
    demand: tuple[float, float] = (100.0, 1.0),
    cost: tuple[float, float] = (10.0, 1.0),
    max_external: float = 40.0,
    frames: int = 30,
) -> FuncAnimation:
    """外部費用が増えると、社会的限界費用が上へ動き、最適な数量が減り、死荷重が広がる。"""
    a, b = demand
    c, d = cost
    data = externality_frames(demand, cost, max_external, frames)
    q_max = a / b
    fig, ax = plt.subplots()
    ax.plot([0, q_max], [a, 0], label="Demand")
    ax.plot([0, q_max], [c, c + d * q_max], label="Private marginal cost")
    (social,) = ax.plot([], [], linestyle="--", label="Social marginal cost")
    (market_point,) = ax.plot([], [], "o", label="Market point")
    (optimal_point,) = ax.plot([], [], "o", label="Optimal point")
    area = Polygon(
        [(0, 0)],
        closed=True,
        alpha=_ALPHA,
        label="Deadweight loss",
        facecolor="tab:red",
    )
    ax.add_patch(area)
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.set_xlim(0, q_max)
    ax.set_ylim(0, a)
    ax.set_xlabel("Quantity Q")
    ax.set_ylabel("Price P")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        frame = data[i]
        e = frame.external_cost
        social.set_data([0, q_max], [c + e, c + e + d * q_max])
        market_point.set_data([frame.market], [a - b * frame.market])
        optimal_point.set_data([frame.optimal], [a - b * frame.optimal])
        area.set_xy(
            [
                (frame.optimal, a - b * frame.optimal),
                (frame.market, a - b * frame.market),
                (frame.market, c + d * frame.market + e),
            ]
        )
        label.set_text(f"External cost = {e:.1f}, loss = {frame.loss:.1f}")

    plt.close(fig)
    return make_animation(fig, update, frames)
