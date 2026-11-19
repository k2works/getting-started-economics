"""オークンの法則とフィリップス曲線を、回帰で調べる。

オークンの法則: 失業率の循環 = c + β·GDP の循環（β < 0。好調なとき、失業が減る）。
フィリップス曲線: 物価上昇率 = c + β·失業率の循環（β < 0。失業が少ないと上がる）。
どちらも、第 9 章の HP フィルターで、循環を取り出してから、第 3 章の回帰を使う。
"""

import pandas as pd

from lib.chapter03.regression import OlsResult, fit_ols
from lib.chapter09.cycles import cycle, log_cycle


def okun_regression(
    unemployment_cycle: pd.Series, output_cycle: pd.Series
) -> OlsResult:
    """失業率の循環（%ポイント）を、GDP の循環（%）に回帰する。"""
    return fit_ols(unemployment_cycle, pd.DataFrame({"output_cycle": output_cycle}))


def okun_regression_from_data(df: pd.DataFrame, smoothing: float = 1600) -> OlsResult:
    """四半期のデータ（gdp・unemployment の列）から、オークンの法則を回帰する。"""
    output = log_cycle(pd.Series(df["gdp"]), smoothing)
    unemployment = cycle(pd.Series(df["unemployment"]), smoothing)
    return okun_regression(unemployment, output)


def phillips_regression(inflation: pd.Series, unemployment_gap: pd.Series) -> OlsResult:
    """物価上昇率（%）を、失業率の循環（%ポイント）に回帰する。"""
    return fit_ols(inflation, pd.DataFrame({"unemployment_gap": unemployment_gap}))


def phillips_regression_from_data(
    df: pd.DataFrame, smoothing: float = 1600
) -> OlsResult:
    """四半期のデータ（unemployment・inflation の列）で、フィリップス曲線を回帰する。"""
    gap = cycle(pd.Series(df["unemployment"]), smoothing)
    return phillips_regression(pd.Series(df["inflation"]), gap)


def phillips_by_period(
    df: pd.DataFrame, split_year: int, smoothing: float = 1600
) -> dict[str, OlsResult]:
    """split_year の前（before）と後（after）で、フィリップス曲線を別々に回帰する。

    失業率の循環は、全期間のデータで求めてから、期間で分ける。
    """
    years = df.index.year  # type: ignore[attr-defined]
    if split_year <= years.min() or split_year > years.max():
        raise ValueError("分ける年は、データの範囲の内側でなければならない")
    gap = cycle(pd.Series(df["unemployment"]), smoothing)
    inflation = pd.Series(df["inflation"])
    before = years < split_year
    return {
        "before": phillips_regression(inflation[before], gap[before]),
        "after": phillips_regression(inflation[~before], gap[~before]),
    }


def rolling_slope(x: pd.Series, y: pd.Series, window: int) -> pd.Series:
    """窓（window 個の観測）をずらしながら、y を x に回帰した傾きを求める。

    行の名前は、窓の最後の時点。傾きが時間とともに変わるか（平らになるか）を見る。
    """
    if window < 3 or window > len(x):
        raise ValueError("窓の幅は 3 以上で、系列の長さ以下でなければならない")
    slopes = {}
    for start in range(len(x) - window + 1):
        stop = start + window
        result = fit_ols(y.iloc[start:stop], pd.DataFrame({"x": x.iloc[start:stop]}))
        slopes[x.index[stop - 1]] = result.coefficients["x"]
    return pd.Series(slopes)
