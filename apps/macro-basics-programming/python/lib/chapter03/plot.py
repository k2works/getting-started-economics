"""物価指数と景気動向指数の図。"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure


def plot_price_indexes(table: pd.DataFrame) -> Figure:
    """ラスパイレス指数とパーシェ指数を、期間ごとに、2 本の線で描く。"""
    fig, ax = plt.subplots()
    ax.plot(table.index, table["laspeyres"], marker="o", label="Laspeyres")
    ax.plot(table.index, table["paasche"], marker="s", label="Paasche")
    ax.set_ylabel("Index (base = 1.0)")
    ax.legend()
    plt.close(fig)
    return fig


def plot_business_indexes(di: pd.Series, ci: pd.Series) -> Figure:
    """上に CI（大きさ）を線で、下に DI（方向）を棒で描く。

    DI の 50％の線が、景気の上向きと下向きの境。
    """
    fig, (top, bottom) = plt.subplots(2, 1, sharex=True)
    positions = list(range(len(ci)))
    top.plot(positions, ci.tolist(), marker="o")
    top.set_ylabel("CI (base = 100)")
    known = [p for p, ok in zip(positions, di.notna(), strict=True) if ok]
    bottom.bar(known, di.dropna().tolist())
    bottom.axhline(50, color="gray", linestyle="--")
    bottom.set_ylabel("DI (%)")
    bottom.set_xticks(positions, list(ci.index))
    plt.close(fig)
    return fig
