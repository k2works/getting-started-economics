"""pandas による経済データ（架空の国のマクロ統計）の分析。

データは `data/economy.csv`（このディレクトリの直下）。実在の統計ではなく、構造だけを
実際の統計（生産・分配・支出の 3 面と、統計上の不突合、GDP デフレーター）にそろえた
架空の値。
"""

from collections.abc import Sequence
from pathlib import Path

import pandas as pd

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "economy.csv"


def load_economy(path: Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """CSV を読み込み、年を行の名前（インデックス）にした表を返す。"""
    return pd.read_csv(path, index_col="year")


def production_gdp(df: pd.DataFrame) -> pd.Series:
    """生産面の GDP: 産業ごとの付加価値の合計。"""
    return df["primary"] + df["secondary"] + df["tertiary"]


def income_gdp(df: pd.DataFrame) -> pd.Series:
    """分配面の GDP: 雇用者報酬・営業余剰・固定資本減耗と間接税の合計。"""
    return df["wages"] + df["profits"] + df["depreciation_and_tax"]


def expenditure_gdp(df: pd.DataFrame) -> pd.Series:
    """支出面の GDP: 消費・投資・政府支出・純輸出（輸出 - 輸入）の合計。"""
    return (
        df["consumption"]
        + df["investment"]
        + df["government"]
        + df["exports"]
        - df["imports"]
    )


def statistical_discrepancy(df: pd.DataFrame) -> pd.Series:
    """統計上の不突合: 生産面の GDP から支出面の GDP を引いた差。"""
    return production_gdp(df) - expenditure_gdp(df)


def real_gdp(df: pd.DataFrame) -> pd.Series:
    """実質 GDP = 名目 GDP ÷ GDP デフレーター × 100（基準年はデフレーターが 100）。"""
    return production_gdp(df) / df["deflator"] * 100


def growth_rates(series: pd.Series) -> pd.Series:
    """前の年からの変化率（%）。最初の年は計算できないので欠損値になる。"""
    return series.pct_change() * 100


def recession_years(df: pd.DataFrame) -> list[int]:
    """実質成長率がマイナスの年を、古い順に返す。"""
    growth = growth_rates(real_gdp(df))
    return [int(year) for year in growth.index[growth < 0]]


def expenditure_shares(df: pd.DataFrame, year: int) -> pd.Series:
    """指定した年の、支出の構成比（GDP に対する %）を返す。"""
    row = df.loc[year]
    shares = pd.Series(
        {
            "consumption": row["consumption"],
            "investment": row["investment"],
            "government": row["government"],
            "net_exports": row["exports"] - row["imports"],
        }
    )
    gdp = production_gdp(df)[year]
    result: pd.Series = shares / gdp * 100
    return result


def _check_same_length(*sequences: Sequence[float]) -> None:
    if len({len(s) for s in sequences}) != 1:
        raise ValueError("財の数が合わない")


def laspeyres_index(
    base_prices: Sequence[float],
    base_quantities: Sequence[float],
    current_prices: Sequence[float],
) -> float:
    """ラスパイレス指数: 基準年の数量を使って、価格の変化を測る（基準年 = 100）。"""
    _check_same_length(base_prices, base_quantities, current_prices)
    current = sum(p * q for p, q in zip(current_prices, base_quantities, strict=True))
    base = sum(p * q for p, q in zip(base_prices, base_quantities, strict=True))
    return current / base * 100


def paasche_index(
    base_prices: Sequence[float],
    current_prices: Sequence[float],
    current_quantities: Sequence[float],
) -> float:
    """パーシェ指数: 比較年の数量を使って、価格の変化を測る（基準年 = 100）。"""
    _check_same_length(base_prices, current_prices, current_quantities)
    current = sum(
        p * q for p, q in zip(current_prices, current_quantities, strict=True)
    )
    base = sum(p * q for p, q in zip(base_prices, current_quantities, strict=True))
    return current / base * 100
