"""第 5 章のアニメーション: 割線の刻み幅 h を縮めると、割線が接線に近づく。"""

import math
from collections.abc import Callable
from typing import NamedTuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

from lib.animations.common import linear_values, make_animation
from lib.chapter05.cost import marginal_cost
from lib.chapter05.derivative import Polynomial, numerical_derivative

_CUBIC = Polynomial((20, 15, -6, 1))  # C(q) = q³ − 6q² + 15q + 20


class SecantFrame(NamedTuple):
    """1 フレームの割線: 刻み幅、傾き（中心差分）、左右の点。"""

    step: float
    slope: float
    left: tuple[float, float]
    right: tuple[float, float]


def secant_frames(
    cost: Polynomial, quantity: float, start: float, end: float, frames: int
) -> list[SecantFrame]:
    """刻み幅を start から end へ、対数で等間隔に縮めたときの、各フレームの割線。"""
    if start <= 0 or end <= 0:
        raise ValueError("刻み幅は、正でなければなりません")
    exponents = linear_values(math.log10(start), math.log10(end), frames)
    result = []
    for exponent in exponents:
        h = 10**exponent
        left, right = quantity - h, quantity + h
        result.append(
            SecantFrame(
                step=h,
                slope=numerical_derivative(cost, quantity, h),
                left=(left, cost(left)),
                right=(right, cost(right)),
            )
        )
    return result


def animate_secant_tangent(
    cost: Polynomial = _CUBIC, quantity: float = 4, frames: int = 25
) -> FuncAnimation:
    """費用曲線の上で、q ± h を結ぶ割線が、h を縮めると、接線（傾き MC）に重なる。"""
    data = secant_frames(cost, quantity, 2, 0.001, frames)
    tangent = marginal_cost(cost, quantity)
    base = cost(quantity)
    xs = np.linspace(0, 2 * quantity, 200).tolist()
    span = [0.0, 2 * quantity]
    fig, ax = plt.subplots()
    ax.plot(xs, [cost(q) for q in xs], label="Cost C(q)")
    ax.plot(
        span,
        [base + tangent * (q - quantity) for q in span],
        ":",
        label="Tangent (slope = MC)",
    )
    (secant,) = ax.plot([], [], "--", label="Secant")
    (ends,) = ax.plot([], [], "o", label="q - h and q + h")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.set_xlabel("Quantity q")
    ax.set_ylabel("Cost")
    ax.set_xlim(*span)
    ax.set_ylim(0, cost(2 * quantity))
    ax.legend(fontsize="x-small", loc="lower right")

    def update(i: int) -> None:
        frame = data[i]
        x0, y0 = frame.left
        secant.set_data(span, [y0 + frame.slope * (q - x0) for q in span])
        ends.set_data([frame.left[0], frame.right[0]], [frame.left[1], frame.right[1]])
        label.set_text(
            f"h = {frame.step:.3g}: secant slope = {frame.slope:.4f} (MC = {tangent:g})"
        )

    plt.close(fig)
    return make_animation(fig, update, frames)


ANIMATIONS: dict[str, Callable[[], FuncAnimation]] = {
    "ch05-secant-tangent": animate_secant_tangent,
}
