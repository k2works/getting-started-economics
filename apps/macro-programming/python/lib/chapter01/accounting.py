"""発展会計: 生産関数 y = A · k^α · h^(1−α) から、所得の差を要因に分ける。

y は労働者 1 人当たりの所得、k は物的資本、h は人的資本、A は全要素生産性（TFP）、
α は資本分配率。TFP は、所得のうち、資本と人的資本では説明できない残りとして求める。
"""

from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "countries.csv"


def _check_alpha(alpha: float) -> None:
    if not 0 < alpha < 1:
        raise ValueError("資本分配率は 0 より大きく 1 より小さくなければならない")


def tfp(output: float, capital: float, human_capital: float, alpha: float) -> float:
    """TFP A = y ÷ (k^α · h^(1−α)) を返す。"""
    _check_alpha(alpha)
    if min(output, capital, human_capital) <= 0:
        raise ValueError("所得・資本・人的資本は正でなければならない")
    return float(output / (capital**alpha * human_capital ** (1 - alpha)))


def load_countries(path: Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """CSV を読み込み、国名を行の名前にした表（列は y・k・h）を返す。"""
    return pd.read_csv(path, index_col="country")


def with_tfp(df: pd.DataFrame, alpha: float) -> pd.DataFrame:
    """TFP の列（tfp）を足した表を返す。元の表は変えない。"""
    _check_alpha(alpha)
    if (df[["y", "k", "h"]] <= 0).any().any():
        raise ValueError("所得・資本・人的資本は正でなければならない")
    return df.assign(tfp=df["y"] / (df["k"] ** alpha * df["h"] ** (1 - alpha)))


def income_gap(df: pd.DataFrame, reference: str, alpha: float) -> pd.DataFrame:
    """基準の国との所得の差（対数の差）を、資本・人的資本・TFP の寄与に分ける。

    ln(y ÷ y₀) = α·ln(k ÷ k₀) + (1−α)·ln(h ÷ h₀) + ln(A ÷ A₀)。
    列は capital・human_capital・tfp・total（total は、3 つの寄与の和）。
    """
    table = with_tfp(df, alpha)
    if reference not in table.index:
        raise ValueError(f"基準の国 {reference} が、データにない")
    logs = table[["y", "k", "h", "tfp"]].apply(np.log)
    diff = logs - logs.loc[reference]
    return pd.DataFrame(
        {
            "capital": alpha * diff["k"],
            "human_capital": (1 - alpha) * diff["h"],
            "tfp": diff["tfp"],
            "total": diff["y"],
        }
    )


def variance_shares(df: pd.DataFrame, alpha: float) -> pd.Series:
    """所得（対数）の分散のうち、資本・人的資本・TFP が説明する割合を返す。

    ln y = α·ln k + (1−α)·ln h + ln A なので、割合 = Cov(ln y, 各項) ÷ Var(ln y)。
    3 つの割合の合計は 1 になる。
    """
    table = with_tfp(df, alpha)
    log_output = np.log(table["y"])
    variance = log_output.var()
    if np.isclose(variance, 0):
        raise ValueError("国による所得の差がないので、分散の割合は求められない")
    parts = {
        "capital": alpha * np.log(table["k"]),
        "human_capital": (1 - alpha) * np.log(table["h"]),
        "tfp": np.log(table["tfp"]),
    }
    return pd.Series(
        {name: log_output.cov(part) / variance for name, part in parts.items()}
    )
