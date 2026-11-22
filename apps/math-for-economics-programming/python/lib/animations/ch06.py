"""第 6 章のアニメーション: テイラー近似の次数を上げると、e^x に近づく。"""

import math
from collections.abc import Callable
from typing import NamedTuple

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from lib.animations.common import linear_values, make_animation
from lib.chapter06.growth import taylor_exp_approximation


class TaylorFrame(NamedTuple):
    """1 つの次数の近似: 曲線の点と、x_point での誤差。"""

    order: int
    xs: list[float]
    approximations: list[float]
    error_at_point: float


def taylor_order_frames(
    x_low: float, x_high: float, max_order: int, x_point: float, points: int
) -> list[TaylorFrame]:
    """次数 0 から max_order までの、各フレームの近似。"""
    if max_order < 0:
        raise ValueError("次数の上限は、0 以上にする")
    xs = linear_values(x_low, x_high, points)
    return [
        TaylorFrame(
            order,
            xs,
            [taylor_exp_approximation(x, order) for x in xs],
            abs(taylor_exp_approximation(x_point, order) - math.exp(x_point)),
        )
        for order in range(max_order + 1)
    ]


def animate_taylor_order(
    x_low: float = -2.0,
    x_high: float = 2.0,
    max_order: int = 6,
    x_point: float = 1.0,
    hold: int = 8,
    points: int = 81,
) -> FuncAnimation:
    """e^x（実線）に、次数を 1 つずつ上げたテイラー近似（破線）が近づく。"""
    data = taylor_order_frames(x_low, x_high, max_order, x_point, points)
    xs = data[0].xs
    fig, ax = plt.subplots()
    ax.plot(xs, [math.exp(x) for x in xs], color="tab:blue", label="e^x")
    (approx,) = ax.plot([], [], "--", color="tab:red", label="Taylor approximation")
    ax.axvline(x_point, color="gray", linestyle=":", label=f"x = {x_point:g}")
    ax.set_xlim(x_low, x_high)
    ax.set_ylim(-2, math.exp(x_high) + 1)
    ax.set_xlabel("x")
    ax.set_ylabel("Value")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.legend(fontsize="x-small", loc="lower right")

    def update(i: int) -> None:
        frame = data[i // hold]
        approx.set_data(frame.xs, frame.approximations)
        label.set_text(
            f"Order {frame.order}, error at x = {x_point:g}: {frame.error_at_point:.4f}"
        )

    plt.close(fig)
    return make_animation(fig, update, len(data) * hold)


ANIMATIONS: dict[str, Callable[[], FuncAnimation]] = {
    "ch06-taylor-order": animate_taylor_order
}
