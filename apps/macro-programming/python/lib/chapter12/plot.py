"""為替レートの図。"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from lib.chapter12.exchange import real_exchange_rate


def plot_exchange_rates(df: pd.DataFrame, break_period: str) -> Figure:
    """名目と実質の為替レートを、最初の四半期 = 100 にそろえて描く。縦線は切り替え。"""
    nominal = df["nominal_rate"] / df["nominal_rate"].iloc[0] * 100
    real = real_exchange_rate(
        df["nominal_rate"], df["price_foreign"], df["price_domestic"]
    )
    real = real / real.iloc[0] * 100
    positions = range(len(df))
    fig, ax = plt.subplots()
    ax.plot(positions, nominal.to_numpy(), label="Nominal")
    ax.plot(positions, real.to_numpy(), label="Real")
    ax.axvline(
        list(df.index).index(pd.Period(break_period, freq="Q")),
        linestyle="--",
        color="gray",
        label="Regime change",
    )
    ax.set_xlabel("Quarter (0 = first quarter)")
    ax.set_ylabel("Exchange rate (first quarter = 100)")
    ax.legend()
    plt.close(fig)
    return fig


def plot_regime_volatility(stats: pd.DataFrame) -> Figure:
    """相場制度ごとの、名目と実質の為替レートの変動の大きさを、棒で描く。"""
    labels = []
    heights = []
    for regime in stats.index:
        for kind in ("nominal", "real"):
            labels.append(f"{regime}\n{kind}")
            heights.append(float(stats.loc[regime, f"{kind}_volatility"]))
    fig, ax = plt.subplots()
    ax.bar(labels, heights)
    ax.set_ylabel("Volatility of quarterly change (%)")
    plt.close(fig)
    return fig
