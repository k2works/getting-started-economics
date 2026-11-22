"""単利・複利・連続複利の増え方の図。左は線形目盛、右は対数目盛。"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from lib.chapter03.interest import compound_amount, continuous_compound_amount


def _draw_growth(ax: Axes, principal: float, rate: float, years: int) -> None:
    """単利の直線・年 1 回の複利の点・連続複利の曲線を、1 つの軸に描く。"""
    annual = list(range(years + 1))
    simple_amounts = [principal * (1 + rate * t) for t in annual]
    ax.plot(annual, simple_amounts, ":", label="Simple interest")
    annual_amounts = [compound_amount(principal, rate, t) for t in annual]
    ax.plot(annual, annual_amounts, "o", markersize=3, label="Annual compounding")
    smooth = np.linspace(0, years, 200)
    smooth_amounts = [continuous_compound_amount(principal, rate, t) for t in smooth]
    ax.plot(smooth, smooth_amounts, label="Continuous compounding")
    ax.set_xlabel("Years")
    ax.legend(fontsize="x-small")


def plot_compound_growth(principal: float, rate: float, years: int) -> Figure:
    """同じ増え方を、線形目盛（左）と対数目盛（右）で、並べて描く。"""
    if years < 1:
        raise ValueError("年数は 1 以上の整数でなければなりません")
    fig, (linear, logarithmic) = plt.subplots(1, 2, figsize=(9, 4))
    _draw_growth(linear, principal, rate, years)
    linear.set_ylabel("Amount")
    _draw_growth(logarithmic, principal, rate, years)
    logarithmic.set_yscale("log")
    logarithmic.set_ylabel("Amount (log scale)")
    fig.tight_layout()
    plt.close(fig)
    return fig
