"""第 8 章のアニメーション: 所得が増えると、予算線が平行に動き、最適点が動く。"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

from lib.animations.common import linear_values, make_animation
from lib.chapter07.budget import budget_intercepts
from lib.chapter08.utility import (
    cobb_douglas_demand,
    cobb_douglas_indifference_y,
    cobb_douglas_utility,
)


@dataclass(frozen=True)
class BudgetFrame:
    """1 フレームの所得・最適点・そのときの効用・予算線の切片。"""

    income: float
    bundle: tuple[float, float]
    level: float
    intercepts: tuple[float, float]


def budget_moves_frames(
    prices: Sequence[float],
    share: float,
    min_income: float,
    max_income: float,
    frames: int,
) -> list[BudgetFrame]:
    """所得を min_income から max_income へ動かしたときの、各フレームの最適点。"""
    result = []
    for income in linear_values(min_income, max_income, frames):
        bundle = cobb_douglas_demand(prices, income, share)
        x_end, y_end = budget_intercepts(prices, income)
        level = cobb_douglas_utility(*bundle, share)
        result.append(BudgetFrame(income, bundle, level, (x_end, y_end)))
    return result


def animate_budget_moves(
    prices: Sequence[float] = (1, 2),
    share: float = 0.5,
    min_income: float = 8.0,
    max_income: float = 40.0,
    frames: int = 25,
) -> FuncAnimation:
    """所得が増えると、予算線が外へ平行に動き、最適点が所得拡張経路の上を動く。"""
    data = budget_moves_frames(prices, share, min_income, max_income, frames)
    x_limit, y_limit = (1.1 * v for v in data[-1].intercepts)
    fig, ax = plt.subplots()
    first = data[0].intercepts
    ax.plot([0, first[0]], [first[1], 0], color="gray", label="Budget (first income)")
    (budget,) = ax.plot([], [], color="C0", label="Budget line")
    (curve,) = ax.plot([], [], color="C2", label="Indifference curve")
    (path,) = ax.plot([], [], "o-", color="C3", markersize=3, label="Optimal bundles")
    label = ax.set_title("", fontsize="small")
    ax.set_xlim(0, x_limit)
    ax.set_ylim(0, y_limit)
    ax.set_xlabel("Good x")
    ax.set_ylabel("Good y")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        frame = data[i]
        budget.set_data([0, frame.intercepts[0]], [frame.intercepts[1], 0])
        xs = np.linspace(x_limit / 40, x_limit, 100)
        ys = [cobb_douglas_indifference_y(frame.level, float(x), share) for x in xs]
        curve.set_data(xs, ys)
        path.set_data(
            [f.bundle[0] for f in data[: i + 1]], [f.bundle[1] for f in data[: i + 1]]
        )
        label.set_text(
            f"Income = {frame.income:.1f}, optimum = "
            f"({frame.bundle[0]:.1f}, {frame.bundle[1]:.1f}), U = {frame.level:.2f}"
        )

    plt.close(fig)
    return make_animation(fig, update, frames)


ANIMATIONS: dict[str, Callable[[], FuncAnimation]] = {
    "ch08-budget-moves": animate_budget_moves
}
