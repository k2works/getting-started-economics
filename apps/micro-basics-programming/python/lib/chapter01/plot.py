"""無差別曲線の図。"""

from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from lib.chapter01.utility import (
    concave_curve_y,
    indifference_curve_y,
    perfect_complements_curve,
    perfect_substitutes_curve_y,
)

_POINTS = 50


def _grid(start: float, stop: float) -> list[float]:
    """start から stop までを、_POINTS 点に等分する。"""
    step = (stop - start) / (_POINTS - 1)
    return [start + i * step for i in range(_POINTS)]


def _style(ax: Axes, title: str | None = None) -> None:
    ax.set_xlabel("Good x")
    ax.set_ylabel("Good y")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    if title is not None:
        ax.set_title(title)
    ax.legend(fontsize="x-small")


def plot_indifference_curves(
    levels: Sequence[float], x_min: float, x_max: float
) -> Figure:
    """効用 U = x·y の無差別曲線を、水準ごとに 1 本描く。右上の曲線ほど、効用が高い。"""
    xs = _grid(x_min, x_max)
    fig, ax = plt.subplots()
    for level in levels:
        ax.plot(xs, [indifference_curve_y(level, x) for x in xs], label=f"U = {level}")
    _style(ax)
    plt.close(fig)
    return fig


def plot_special_utilities() -> Figure:
    """完全代替財（直線）・完全補完財（L 字）・原点に凹の曲線を、左右に並べて描く。"""
    fig, (left, middle, right) = plt.subplots(1, 3, figsize=(10, 3.5))
    for level in (20, 40):
        left.plot(
            [0, level / 2],
            [perfect_substitutes_curve_y(level, x, 2, 1) for x in (0, level / 2)],
            label=f"U = {level}",
        )
    _style(left, "Perfect substitutes")
    for level in (4, 8):
        points = perfect_complements_curve(level, 10)
        middle.plot(
            [x for x, _ in points], [y for _, y in points], label=f"U = {level}"
        )
    _style(middle, "Perfect complements")
    for level in (25, 100):
        xs = _grid(0, level**0.5)
        right.plot(xs, [concave_curve_y(level, x) for x in xs], label=f"U = {level}")
    _style(right, "Concave")
    fig.tight_layout()
    plt.close(fig)
    return fig
