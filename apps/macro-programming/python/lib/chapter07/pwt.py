"""Penn World Table（実際の国際比較データ）を、この記事の表の形に直す。

PWT 10.01（Feenstra, Inklaar and Timmer, 2015）の Stata ファイル（pwt1001.dta）を読む。
就業者 1 人当たりの GDP（y = cgdpo ÷ emp）、資本ストック（k = cn ÷ emp）、
人的資本の指数（h = hc）に直す。cgdpo と cn は、購買力平価（PPP）で、
共通の単位（2017 年の百万ドル）にそろえてある。emp は百万人。
"""

from pathlib import Path

import pandas as pd

_COLUMNS = ["countrycode", "year", "cgdpo", "cn", "emp", "hc", "pop", "pl_gdpo"]


def load_pwt(path: Path) -> pd.DataFrame:
    """PWT の Stata ファイルを読み、国と年を行の名前にした表を返す。

    列は y・k・h（第 1〜3 章と同じ）、income_pc（人口 1 人当たりの GDP）、
    price_level（相対価格水準 pl_gdpo。米国の 2017 年 = 1）。
    値が欠けている行と、就業者・人口が 0 以下の行は、除く。
    """
    raw = pd.read_stata(path, columns=_COLUMNS).dropna()
    raw = raw[(raw["emp"] > 0) & (raw["pop"] > 0)]
    df = pd.DataFrame(
        {
            "country": raw["countrycode"].astype(str),
            "year": raw["year"].astype(int),
            "y": raw["cgdpo"].astype(float) / raw["emp"].astype(float),
            "k": raw["cn"].astype(float) / raw["emp"].astype(float),
            "h": raw["hc"].astype(float),
            "income_pc": raw["cgdpo"].astype(float) / raw["pop"].astype(float),
            "price_level": raw["pl_gdpo"].astype(float),
        }
    )
    return df.set_index(["country", "year"]).sort_index()


def balanced_countries(panel: pd.DataFrame, start: int, end: int) -> pd.DataFrame:
    """start 年から end 年までの全年に、値がそろっている国だけを、残す。"""
    if start >= end:
        raise ValueError("期間の始まりは終わりより前でなければならない")
    years = panel.index.get_level_values("year")
    within = panel[(years >= start) & (years <= end)]
    counts = within.groupby(level="country").size()
    complete = counts[counts == end - start + 1].index
    countries = within.index.get_level_values("country")
    return within[countries.isin(complete)]
