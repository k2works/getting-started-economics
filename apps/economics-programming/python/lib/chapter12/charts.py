"""pandas による経済指標の図示・移動平均・景気動向指数。"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from lib.chapter11.economy import growth_rates, production_gdp, real_gdp


def moving_average(series: pd.Series, window: int) -> pd.Series:
    """window 個ごとの移動平均。最初の window - 1 個は計算できず欠損値になる。"""
    if window < 1:
        raise ValueError("窓の幅は 1 以上でなければならない")
    return series.rolling(window).mean()


def diffusion_index(df: pd.DataFrame) -> pd.Series:
    """景気動向指数（DI）: 前の年より増えた系列の割合（%）。最初の年は含まない。"""
    increased = df.diff().iloc[1:] > 0
    return increased.mean(axis=1) * 100


def plot_gdp_chart(df: pd.DataFrame) -> Figure:
    """名目 GDP と実質 GDP の推移を、1 つの図に描いて返す。"""
    data = pd.DataFrame({"Nominal GDP": production_gdp(df), "Real GDP": real_gdp(df)})
    fig, ax = plt.subplots()
    data.plot(ax=ax)
    ax.set_xlabel("Year")
    ax.set_ylabel("GDP")
    plt.close(fig)
    return fig


def plot_growth_chart(df: pd.DataFrame) -> Figure:
    """実質成長率（%）を、棒グラフにして返す。最初の年は計算できないので除く。"""
    growth = growth_rates(real_gdp(df)).dropna()
    fig, ax = plt.subplots()
    growth.plot.bar(ax=ax)
    ax.set_xlabel("Year")
    ax.set_ylabel("Real growth rate (%)")
    fig.tight_layout()
    plt.close(fig)
    return fig
