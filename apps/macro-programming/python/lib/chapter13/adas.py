"""動学的 AD-AS モデルとカリブレーション。

y は産出量、p は物価水準の、トレンドからの乖離（%）。
  AS 曲線  p(t) = p(t-1) + a·y(t) + v(t)   （適応的期待: 期待物価 = 前期の物価）
  AD 曲線  y(t) = -c·p(t) + u(t)
2 つを連立して解くと、均衡式（h = 1 ÷ (1 + a·c)）:
  p(t) = h·p(t-1) + h·(a·u(t) + v(t))
  y(t) = -c·h·p(t-1) + h·(u(t) - c·v(t))
カリブレーション: a・c・σu・σv を、データの特徴に合わせて決める。
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from lib.chapter03.regression import fit_ols
from lib.chapter08.stochastic import sample_autocorrelation
from lib.chapter09.cycles import (
    cross_correlation,
    load_quarterly,
    log_cycle,
    volatility,
)

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "adas_quarterly.csv"


@dataclass(frozen=True)
class AdasParameters:
    """AS 曲線の傾き a、AD 曲線の傾き c、需要・供給ショックの標準偏差。"""

    a: float
    c: float
    sigma_u: float
    sigma_v: float

    def __post_init__(self) -> None:
        if self.a <= 0 or self.c <= 0 or self.sigma_u < 0 or self.sigma_v < 0:
            raise ValueError(
                "パラメーターは、a・c が正、標準偏差が 0 以上でなければならない"
            )

    @property
    def h(self) -> float:
        """物価の持続性 h = 1 ÷ (1 + a·c)。0 と 1 の間。"""
        return 1 / (1 + self.a * self.c)


def adas_step(
    p_prev: float, u: float, v: float, params: AdasParameters
) -> tuple[float, float]:
    """前期の物価の乖離と、今期のショックから、今期の（物価, 産出量）を求める。"""
    h = params.h
    p = h * p_prev + h * (params.a * u + v)
    y = -params.c * h * p_prev + h * (u - params.c * v)
    return p, y


def calibrate(y: pd.Series, p: pd.Series) -> AdasParameters:
    """乖離の系列 y, p から、パラメーターを決める。

    p(t) を p(t-1) に回帰して h、y(t) を p(t-1) に回帰して d = -c·h を求める。
    c = -d ÷ h、a = (1 ÷ h - 1) ÷ c。回帰の残差 e_p = h(a·u + v)、
    e_y = h(u - c·v) から、v = e_p - a·e_y、u = c·e_p + e_y を求め、
    その標準偏差を、σv、σu にする（標準偏差は定数のずれに影響されないので、
    残差の定数項は、引かなくてよい）。
    """
    lag = pd.DataFrame({"p_lag": p.shift().dropna()})
    p_now = pd.Series(p.iloc[1:])
    y_now = pd.Series(y.iloc[1:])
    fit_p = fit_ols(p_now, lag)
    fit_y = fit_ols(y_now, lag)
    h = float(fit_p.coefficients["p_lag"])
    d = float(fit_y.coefficients["p_lag"])
    e_p = p_now - h * lag["p_lag"]
    e_y = y_now - d * lag["p_lag"]
    c = -d / h
    a = (1 / h - 1) / c
    return AdasParameters(
        a=a,
        c=c,
        sigma_u=float((c * e_p + e_y).std()),
        sigma_v=float((e_p - a * e_y).std()),
    )


def model_moments(params: AdasParameters) -> dict[str, float]:
    """モデルが示す（理論の）標準偏差・自己相関・相関。

    Var(p) = ((a·h)²σu² + h²σv²) ÷ (1 - h²)。p の自己相関 = h。
    """
    a, c, h = params.a, params.c, params.h
    su2, sv2 = params.sigma_u**2, params.sigma_v**2
    var_p = ((a * h) ** 2 * su2 + h**2 * sv2) / (1 - h**2)
    var_y = (c * h) ** 2 * var_p + h**2 * (su2 + c**2 * sv2)
    cov_py = -c * h**2 * var_p + h**2 * (a * su2 - c * sv2)
    return {
        "y_std": float(np.sqrt(var_y)),
        "p_std": float(np.sqrt(var_p)),
        "y_autocorr": -c * h * cov_py / var_y,
        "p_autocorr": h,
        "correlation": cov_py / float(np.sqrt(var_y * var_p)),
    }


def data_features(y: pd.Series, p: pd.Series) -> dict[str, float]:
    """データの特徴（モデルの積率と同じ 5 つ）。標準偏差は不偏、自己相関はラグ 1。"""
    return {
        "y_std": volatility(y),
        "p_std": volatility(p),
        "y_autocorr": sample_autocorrelation(y.to_numpy(), 1),
        "p_autocorr": sample_autocorrelation(p.to_numpy(), 1),
        "correlation": cross_correlation(y, p),
    }


def load_adas_quarterly(path: Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """GDP とデフレーター（水準）の四半期データを読み込む。"""
    return load_quarterly(path)


def adas_cycles(df: pd.DataFrame) -> pd.DataFrame:
    """GDP とデフレーターの、対数のトレンドからの乖離（%）。列は y と p。"""
    return pd.DataFrame(
        {
            "y": log_cycle(pd.Series(df["gdp"])),
            "p": log_cycle(pd.Series(df["deflator"])),
        }
    )
