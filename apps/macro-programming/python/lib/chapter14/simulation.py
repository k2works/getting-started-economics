"""インパルス反応と確率的シミュレーション（動学的 AD-AS モデル）。

モデルは第 13 章。ショックがなければ p(t) = h·p(t-1)、y(t) = -c·p(t) で、
|h| < 1 なら、定常状態（0, 0）に戻る（安定）。
インパルス反応: 1 期間だけのショックへの、y と p の反応。
確率的シミュレーション: 毎期、正規分布のショックが発生する。
分散分解: 変動のうち、需要ショック・供給ショックに起因する割合。
"""

import numpy as np
import pandas as pd

from lib.chapter08.stochastic import shock_half_life, white_noise
from lib.chapter13.adas import AdasParameters, adas_step


def is_stable(h: float) -> bool:
    """p(t) = h·p(t-1) が、安定（|h| < 1）か。"""
    return abs(h) < 1


def price_half_life(params: AdasParameters) -> float:
    """物価の乖離が、半分になるまでの期間（四半期）。"""
    return shock_half_life(params.h)


def convergence_path(p0: float, params: AdasParameters, periods: int) -> pd.DataFrame:
    """ショックがない経済が、初期の物価の乖離 p0 から、定常状態に戻る道筋。

    最初の期の産出量は、AD 曲線 y = -c·p から決まる。
    """
    p = p0
    rows = [{"y": -params.c * p, "p": p}]
    for _ in range(periods):
        p, y = adas_step(p, 0.0, 0.0, params)
        rows.append({"y": y, "p": p})
    return pd.DataFrame(rows)


def impulse_response(
    params: AdasParameters,
    u: float = 0.0,
    v: float = 0.0,
    periods_after: int = 20,
    periods_before: int = 3,
) -> pd.DataFrame:
    """1 期間だけの需要ショック u、供給ショック v への反応。

    最初の periods_before 期間は定常状態、次の 1 期間にショック、
    その後 periods_after 期間はショックなし。列は y, p, u, v。
    """
    rows = [{"y": 0.0, "p": 0.0, "u": 0.0, "v": 0.0} for _ in range(periods_before)]
    p = 0.0
    for shock_u, shock_v in [(u, v)] + [(0.0, 0.0)] * periods_after:
        p, y = adas_step(p, shock_u, shock_v, params)
        rows.append({"y": y, "p": p, "u": shock_u, "v": shock_v})
    return pd.DataFrame(rows)


def simulate(params: AdasParameters, n: int, rng: np.random.Generator) -> pd.DataFrame:
    """毎期、ショックが発生する n 期間のシミュレーション。列は y, p, u, v。

    乱数の生成器を、引数で渡す。最初の期は、定常状態から始まる。
    """
    u = white_noise(n, params.sigma_u, rng)
    v = white_noise(n, params.sigma_v, rng)
    p = 0.0
    rows = []
    for shock_u, shock_v in zip(u, v, strict=True):
        p, y = adas_step(p, float(shock_u), float(shock_v), params)
        rows.append({"y": y, "p": p, "u": float(shock_u), "v": float(shock_v)})
    return pd.DataFrame(rows)


def variance_contributions(params: AdasParameters) -> pd.DataFrame:
    """物価と産出量の分散の、需要ショック・供給ショックに起因する部分。

    p: u は (a·h)²σu² ÷ (1 - h²)、v は h²σv² ÷ (1 - h²)。
    y = -c·h·p(t-1) + h·u - c·h·v なので、それぞれ、
    u は (c·h)²·(p の u の分散) + h²σu²、v は (c·h)²·(p の v の分散) + (c·h)²σv²。
    """
    a, c, h = params.a, params.c, params.h
    p_u = (a * h) ** 2 * params.sigma_u**2 / (1 - h**2)
    p_v = h**2 * params.sigma_v**2 / (1 - h**2)
    y_u = (c * h) ** 2 * p_u + h**2 * params.sigma_u**2
    y_v = (c * h) ** 2 * p_v + (c * h) ** 2 * params.sigma_v**2
    return pd.DataFrame({"p": [p_u, p_v], "y": [y_u, y_v]}, index=["demand", "supply"])


def variance_decomposition(params: AdasParameters) -> pd.DataFrame:
    """分散分解: 変動に占める、需要ショックと供給ショックの割合（列ごとに合計 1）。"""
    contributions = variance_contributions(params)
    return contributions / contributions.sum()
