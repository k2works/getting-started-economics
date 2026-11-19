"""二分法の図。横軸が価格、縦軸が超過需要。"""

from collections.abc import Callable

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

_CURVE_POINTS = 100


def bisection_midpoints(
    excess_demand: Callable[[float], float], low: float, high: float, steps: int
) -> list[float]:
    """二分法で、区間を半分ずつに絞るときの、中点を順に返す。"""
    middles = []
    excess_low = excess_demand(low)
    for _ in range(steps):
        middle = (low + high) / 2
        middles.append(middle)
        excess_middle = excess_demand(middle)
        if excess_low * excess_middle <= 0:
            high = middle
        else:
            low, excess_low = middle, excess_middle
    return middles


def plot_bisection(
    excess_demand: Callable[[float], float], low: float, high: float, steps: int = 6
) -> Figure:
    """超過需要の曲線と、二分法の中点（steps 個）を描く。中点は、0 の線に近づく。"""
    prices = [low + (high - low) * i / _CURVE_POINTS for i in range(_CURVE_POINTS + 1)]
    middles = bisection_midpoints(excess_demand, low, high, steps)

    fig, ax = plt.subplots()
    ax.plot(prices, [excess_demand(p) for p in prices], label="Excess demand")
    ax.plot([low, high], [0, 0], "--", color="gray", label="Zero")
    ax.plot(
        middles,
        [excess_demand(m) for m in middles],
        "o",
        color="black",
        label="Midpoints",
    )
    for number, middle in enumerate(middles, start=1):
        ax.annotate(
            str(number),
            (middle, excess_demand(middle)),
            textcoords="offset points",
            xytext=(4, 6),
        )
    ax.set_xlabel("Price")
    ax.set_ylabel("Excess demand")
    ax.legend()
    plt.close(fig)
    return fig
