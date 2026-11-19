"""為替レートと貨幣の中立性。

実質為替レート q = e × P* ÷ P
（e は自国通貨 / 外国通貨、P* は外国の物価、P は自国の物価）。
物価が粘着的なら、名目為替レートの動きが、そのまま、実質為替レートの動きになる。
貨幣の中立性: 貨幣量は、長期には、実質変数（実質成長率）に影響しない。
"""

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from lib.chapter03.regression import OlsResult, fit_ols

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "exchange.csv"


def real_exchange_rate(
    nominal_rate: Any, price_foreign: Any, price_domestic: Any
) -> Any:
    """実質為替レート q = e × P* ÷ P。数でも、系列でも計算できる。"""
    for value in (nominal_rate, price_foreign, price_domestic):
        if np.any(np.asarray(value) <= 0):
            raise ValueError("為替レートと物価は正でなければならない")
    return nominal_rate * price_foreign / price_domestic


def log_change(series: pd.Series) -> pd.Series:
    """対数の変化率（%）= 100 × Δln x。最初の期は、前がないので、除く。"""
    return (100 * series.apply(np.log).diff()).dropna()


def load_exchange(path: Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """CSV を読み込み、四半期を行の名前にした表を返す。

    列は nominal_rate（自国通貨 / 外国通貨）・price_domestic・price_foreign
    （物価指数）。
    """
    raw = pd.read_csv(path)
    periods = pd.PeriodIndex(
        [f"{y}Q{q}" for y, q in zip(raw["year"], raw["quarter"], strict=True)],
        freq="Q",
    )
    return raw.drop(columns=["year", "quarter"]).set_index(periods)


def regime_statistics(df: pd.DataFrame, break_period: str) -> pd.DataFrame:
    """切り替えの前（fixed）と後（floating）で、為替レートの動きを比べる。

    名目為替レートの変動の大きさ、実質為替レートの変動の大きさ
    （対数の変化率の標準偏差）、名目と実質の変化率の相関。
    切り替えの前後に、3 四半期以上のデータが必要（変化率が 2 個以上）。
    """
    period = pd.Period(break_period, freq="Q")
    if min((df.index < period).sum(), (df.index >= period).sum()) < 3:
        raise ValueError("切り替えの前後に、それぞれ 3 四半期以上のデータが必要")
    real = real_exchange_rate(
        df["nominal_rate"], df["price_foreign"], df["price_domestic"]
    )
    rows = {}
    for name, mask in (("fixed", df.index < period), ("floating", df.index >= period)):
        nominal_change = log_change(pd.Series(df["nominal_rate"][mask]))
        real_change = log_change(pd.Series(real[mask]))
        rows[name] = {
            "nominal_volatility": float(nominal_change.std()),
            "real_volatility": float(real_change.std()),
            "correlation": float(nominal_change.corr(real_change)),
        }
    return pd.DataFrame.from_dict(rows, orient="index")


def money_neutrality_regression(panel: pd.DataFrame) -> OlsResult:
    """実質成長率を、貨幣の伸び率に回帰する（第 11 章のパネル）。

    貨幣が中立なら、傾きは 0 に近い。
    """
    return fit_ols(
        pd.Series(panel["real_growth"]),
        pd.DataFrame({"money_growth": panel["money_growth"]}),
    )
