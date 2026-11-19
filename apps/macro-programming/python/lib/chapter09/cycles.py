"""トレンドと景気循環: HP フィルターで、系列を、トレンドと循環に分ける。

HP フィルターは、トレンド τ を、(I + λ·D'D)·τ = y の解として求める
（D は 2 階差分の行列）。λ が大きいほど、トレンドは滑らか（直線に近い）。
四半期のデータでは、λ = 1600 が標準。循環は、系列とトレンドの差。
GDP などの水準は、対数をとって、トレンドからの乖離（%）にする。
"""

from pathlib import Path

import numpy as np
import pandas as pd

from lib.chapter08.stochastic import sample_autocorrelation

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "quarterly.csv"
_LEVELS = ["gdp", "consumption", "investment"]
_RATES = ["unemployment", "inflation"]


def load_quarterly(path: Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """CSV を読み込み、四半期（1980Q1 など）を行の名前にした表を返す。"""
    raw = pd.read_csv(path)
    periods = pd.PeriodIndex(
        [f"{y}Q{q}" for y, q in zip(raw["year"], raw["quarter"], strict=True)],
        freq="Q",
    )
    return raw.drop(columns=["year", "quarter"]).set_index(periods)


def hp_trend(series: pd.Series, smoothing: float = 1600) -> pd.Series:
    """HP フィルターのトレンド。直線の系列は、そのまま残る。"""
    n = len(series)
    if n < 3:
        raise ValueError("系列の長さは 3 以上でなければならない")
    if smoothing <= 0:
        raise ValueError("平滑化の強さは正でなければならない")
    second_difference = np.diff(np.eye(n), 2, axis=0)
    system = np.eye(n) + smoothing * second_difference.T @ second_difference
    trend = np.linalg.solve(system, series.to_numpy(dtype=float))
    return pd.Series(trend, index=series.index)


def cycle(series: pd.Series, smoothing: float = 1600) -> pd.Series:
    """循環 = 系列 − HP トレンド（失業率や物価上昇率のような、率の系列に使う）。"""
    return series - hp_trend(series, smoothing)


def log_cycle(series: pd.Series, smoothing: float = 1600) -> pd.Series:
    """対数のトレンドからの乖離（%）。GDP などの水準の系列に使う。"""
    logs = series.apply(np.log)
    return 100 * (logs - hp_trend(logs, smoothing))


def volatility(x: pd.Series) -> float:
    """変動の大きさ = 標本の標準偏差。"""
    return float(x.std())


def relative_volatility(x: pd.Series, y: pd.Series) -> float:
    """x の変動の大きさが、y の何倍か。"""
    return volatility(x) / volatility(y)


def cross_correlation(x: pd.Series, y: pd.Series, lag: int = 0) -> float:
    """x(t) と y(t − lag) の相関係数。lag = 0 なら、同じ時点の相関。"""
    return float(x.corr(y.shift(lag)))


def cycle_statistics(df: pd.DataFrame, smoothing: float = 1600) -> pd.DataFrame:
    """変数ごとの循環の統計。

    変動の大きさ、GDP に対する相対的な変動、GDP との相関、自己相関。
    GDP・消費・投資は対数の乖離（%）、失業率・物価上昇率は差（%ポイント）で見る。
    """
    cycles = pd.DataFrame(
        {
            **{name: log_cycle(df[name], smoothing) for name in _LEVELS},
            **{name: cycle(df[name], smoothing) for name in _RATES},
        }
    )
    gdp = cycles["gdp"]
    return pd.DataFrame(
        {
            "volatility": [volatility(cycles[c]) for c in cycles],
            "relative_to_gdp": [relative_volatility(cycles[c], gdp) for c in cycles],
            "correlation_with_gdp": [cross_correlation(cycles[c], gdp) for c in cycles],
            "autocorrelation": [
                sample_autocorrelation(cycles[c].to_numpy(), 1) for c in cycles
            ],
        },
        index=list(cycles.columns),
    )
