"""ダミー変数の直線の図。"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from numpy.typing import ArrayLike, NDArray

from lib.chapter03.multiple import fit_ols
from lib.chapter07.dummies import with_interaction


def plot_group_lines(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    d: NDArray[np.float64],
    interaction: bool,
) -> Figure:
    """ダミー変数 d で分けた 2 群のデータと、回帰直線を描く。

    interaction が偽なら、切片だけが違う（平行な）直線。真なら、傾きも違う直線。
    """
    columns: dict[str, ArrayLike] = {"x": x, "d": d}
    if interaction:
        columns["x:d"] = with_interaction(
            pd.Series(x, name="x"), pd.Series(d, name="d")
        )
    coefficients = fit_ols(y, pd.DataFrame(columns)).coefficients
    fig, ax = plt.subplots()
    ends = [float(np.min(x)), float(np.max(x))]
    for group in (0, 1):
        mask = d == group
        ax.plot(x[mask], y[mask], "o", label=f"Group {group}")
    for group in (0, 1):
        intercept = coefficients["const"] + coefficients["d"] * group
        slope = coefficients["x"] + (coefficients["x:d"] * group if interaction else 0)
        ax.plot(ends, [intercept + slope * v for v in ends], label=f"Fit group {group}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()
    plt.close(fig)
    return fig
