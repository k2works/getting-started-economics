"""操作変数法の検定（外生性・過剰識別）と、同時方程式・測定誤差への応用。"""

import math

import numpy as np
import pandas as pd
from scipy import stats

from lib.chapter03.multiple import fit_ols
from lib.chapter05.inference import TestResult, f_test
from lib.chapter12.iv import draw_iv_sample, two_stage_least_squares


def wu_hausman(
    y: pd.Series,
    endogenous: pd.Series,
    instruments: pd.DataFrame,
    exogenous: pd.DataFrame | None = None,
) -> TestResult:
    """Wu-Hausman 検定: 説明変数 x が外生か（帰無仮説: 外生）。

    第 1 段階の残差 v̂ を、元の回帰に足し、v̂ の係数が 0 かを F 検定する。
    x が外生なら、v̂（x の内生的な部分）は、y と関係しない。
    """
    columns = instruments if exogenous is None else exogenous.join(instruments)
    residual = fit_ols(endogenous, columns).residuals
    base = pd.DataFrame({endogenous.name: endogenous})
    if exogenous is not None:
        base = exogenous.join(base)
    return f_test(y, base.assign(v_hat=residual), ["v_hat"])


def sargan_test(
    y: pd.Series,
    endogenous: pd.DataFrame,
    instruments: pd.DataFrame,
    exogenous: pd.DataFrame | None = None,
) -> TestResult:
    """Sargan 検定（過剰識別制約の検定）: 操作変数が、すべて外生か（帰無仮説: 外生）。

    2SLS の残差 û を、外生の変数と、すべての操作変数で回帰する。
    LM = n · R² は、χ²(操作変数の数 − 内生変数の数) に従う。
    """
    degrees = instruments.shape[1] - endogenous.shape[1]
    if degrees <= 0:
        raise ValueError("操作変数が内生変数より多くないと、過剰識別の検定はできない")
    result = two_stage_least_squares(y, endogenous, instruments, exogenous)
    columns = instruments if exogenous is None else exogenous.join(instruments)
    statistic = result.n_obs * fit_ols(result.residuals, columns).r_squared
    return TestResult(float(statistic), float(stats.chi2.sf(statistic, degrees)))


def draw_overid_sample(
    n: int, invalid: float, rng: np.random.Generator
) -> pd.DataFrame:
    """操作変数が 2 つ（過剰識別）の標本。z2 が、誤差項 u と相関する度合いが invalid。

    y = 1 + x + u、x = z1 + z2 + v、u = 0.5·v + √0.75·w + invalid·z2。
    invalid = 0 なら、z1 も z2 も有効。invalid > 0 なら、z2 は無効（外生でない）。
    """
    z1, z2, v, w = rng.standard_normal((4, n))
    u = 0.5 * v + math.sqrt(0.75) * w + invalid * z2
    x = z1 + z2 + v
    return pd.DataFrame({"y": 1 + x + u, "x": x, "z1": z1, "z2": z2})


def wu_hausman_rejection_rate(
    n: int,
    endogeneity: float,
    repetitions: int,
    significance: float,
    rng: np.random.Generator,
) -> float:
    """Wu-Hausman 検定が、外生という帰無仮説を棄却する割合。"""
    rejected = 0
    for _ in range(repetitions):
        s = draw_iv_sample(n, 1.0, endogeneity, rng)
        rejected += wu_hausman(s["y"], s["x"], s[["z"]]).p_value < significance
    return rejected / repetitions


def sargan_rejection_rate(
    n: int,
    invalid: float,
    repetitions: int,
    significance: float,
    rng: np.random.Generator,
) -> float:
    """Sargan 検定が、操作変数は外生という帰無仮説を棄却する割合。"""
    rejected = 0
    for _ in range(repetitions):
        s = draw_overid_sample(n, invalid, rng)
        test = sargan_test(s["y"], s[["x"]], s[["z1", "z2"]])
        rejected += test.p_value < significance
    return rejected / repetitions


def draw_market_with_shifter(n: int, rng: np.random.Generator) -> pd.DataFrame:
    """需要曲線を識別できる、供給の変動要因 w（たとえば天候）つきの市場の標本。

    需要: q = 10 − p + u_d、供給: q = p + 2·w + u_s（w は需要に入らない）。
    均衡で、p = (10 + u_d − u_s − 2w) ÷ 2、q = (10 + u_d + u_s + 2w) ÷ 2。
    """
    u_d, u_s, w = rng.standard_normal((3, n))
    return pd.DataFrame(
        {
            "p": (10 + u_d - u_s - 2 * w) / 2,
            "q": (10 + u_d + u_s + 2 * w) / 2,
            "w": w,
        }
    )


def draw_two_measurements(
    n: int, error_sd: float, rng: np.random.Generator
) -> pd.DataFrame:
    """y = 1 + x* + u。x* を、独立な誤差で 2 回測った x1・x2（x* は分散 1）。"""
    x_true = rng.standard_normal(n)
    y = 1 + x_true + rng.standard_normal(n)
    return pd.DataFrame(
        {
            "y": y,
            "x1": x_true + error_sd * rng.standard_normal(n),
            "x2": x_true + error_sd * rng.standard_normal(n),
        }
    )
