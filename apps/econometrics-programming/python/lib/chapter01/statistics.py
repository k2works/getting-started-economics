"""統計学の復習: 標本の特徴を表す数値と、確率分布。"""

import math
from collections.abc import Sequence

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy import stats

# 1 次元の数列（第 1・2 章などの、1 つの変数）。説明変数の行列（DataFrame を含む）は、
# 第 3 章以降の ArrayLike（numpy.typing）を使う
Array = Sequence[float] | NDArray[np.float64] | pd.Series

# 臨界値を求められる分布（名前 -> SciPy の分布）
_DISTRIBUTIONS = {
    "normal": stats.norm,
    "t": stats.t,
    "chi2": stats.chi2,
    "f": stats.f,
}


def sample_variance(x: Array, ddof: int = 1) -> float:
    """分散。分母は n - ddof（既定は不偏分散の n - 1）。"""
    values = np.asarray(x, dtype=float)
    if values.size <= ddof:
        raise ValueError("観測値の数が足りない（分母が 0 以下になる）")
    return float(np.sum((values - values.mean()) ** 2) / (values.size - ddof))


def sample_covariance(x: Array, y: Array) -> float:
    """標本共分散（分母は n - 1）。"""
    a = np.asarray(x, dtype=float)
    b = np.asarray(y, dtype=float)
    if a.size != b.size:
        raise ValueError("x と y の長さが違う")
    if a.size < 2:
        raise ValueError("観測値の数が足りない（2 個以上必要）")
    return float(np.sum((a - a.mean()) * (b - b.mean())) / (a.size - 1))


def sample_correlation(x: Array, y: Array) -> float:
    """標本相関係数。どちらかの分散が 0 なら、計算できない。"""
    var_x = sample_variance(x)
    var_y = sample_variance(y)
    if var_x == 0 or var_y == 0:
        raise ValueError("分散が 0 の変数の相関は計算できない")
    return sample_covariance(x, y) / math.sqrt(var_x * var_y)


def standardize(x: Array) -> NDArray[np.float64]:
    """平均を引いて、標準偏差で割る（平均 0、分散 1 にする）。"""
    values = np.asarray(x, dtype=float)
    return (values - values.mean()) / math.sqrt(sample_variance(values))


def standard_error_of_mean(x: Array) -> float:
    """標本平均の標準誤差 = √(不偏分散 ÷ n)。"""
    return math.sqrt(sample_variance(x) / len(x))


def normal_cdf(z: float) -> float:
    """標準正規分布の累積分布関数 Φ(z)。誤差関数 erf で書く。"""
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def critical_value(name: str, probability: float, *df: float) -> float:
    """分布の下側確率が probability になる点（臨界値）。df は自由度。"""
    if name not in _DISTRIBUTIONS:
        raise ValueError(f"知らない分布: {name}（normal・t・chi2・f のどれか）")
    if not 0 < probability < 1:
        raise ValueError("確率は 0 と 1 の間（0 と 1 は含まない）")
    return float(_DISTRIBUTIONS[name].ppf(probability, *df))


def sampling_distribution_of_mean(
    n: int, repetitions: int, rng: np.random.Generator
) -> NDArray[np.float64]:
    """標準正規分布から n 個を取り出して平均を求める作業を、繰り返す。"""
    draws = rng.standard_normal((repetitions, n))
    result: NDArray[np.float64] = draws.mean(axis=1)
    return result
