"""景気動向指数（DI・CI）と、雇用の指標（有効求人倍率・完全失業率）。"""

from pathlib import Path

import pandas as pd


def diffusion_index(indicators: pd.DataFrame) -> pd.Series:
    """DI（％）。前の月より上昇した系列の割合。変わらない系列は半分と数える。

    行は月、列は系列。最初の月と、欠損のある月は、計算できないので NaN。
    50％を超えると、景気は上向き。
    """
    change = indicators.diff()
    score = (change > 0).sum(axis=1) + 0.5 * (change == 0).sum(axis=1)
    di = score / indicators.shape[1] * 100
    known: pd.Series = di.where(change.notna().all(axis=1))
    return known


def composite_index(indicators: pd.DataFrame, base: str) -> pd.Series:
    """CI。各系列の前の月からの変化率の平均を、積み上げた指数。base の月が 100。"""
    if base not in indicators.index:
        raise ValueError(f"基準の月 {base} が、表にない")
    change = indicators.pct_change().mean(axis=1).fillna(0)
    index = (1 + change).cumprod() * 100
    rebased: pd.Series = index / index[base] * 100
    return rebased


def job_openings_ratio(openings: float, applicants: float) -> float:
    """有効求人倍率 = 有効求人数 ÷ 有効求職者数。1 を超えると、求人のほうが多い。"""
    if openings < 0:
        raise ValueError("求人数は、0 以上にする")
    if applicants <= 0:
        raise ValueError("求職者数は、正の値にする")
    return openings / applicants


def unemployment_rate(employed: float, unemployed: float) -> float:
    """完全失業率（％）= 完全失業者 ÷ 労働力人口 × 100。

    労働力人口 = 就業者 + 完全失業者。
    """
    if employed < 0 or unemployed < 0:
        raise ValueError("就業者数と完全失業者数は、負にならない")
    labor_force = employed + unemployed
    if labor_force == 0:
        raise ValueError("労働力人口が 0 で、完全失業率を計算できない")
    return unemployed / labor_force * 100


def load_indicators(path: Path | str) -> pd.DataFrame:
    """CSV の指標を読み込む。1 列目（month）を行の名前にする。欠損があればエラー。"""
    table = pd.read_csv(path, index_col="month", dtype={"month": str})
    if table.isna().any().any():
        raise ValueError("指標の CSV に、欠損がある")
    return table
