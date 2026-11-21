"""三面等価と産業連関表の図。"""

from collections.abc import Mapping, Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from numpy.typing import ArrayLike

from lib.chapter02.input_output import output_for_demand


def plot_three_way(sides: Mapping[str, Mapping[str, float]]) -> Figure:
    """生産・分配・支出の GDP を、部分を積み上げた棒で描く。

    面の名前 -> {部分の名前: 値}。三面等価が成り立てば、積み上げた高さは、すべて等しい。
    """
    fig, ax = plt.subplots()
    for position, (side, parts) in enumerate(sides.items()):
        bottom = 0.0
        for name, value in parts.items():
            ax.bar(side, value, bottom=bottom, edgecolor="white")
            ax.text(position, bottom + value / 2, name, ha="center", va="center")
            bottom += value
    ax.set_ylabel("GDP (100 million yen)")
    plt.close(fig)
    return fig


def plot_io_output(
    coefficients: ArrayLike, final_demand: Sequence[float], sectors: Sequence[str]
) -> Figure:
    """部門ごとに、最終需要と、それを満たす生産量を、並べた棒で描く。

    生産量が最終需要より大きいのは、部門どうしが、中間財を買い合うため。
    """
    output = output_for_demand(coefficients, final_demand)
    x = np.arange(len(sectors))
    width = 0.4
    fig, ax = plt.subplots()
    ax.bar(x - width / 2, final_demand, width, label="Final demand")
    ax.bar(x + width / 2, output, width, label="Output")
    ax.set_xticks(x, sectors)
    ax.set_ylabel("Value (100 million yen)")
    ax.legend()
    plt.close(fig)
    return fig
