"""インフレとマネーストック: 貨幣数量説を、データで確かめる。

貨幣数量説 MV = PY を、成長率で書くと、
  物価上昇率 = 貨幣の伸び率 − 実質成長率 + 流通速度の伸び率。
流通速度が安定なら、貨幣の伸び率が高い国ほど、物価上昇率が高い（傾き 1）。
"""

from pathlib import Path

import pandas as pd

from lib.chapter03.regression import OlsResult, fit_ols

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "money_panel.csv"


def quantity_theory_inflation(
    money_growth: float, real_growth: float, velocity_growth: float = 0.0
) -> float:
    """物価上昇率 = 貨幣の伸び率 − 実質成長率 + 流通速度の伸び率（% / 年）。"""
    return money_growth - real_growth + velocity_growth


def implied_velocity_growth(
    money_growth: float, real_growth: float, inflation: float
) -> float:
    """観測した物価上昇率から、貨幣数量説が成り立つ流通速度の伸び率を求める。"""
    return inflation - money_growth + real_growth


def to_annual_average(series: pd.Series) -> pd.Series:
    """四半期（PeriodIndex）の系列を、年ごとの平均にする。"""
    index = series.index
    if not isinstance(index, pd.PeriodIndex) or not index.freqstr.startswith("Q"):
        raise ValueError("四半期（PeriodIndex）の系列でなければならない")
    return series.groupby(index.year).mean()


def load_money_panel(path: Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """CSV を読み込み、国と年を行の名前にした表を返す。

    列は money_growth（貨幣の伸び率）・real_growth（実質成長率）・
    inflation（物価上昇率）。すべて % / 年。
    """
    return pd.read_csv(path, index_col=["country", "year"])


def money_inflation_regression(
    panel: pd.DataFrame, max_inflation: float | None = None
) -> OlsResult:
    """物価上昇率を、貨幣の伸び率に回帰する。

    max_inflation を渡すと、物価上昇率がそれを超える行（ハイパーインフレ）を除く。
    """
    data = (
        panel if max_inflation is None else panel[panel["inflation"] <= max_inflation]
    )
    return fit_ols(
        pd.Series(data["inflation"]),
        pd.DataFrame({"money_growth": data["money_growth"]}),
    )


def hyperinflation_episodes(
    panel: pd.DataFrame, threshold: float = 100
) -> pd.DataFrame:
    """物価上昇率が threshold（% / 年）を超える、国と年の行を取り出す。"""
    return panel[panel["inflation"] > threshold]


def country_averages(panel: pd.DataFrame) -> pd.DataFrame:
    """国ごとの、全期間の平均（貨幣の伸び率・実質成長率・物価上昇率）。"""
    return panel.groupby(level="country")[
        ["money_growth", "real_growth", "inflation"]
    ].mean()


def long_run_relation(panel: pd.DataFrame) -> OlsResult:
    """長期の関係: 国ごとの平均の物価上昇率を、平均の貨幣と成長の差に回帰する。"""
    averages = country_averages(panel)
    x = pd.DataFrame(
        {"money_minus_real_growth": averages["money_growth"] - averages["real_growth"]}
    )
    return fit_ols(pd.Series(averages["inflation"]), x)
