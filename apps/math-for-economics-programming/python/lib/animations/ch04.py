"""第 4 章のアニメーション: 等比級数の項を 1 つずつ足し、部分和が無限級数に近づく。"""

from collections.abc import Callable
from typing import NamedTuple

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from lib.animations.common import make_animation
from lib.chapter04.sequence import geometric_partial_sum, geometric_series_limit


class SeriesFrame(NamedTuple):
    """1 フレーム: 足した項数、部分和、無限級数との差（無限級数 − 部分和）。"""

    terms: int
    partial_sum: float
    gap: float


def series_frames(first: float, ratio: float, terms: int) -> list[SeriesFrame]:
    """第 1 項から第 terms 項まで、1 つずつ足したときの、各フレームの部分和と差。"""
    limit = geometric_series_limit(first, ratio)
    frames = []
    for n in range(1, terms + 1):
        partial = geometric_partial_sum(first, ratio, n)
        frames.append(SeriesFrame(n, partial, limit - partial))
    return frames


def animate_series_converge(
    first: float = 2.0, ratio: float = 0.6, terms: int = 15
) -> FuncAnimation:
    """部分和の棒が、1 本ずつ増え、無限級数の値（点線）に近づく。

    最新の部分和の棒を、橙色にする。
    """
    data = series_frames(first, ratio, terms)
    limit = geometric_series_limit(first, ratio)
    fig, ax = plt.subplots()
    bars = ax.bar(
        [f.terms for f in data],
        [0.0] * len(data),
        color="tab:blue",
        label="Partial sum",
    )
    ax.plot([0.5, terms + 0.5], [limit, limit], ":", color="black", label="Limit")
    heights = [f.partial_sum for f in data]
    ax.set_ylim(min(0.0, *heights) * 1.1, max(limit, *heights) * 1.35)
    ax.set_xlabel("Number of terms")
    ax.set_ylabel("Sum")
    ax.legend(fontsize="x-small", loc="upper right")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")

    def update(i: int) -> None:
        for k, bar in enumerate(bars):
            bar.set_height(data[k].partial_sum if k <= i else 0.0)
            bar.set_color("tab:orange" if k == i else "tab:blue")
        frame = data[i]
        label.set_text(
            f"{frame.terms} terms: sum = {frame.partial_sum:.4f}, gap = {frame.gap:.4f}"
        )

    plt.close(fig)
    return make_animation(fig, update, len(data))


ANIMATIONS: dict[str, Callable[[], FuncAnimation]] = {
    "ch04-series-converge": animate_series_converge,
}
