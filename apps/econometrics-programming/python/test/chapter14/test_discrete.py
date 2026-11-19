"""第 14 章: ロジット・プロビット（最尤法）のテスト。"""

import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm
from scipy import stats

from lib.chapter03.multiple import fit_ols
from lib.chapter14.discrete import (
    _score_and_weights,
    average_marginal_effects,
    draw_binary_sample,
    fit_binary,
    likelihood_ratio_test,
    linear_probability,
    log_likelihood,
    predicted_probabilities,
)

# 2 × 2 の表: x = 0 の 40 人のうち y = 1 は 10 人（確率 0.25）、x = 1 の 40 人のうち 30 人（0.75）
Y = np.r_[np.zeros(30), np.ones(10), np.zeros(10), np.ones(30)]
X = np.r_[np.zeros(40), np.ones(40)]


def sample(link: str = "logit", n: int = 500) -> pd.DataFrame:
    return draw_binary_sample(n, link, np.random.default_rng(0))


def test_定数項だけのロジットは対数オッズ() -> None:
    y = np.r_[np.ones(30), np.zeros(10)]
    fit = fit_binary(y, np.empty((40, 0)), "logit")
    assert fit.coefficients["const"] == pytest.approx(np.log(3))
    assert fit.coefficients["const"] == pytest.approx(1.0986, abs=1e-4)


def test_定数項だけのプロビットは標準正規分布の分位点() -> None:
    y = np.r_[np.ones(30), np.zeros(10)]
    fit = fit_binary(y, np.empty((40, 0)), "probit")
    assert fit.coefficients["const"] == pytest.approx(stats.norm.ppf(0.75))
    assert fit.coefficients["const"] == pytest.approx(0.6745, abs=1e-4)


def test_ダミー変数1つのロジットの傾きは対数オッズ比() -> None:
    fit = fit_binary(Y, X, "logit")
    assert fit.coefficients["const"] == pytest.approx(np.log(1 / 3))
    assert fit.coefficients["x1"] == pytest.approx(np.log(9))


def test_ダミー変数1つのプロビットの係数は分位点の差() -> None:
    fit = fit_binary(Y, X, "probit")
    assert fit.coefficients["const"] == pytest.approx(stats.norm.ppf(0.25))
    assert fit.coefficients["x1"] == pytest.approx(
        stats.norm.ppf(0.75) - stats.norm.ppf(0.25)
    )


def test_予測確率は表の割合に一致する() -> None:
    fit = fit_binary(Y, X, "logit")
    p = predicted_probabilities(fit, X)
    assert p[0] == pytest.approx(0.25)
    assert p[-1] == pytest.approx(0.75)


@pytest.mark.parametrize(
    ("link", "model"), [("logit", sm.Logit), ("probit", sm.Probit)]
)
def test_statsmodelsと係数も標準誤差も対数尤度も一致する(
    link: str, model: type
) -> None:
    s = sample(link)
    x = s[["x1", "x2"]]
    fit = fit_binary(s["y"], x, link)
    reference = model(s["y"], sm.add_constant(x)).fit(disp=0)
    assert fit.coefficients.to_numpy() == pytest.approx(reference.params.to_numpy())
    assert fit.standard_errors.to_numpy() == pytest.approx(reference.bse.to_numpy())
    assert fit.log_likelihood == pytest.approx(reference.llf)
    assert fit.n_obs == 500


@pytest.mark.parametrize(
    ("link", "model"), [("logit", sm.Logit), ("probit", sm.Probit)]
)
def test_平均限界効果はstatsmodelsと一致する(link: str, model: type) -> None:
    s = sample(link)
    x = s[["x1", "x2"]]
    fit = fit_binary(s["y"], x, link)
    reference = model(s["y"], sm.add_constant(x)).fit(disp=0).get_margeff().margeff
    assert average_marginal_effects(fit, x).to_numpy() == pytest.approx(reference)
    assert list(average_marginal_effects(fit, x).index) == ["x1", "x2"]


def test_対数尤度は最大値でスコアが0() -> None:
    s = sample()
    x = s[["x1", "x2"]]
    fit = fit_binary(s["y"], x, "logit")
    design = np.column_stack([np.ones(500), x.to_numpy()])
    beta = fit.coefficients.to_numpy()
    best = log_likelihood("logit", s["y"], design, beta)
    for direction in np.eye(3):
        for delta in (0.05, -0.05):
            assert (
                log_likelihood("logit", s["y"], design, beta + delta * direction) < best
            )
    residual = s["y"].to_numpy() - predicted_probabilities(fit, x)
    assert design.T @ residual == pytest.approx(0, abs=1e-7)


def test_完全に分離できるデータは収束しない() -> None:
    with pytest.raises(ValueError, match="完全分離"):
        fit_binary([0, 0, 0, 1, 1, 1], [1, 2, 3, 4, 5, 6])


def test_ニュートン法は2_x_2の表で5回で収束する() -> None:
    assert fit_binary(Y, X, "logit").iterations == 5
    assert fit_binary(Y, X, "probit").iterations == 5


def test_知らないリンク関数は受け付けない() -> None:
    with pytest.raises(ValueError, match="リンク"):
        fit_binary(Y, X, "cauchy")


def test_反復の回数が少ないと収束しない() -> None:
    s = sample()
    with pytest.raises(ValueError, match="収束"):
        fit_binary(s["y"], s[["x1", "x2"]], "logit", max_iterations=2)


def test_配列と列の名前() -> None:
    s = sample()
    named = fit_binary(s["y"], s[["x1", "x2"]])
    plain = fit_binary(s["y"], s[["x1", "x2"]].to_numpy())
    single = fit_binary(s["y"], s["x1"])
    assert list(named.coefficients.index) == ["const", "x1", "x2"]
    assert list(plain.coefficients.index) == ["const", "x1", "x2"]
    assert list(single.coefficients.index) == ["const", "x1"]
    assert named.coefficients.to_numpy() == pytest.approx(plain.coefficients.to_numpy())


def test_尤度比検定の手計算() -> None:
    test = likelihood_ratio_test(-40.0, -45.0, 2)
    assert test.statistic == pytest.approx(10)
    assert test.p_value == pytest.approx(stats.chi2.sf(10, 2))


def test_関係のある変数を除くと尤度比検定は棄却する() -> None:
    s = sample(n=1000)
    full = fit_binary(s["y"], s[["x1", "x2"]])
    restricted = fit_binary(s["y"], np.empty((1000, 0)))
    test = likelihood_ratio_test(full.log_likelihood, restricted.log_likelihood, 2)
    assert test.p_value < 1e-10


def test_関係のない変数を足しても尤度比検定は棄却しない() -> None:
    s = sample(n=1000)
    noise = np.random.default_rng(9).standard_normal(1000)
    full = fit_binary(s["y"], np.column_stack([s["x1"], s["x2"], noise]))
    restricted = fit_binary(s["y"], s[["x1", "x2"]])
    test = likelihood_ratio_test(full.log_likelihood, restricted.log_likelihood, 1)
    assert test.p_value > 0.05


def test_線形確率モデルはOLSの係数() -> None:
    s = sample()
    x = s[["x1", "x2"]]
    assert linear_probability(s["y"], x).to_numpy() == pytest.approx(
        fit_ols(s["y"], x).coefficients.to_numpy()
    )


def test_標本の形と割合() -> None:
    s = draw_binary_sample(50000, "probit", np.random.default_rng(0))
    assert list(s.columns) == ["y", "x1", "x2"]
    assert set(s["y"]) == {0.0, 1.0}
    expected = stats.norm.cdf(0.5 / (1 + 1 + 0.64) ** 0.5)
    assert s["y"].mean() == pytest.approx(expected, abs=0.01)


def test_ロジットの標本は標準ロジスティック分布の誤差() -> None:
    s = draw_binary_sample(100000, "logit", np.random.default_rng(1))
    fit = fit_binary(s["y"], s[["x1", "x2"]], "logit")
    assert fit.coefficients.to_numpy() == pytest.approx([0.5, 1.0, -0.8], abs=0.04)


def test_プロビットの標本ではプロビットの係数が真の値でロジットは約1点7倍() -> None:
    s = draw_binary_sample(100000, "probit", np.random.default_rng(1))
    probit = fit_binary(s["y"], s[["x1", "x2"]], "probit")
    logit = fit_binary(s["y"], s[["x1", "x2"]], "logit")
    assert probit.coefficients.to_numpy() == pytest.approx([0.5, 1.0, -0.8], abs=0.04)
    ratio = logit.coefficients["x1"] / probit.coefficients["x1"]
    assert ratio == pytest.approx(1.7, abs=0.1)


def test_平均限界効果はロジット_プロビット_線形確率モデルでほぼ同じ() -> None:
    s = draw_binary_sample(100000, "probit", np.random.default_rng(1))
    x = s[["x1", "x2"]]
    logit = average_marginal_effects(fit_binary(s["y"], x, "logit"), x)
    probit = average_marginal_effects(fit_binary(s["y"], x, "probit"), x)
    lpm = linear_probability(s["y"], x).drop("const")
    assert logit.to_numpy() == pytest.approx(probit.to_numpy(), abs=0.005)
    assert lpm.to_numpy() == pytest.approx(probit.to_numpy(), abs=0.01)


def test_線形確率モデルは確率の範囲の外に出ることがある() -> None:
    s = sample(n=2000)
    x = s[["x1", "x2"]]
    fitted = fit_ols(s["y"], x).coefficients
    values = fitted["const"] + x @ fitted[["x1", "x2"]]
    assert (values > 1).any() or (values < 0).any()
    probabilities = predicted_probabilities(fit_binary(s["y"], x), x)
    assert ((probabilities > 0) & (probabilities < 1)).all()


def test_極端な線形予測値でもスコアは有限() -> None:
    y = np.array([1.0, 0.0, 1.0])
    xb = np.array([-40.0, 40.0, -800.0])
    for link in ("logit", "probit"):
        score, weights = _score_and_weights(link, y, xb)
        assert np.all(np.isfinite(score))
        assert np.all(np.isfinite(weights))
    # 外れた観測値のスコアは、ほぼ |x′β|（誤って予測した側）になる
    probit_score, _ = _score_and_weights("probit", y, xb)
    assert probit_score == pytest.approx([40.0, -40.0, 800.0], rel=0.01)


def test_まれな外れ値があっても完全分離と誤報しない() -> None:
    rng = np.random.default_rng(0)
    x = rng.standard_normal(20000)
    y = (4 * x + rng.standard_normal(20000) > 0).astype(float)
    x = np.append(x, -6.0)
    y = np.append(y, 1.0)
    fit = fit_binary(y, x, "probit")
    # 最大値では、スコアの合計が 0（statsmodels は確率を 2.2e-16 で切り詰めるので、照合に使わない）
    design = sm.add_constant(x)
    score, _ = _score_and_weights("probit", y, design @ fit.coefficients.to_numpy())
    assert design.T @ score == pytest.approx([0.0, 0.0], abs=1e-6)
    assert fit.coefficients["x1"] == pytest.approx(3.4944, abs=1e-3)
