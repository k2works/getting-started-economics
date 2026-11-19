"""一物一価と購買力平価（PPP）。

同じ商品を、自国と米国で比べる。為替レート e は、1 ドル当たりの自国通貨。
  価格のドル換算 = 自国の価格 ÷ e
  PPP レート = 自国の価格 ÷ 米国の価格（一物一価が成り立つときの為替レート）
  相対価格水準 = PPP レート ÷ e = 価格のドル換算 ÷ 米国の価格（1 なら、一物一価）
"""

from pathlib import Path

import numpy as np
import pandas as pd

from lib.chapter03.regression import OlsResult, fit_ols

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "prices.csv"


def price_in_dollars(local_price: float, exchange_rate: float) -> float:
    """自国通貨の価格を、ドルに直す。"""
    if local_price <= 0 or exchange_rate <= 0:
        raise ValueError("価格と為替レートは正でなければならない")
    return local_price / exchange_rate


def ppp_rate(local_price: float, us_price: float) -> float:
    """PPP レート = 自国の価格 ÷ 米国の価格（自国通貨 / ドル）。"""
    if local_price <= 0 or us_price <= 0:
        raise ValueError("価格は正でなければならない")
    return local_price / us_price


def relative_price_level(
    local_price: float, exchange_rate: float, us_price: float
) -> float:
    """相対価格水準 = ドル換算の価格 ÷ 米国の価格。1 より小さければ、米国より安い。"""
    if us_price <= 0:
        raise ValueError("価格は正でなければならない")
    return price_in_dollars(local_price, exchange_rate) / us_price


def load_prices(path: Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """CSV を読み込み、国名を行の名前にした表を返す。

    列は local_price（自国通貨の価格）・exchange_rate（自国通貨 / ドル）・
    income（1 人当たりの所得、ドル）。
    """
    return pd.read_csv(path, index_col="country")


def relative_price_levels(df: pd.DataFrame, base: str = "BASE") -> pd.Series:
    """国ごとの相対価格水準（基準の国のドル換算の価格 = 1）を返す。"""
    if base not in df.index:
        raise ValueError(f"基準の国 {base} が、データにない")
    dollars = df["local_price"] / df["exchange_rate"]
    levels: pd.Series = dollars / dollars[base]
    return levels


def penn_effect_regression(df: pd.DataFrame, base: str = "BASE") -> OlsResult:
    """対数の相対価格水準を、対数の所得に回帰する（ペン効果）。

    傾きが正なら、豊かな国ほど、物価が高い。
    """
    levels = relative_price_levels(df, base)
    x = pd.DataFrame({"ln_income": np.log(df["income"])})
    return fit_ols(np.log(levels), x)


def income_adjusted_gaps(df: pd.DataFrame, base: str = "BASE") -> pd.Series:
    """所得で説明できる分を除いた、対数の相対価格水準の差（回帰の残差）を返す。

    正なら、所得の割に、物価が高い。負なら、安い。合計は 0 になる。
    """
    result = penn_effect_regression(df, base)
    levels = relative_price_levels(df, base)
    fitted = result.coefficients["const"] + result.coefficients["ln_income"] * np.log(
        df["income"]
    )
    gaps: pd.Series = np.log(levels) - fitted
    return gaps
