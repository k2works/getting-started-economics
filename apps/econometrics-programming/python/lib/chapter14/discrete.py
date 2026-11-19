"""離散選択モデル: ロジット・プロビットの最尤法、限界効果、尤度比検定。"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray
from scipy import stats

from lib.chapter03.multiple import fit_ols, regressor_names
from lib.chapter05.inference import TestResult

# リンク関数（誤差項の分布）: ロジットは標準ロジスティック分布、プロビットは標準正規分布
LINKS = {"logit": stats.logistic, "probit": stats.norm}


@dataclass(frozen=True)
class BinaryFit:
    """ロジット・プロビットの推定結果。"""

    coefficients: pd.Series
    standard_errors: pd.Series
    log_likelihood: float
    n_obs: int
    iterations: int
    link: str


def _design(x: ArrayLike) -> tuple[NDArray[np.float64], list[str]]:
    """定数項を先頭に足した説明変数の行列と、係数の名前。"""
    values = np.asarray(x, dtype=float)
    if values.ndim == 1:
        values = values.reshape(-1, 1)
    names = regressor_names(x, values.shape[1])
    return np.column_stack([np.ones(len(values)), values]), ["const", *names]


def log_likelihood(
    link: str, y: ArrayLike, design: NDArray[np.float64], beta: NDArray[np.float64]
) -> float:
    """対数尤度 Σ [y·ln F(x′β) + (1 − y)·ln(1 − F(x′β))]。"""
    dist = LINKS[link]
    xb = design @ beta
    values = np.asarray(y, dtype=float)
    return float(np.sum(values * dist.logcdf(xb) + (1 - values) * dist.logsf(xb)))


def _score_and_weights(
    link: str, y: NDArray[np.float64], xb: NDArray[np.float64]
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """x′β についての、対数尤度の 1 階微分（スコア）と、2 階微分の符号を変えたもの。"""
    dist = LINKS[link]
    q = 2 * y - 1
    # 比を、対数の差から作る（極端な x′β でも、0 ÷ 0 や 0 での除算にならない）
    lam = q * np.exp(dist.logpdf(xb) - dist.logcdf(q * xb))
    if link == "logit":
        p = dist.cdf(xb)
        return lam, p * (1 - p)
    return lam, lam * (lam + xb)


def fit_binary(
    y: ArrayLike, x: ArrayLike, link: str = "logit", max_iterations: int = 100
) -> BinaryFit:
    """最尤法（ニュートン法）でロジット・プロビットを推定する。

    β ← β + (X′WX)⁻¹ X′s。s は x′β についてのスコア、W は 2 階微分の符号を変えたもの。
    収束しないとき（完全分離など）は、エラーにする。
    """
    if link not in LINKS:
        raise ValueError(f"知らないリンク関数: {link}（logit か probit）")
    design, names = _design(x)
    target = np.asarray(y, dtype=float)
    if np.linalg.matrix_rank(design) < design.shape[1]:
        raise ValueError("多重共線性（説明変数の間に、完全な線形関係がある）")
    beta = np.zeros(design.shape[1])
    for iteration in range(1, max_iterations + 1):
        score, weights = _score_and_weights(link, target, design @ beta)
        information = design.T @ (design * weights[:, None])
        try:
            step = np.linalg.solve(information, design.T @ score)
        except np.linalg.LinAlgError:
            raise ValueError("収束しない（完全分離の可能性がある）") from None
        beta = beta + step
        if np.max(np.abs(step)) < 1e-10:
            _, weights = _score_and_weights(link, target, design @ beta)
            covariance = np.linalg.inv(design.T @ (design * weights[:, None]))
            return BinaryFit(
                coefficients=pd.Series(beta, index=names),
                standard_errors=pd.Series(np.sqrt(np.diag(covariance)), index=names),
                log_likelihood=log_likelihood(link, target, design, beta),
                n_obs=len(target),
                iterations=iteration,
                link=link,
            )
    raise ValueError("収束しない（完全分離の可能性がある）")


def predicted_probabilities(fit: BinaryFit, x: ArrayLike) -> NDArray[np.float64]:
    """P(y = 1 | x) = F(x′β)。"""
    design, _ = _design(x)
    result: NDArray[np.float64] = LINKS[fit.link].cdf(
        design @ fit.coefficients.to_numpy()
    )
    return result


def average_marginal_effects(fit: BinaryFit, x: ArrayLike) -> pd.Series:
    """平均限界効果 = 密度 f(x′β) の平均 × 係数（連続変数）。定数項は含めない。"""
    design, _ = _design(x)
    density = LINKS[fit.link].pdf(design @ fit.coefficients.to_numpy())
    return float(np.mean(density)) * fit.coefficients.drop("const")


def likelihood_ratio_test(
    log_likelihood_full: float, log_likelihood_restricted: float, restrictions: int
) -> TestResult:
    """尤度比検定: LR = 2 · (ln L_制約なし − ln L_制約あり) ~ χ²(制約の数)。"""
    statistic = 2 * (log_likelihood_full - log_likelihood_restricted)
    return TestResult(float(statistic), float(stats.chi2.sf(statistic, restrictions)))


def linear_probability(y: ArrayLike, x: ArrayLike) -> pd.Series:
    """線形確率モデル: y（0 か 1）を、OLS で x に回帰した係数。"""
    return fit_ols(y, x).coefficients


def draw_binary_sample(n: int, link: str, rng: np.random.Generator) -> pd.DataFrame:
    """潜在変数 y* = 0.5 + x1 − 0.8·x2 + ε から、y = 1（y* > 0）の標本を作る。

    ε は、link が logit なら標準ロジスティック分布、probit なら標準正規分布。
    """
    x1, x2 = rng.standard_normal((2, n))
    error = rng.logistic(size=n) if link == "logit" else rng.standard_normal(n)
    latent = 0.5 + x1 - 0.8 * x2 + error
    return pd.DataFrame({"y": (latent > 0).astype(float), "x1": x1, "x2": x2})
