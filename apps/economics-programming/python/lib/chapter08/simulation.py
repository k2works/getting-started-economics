"""乱数によるシミュレーション（大数の法則と中心極限定理）。"""

import random
import statistics
from itertools import accumulate

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from lib.chapter01.demand import quantity_demanded


def simulate_demand(
    price: float,
    intercept: float,
    slope: float,
    sigma: float,
    n: int,
    rng: random.Random,
) -> list[float]:
    """需要曲線の値に、標準偏差 sigma の正規分布のばらつきを足した観測値を n 個作る。"""
    if sigma < 0:
        raise ValueError("ばらつきは 0 以上でなければならない")
    expected = quantity_demanded(price, intercept, slope)
    return [expected + rng.gauss(0, sigma) for _ in range(n)]


def running_means(values: list[float]) -> list[float]:
    """先頭から i 個目までの平均（累積平均）を並べて返す。"""
    return [total / count for count, total in enumerate(accumulate(values), start=1)]


def roll_dice(n: int, rng: random.Random) -> list[int]:
    """サイコロを n 回振った目を返す。"""
    return [rng.randint(1, 6) for _ in range(n)]


def sample_means(sample_size: int, trials: int, rng: random.Random) -> list[float]:
    """サイコロを sample_size 回振って平均を求める試行を trials 回行う。"""
    return [statistics.mean(roll_dice(sample_size, rng)) for _ in range(trials)]


def plot_histogram(values: list[float], bins: int) -> Figure:
    """観測値のヒストグラムを描いた図を返す。"""
    fig, ax = plt.subplots()
    ax.hist(values, bins=bins)
    ax.set_xlabel("Value")
    ax.set_ylabel("Frequency")
    plt.close(fig)
    return fig
