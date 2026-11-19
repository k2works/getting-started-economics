"""プーリング・データ: 差分の差分（DiD）と、パネル・データの 1 階差分推定。"""

import numpy as np
import pandas as pd

from lib.chapter03.multiple import OlsResult, fit_ols
from lib.chapter07.dummies import with_interaction


def group_period_means(df: pd.DataFrame) -> pd.DataFrame:
    """処置群・対照群の、処置の前後の、y の平均（2 × 2 の表）。"""
    table = df.groupby(["treated", "post"])["y"].mean().unstack()
    table.index = ["control", "treated"]
    table.columns = ["before", "after"]
    return table


def did_estimate(df: pd.DataFrame) -> float:
    """差分の差分 = (処置群の変化) − (対照群の変化)。"""
    means = group_period_means(df)
    change = means["after"] - means["before"]
    return float(change["treated"] - change["control"])


def did_regression(df: pd.DataFrame) -> OlsResult:
    """y を、処置群ダミー・処置後ダミー・その交差項で回帰する。交差項の係数が DiD。"""
    x = pd.DataFrame(
        {
            "treated": df["treated"],
            "post": df["post"],
            "treated:post": with_interaction(df["treated"], df["post"]),
        }
    )
    return fit_ols(df["y"], x)


def draw_did_sample(n: int, effect: float, rng: np.random.Generator) -> pd.DataFrame:
    """2 × 2（処置群・対照群 × 処置の前後）に、n 個ずつの標本を作る。

    y = 5 + 3·treated + 2·post + effect·treated·post + u（u は標準正規）。
    群の差 3 と、共通の時間変化 2 は、DiD で除かれる。
    """
    treated = np.repeat([0.0, 0.0, 1.0, 1.0], n)
    post = np.repeat([0.0, 1.0, 0.0, 1.0], n)
    y = 5 + 3 * treated + 2 * post + effect * treated * post
    return pd.DataFrame(
        {"y": y + rng.standard_normal(4 * n), "treated": treated, "post": post}
    )


def draw_panel(
    entities: int, periods: int, correlation: float, rng: np.random.Generator
) -> pd.DataFrame:
    """個人ごとの効果 a が x と相関するパネル・データ。真の傾きは 1。

    x = correlation·a + v、y = 1 + x + a + 0.5·u。
    """
    a = np.repeat(rng.standard_normal(entities), periods)
    x = correlation * a + rng.standard_normal(entities * periods)
    y = 1 + x + a + 0.5 * rng.standard_normal(entities * periods)
    return pd.DataFrame(
        {
            "entity": np.repeat(np.arange(entities), periods),
            "time": np.tile(np.arange(periods), entities),
            "x": x,
            "y": y,
        }
    )


def first_difference(panel: pd.DataFrame) -> pd.DataFrame:
    """個人ごとに、1 期前との差（Δy・Δx）を取る。最初の期は、差が取れないので除く。"""
    ordered = panel.sort_values(["entity", "time"])
    differences = ordered.groupby("entity")[["x", "y"]].diff().dropna()
    return differences.rename(columns={"x": "dx", "y": "dy"})


def first_difference_estimate(panel: pd.DataFrame) -> float:
    """1 階差分推定: Δy を Δx で回帰した傾き。個人ごとの効果 a が差で消える。"""
    d = first_difference(panel)
    return float(fit_ols(d["dy"], d[["dx"]]).coefficients["dx"])


def pooled_estimate(panel: pd.DataFrame) -> float:
    """プーリング OLS: 個人を区別せず、y を x で回帰した傾き。"""
    return float(fit_ols(panel["y"], panel[["x"]]).coefficients["x"])


def panel_estimators(
    entities: int,
    periods: int,
    correlation: float,
    repetitions: int,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """パネルを作り直して、プーリング OLS と 1 階差分推定を繰り返す（真の傾きは 1）。"""
    rows = []
    for _ in range(repetitions):
        panel = draw_panel(entities, periods, correlation, rng)
        rows.append((pooled_estimate(panel), first_difference_estimate(panel)))
    return pd.DataFrame(rows, columns=["pooled", "first_difference"])
