"""成長会計: 所得の成長率を、物的資本・人的資本・TFP の寄与に分ける。

成長率は、対数の差を年数で割った値（% / 年）。y = A·k^α·h^(1−α) の対数をとって
時間で差をとると、g_y = g_A + α·g_k + (1−α)·g_h が成り立つ。
"""

from pathlib import Path

import numpy as np
import pandas as pd

from lib.chapter01.accounting import with_tfp

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "panel.csv"


def load_panel(path: Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """CSV を読み込み、国と年を行の名前にした表（列は y・k・h）を返す。"""
    return pd.read_csv(path, index_col=["country", "year"])


def log_growth_rate(start_value: float, end_value: float, years: float) -> float:
    """1 年当たりの成長率（%）= 100 × (ln 終わり − ln 始まり) ÷ 年数。"""
    if min(start_value, end_value) <= 0:
        raise ValueError("値は正でなければならない")
    if years <= 0:
        raise ValueError("年数は正でなければならない")
    return float(100 * np.log(end_value / start_value) / years)


def growth_contribution(
    panel: pd.DataFrame, start: int, end: int, alpha: float
) -> pd.DataFrame:
    """start 年から end 年までの平均の成長率を、資本・人的資本・TFP の寄与に分ける。

    列は output・capital・human_capital・tfp（% / 年）。
    3 つの寄与の和が、output（所得の成長率）に等しい。
    """
    if start >= end:
        raise ValueError("期間の始まりは終わりより前でなければならない")
    available = set(panel.index.get_level_values("year"))
    for year in (start, end):
        if year not in available:
            raise ValueError(f"パネルに {year} 年がない")
    first = with_tfp(pd.DataFrame(panel.xs(start, level="year")), alpha)
    last = with_tfp(pd.DataFrame(panel.xs(end, level="year")), alpha)
    growth = 100 * (last / first).apply(np.log) / (end - start)
    return pd.DataFrame(
        {
            "output": growth["y"],
            "capital": alpha * growth["k"],
            "human_capital": (1 - alpha) * growth["h"],
            "tfp": growth["tfp"],
        }
    )


def contribution_shares(table: pd.DataFrame) -> pd.DataFrame:
    """各寄与が、所得の成長率に占める割合を返す。3 つの割合の合計は 1。"""
    if (table["output"] == 0).any():
        raise ValueError("成長率が 0 の国があるので、割合は求められない")
    return table[["capital", "human_capital", "tfp"]].div(table["output"], axis=0)
