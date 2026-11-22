"""部分和の収束と、債券価格と利子率の図。"""

from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter04.sequence import (
    coupon_bond_price,
    geometric_series_limit,
    partial_sums,
)


def plot_partial_sums(first: float, ratio: float, n: int) -> Figure:
    """第 1〜n 項までの部分和（点）と、無限級数の値（水平の点線）を描く。"""
    limit = geometric_series_limit(first, ratio)
    terms = list(range(1, n + 1))
    fig, ax = plt.subplots()
    ax.plot(terms, partial_sums(first, ratio, n), "o-", label="Partial sum")
    ax.plot([1, n], [limit, limit], ":", color="black", label="Infinite series")
    ax.set_xlabel("Number of terms")
    ax.set_ylabel("Sum")
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig


def plot_bond_prices(
    face: float, coupon: float, years: int, rates: Sequence[float]
) -> Figure:
    """利子率（横軸、%）ごとの利付債の価格と、価格が額面に等しくなる点を描く。"""
    fig, ax = plt.subplots()
    prices = [coupon_bond_price(face, coupon, r, years) for r in rates]
    ax.plot([r * 100 for r in rates], prices, label="Bond price")
    ax.plot([coupon / face * 100], [face], "ko", label="Price = face value")
    ax.set_xlabel("Interest rate (%)")
    ax.set_ylabel("Bond price")
    ax.legend(fontsize="x-small")
    plt.close(fig)
    return fig
