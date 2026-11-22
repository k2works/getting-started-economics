"""外れ値で回帰直線が動く（第 2 章）。相関が高いと推定値が散らばる（第 3 章）。"""

from collections.abc import Sequence
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation
from numpy.typing import NDArray

from lib.animations.common import linear_values, make_animation
from lib.chapter02.simple import SimpleFit, draw_sample, fit_simple, fitted_values
from lib.chapter03.multiple import multicollinearity_experiment


@dataclass(frozen=True)
class OutlierFrame:
    """外れ値の y の位置と、それを含めた標本・回帰直線。"""

    outlier_y: float
    x: NDArray[np.float64]
    y: NDArray[np.float64]
    fit: SimpleFit


def outlier_frames(
    n: int, outlier_x: float, y_end: float, frames: int, seed: int
) -> list[OutlierFrame]:
    """n 個の標本（y = 1 + 0.5x + u）に 1 点を足し、その y を直線上から動かす。"""
    x, y = draw_sample(n, 1.0, 0.5, 1.0, np.random.default_rng(seed))
    xs = np.append(x, outlier_x)
    result = []
    for outlier_y in linear_values(1.0 + 0.5 * outlier_x, y_end, frames):
        ys = np.append(y, outlier_y)
        result.append(OutlierFrame(outlier_y, xs, ys, fit_simple(xs, ys)))
    return result


def animate_outlier(
    n: int = 20,
    outlier_x: float = 2.5,
    y_end: float = -4.0,
    frames: int = 30,
    seed: int = 0,
) -> FuncAnimation:
    """x の端にある 1 点を下へ動かす。回帰直線が、その点に引きずられる。"""
    data = outlier_frames(n, outlier_x, y_end, frames, seed)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(data[0].x[:-1], data[0].y[:-1], "o", label="Data")
    (moving,) = ax.plot([], [], "o", color="tab:red", label="Moving point")
    (line,) = ax.plot([], [], color="tab:orange", label="Fitted line")
    (reference,) = ax.plot([], [], color="gray", linestyle=":", label="Initial line")
    ends = [float(data[0].x.min()), float(data[0].x.max())]
    reference.set_data(ends, fitted_values(data[0].fit, ends))
    ax.set_xlim(ends[0] - 0.5, ends[1] + 0.5)
    ys = [v for f in data for v in f.y]
    ax.set_ylim(min(ys) - 1, max(ys) + 1)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend(fontsize="x-small", loc="upper left")
    text = ax.text(0.98, 0.04, "", transform=ax.transAxes, ha="right")

    def update(i: int) -> None:
        frame = data[i]
        moving.set_data([outlier_x], [frame.outlier_y])
        line.set_data(ends, fitted_values(frame.fit, ends))
        text.set_text(f"slope = {frame.fit.slope:.2f}")

    plt.close(fig)
    return make_animation(fig, update, frames)


@dataclass(frozen=True)
class CollinearityFrame:
    """x1 と x2 の相関と、2 つの係数の推定値（繰り返した分）。"""

    correlation: float
    estimates: pd.DataFrame


def collinearity_frames(
    correlations: Sequence[float], n: int, repetitions: int, seed: int
) -> list[CollinearityFrame]:
    """相関ごとに、同じ種で、係数の推定を繰り返す（真の値は、どちらも 1）。"""
    return [
        CollinearityFrame(
            c,
            multicollinearity_experiment(
                c, n, repetitions, np.random.default_rng(seed)
            ),
        )
        for c in correlations
    ]


def animate_collinearity(
    n: int = 50,
    repetitions: int = 200,
    frames: int = 20,
    seed: int = 0,
    max_correlation: float = 0.97,
) -> FuncAnimation:
    """x1 と x2 の相関を 0 から上げる。2 つの係数の推定値の散らばりが、伸びていく。"""
    data = collinearity_frames(
        linear_values(0.0, max_correlation, frames), n, repetitions, seed
    )
    fig, ax = plt.subplots(figsize=(5, 5))
    cloud = ax.scatter([], [], s=8, alpha=0.5, label="Estimates")
    ax.plot([1], [1], "*", color="tab:red", markersize=12, label="True value")
    low = min(float(f.estimates.min().min()) for f in data) - 0.2
    high = max(float(f.estimates.max().max()) for f in data) + 0.2
    ax.set_xlim(low, high)
    ax.set_ylim(low, high)
    ax.set_xlabel("Estimate of b1")
    ax.set_ylabel("Estimate of b2")
    ax.legend(fontsize="x-small", loc="upper right")
    text = ax.text(0.02, 0.96, "", transform=ax.transAxes, va="top")

    def update(i: int) -> None:
        frame = data[i]
        cloud.set_offsets(frame.estimates[["x1", "x2"]].to_numpy())
        text.set_text(f"corr(x1, x2) = {frame.correlation:.2f}")

    plt.close(fig)
    return make_animation(fig, update, frames)
