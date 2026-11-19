"""パネル・データ分析: 固定効果・ランダム効果・相関ランダム効果・Hausman 検定。"""

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from lib.chapter03.multiple import fit_ols
from lib.chapter05.inference import TestResult
from lib.chapter07.dummies import make_dummies
from lib.chapter09.did import draw_panel, pooled_estimate


@dataclass(frozen=True)
class PanelFit:
    """パネル・データの推定結果（係数・標準誤差・共分散行列・誤差の分散の推定値）。"""

    coefficients: pd.Series
    standard_errors: pd.Series
    covariance: pd.DataFrame
    sigma2: float
    r_squared: float
    n_obs: int
    df_resid: int


def within_transform(
    panel: pd.DataFrame, columns: list[str], entity: str = "entity"
) -> pd.DataFrame:
    """ウィズイン変換: 各列から、個人ごとの平均を引く。"""
    means = panel.groupby(entity)[columns].transform("mean")
    return panel[columns] - means


def _fit_without_constant(y: pd.Series, x: pd.DataFrame, df_resid: int) -> PanelFit:
    """定数項なしの回帰。誤差の分散は、指定した自由度 df_resid で割って推定する。"""
    result = fit_ols(y, x, constant=False)
    design = x.to_numpy(dtype=float)
    sigma2 = float(result.residuals @ result.residuals) / df_resid
    covariance = sigma2 * np.linalg.inv(design.T @ design)
    names = list(x.columns)
    return PanelFit(
        coefficients=result.coefficients,
        standard_errors=pd.Series(np.sqrt(np.diag(covariance)), index=names),
        covariance=pd.DataFrame(covariance, index=names, columns=names),
        sigma2=sigma2,
        r_squared=result.r_squared,
        n_obs=len(y),
        df_resid=df_resid,
    )


def fixed_effects(
    panel: pd.DataFrame, y: str, xs: list[str], entity: str = "entity"
) -> PanelFit:
    """固定効果推定: ウィズイン変換した y を、x で回帰する（定数項なし）。

    個人の数 N を引いた、自由度 n − N − k で、標準誤差を計算する。
    """
    tilde = within_transform(panel, [y, *xs], entity)
    df_resid = len(panel) - panel[entity].nunique() - len(xs)
    return _fit_without_constant(tilde[y], tilde[xs], df_resid)


def least_squares_dummy_variables(
    panel: pd.DataFrame, y: str, xs: list[str], entity: str = "entity"
) -> pd.DataFrame:
    """ダミー変数による固定効果推定: 個人ごとのダミー変数を、説明変数に足して回帰する。

    x の係数と標準誤差の表（列は coefficient・standard_error）を返す。
    """
    result = fit_ols(panel[y], panel[xs].join(make_dummies(panel[entity])))
    return pd.DataFrame(
        {
            "coefficient": result.coefficients[xs],
            "standard_error": result.standard_errors[xs],
        }
    )


def _balanced_periods(panel: pd.DataFrame, entity: str) -> int:
    counts = panel.groupby(entity).size()
    if counts.nunique() != 1:
        raise ValueError("バランスしたパネル（どの個人も同じ期数）だけを扱う")
    return int(counts.iloc[0])


def random_effects_theta(
    panel: pd.DataFrame, y: str, xs: list[str], entity: str = "entity"
) -> float:
    """ランダム効果の θ（Swamy-Arora の分散成分から求める）。

    σ_u² は固定効果の誤差の分散、σ_b² = σ_a² + σ_u² ÷ T は個人平均の回帰の
    誤差の分散。θ = 1 − √(σ_u² ÷ (σ_u² + T·σ_a²))。
    """
    periods = _balanced_periods(panel, entity)
    sigma_u2 = fixed_effects(panel, y, xs, entity).sigma2
    means = panel.groupby(entity)[[y, *xs]].mean()
    between = fit_ols(means[y], means[xs])
    sigma_b2 = float(between.residuals @ between.residuals) / between.df_resid
    sigma_a2 = max(sigma_b2 - sigma_u2 / periods, 0.0)
    return 1 - math.sqrt(sigma_u2 / (sigma_u2 + periods * sigma_a2))


def random_effects(
    panel: pd.DataFrame, y: str, xs: list[str], entity: str = "entity"
) -> PanelFit:
    """ランダム効果推定: 個人平均の θ 倍を引いた（準差分の）変数で、回帰する。"""
    theta = random_effects_theta(panel, y, xs, entity)
    columns = [y, *xs]
    means = panel.groupby(entity)[columns].transform("mean")
    quasi = panel[columns] - theta * means
    x = quasi[xs].assign(const=1 - theta)[["const", *xs]]
    return _fit_without_constant(quasi[y], x, len(panel) - len(xs) - 1)


def correlated_random_effects(
    panel: pd.DataFrame, y: str, xs: list[str], entity: str = "entity"
) -> pd.DataFrame:
    """相関ランダム効果（Mundlak）: x の個人平均を足して、プーリング OLS で回帰する。

    x の係数は、固定効果推定と、ちょうど一致する。
    """
    means = panel.groupby(entity)[xs].transform("mean").add_suffix("_mean")
    result = fit_ols(panel[y], panel[xs].join(means))
    return pd.DataFrame(
        {
            "coefficient": result.coefficients[xs],
            "standard_error": result.standard_errors[xs],
        }
    )


def hausman_test(fixed: PanelFit, random: PanelFit, names: list[str]) -> TestResult:
    """Hausman 検定: 固定効果とランダム効果の係数が、同じか（帰無仮説: 同じ）。

    H = (b_fe − b_re)′ (V_fe − V_re)⁻¹ (b_fe − b_re) は、χ²(k) に従う。
    2 つの推定で誤差の分散の推定値が違うと、H が負になることがある。
    そこで、ランダム効果の共分散行列を、固定効果の σ² に、そろえて使う。
    """
    diff = (fixed.coefficients[names] - random.coefficients[names]).to_numpy()
    scale = fixed.sigma2 / random.sigma2
    variance = (
        fixed.covariance.loc[names, names] - scale * random.covariance.loc[names, names]
    ).to_numpy()
    statistic = float(diff @ np.linalg.inv(variance) @ diff)
    return TestResult(statistic, float(stats.chi2.sf(statistic, len(names))))


def cluster_standard_errors(
    y: pd.Series, x: pd.DataFrame, groups: pd.Series
) -> pd.Series:
    """個人（クラスター）ごとの相関に頑健な標準誤差。同じ個人の誤差は、相関してよい。

    Var(b) = (X′X)⁻¹ · Σ_g X_g′ e_g e_g′ X_g · (X′X)⁻¹ に、
    G ÷ (G − 1) · (n − 1) ÷ (n − k) を掛ける。
    """
    result = fit_ols(y, x)
    design = np.column_stack([np.ones(len(x)), x.to_numpy(dtype=float)])
    n, k = design.shape
    scores = (
        pd.DataFrame(design * result.residuals[:, None])
        .groupby(groups.to_numpy())
        .sum()
    )
    meat = scores.to_numpy().T @ scores.to_numpy()
    g = len(scores)
    bread = np.linalg.inv(design.T @ design)
    variance = g / (g - 1) * (n - 1) / (n - k) * bread @ meat @ bread
    return pd.Series(np.sqrt(np.diag(variance)), index=result.coefficients.index)


def estimator_comparison(
    entities: int,
    periods: int,
    correlation: float,
    repetitions: int,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """パネルを作り直し、3 つの推定量（真の傾きは 1）を繰り返す。"""
    rows = []
    for _ in range(repetitions):
        panel = draw_panel(entities, periods, correlation, rng)
        rows.append(
            (
                pooled_estimate(panel),
                fixed_effects(panel, "y", ["x"]).coefficients["x"],
                random_effects(panel, "y", ["x"]).coefficients["x"],
            )
        )
    return pd.DataFrame(rows, columns=["pooled", "fixed_effects", "random_effects"])


def hausman_rejection_rate(
    entities: int,
    periods: int,
    correlation: float,
    repetitions: int,
    significance: float,
    rng: np.random.Generator,
) -> float:
    """Hausman 検定が、同じという帰無仮説を、棄却する割合。"""
    rejected = 0
    for _ in range(repetitions):
        panel = draw_panel(entities, periods, correlation, rng)
        test = hausman_test(
            fixed_effects(panel, "y", ["x"]), random_effects(panel, "y", ["x"]), ["x"]
        )
        rejected += test.p_value < significance
    return rejected / repetitions


def pooled_standard_errors(
    entities: int, periods: int, repetitions: int, rng: np.random.Generator
) -> dict[str, float]:
    """プーリング OLS の傾きのばらつきと、通常・クラスター標準誤差の平均。

    x = m + v（m は個人ごとの成分）、y = 1 + x + a + 0.5·u（a は個人ごとの効果）。
    a と m は無関係なので、推定値は偏らないが、同じ個人の誤差と x が、相関する。
    """
    slopes, classical, clustered = [], [], []
    for _ in range(repetitions):
        entity = np.repeat(np.arange(entities), periods)
        n = entities * periods
        m = np.repeat(rng.standard_normal(entities), periods)
        a = np.repeat(rng.standard_normal(entities), periods)
        x = pd.DataFrame({"x": m + rng.standard_normal(n)})
        y = pd.Series(1 + x["x"] + a + 0.5 * rng.standard_normal(n))
        result = fit_ols(y, x)
        slopes.append(result.coefficients["x"])
        classical.append(result.standard_errors["x"])
        clustered.append(cluster_standard_errors(y, x, pd.Series(entity))["x"])
    return {
        "sd": float(np.std(slopes, ddof=1)),
        "classical": float(np.mean(classical)),
        "clustered": float(np.mean(clustered)),
    }
