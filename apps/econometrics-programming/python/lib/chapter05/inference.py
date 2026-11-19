"""推論: t 検定・p 値・信頼区間・F 検定と、その性質のシミュレーション。"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike
from scipy import stats

from lib.chapter02.simple import draw_sample
from lib.chapter03.multiple import OlsResult, fit_ols


@dataclass(frozen=True)
class TestResult:
    """検定の結果（検定統計量と p 値）。"""

    __test__ = False  # pytest が、テストのクラスと間違えないようにする

    statistic: float
    p_value: float


def t_statistics(result: OlsResult, null: float = 0.0) -> pd.Series:
    """t 値 = (係数 − 帰無仮説の値) ÷ 標準誤差。"""
    return (result.coefficients - null) / result.standard_errors


def p_value(t: float, df: float, alternative: str = "two-sided") -> float:
    """t 値の p 値。対立仮説は two-sided（両側）・greater・less。"""
    if alternative == "two-sided":
        return float(2 * stats.t.sf(abs(t), df))
    if alternative == "greater":
        return float(stats.t.sf(t, df))
    if alternative == "less":
        return float(stats.t.cdf(t, df))
    raise ValueError(f"知らない対立仮説: {alternative}")


def confidence_interval(result: OlsResult, level: float = 0.95) -> pd.DataFrame:
    """係数の信頼区間 = 係数 ± t の臨界値 × 標準誤差。"""
    critical = float(stats.t.ppf(1 - (1 - level) / 2, result.df_resid))
    half = critical * result.standard_errors
    return pd.DataFrame(
        {"lower": result.coefficients - half, "upper": result.coefficients + half}
    )


def _rss(y: ArrayLike, x: pd.DataFrame) -> tuple[float, int]:
    """残差平方和と、残差の自由度。説明変数がなければ、定数項だけの回帰。"""
    if x.shape[1] == 0:
        values = np.asarray(y, dtype=float)
        return float(np.sum((values - values.mean()) ** 2)), len(values) - 1
    result = fit_ols(y, x)
    return float(result.residuals @ result.residuals), result.df_resid


def f_test(y: ArrayLike, x: pd.DataFrame, zero: list[str]) -> TestResult:
    """列 zero の係数が、すべて 0 という仮説の F 検定（制約付き回帰との比較）。"""
    rss_full, df_full = _rss(y, x)
    rss_restricted, df_restricted = _rss(y, x.drop(columns=zero))
    q = df_restricted - df_full
    statistic = ((rss_restricted - rss_full) / q) / (rss_full / df_full)
    return TestResult(float(statistic), float(stats.f.sf(statistic, q, df_full)))


def slope_intervals(
    n: int, repetitions: int, level: float, rng: np.random.Generator
) -> pd.DataFrame:
    """標本を取り直して、傾きの信頼区間を繰り返し作る（真の傾きは 0.5）。"""
    rows = []
    for _ in range(repetitions):
        x, y = draw_sample(n, 1.0, 0.5, 1.0, rng)
        interval = confidence_interval(fit_ols(y, x), level).loc["x1"]
        rows.append((interval["lower"], interval["upper"]))
    return pd.DataFrame(rows, columns=["lower", "upper"])


def coverage_rate(
    n: int, repetitions: int, level: float, rng: np.random.Generator
) -> float:
    """信頼区間が真の傾き（0.5）を含む割合（被覆率）。水準に近いはず。"""
    table = slope_intervals(n, repetitions, level, rng)
    return float(((table["lower"] <= 0.5) & (0.5 <= table["upper"])).mean())


def rejection_rate(
    n: int,
    repetitions: int,
    true_slope: float,
    null_slope: float,
    significance: float,
    rng: np.random.Generator,
) -> float:
    """傾きが null_slope という仮説を、両側 t 検定で棄却する割合。"""
    rejected = 0
    for _ in range(repetitions):
        x, y = draw_sample(n, 1.0, true_slope, 1.0, rng)
        result = fit_ols(y, x)
        t = t_statistics(result, null_slope)["x1"]
        rejected += p_value(t, result.df_resid) < significance
    return rejected / repetitions
