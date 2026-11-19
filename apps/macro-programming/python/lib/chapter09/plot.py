"""トレンドと循環の図。"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from lib.chapter09.cycles import hp_trend


def plot_trend(series: pd.Series, smoothing: float = 1600) -> Figure:
    """系列と、その HP トレンドを、重ねて描く。"""
    trend = hp_trend(series, smoothing)
    positions = range(len(series))
    fig, ax = plt.subplots()
    ax.plot(positions, series.to_numpy(), label="Series")
    ax.plot(positions, trend.to_numpy(), label="HP trend")
    ax.set_xlabel("Quarter")
    ax.legend()
    plt.close(fig)
    return fig


def plot_cycle(cycles: pd.DataFrame) -> Figure:
    """循環の系列（列ごと）を、0 の線と一緒に描く。"""
    n = len(cycles)
    fig, ax = plt.subplots()
    for name in cycles.columns:
        ax.plot(range(n), cycles[name].to_numpy(), label=str(name))
    ax.plot([0, n - 1], [0, 0], "--", color="gray", label="Zero")
    ax.set_xlabel("Quarter")
    ax.set_ylabel("Deviation from trend")
    ax.legend()
    plt.close(fig)
    return fig


def plot_volatility(stats: pd.DataFrame) -> Figure:
    """GDP に対する、変数ごとの変動の大きさを、棒で描く（GDP = 1）。"""
    fig, ax = plt.subplots()
    ax.bar([str(i) for i in stats.index], stats["relative_to_gdp"].to_numpy())
    ax.axhline(1, linestyle="--", color="gray", label="GDP")
    ax.set_ylabel("Volatility relative to GDP")
    ax.legend()
    plt.close(fig)
    return fig
