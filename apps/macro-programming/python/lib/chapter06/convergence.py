"""所得の収斂: 初期の所得が低い国ほど、速く成長するか。

収斂の式: (1 ÷ T)·ln(y_T ÷ y_0) = a + β·ln y_0。β < 0 なら、収斂している。
全国が、同じ速さ λ で、共通の定常状態に近づくなら、β = −(1 − e^(−λT)) ÷ T。
"""

import math
from collections.abc import Sequence

import numpy as np
import pandas as pd

from lib.chapter03.regression import OlsResult, fit_ols


def _endpoints(
    panel: pd.DataFrame, start: int, end: int
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """始まりの年と終わりの年の表を返す。期間や年がおかしければ、エラーにする。"""
    if start >= end:
        raise ValueError("期間の始まりは終わりより前でなければならない")
    available = set(panel.index.get_level_values("year"))
    for year in (start, end):
        if year not in available:
            raise ValueError(f"パネルに {year} 年がない")
    return (
        pd.DataFrame(panel.xs(start, level="year")),
        pd.DataFrame(panel.xs(end, level="year")),
    )


def income_growth(panel: pd.DataFrame, start: int, end: int) -> pd.Series:
    """国ごとの、所得の 1 年当たりの成長率（%）= 100 × ln(y_end ÷ y_start) ÷ 年数。"""
    first, last = _endpoints(panel, start, end)
    return 100 * (last["y"] / first["y"]).apply(np.log) / (end - start)


def beta_convergence(
    panel: pd.DataFrame, start: int, end: int, controls: Sequence[str] = ()
) -> OlsResult:
    """成長率を、初期の対数の所得（ln_y0）に回帰する。

    controls に "k"・"h" を渡すと、初期の対数の資本・人的資本も説明変数に加える
    （条件付き収斂）。ln_y0 の係数 β が負なら、初期の所得が低い国ほど、速く成長した。
    """
    first, _ = _endpoints(panel, start, end)
    x = pd.DataFrame({"ln_y0": np.log(first["y"])})
    for name in controls:
        if name not in ("k", "h"):
            raise ValueError("条件に使える変数は k と h だけ")
        x[f"ln_{name}0"] = np.log(first[name])
    return fit_ols(income_growth(panel, start, end), x)


def implied_speed(beta: float, years: float) -> float:
    """傾き β（成長率は % / 年）から、収束の速さ λ を求める。

    β（小数）= −(1 − e^(−λT)) ÷ T を、λ について解く: λ = −ln(1 + β·T) ÷ T。
    """
    argument = 1 + beta / 100 * years
    if argument <= 0:
        raise ValueError("傾きが小さすぎて、収束の速さが決まらない")
    return -math.log(argument) / years


def half_life_years(speed: float) -> float:
    """乖離が半分になる年数 = ln 2 ÷ λ。"""
    if speed <= 0:
        raise ValueError("収束の速さは正でなければならない")
    return math.log(2) / speed


def club_convergence(panel: pd.DataFrame, start: int, end: int) -> dict[str, OlsResult]:
    """初期の所得の低い半分（poor）と高い半分（rich）に分けて、それぞれ推定する。

    全体で収斂していても、グループの中では、収斂していないことがある（クラブ収斂）。
    """
    first, _ = _endpoints(panel, start, end)
    ranked = first["y"].sort_values()
    half = len(ranked) // 2
    groups = {"poor": list(ranked.index[:half]), "rich": list(ranked.index[half:])}
    countries = panel.index.get_level_values("country")
    return {
        name: beta_convergence(panel[countries.isin(members)], start, end)
        for name, members in groups.items()
    }


def beta_by_start_year(panel: pd.DataFrame, window: int) -> pd.Series:
    """開始年をずらしながら、window 年間の傾き β を求める（開始年 -> β）。"""
    if window < 1:
        raise ValueError("期間の幅は 1 年以上でなければならない")
    years = sorted(set(panel.index.get_level_values("year")))
    betas = {}
    for start in years:
        if start + window in years:
            result = beta_convergence(panel, start, start + window)
            betas[start] = result.coefficients["ln_y0"]
    return pd.Series(betas)
