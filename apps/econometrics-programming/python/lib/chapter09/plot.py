"""差分の差分の図。"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure


def plot_did(means: pd.DataFrame) -> Figure:
    """処置群・対照群の平均と、反事実（処置がなかったときの処置群）を描く。

    反事実は、処置群の処置前の平均から、対照群と同じだけ動く（平行トレンド）。
    """
    values = means.to_numpy(dtype=float)  # 1 行目が対照群、2 行目が処置群
    control, treated = values[0], values[1]
    fig, ax = plt.subplots()
    ax.plot([0, 1], control, marker="o", label="Control")
    ax.plot([0, 1], treated, marker="o", label="Treated")
    ax.plot(
        [0, 1],
        [treated[0], treated[0] + control[1] - control[0]],
        "--",
        marker="o",
        label="Counterfactual",
    )
    ax.set_xticks([0, 1], ["Before", "After"])
    ax.set_ylabel("Mean of y")
    ax.legend()
    plt.close(fig)
    return fig
