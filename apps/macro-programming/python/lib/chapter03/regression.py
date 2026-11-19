"""回帰分析（最小二乗法）を、行列で書く。

y = X·β + 誤差 の β を、正規方程式 (X'X)·β = X'y を解いて求める。
定数項は、先頭の列（名前は const）として、自動で足す。
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class OlsResult:
    """最小二乗法の結果。"""

    coefficients: pd.Series
    standard_errors: pd.Series
    r_squared: float
    n_obs: int
    df_resid: int

    def t_values(self) -> pd.Series:
        """t 値 = 係数 ÷ 標準誤差。標準誤差が 0 なら、無限大になる。"""
        with np.errstate(divide="ignore", invalid="ignore"):
            return self.coefficients / self.standard_errors


def fit_ols(y: pd.Series, x: pd.DataFrame) -> OlsResult:
    """y を、定数項と x の各列に回帰する。

    係数 = (X'X)⁻¹X'y、標準誤差 = √(σ²·(X'X)⁻¹ の対角)、σ² = 残差の二乗和 ÷ (n − k)、
    決定係数 = 1 − 残差の二乗和 ÷ y の変動の二乗和。
    """
    if len(y) != len(x):
        raise ValueError("y と x の長さが違う")
    design = np.column_stack([np.ones(len(x)), x.to_numpy(dtype=float)])
    n, k = design.shape
    if n <= k:
        raise ValueError("観測数は、係数の数より多くなければならない")
    if np.linalg.matrix_rank(design) < k:
        raise ValueError("説明変数が完全に共線形なので、係数が決まらない")
    values = y.to_numpy(dtype=float)
    gram = design.T @ design
    beta = np.linalg.solve(gram, design.T @ values)
    residuals = values - design @ beta
    sum_squared_residuals = float(residuals @ residuals)
    total_variation = float(((values - values.mean()) ** 2).sum())
    if total_variation == 0:
        raise ValueError("y に差がないので、決定係数は求められない")
    sigma_squared = sum_squared_residuals / (n - k)
    errors = np.sqrt(np.diag(sigma_squared * np.linalg.inv(gram)))
    names = ["const", *x.columns]
    return OlsResult(
        coefficients=pd.Series(beta, index=names),
        standard_errors=pd.Series(errors, index=names),
        r_squared=1 - sum_squared_residuals / total_variation,
        n_obs=n,
        df_resid=n - k,
    )


def development_accounting_regression(df: pd.DataFrame) -> OlsResult:
    """対数の所得を、対数の物的資本・対数の人的資本に回帰する（第 1 章のデータ）。

    係数は、資本分配率 α と 1 − α の推定値に見える。ただし、TFP が資本と
    相関していると、係数は偏る（欠落変数バイアス）。
    """
    y = np.log(df["y"])
    x = pd.DataFrame({"ln_k": np.log(df["k"]), "ln_h": np.log(df["h"])})
    return fit_ols(y, x)
