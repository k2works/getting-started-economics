"""標本選択とヘックマンの 2 段階推定（Heckit）。"""

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray
from scipy import stats

from lib.chapter03.multiple import design_matrix, fit_ols
from lib.chapter14.discrete import BinaryFit, binary_covariance, fit_binary


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
    # 対数の差から作る（c が非常に小さくても、0 ÷ 0 にならない）
    result: NDArray[np.float64] = np.exp(
        stats.norm.logpdf(values) - stats.norm.logcdf(values)
    )
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


def heckit_corrected_standard_errors(
    df: pd.DataFrame, x_columns: list[str], selection_columns: list[str]
) -> pd.Series:
    """Heckman の補正した標準誤差（解析式）。第 1 段階の推定誤差も反映する。

    Var(b) = σ̂² (Z′Z)⁻¹ [Z′(I − ρ̂²Δ)Z + ρ̂² F V_γ F′] (Z′Z)⁻¹。
    Z は、第 2 段階の説明変数と λ̂。Δ は、対角成分が δ_i = λ̂_i (λ̂_i + w_i′γ̂) の行列。
    F = Z′Δ W（W は、選択された観測値の、選択の式の説明変数）。
    V_γ は、第 1 段階の共分散行列。σ̂² = e′e ÷ n_s + β̂_λ² · mean(δ)、ρ̂² = β̂_λ² ÷ σ̂²。
    """
    fit = heckit_two_step(df, x_columns, selection_columns)
    chosen = (df["selected"] == 1).to_numpy()
    selection_x = df[selection_columns]
    w_all, _ = design_matrix(selection_x)
    index = w_all @ fit.selection.coefficients.to_numpy()
    mills = inverse_mills_ratio(index)[chosen]
    delta = mills * (mills + index[chosen])
    z, names = design_matrix(df.loc[chosen, x_columns].assign(lambda_=mills))
    names[-1] = "lambda"
    y = df.loc[chosen, "y"].to_numpy(dtype=float)
    residuals = y - z @ fit.coefficients.to_numpy()
    lambda_coefficient = float(fit.coefficients["lambda"])
    sigma2 = float(residuals @ residuals) / len(y) + lambda_coefficient**2 * float(
        delta.mean()
    )
    rho2 = lambda_coefficient**2 / sigma2
    gram_inverse = np.linalg.inv(z.T @ z)
    f = z.T @ (delta[:, None] * w_all[chosen])
    v_gamma = binary_covariance(fit.selection, df["selected"], selection_x).to_numpy()
    middle = z.T @ (z - rho2 * delta[:, None] * z) + rho2 * f @ v_gamma @ f.T
    variance = sigma2 * gram_inverse @ middle @ gram_inverse
    return pd.Series(np.sqrt(np.diag(variance)), index=names)


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
