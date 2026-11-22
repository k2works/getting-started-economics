"""欠落変数の偏り（第 11 章）、弱い操作変数（第 12 章）、尤度（第 14 章）。"""

from collections.abc import Sequence
from dataclasses import dataclass, replace

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation
from matplotlib.axes import Axes
from matplotlib.container import BarContainer
from numpy.typing import NDArray

from lib.animations.common import histogram_heights, linear_values, make_animation
from lib.chapter03.multiple import design_matrix
from lib.chapter11.endogeneity import simulate_omitted
from lib.chapter12.iv import weak_instrument_experiment
from lib.chapter14.discrete import (
    draw_binary_sample,
    fit_binary,
    log_likelihood,
    predicted_probabilities,
)


def _overlay_bars(
    ax: Axes,
    edges: NDArray[np.float64],
    top: float,
    xlabel: str,
    names: tuple[str, str],
    colors: tuple[str, str],
) -> tuple[BarContainer, BarContainer]:
    """2 つの推定量を重ねて描くための、空のヒストグラム。"""
    ax.set_xlim(edges[0], edges[-1])
    ax.set_ylim(0, top)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Share of samples")
    zeros = [0.0] * (len(edges) - 1)
    first, second = (
        ax.bar(
            edges[:-1],
            zeros,
            width=np.diff(edges),
            align="edge",
            alpha=0.6,
            color=color,
            label=name,
        )
        for name, color in zip(names, colors, strict=True)
    )
    return first, second


def _set_bars(bars: BarContainer, heights: list[float]) -> None:
    for bar, height in zip(bars, heights, strict=True):
        bar.set_height(height)


@dataclass(frozen=True)
class OmittedFrame:
    """x1 と x2 の相関と、x2 を落とした回帰・入れた回帰の、x1 の係数。"""

    correlation: float
    estimates: pd.DataFrame


def omitted_frames(
    correlations: Sequence[float], n: int, repetitions: int, seed: int
) -> list[OmittedFrame]:
    """相関ごとに、同じ種で、短い回帰と長い回帰の係数を繰り返す（真の値は 1）。"""
    return [
        OmittedFrame(
            c, simulate_omitted(n, c, repetitions, np.random.default_rng(seed))
        )
        for c in correlations
    ]


def animate_omitted_variable(
    n: int = 200, repetitions: int = 300, frames: int = 20, seed: int = 0
) -> FuncAnimation:
    """x1 と x2 の相関を上げる。x2 を落とした回帰（赤）だけが、真の値から離れる。"""
    data = omitted_frames(linear_values(0.0, 0.9, frames), n, repetitions, seed)
    edges = np.linspace(0.0, 3.2, 65)
    heights = [
        [histogram_heights(f.estimates[c], edges) for c in ("short", "long")]
        for f in data
    ]
    fig, ax = plt.subplots(figsize=(6, 4))
    short, long = _overlay_bars(
        ax,
        edges,
        1.1 * max(max(h) for pair in heights for h in pair),
        "Estimate of b1",
        ("Without x2 (short)", "With x2 (long)"),
        ("tab:red", "tab:blue"),
    )
    ax.axvline(1.0, color="black", linestyle="--", label="True value")
    ax.legend(fontsize="x-small", loc="upper right")
    text = ax.text(0.02, 0.96, "", transform=ax.transAxes, va="top")

    def update(i: int) -> None:
        _set_bars(short, heights[i][0])
        _set_bars(long, heights[i][1])
        text.set_text(f"corr(x1, x2) = {data[i].correlation:.2f}")

    plt.close(fig)
    return make_animation(fig, update, frames)


@dataclass(frozen=True)
class WeakFrame:
    """操作変数の強さと、OLS・IV の傾きの推定値（繰り返した分）。"""

    strength: float
    estimates: pd.DataFrame


def weak_instrument_frames(
    strengths: Sequence[float], n: int, repetitions: int, seed: int
) -> list[WeakFrame]:
    """操作変数の強さごとに、同じ種で、OLS と IV の傾きを繰り返す（真の傾きは 1）。"""
    return [
        WeakFrame(
            s,
            weak_instrument_experiment(n, s, repetitions, np.random.default_rng(seed)),
        )
        for s in strengths
    ]


def animate_weak_instrument(
    n: int = 100, repetitions: int = 300, frames: int = 20, seed: int = 0
) -> FuncAnimation:
    """操作変数の強さを 1 から 0.05 へ下げる。IV（青）の推定値が、広く散らばる。"""
    data = weak_instrument_frames(
        linear_values(1.0, 0.05, frames), n, repetitions, seed
    )
    edges = np.linspace(-1.0, 3.0, 81)
    heights = [
        [
            histogram_heights(f.estimates[c].clip(edges[0], edges[-1] - 1e-9), edges)
            for c in ("ols", "iv")
        ]
        for f in data
    ]
    fig, ax = plt.subplots(figsize=(6, 4))
    ols, iv = _overlay_bars(
        ax,
        edges,
        1.1 * max(max(h) for pair in heights for h in pair),
        "Estimated slope (clipped at the ends)",
        ("OLS", "IV"),
        ("tab:orange", "tab:blue"),
    )
    ax.axvline(1.0, color="black", linestyle="--", label="True slope")
    ax.legend(fontsize="x-small", loc="upper right")
    text = ax.text(0.02, 0.96, "", transform=ax.transAxes, va="top")

    def update(i: int) -> None:
        _set_bars(ols, heights[i][0])
        _set_bars(iv, heights[i][1])
        text.set_text(f"strength of z = {data[i].strength:.2f}")

    plt.close(fig)
    return make_animation(fig, update, frames)


@dataclass(frozen=True)
class LikelihoodFrame:
    """傾き（定数項は、推定値に固定）と、そのときの確率の曲線・対数尤度。"""

    slope: float
    log_likelihood: float
    grid: NDArray[np.float64]
    curve: NDArray[np.float64]


def likelihood_frames(n: int, frames: int, seed: int) -> list[LikelihoodFrame]:
    """ロジットの傾きを 0 から、推定値の 1.8 倍まで動かして、対数尤度を求める。"""
    sample = draw_binary_sample(n, "logit", np.random.default_rng(seed))
    x, y = sample["x1"].to_numpy(), sample["y"].to_numpy()
    fit = fit_binary(y, x, "logit")
    design, _ = design_matrix(x)
    grid = np.linspace(float(x.min()) - 0.5, float(x.max()) + 0.5, 100)
    result = []
    for slope in linear_values(0.0, 1.8 * fit.coefficients["x1"], frames):
        coefficients = fit.coefficients.copy()
        coefficients["x1"] = slope
        beta = coefficients.to_numpy()
        curve = predicted_probabilities(replace(fit, coefficients=coefficients), grid)
        result.append(
            LikelihoodFrame(
                slope, log_likelihood("logit", y, design, beta), grid, curve
            )
        )
    return result


def animate_likelihood(n: int = 150, frames: int = 30, seed: int = 0) -> FuncAnimation:
    """傾きを動かす。左のロジット曲線が変わり、右の対数尤度が、山を登って下る。"""
    data = likelihood_frames(n, frames, seed)
    sample = draw_binary_sample(n, "logit", np.random.default_rng(seed))
    fig, (left, right) = plt.subplots(1, 2, figsize=(9, 4))
    left.plot(sample["x1"], sample["y"], "o", alpha=0.3, label="Data")
    (curve,) = left.plot([], [], label="Logit curve")
    left.set_xlim(float(data[0].grid[0]), float(data[0].grid[-1]))
    left.set_ylim(-0.05, 1.05)
    left.set_xlabel("x")
    left.set_ylabel("P(y = 1)")
    left.legend(fontsize="x-small", loc="upper left")
    right.plot(
        [f.slope for f in data],
        [f.log_likelihood for f in data],
        color="gray",
        label="Log-likelihood",
    )
    (now,) = right.plot([], [], "o", color="tab:red", label="Now")
    right.set_xlabel("Slope")
    right.set_ylabel("Log-likelihood")
    right.legend(fontsize="x-small", loc="lower center")

    def update(i: int) -> None:
        frame = data[i]
        curve.set_data(frame.grid, frame.curve)
        now.set_data([frame.slope], [frame.log_likelihood])

    plt.close(fig)
    return make_animation(fig, update, len(data))
