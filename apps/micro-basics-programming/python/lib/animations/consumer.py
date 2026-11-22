"""価格が下がると、予算線が回り、最適点が動いて、需要曲線ができる（第 2・3 章）。"""

from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from lib.animations.common import linear_values, make_animation
from lib.chapter01.utility import cobb_douglas_utility, indifference_curve_y
from lib.chapter02.budget import budget_intercepts, optimal_bundle

_GRID = [float(x) for x in range(1, 101)]


@dataclass(frozen=True)
class PriceFrame:
    """ある価格のもとの、最適消費点・予算線の切片・無差別曲線の水準。"""

    price: float
    bundle: tuple[float, float]
    intercepts: tuple[float, float]
    level: float


def price_change_frames(
    income: float, py: float, p_start: float, p_end: float, frames: int
) -> list[PriceFrame]:
    """財 x の価格を p_start から p_end へ動かしたときの、各フレームのデータ。"""
    result = []
    for px in linear_values(p_start, p_end, frames):
        x, y = optimal_bundle(income, px, py)
        result.append(
            PriceFrame(
                px,
                (x, y),
                budget_intercepts(income, px, py),
                cobb_douglas_utility(x, y),
            )
        )
    return result


def animate_price_change(
    income: float = 100.0,
    py: float = 1.0,
    p_start: float = 4.0,
    p_end: float = 1.0,
    frames: int = 30,
) -> FuncAnimation:
    """左: 予算線・無差別曲線・最適点。右: 最適点の x と価格から、需要曲線を描く。"""
    data = price_change_frames(income, py, p_start, p_end, frames)
    fig, (left, right) = plt.subplots(1, 2, figsize=(9, 4))
    (budget,) = left.plot([], [], label="Budget line")
    (curve,) = left.plot([], [], label="Indifference curve")
    (point,) = left.plot([], [], "o", label="Optimum")
    left.set_xlim(0, 110)
    left.set_ylim(0, 1.1 * income / py)
    left.set_xlabel("Good x")
    left.set_ylabel("Good y")
    left.legend(fontsize="x-small")
    (trace,) = right.plot([], [], label="Demand curve")
    (now,) = right.plot([], [], "o", label="Now")
    right.set_xlim(0, 110)
    right.set_ylim(0, 1.1 * max(p_start, p_end))
    right.set_xlabel("Good x")
    right.set_ylabel("Price Px")
    right.legend(fontsize="x-small")

    def update(i: int) -> None:
        frame = data[i]
        budget.set_data([0, frame.intercepts[0]], [frame.intercepts[1], 0])
        curve.set_data(_GRID, [indifference_curve_y(frame.level, x) for x in _GRID])
        point.set_data([frame.bundle[0]], [frame.bundle[1]])
        so_far = data[: i + 1]
        trace.set_data([f.bundle[0] for f in so_far], [f.price for f in so_far])
        now.set_data([frame.bundle[0]], [frame.price])

    plt.close(fig)
    return make_animation(fig, update, frames)
