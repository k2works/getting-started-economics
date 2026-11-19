"""個人ごとの直線と、推定値の比較の図。"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from lib.chapter09.did import pooled_estimate
from lib.chapter10.panel import fixed_effects


def plot_entity_lines(panel: pd.DataFrame, entities: int = 5) -> Figure:
    """最初の数人のデータと、固定効果の傾きの直線（個人ごと）、プーリング OLS の直線。

    個人ごとの直線は平行（同じ傾き）で、プーリング OLS の直線は、傾きが違う。
    """
    beta = fixed_effects(panel, "y", ["x"]).coefficients["x"]
    fig, ax = plt.subplots()
    for entity in range(entities):
        data = panel[panel["entity"] == entity]
        ax.plot(data["x"], data["y"], "o", label=f"Entity {entity}")
        ends = np.array([data["x"].min(), data["x"].max()])
        center = data["y"].mean() + beta * (ends - data["x"].mean())
        ax.plot(ends, center, color="gray", label="_fit")
    shown = panel[panel["entity"] < entities]
    ends = np.array([shown["x"].min(), shown["x"].max()])
    pooled = pooled_estimate(shown)
    line = shown["y"].mean() + pooled * (ends - shown["x"].mean())
    ax.plot(ends, line, "--", color="black", label="Pooled OLS")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()
    plt.close(fig)
    return fig


def plot_estimate_comparison(estimates: pd.DataFrame, true_value: float) -> Figure:
    """推定量ごとの、傾きの推定値のヒストグラムと、真の値の線を重ねて描く。"""
    fig, ax = plt.subplots()
    for name in estimates.columns:
        ax.hist(estimates[name], bins=20, alpha=0.5, label=name)
    ax.axvline(true_value, color="black", linestyle="--", label="True value")
    ax.set_xlabel("Estimated slope")
    ax.set_ylabel("Frequency")
    ax.legend()
    plt.close(fig)
    return fig
