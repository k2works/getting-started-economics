"""標本選択とヘックマンの 2 段階推定（Heckit）。"""

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray
from scipy import stats

from lib.chapter03.multiple import fit_ols
from lib.chapter14.discrete import BinaryFit, fit_binary


@dataclass(frozen=True)
class HeckitFit:
    """2 段階推定の結果。係数の最後の `lambda` は、逆ミルズ比の係数（= ρ·σ_u）。"""

    coefficients: pd.Series
    naive_standard_errors: pd.Series
    selection: BinaryFit
    n_selected: int


def inverse_mills_ratio(c: ArrayLike) -> NDArray[np.float64]:
    """逆ミルズ比 λ(c) = φ(c) ÷ Φ(c)。選択された観測値の、誤差項の平均の補正に使う。"""
    values = np.asarray(c, dtype=float)
    result: NDArray[np.float64] = stats.norm.pdf(values) / stats.norm.cdf(values)
    return result


def heckit_two_step(
    df: pd.DataFrame, x_columns: list[str], selection_columns: list[str]
) -> HeckitFit:
    """ヘックマンの 2 段階推定。

    第 1 段階: 選択（selected）を、selection_columns でプロビット（全標本）。
    第 2 段階: 選択された観測値だけで、y を、x_columns と逆ミルズ比 λ で回帰する。
    selection_columns には、x_columns に入らない変数（除外制約）を、含める。
    """
    selection = fit_binary(df["selected"], df[selection_columns], "probit")
    index = selection.coefficients.drop("const")
    linear = selection.coefficients["const"] + df[selection_columns] @ index
    chosen = df["selected"] == 1
    mills = pd.Series(inverse_mills_ratio(linear), index=df.index, name="lambda")
    columns = df.loc[chosen, x_columns].join(mills[chosen])
    second = fit_ols(df.loc[chosen, "y"], columns)
    return HeckitFit(
        coefficients=second.coefficients,
        naive_standard_errors=second.standard_errors,
        selection=selection,
        n_selected=int(chosen.sum()),
    )


def heckit_bootstrap_standard_errors(
    df: pd.DataFrame,
    x_columns: list[str],
    selection_columns: list[str],
    repetitions: int,
    rng: np.random.Generator,
) -> pd.Series:
    """ブートストラップ標準誤差: 全標本から復元抽出して、2 段階推定を繰り返す。

    λ は、第 1 段階の推定値なので、第 2 段階の OLS の標準誤差は、正しくない。
    """
    rows = []
    for _ in range(repetitions):
        sample = df.iloc[rng.integers(0, len(df), len(df))].reset_index(drop=True)
        rows.append(heckit_two_step(sample, x_columns, selection_columns).coefficients)
    return pd.DataFrame(rows).std(ddof=1)


def draw_selection_sample(
    n: int, correlation: float, rng: np.random.Generator
) -> pd.DataFrame:
    """選択（selected）と、選択された人だけで観測される y の標本。

    選択: 0.5 + x + z + v > 0、結果: y = 1 + 2x + u。z は結果の式に入らない。
    u = correlation·v + √(1 − correlation²)·w（選択と結果の誤差の相関が correlation）。
    """
    x, z, v, w = rng.standard_normal((4, n))
    u = correlation * v + math.sqrt(1 - correlation**2) * w
    selected = (0.5 + x + z + v > 0).astype(float)
    y = np.where(selected == 1, 1 + 2 * x + u, np.nan)
    return pd.DataFrame({"x": x, "z": z, "selected": selected, "y": y})


def selection_bias_experiment(
    n: int, correlation: float, repetitions: int, rng: np.random.Generator
) -> pd.DataFrame:
    """選択された標本の OLS と、2 段階推定の x の傾き（真の値 2）を繰り返す。"""
    rows = []
    for _ in range(repetitions):
        df = draw_selection_sample(n, correlation, rng)
        chosen = df[df["selected"] == 1]
        ols = fit_ols(chosen["y"], chosen[["x"]]).coefficients["x"]
        heckit = heckit_two_step(df, ["x"], ["x", "z"]).coefficients["x"]
        rows.append((ols, heckit))
    return pd.DataFrame(rows, columns=["ols_selected", "heckit"])
