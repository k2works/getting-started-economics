"""信頼区間（第 5 章）と、標本の大きさによる推定値の集まり（第 6 章）。"""

from collections.abc import Sequence
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from numpy.typing import NDArray

from lib.animations.common import histogram_heights, make_animation
from lib.chapter05.inference import slope_intervals
from lib.chapter06.asymptotics import consistency_experiment

_TRUE_SLOPE = 0.5


@dataclass(frozen=True)
class CoverageFrame:
    """i 番目の標本の信頼区間と、真の値を含むか、ここまでに含んだ数。"""

    lower: float
    upper: float
    contains: bool
    covered: int


def coverage_frames(
    n: int, repetitions: int, level: float, seed: int
) -> list[CoverageFrame]:
    """標本を取り直して作った信頼区間を、1 本ずつ並べる（真の傾きは 0.5）。"""
    table = slope_intervals(n, repetitions, level, np.random.default_rng(seed))
    result = []
    covered = 0
    for lower, upper in zip(table["lower"], table["upper"], strict=True):
        contains = bool(lower <= _TRUE_SLOPE <= upper)
        covered += contains
        result.append(CoverageFrame(float(lower), float(upper), contains, covered))
    return result


def animate_confidence_intervals(
    n: int = 30, repetitions: int = 60, level: float = 0.95, seed: int = 0
) -> FuncAnimation:
    """標本ごとの信頼区間を、1 本ずつ足す。真の値を外した区間は、赤で示す。"""
    data = coverage_frames(n, repetitions, level, seed)
    fig, ax = plt.subplots(figsize=(7, 4))
    lines = []
    for i, frame in enumerate(data):
        color = "tab:blue" if frame.contains else "tab:red"
        (line,) = ax.plot([i, i], [frame.lower, frame.upper], color=color)
        line.set_visible(False)
        lines.append(line)
    ax.axhline(_TRUE_SLOPE, color="black", linestyle="--", label="True value")
    ax.set_xlim(-1, repetitions)
    ax.set_xlabel("Sample")
    ax.set_ylabel(f"{level:.0%} confidence interval of the slope")
    ax.legend(fontsize="x-small", loc="upper right")
    text = ax.text(0.02, 0.96, "", transform=ax.transAxes, va="top")

    def update(i: int) -> None:
        lines[i].set_visible(True)
        text.set_text(f"{data[i].covered} of {i + 1} contain the true value")

    plt.close(fig)
    return make_animation(fig, update, len(data))


@dataclass(frozen=True)
class ConsistencyFrame:
    """標本の大きさと、傾きの推定値（繰り返した分）。"""

    size: int
    slopes: NDArray[np.float64]


def consistency_frames(
    sizes: Sequence[int], repetitions: int, seed: int
) -> list[ConsistencyFrame]:
    """標本の大きさごとに、傾きの推定値を繰り返し求める（真の傾きは 0.5）。"""
    estimates = consistency_experiment(
        list(sizes), repetitions, np.random.default_rng(seed)
    )
    return [ConsistencyFrame(n, estimates[n]) for n in sizes]


def animate_consistency(
    sizes: Sequence[int] = (20, 30, 50, 100, 200, 500, 1000),
    repetitions: int = 300,
    seed: int = 0,
) -> FuncAnimation:
    """標本の大きさを増やす。推定値のヒストグラムが、真の値のまわりに集まっていく。"""
    data = consistency_frames(sizes, repetitions, seed)
    edges = np.linspace(-0.2, 1.2, 57)
    heights = [histogram_heights(f.slopes, edges) for f in data]
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(
        edges[:-1], [0.0] * (len(edges) - 1), width=np.diff(edges), align="edge"
    )
    ax.axvline(_TRUE_SLOPE, color="red", label="True slope")
    ax.set_xlim(edges[0], edges[-1])
    ax.set_ylim(0, 1.1 * max(max(h) for h in heights))
    ax.set_xlabel("Estimated slope")
    ax.set_ylabel("Share of samples")
    ax.legend(fontsize="x-small", loc="upper right")
    text = ax.text(0.02, 0.96, "", transform=ax.transAxes, va="top")

    def update(i: int) -> None:
        for bar, height in zip(bars, heights[i], strict=True):
            bar.set_height(height)
        text.set_text(f"n = {data[i].size}")

    plt.close(fig)
    return make_animation(fig, update, len(data))
