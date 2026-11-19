"""第 10 章: 固定効果・ランダム効果・相関ランダム効果・Hausman 検定のテスト。"""

import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm
from linearmodels.panel import PanelOLS, RandomEffects
from scipy import stats

from lib.chapter03.multiple import fit_ols
from lib.chapter09.did import (
    draw_panel,
    first_difference,
    first_difference_estimate,
    pooled_estimate,
)
from lib.chapter10.panel import (
    PanelFit,
    cluster_standard_errors,
    correlated_random_effects,
    estimator_comparison,
    fixed_effects,
    hausman_rejection_rate,
    hausman_test,
    least_squares_dummy_variables,
    pooled_standard_errors,
    random_effects,
    random_effects_theta,
    within_transform,
)
from test.chapter09.test_did import PANEL


def sample(
    entities: int = 50, periods: int = 4, correlation: float = 0.7
) -> pd.DataFrame:
    return draw_panel(entities, periods, correlation, np.random.default_rng(0))


def known_fit(coefficient: float, variance: float, sigma2: float) -> PanelFit:
    return PanelFit(
        pd.Series({"x": coefficient}),
        pd.Series({"x": variance**0.5}),
        pd.DataFrame({"x": [variance]}, index=["x"]),
        sigma2,
        0.5,
        10,
        8,
    )


def test_ウィズイン変換は個人ごとの平均を引く() -> None:
    tilde = within_transform(PANEL, ["x", "y"])
    assert tilde["x"].tolist() == [-0.5, 0.5, -1, 1, -1.5, 1.5]
    assert tilde["y"].tolist() == [-1, 1, -2, 2, -3, 3]


def test_ウィズイン変換すると個人ごとの平均は0() -> None:
    panel = sample()
    tilde = within_transform(panel, ["x", "y"])
    means = tilde.groupby(panel["entity"]).mean()
    assert means.to_numpy() == pytest.approx(0, abs=1e-12)


def test_固定効果は個人の効果を除いて真の傾きを復元する() -> None:
    fit = fixed_effects(PANEL, "y", ["x"])
    assert fit.coefficients["x"] == pytest.approx(2)
    assert fit.standard_errors["x"] == pytest.approx(0, abs=1e-9)
    assert fit.df_resid == 6 - 3 - 1
    assert fit.n_obs == 6


def test_固定効果とダミー変数推定は係数も標準誤差もちょうど一致する() -> None:
    panel = sample()
    fit = fixed_effects(panel, "y", ["x"])
    dummy = least_squares_dummy_variables(panel, "y", ["x"])
    assert dummy.loc["x", "coefficient"] == pytest.approx(
        fit.coefficients["x"], abs=1e-10
    )
    assert dummy.loc["x", "standard_error"] == pytest.approx(
        fit.standard_errors["x"], abs=1e-10
    )


def test_固定効果はlinearmodelsと一致する() -> None:
    panel = sample()
    fit = fixed_effects(panel, "y", ["x"])
    reference = PanelOLS.from_formula(
        "y ~ x + EntityEffects", panel.set_index(["entity", "time"])
    ).fit()
    assert fit.coefficients["x"] == pytest.approx(reference.params["x"])
    assert fit.standard_errors["x"] == pytest.approx(reference.std_errors["x"])


def test_2期間の固定効果は定数項なしの1階差分とちょうど一致する() -> None:
    panel = draw_panel(60, 2, 0.8, np.random.default_rng(1))
    d = first_difference(panel)
    no_constant = fit_ols(d["dy"], d[["dx"]], constant=False).coefficients["dx"]
    assert fixed_effects(panel, "y", ["x"]).coefficients["x"] == pytest.approx(
        no_constant
    )


def test_定数項ありの1階差分は固定効果と少しだけ違う() -> None:
    panel = draw_panel(60, 2, 0.8, np.random.default_rng(1))
    with_constant = first_difference_estimate(panel)
    fixed = fixed_effects(panel, "y", ["x"]).coefficients["x"]
    assert with_constant != pytest.approx(fixed, abs=1e-6)
    assert with_constant == pytest.approx(fixed, abs=0.05)


def test_相関ランダム効果の係数は固定効果とちょうど一致する() -> None:
    panel = sample()
    cre = correlated_random_effects(panel, "y", ["x"])
    assert cre.loc["x", "coefficient"] == pytest.approx(
        fixed_effects(panel, "y", ["x"]).coefficients["x"], abs=1e-10
    )


def test_ランダム効果はlinearmodelsと一致する() -> None:
    panel = sample()
    fit = random_effects(panel, "y", ["x"])
    reference = RandomEffects.from_formula(
        "y ~ 1 + x", panel.set_index(["entity", "time"])
    ).fit()
    assert fit.coefficients["x"] == pytest.approx(reference.params["x"])
    assert fit.coefficients["const"] == pytest.approx(reference.params["Intercept"])
    assert fit.standard_errors["x"] == pytest.approx(reference.std_errors["x"])
    assert random_effects_theta(panel, "y", ["x"]) == pytest.approx(
        float(np.asarray(reference.theta)[0, 0])
    )


def test_θは0から1の間() -> None:
    assert 0 < random_effects_theta(sample(), "y", ["x"]) < 1


def test_個人の効果がなければθは0でランダム効果はプーリングに一致する() -> None:
    rng = np.random.default_rng(4)
    panel = pd.DataFrame(
        {
            "entity": np.repeat(range(4), 6),
            "time": np.tile(range(6), 4),
            "x": rng.standard_normal(24),
        }
    )
    panel["y"] = 1 + panel["x"] + rng.standard_normal(24)
    assert random_effects_theta(panel, "y", ["x"]) == 0
    pooled = fit_ols(panel["y"], panel[["x"]])
    fit = random_effects(panel, "y", ["x"])
    assert fit.coefficients["x"] == pytest.approx(pooled.coefficients["x"])
    assert fit.coefficients["const"] == pytest.approx(pooled.coefficients["const"])


def test_期数がそろっていないパネルは扱わない() -> None:
    with pytest.raises(ValueError, match="バランス"):
        random_effects_theta(sample().iloc[:-1], "y", ["x"])


def test_Hausman統計量の手計算() -> None:
    test = hausman_test(known_fit(1.0, 0.04, 1.0), known_fit(0.7, 0.01, 1.0), ["x"])
    assert test.statistic == pytest.approx(0.3**2 / (0.04 - 0.01))
    assert test.p_value == pytest.approx(stats.chi2.sf(3.0, 1))


def test_Hausman検定はランダム効果の分散を固定効果のσ2にそろえる() -> None:
    test = hausman_test(known_fit(1.0, 0.04, 1.0), known_fit(0.7, 0.01, 2.0), ["x"])
    assert test.statistic == pytest.approx(0.09 / 0.035)


def test_Hausman検定は係数が2つなら自由度2のカイ2乗() -> None:
    def fit(b: tuple[float, float], v: tuple[float, float]) -> PanelFit:
        return PanelFit(
            pd.Series({"x": b[0], "z": b[1]}),
            pd.Series({"x": v[0] ** 0.5, "z": v[1] ** 0.5}),
            pd.DataFrame(np.diag(v), index=["x", "z"], columns=["x", "z"]),
            1.0,
            0.5,
            10,
            8,
        )

    test = hausman_test(
        fit((1.0, 2.0), (0.04, 0.09)), fit((0.5, 1.5), (0.01, 0.01)), ["x", "z"]
    )
    expected = 0.25 / 0.03 + 0.25 / 0.08
    assert test.statistic == pytest.approx(expected)
    assert test.p_value == pytest.approx(stats.chi2.sf(expected, 2))


def test_個人の効果が説明変数と相関するとHausman検定は棄却する() -> None:
    rate = hausman_rejection_rate(100, 5, 1.0, 100, 0.05, np.random.default_rng(0))
    assert rate > 0.95


def test_相関がなければHausman検定の棄却率は有意水準に近い() -> None:
    rate = hausman_rejection_rate(200, 5, 0.0, 300, 0.05, np.random.default_rng(0))
    assert rate == pytest.approx(0.05, abs=4 * (0.05 * 0.95 / 300) ** 0.5)


def test_クラスター標準誤差はstatsmodelsと一致する() -> None:
    panel = sample()
    robust = cluster_standard_errors(panel["y"], panel[["x"]], panel["entity"])
    reference = sm.OLS(panel["y"], sm.add_constant(panel[["x"]])).fit(
        cov_type="cluster", cov_kwds={"groups": panel["entity"]}
    )
    assert robust.to_numpy() == pytest.approx(reference.bse.to_numpy())
    assert list(robust.index) == ["const", "x"]


def test_相関があるとプーリングは偏りランダム効果は中間で固定効果は偏らない() -> None:
    table = estimator_comparison(200, 5, 1.0, 300, np.random.default_rng(0))
    means = table.mean()
    se = table.std() / 300**0.5
    assert abs(means["fixed_effects"] - 1.0) < 4 * se["fixed_effects"]
    assert abs(means["pooled"] - 1.5) < 4 * se["pooled"]
    assert means["fixed_effects"] < means["random_effects"] < means["pooled"]


def test_相関がなければ3つの推定量はどれも偏らない() -> None:
    table = estimator_comparison(200, 5, 0.0, 300, np.random.default_rng(0))
    se = table.std() / 300**0.5
    for name in table.columns:
        assert abs(table[name].mean() - 1.0) < 4 * se[name]
    assert table["pooled"].std() > table["fixed_effects"].std()


def test_個人内で相関があると通常の標準誤差は過小でクラスターは近い() -> None:
    r = pooled_standard_errors(100, 5, 500, np.random.default_rng(0))
    assert r["classical"] < 0.75 * r["sd"]
    assert r["clustered"] == pytest.approx(r["sd"], rel=0.1)


def test_プーリングの推定値は手計算と一致する() -> None:
    assert pooled_estimate(PANEL) == pytest.approx(3.2)


def test_クラスターが1つなら頑健な標準誤差は計算できない() -> None:
    x = pd.DataFrame({"x": [1.0, 2.0, 3.0, 4.0, 6.0, 7.0]})
    y = pd.Series([2.0, 3.0, 3.0, 5.0, 4.0, 8.0])
    with pytest.raises(ValueError, match="クラスター"):
        cluster_standard_errors(y, x, pd.Series([1, 1, 1, 1, 1, 1]))


def test_期間の数がそろわないパネルでも固定効果はlinearmodelsと一致する() -> None:
    panel = sample()
    unbalanced = panel.drop(panel.index[::7]).reset_index(drop=True)
    assert unbalanced.groupby("entity").size().nunique() > 1
    fit = fixed_effects(unbalanced, "y", ["x"])
    reference = PanelOLS.from_formula(
        "y ~ x + EntityEffects", unbalanced.set_index(["entity", "time"])
    ).fit()
    assert fit.coefficients["x"] == pytest.approx(reference.params["x"])
    assert fit.standard_errors["x"] == pytest.approx(reference.std_errors["x"])
