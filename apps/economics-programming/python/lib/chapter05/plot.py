"""価格の調整経路の図。横軸が繰り返しの回数、縦軸が価格。"""

from collections.abc import Mapping

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def plot_price_paths(
    paths: Mapping[str, list[float]], equilibrium_price: float
) -> Figure:
    """調整の経路（名前 -> 価格の推移）を重ねて、均衡価格の線と一緒に描く。"""
    longest = max(len(path) for path in paths.values())

    fig, ax = plt.subplots()
    for name, path in paths.items():
        ax.plot(range(len(path)), path, "o-", markersize=3, label=name)
    ax.plot(
        [0, longest - 1],
        [equilibrium_price] * 2,
        "--",
        color="gray",
        label="Equilibrium",
    )
    ax.set_xlabel("Step")
    ax.set_ylabel("Price")
    ax.legend()
    plt.close(fig)
    return fig
