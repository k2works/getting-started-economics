"""AR(1) 過程のアニメーション（第 8 章）。"""

from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from numpy.typing import NDArray

from lib.animations.common import linear_values, make_animation
from lib.chapter08.stochastic import ar1_series, sample_autocorrelation


@dataclass(frozen=True)
class Ar1Frame:
    rho: float
    series: NDArray[np.float64]
    autocorrelation: float


def ar1_frames(
    rho_end: float, sigma: float, n: int, seed: int, frames: int
) -> list[Ar1Frame]:
    """ρ を 0 から rho_end へ動かしたときの系列（同じ種で、同じショック）。"""
    result = []
    for rho in linear_values(0.0, rho_end, frames):
        series = ar1_series(rho, sigma, n, np.random.default_rng(seed))
        result.append(Ar1Frame(rho, series, sample_autocorrelation(series, 1)))
    return result


def animate_ar1(
    rho_end: float = 0.98,
    sigma: float = 1.0,
    n: int = 100,
    seed: int = 0,
    frames: int = 25,
) -> FuncAnimation:
    """同じショックで ρ を上げると、系列がなめらかになり、ショックの影響が長く残る。"""
    data = ar1_frames(rho_end, sigma, n, seed, frames)
    bound = 1.1 * max(float(np.abs(f.series).max()) for f in data)
    fig, ax = plt.subplots()
    ax.plot([0, n - 1], [0, 0], "--", color="gray", label="Zero")
    (line,) = ax.plot([], [], label="x(t)")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.set_xlim(0, n - 1)
    ax.set_ylim(-bound, bound)
    ax.set_xlabel("Period t")
    ax.set_ylabel("x(t)")
    ax.legend(fontsize="x-small", loc="lower right")

    def update(i: int) -> None:
        frame = data[i]
        line.set_data(range(len(frame.series)), frame.series)
        label.set_text(f"rho = {frame.rho:.2f}, autocorr = {frame.autocorrelation:.2f}")

    plt.close(fig)
    return make_animation(fig, update, frames)
