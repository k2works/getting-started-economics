"""第 8 章: 不均一分散（頑健な標準誤差・検定）のテスト。"""

import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan, het_white, linear_reset

from lib.chapter03.multiple import fit_ols
from lib.chapter08.hetero import (
    breusch_pagan,
    draw_fan_sample,
    reset_test,
    robust_standard_errors,
    standard_error_comparison,
    white_test,
)

X = [1, 2, 3, 4]
Y = [2, 4, 5, 9]


def two_variable_data(n: int = 80, seed: int = 0) -> tuple[pd.Series, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    x = pd.DataFrame({"x1": rng.standard_normal(n), "x2": rng.standard_normal(n)})
    y = 1 + x["x1"] + 0.5 * x["x2"] + (0.5 + np.abs(x["x1"])) * rng.standard_normal(n)
    return y, x


def test_手計算の例のHC0とHC1() -> None:
    hc0 = robust_standard_errors(Y, X, "HC0")
    hc1 = robust_standard_errors(Y, X, "HC1")
    assert hc0["x1"] == pytest.approx((1.61 / 25) ** 0.5)
    assert hc1["x1"] == pytest.approx((2 * 1.61 / 25) ** 0.5)
    assert hc0["x1"] == pytest.approx(0.2538, abs=1e-4)
    assert hc1["x1"] == pytest.approx(0.3589, abs=1e-4)


def test_既定はHC1() -> None:
    assert (
        robust_standard_errors(Y, X).tolist()
        == robust_standard_errors(Y, X, "HC1").tolist()
    )


@pytest.mark.parametrize("kind", ["HC0", "HC1", "HC2", "HC3"])
def test_頑健な標準誤差はstatsmodelsと一致する(kind: str) -> None:
    y, x = two_variable_data()
    reference = sm.OLS(y, sm.add_constant(x)).fit(cov_type=kind).bse
    assert robust_standard_errors(y, x, kind).to_numpy() == pytest.approx(
        reference.to_numpy()
    )


def test_HC3はHC2より大きくHC2はHC0より大きい() -> None:
    se = {k: robust_standard_errors(Y, X, k)["x1"] for k in ("HC0", "HC2", "HC3")}
    assert se["HC0"] < se["HC2"] < se["HC3"]


def test_知らない種類は受け付けない() -> None:
    with pytest.raises(ValueError, match="種類"):
        robust_standard_errors(Y, X, "HC9")


def test_配列でも使える() -> None:
    assert list(robust_standard_errors(Y, np.array(X, dtype=float)).index) == [
        "const",
        "x1",
    ]


def test_Breusch_Paganはstatsmodelsと一致する() -> None:
    y, x = two_variable_data()
    fit = sm.OLS(y, sm.add_constant(x)).fit()
    lm, p, _, _ = het_breuschpagan(fit.resid, fit.model.exog)
    test = breusch_pagan(y, x)
    assert test.statistic == pytest.approx(lm)
    assert test.p_value == pytest.approx(p)


def test_Whiteはstatsmodelsと一致する() -> None:
    y, x = two_variable_data()
    fit = sm.OLS(y, sm.add_constant(x)).fit()
    lm, p, _, _ = het_white(fit.resid, fit.model.exog)
    test = white_test(y, x)
    assert test.statistic == pytest.approx(lm)
    assert test.p_value == pytest.approx(p)


def test_RESETはstatsmodelsと一致する() -> None:
    y, x = two_variable_data()
    fit = sm.OLS(y, sm.add_constant(x)).fit()
    reference = linear_reset(fit, power=3, test_type="fitted", use_f=True)
    test = reset_test(y, x)
    assert test.statistic == pytest.approx(float(reference.fvalue))
    assert test.p_value == pytest.approx(float(reference.pvalue))


def test_不均一分散のデータでは均一分散の帰無仮説を棄却する() -> None:
    x, y = draw_fan_sample(200, np.random.default_rng(1), True)
    assert breusch_pagan(y, x).p_value < 0.001
    assert white_test(y, x).p_value < 0.001


def test_均一分散のデータでは棄却しない() -> None:
    x, y = draw_fan_sample(200, np.random.default_rng(1), False)
    # 種を固定した 1 標本の例示。帰無仮説が正しくても、種を変えれば、約 5% で p < 0.05 になる
    assert breusch_pagan(y, x).p_value > 0.05
    assert white_test(y, x).p_value > 0.05


def test_RESETは2乗の項が欠落したモデルを棄却する() -> None:
    rng = np.random.default_rng(3)
    x = rng.uniform(0, 3, 200)
    y = 1 + x + 0.8 * x**2 + 0.3 * rng.standard_normal(200)
    assert reset_test(y, x).p_value < 0.001
    linear = 1 + x + 0.3 * rng.standard_normal(200)
    assert reset_test(linear, x).p_value > 0.01


def test_標本の形() -> None:
    x, y = draw_fan_sample(30, np.random.default_rng(0), True)
    assert x.shape == y.shape == (30,)
    assert x.min() >= 0
    assert x.max() <= 4


def test_誤差の大きさは不均一分散なら_x_が大きいほど大きい() -> None:
    x, y = draw_fan_sample(20000, np.random.default_rng(0), True)
    e = y - 1 - 2 * x
    assert np.std(e[x > 3]) > 5 * np.std(e[x < 1])
    x, y = draw_fan_sample(20000, np.random.default_rng(0), False)
    e = y - 1 - 2 * x
    assert np.std(e[x > 3]) == pytest.approx(np.std(e[x < 1]), rel=0.1)


def test_均一分散の標本の誤差は標準偏差1で係数は真の値() -> None:
    x, y = draw_fan_sample(20000, np.random.default_rng(0), False)
    result = fit_ols(y, x)
    assert result.coefficients["const"] == pytest.approx(1, abs=0.05)
    assert result.coefficients["x1"] == pytest.approx(2, abs=0.02)
    assert np.std(result.residuals) == pytest.approx(1, rel=0.03)


def test_不均一分散の標本の係数は真の値() -> None:
    x, y = draw_fan_sample(20000, np.random.default_rng(0), True)
    result = fit_ols(y, x)
    assert result.coefficients["const"] == pytest.approx(1, abs=0.1)
    assert result.coefficients["x1"] == pytest.approx(2, abs=0.1)


def test_均一分散なら通常の標準誤差も頑健な標準誤差も実際のばらつきに近い() -> None:
    r = standard_error_comparison(50, 2000, False, np.random.default_rng(0))
    # 許容誤差: sd の推定誤差（約 1.6%）の 4 倍。HC1 は n = 50 で 5% ほど過小なので、その分を足す
    assert r["classical"] == pytest.approx(r["sd"], rel=0.07)
    assert r["hc1"] == pytest.approx(r["sd"], rel=0.12)


def test_不均一分散なら通常の標準誤差は過小で頑健な標準誤差は近い() -> None:
    r = standard_error_comparison(50, 2000, True, np.random.default_rng(0))
    assert r["classical"] < 0.85 * r["sd"]
    assert r["hc1"] == pytest.approx(r["sd"], rel=0.12)


def test_頑健な標準誤差の係数は通常の最小二乗法と同じ() -> None:
    y, x = two_variable_data()
    assert list(robust_standard_errors(y, x).index) == list(
        fit_ols(y, x).coefficients.index
    )


@pytest.mark.filterwarnings(
    "ignore::statsmodels.tools.sm_exceptions.SingularMatrixWarning"
)
def test_ダミー変数を含んでもWhite検定は_statsmodels_と一致する() -> None:
    rng = np.random.default_rng(3)
    n = 400
    d = (rng.random(n) < 0.4).astype(float)
    x = rng.standard_normal(n)
    y = 1 + 2 * x + d + (0.5 + d) * rng.standard_normal(n)
    frame = pd.DataFrame({"x": x, "d": d})
    result = white_test(y, frame)
    fit = sm.OLS(y, sm.add_constant(frame)).fit()
    lm, p, _, _ = het_white(fit.resid, fit.model.exog)
    assert result.statistic == pytest.approx(lm)
    assert result.p_value == pytest.approx(p)


def test_頑健な標準誤差の名前は通常の推定の係数名と一致する() -> None:
    x = pd.Series([1.0, 2.0, 3.0, 4.0, 6.0, 7.0, 9.0], name="educ")
    y = [2.0, 4.1, 5.9, 8.2, 12.1, 13.8, 18.3]
    named = robust_standard_errors(y, x)
    assert list(named.index) == list(fit_ols(y, x).coefficients.index)
    unnamed = robust_standard_errors(y, x.rename(None))
    assert list(unnamed.index) == ["const", "x1"]
