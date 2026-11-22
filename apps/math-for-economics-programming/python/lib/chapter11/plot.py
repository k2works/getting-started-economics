"""一様分布の密度と分布関数、オークションの収入の分布、数値積分の誤差の図。"""

from collections.abc import Callable, Sequence
from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from lib.chapter11.auction import (
    expected_auction_revenue_formula,
    simulate_auction_revenues,
)
from lib.chapter11.distribution import uniform_cdf, uniform_density
from lib.chapter11.integral import (
    midpoint_rule_integral,
    quadrature_errors,
    trapezoid_rule_integral,
)


def plot_uniform_distribution(
    low: float, high: float, shaded_low: float, shaded_high: float
) -> Figure:
    """左に密度（塗った面積が確率）、右に分布関数（2 点の高さの差が、同じ確率）。"""
    margin = (high - low) / 2
    xs = np.linspace(low - margin, high + margin, 801).tolist()
    probability = uniform_cdf(shaded_high, low, high) - uniform_cdf(
        shaded_low, low, high
    )
    fig, (density_ax, cdf_ax) = plt.subplots(1, 2, figsize=(10, 4))
    density_ax.plot(
        xs, [uniform_density(x, low, high) for x in xs], label="Density f(x)"
    )
    shaded = np.linspace(shaded_low, shaded_high, 101).tolist()
    density_ax.fill_between(
        shaded,
        [uniform_density(x, low, high) for x in shaded],
        alpha=0.3,
        label=f"P({shaded_low:g} <= X <= {shaded_high:g}) = {probability:.2f}",
    )
    cdf_ax.plot(
        xs, [uniform_cdf(x, low, high) for x in xs], label="Distribution function F(x)"
    )
    cdf_ax.plot(
        [shaded_high, shaded_high],
        [uniform_cdf(shaded_low, low, high), uniform_cdf(shaded_high, low, high)],
        ":",
        lw=3,
        label=f"F({shaded_high:g}) - F({shaded_low:g})",
    )
    for ax, ylabel in [(density_ax, "Density"), (cdf_ax, "Probability P(X <= x)")]:
        ax.set_xlabel("Value x")
        ax.set_ylabel(ylabel)
        ax.set_ylim(top=ax.get_ylim()[1] * 1.3)
        ax.legend(fontsize="small", loc="upper left")
    plt.close(fig)
    return fig


def plot_auction_revenues(bidders: int, rounds: int, seed: int) -> Figure:
    """2 つの方式の、売り手の収入のヒストグラムと、公式の期待収入の縦線。"""
    bins = np.linspace(0, 1, 41).tolist()
    rules: list[tuple[Literal["first", "second"], str]] = [
        ("first", "First-price"),
        ("second", "Second-price"),
    ]
    fig, ax = plt.subplots()
    for rule, label in rules:
        revenues = simulate_auction_revenues(bidders, rounds, seed, rule=rule)
        ax.hist(revenues, bins=bins, density=True, alpha=0.5, label=f"{label} revenue")
    mean = float(expected_auction_revenue_formula(bidders))
    ax.axvline(
        mean,
        ls="--",
        color="black",
        label=f"Expected revenue (n - 1)/(n + 1) = {mean:.3f}",
    )
    ax.set_xlabel("Seller's revenue")
    ax.set_ylabel("Density")
    ax.set_ylim(top=ax.get_ylim()[1] * 1.3)
    ax.legend(fontsize="small")
    plt.close(fig)
    return fig


def plot_integration_errors(
    func: Callable[[float], float],
    exact: float,
    low: float,
    high: float,
    pieces: Sequence[int],
) -> Figure:
    """分割数と誤差を両対数で描く。傾き −2 の直線（誤差 ∝ 1/n²）と比べる。"""
    pieces = list(pieces)
    fig, ax = plt.subplots()
    for label, rule in [
        ("Midpoint rule", midpoint_rule_integral),
        ("Trapezoid rule", trapezoid_rule_integral),
    ]:
        errors = quadrature_errors(rule, func, exact, low, high, pieces)
        ax.plot(pieces, errors, "o-", label=label)
    # 台形法（最後に描いた線）の、最初の点を通る、傾き −2 の直線
    reference = [errors[0] * (pieces[0] / n) ** 2 for n in pieces]
    ax.plot(pieces, reference, "--", color="gray", label="Slope of 1/n^2")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Number of pieces n")
    ax.set_ylabel("Absolute error")
    ax.legend(fontsize="small")
    plt.close(fig)
    return fig
