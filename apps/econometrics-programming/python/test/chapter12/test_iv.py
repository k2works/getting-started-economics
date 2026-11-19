"""第 12 章: 操作変数法と 2 段階最小二乗法のテスト。"""

import numpy as np
import pandas as pd
import pytest
from linearmodels.iv import IV2SLS

from lib.chapter02.simple import fit_simple
from lib.chapter03.multiple import fit_ols
from lib.chapter05.inference import f_test, t_statistics
from lib.chapter12.iv import (
    draw_iv_sample,
    first_stage_f,
    iv_estimate,
    iv_slope_standard_error,
    manual_second_stage,
    two_stage_least_squares,
    weak_instrument_experiment,
)

X = [1, 3, 2, 5]
Y = [2, 5, 3, 7]
Z = [1, 2, 3, 4]


def test_手計算の単純なIV推定() -> None:
    fit = iv_estimate(Y, X, Z)
    assert fit.slope == pytest.approx(6.5 / 5.5)
    assert fit.intercept == pytest.approx(1.0)


def test_同じデータのOLSとは傾きが違う() -> None:
    assert fit_simple(X, Y).slope == pytest.approx(9 / 7)
    assert iv_estimate(Y, X, Z).slope != pytest.approx(9 / 7)


def test_操作変数が説明変数そのものならOLSと一致する() -> None:
    fit = iv_estimate(Y, X, X)
    assert fit.slope == pytest.approx(fit_simple(X, Y).slope)


def test_手計算の例の傾きの標準誤差() -> None:
    fit = iv_estimate(Y, X, Z)
    assert iv_slope_standard_error(Y, X, Z, fit) == pytest.approx(0.17725, abs=1e-5)


def test_識別のちょうどの場合2SLSは単純なIV推定と係数も標準誤差も一致する() -> None:
    result = two_stage_least_squares(Y, pd.DataFrame({"x": X}), pd.DataFrame({"z": Z}))
    fit = iv_estimate(Y, X, Z)
    assert result.coefficients["x"] == pytest.approx(fit.slope)
    assert result.coefficients["const"] == pytest.approx(fit.intercept)
    assert result.standard_errors["x"] == pytest.approx(
        iv_slope_standard_error(Y, X, Z, fit)
    )
    assert result.df_resid == 2
    assert result.n_obs == 4


def sample_with_control(n: int = 300) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    base = draw_iv_sample(n, 1.0, 0.5, rng)
    base["z2"] = 0.5 * base["z"] + rng.standard_normal(n)
    base["w"] = rng.standard_normal(n)
    return base.assign(y=base["y"] + 0.5 * base["w"])


def test_2SLSはlinearmodelsと一致する() -> None:
    s = draw_iv_sample(500, 1.0, 0.5, np.random.default_rng(0))
    result = two_stage_least_squares(s["y"], s[["x"]], s[["z"]])
    reference = IV2SLS(
        s["y"], pd.DataFrame({"const": np.ones(500)}), s[["x"]], s[["z"]]
    ).fit(cov_type="unadjusted", debiased=True)
    assert result.coefficients["x"] == pytest.approx(reference.params["x"])
    assert result.coefficients["const"] == pytest.approx(reference.params["const"])
    assert result.standard_errors["x"] == pytest.approx(reference.std_errors["x"])


def test_外生の説明変数と複数の操作変数でもlinearmodelsと一致する() -> None:
    s = sample_with_control()
    result = two_stage_least_squares(s["y"], s[["x"]], s[["z", "z2"]], s[["w"]])
    reference = IV2SLS(
        s["y"],
        pd.DataFrame({"const": np.ones(len(s)), "w": s["w"]}),
        s[["x"]],
        s[["z", "z2"]],
    ).fit(cov_type="unadjusted", debiased=True)
    assert list(result.coefficients.index) == ["const", "w", "x"]
    for name in ("const", "w", "x"):
        assert result.coefficients[name] == pytest.approx(reference.params[name])
        assert result.standard_errors[name] == pytest.approx(reference.std_errors[name])


def test_操作変数が内生変数より少ないと識別されない() -> None:
    s = sample_with_control()
    endogenous = s[["x", "z2"]]
    with pytest.raises(ValueError, match="識別"):
        two_stage_least_squares(s["y"], endogenous, s[["z"]])


def test_手作業の2段階は係数は同じだが標準誤差が合わない() -> None:
    endogenous, instruments = pd.DataFrame({"x": X}), pd.DataFrame({"z": Z})
    result = two_stage_least_squares(Y, endogenous, instruments)
    coefficients, errors = manual_second_stage(Y, endogenous, instruments)
    assert coefficients["x"] == pytest.approx(result.coefficients["x"])
    assert errors["x"] > 3 * result.standard_errors["x"]


def test_手作業の2段階の標準誤差は乱数の標本でも合わない() -> None:
    s = draw_iv_sample(500, 1.0, 0.5, np.random.default_rng(0))
    result = two_stage_least_squares(s["y"], s[["x"]], s[["z"]])
    _, errors = manual_second_stage(s["y"], s[["x"]], s[["z"]])
    assert errors["x"] != pytest.approx(result.standard_errors["x"], rel=0.05)


def test_第1段階のF値は操作変数のt値の2乗() -> None:
    s = draw_iv_sample(200, 0.5, 0.5, np.random.default_rng(1))
    first = fit_ols(s["x"], s[["z"]])
    assert first_stage_f(s["x"], s[["z"]]).statistic == pytest.approx(
        t_statistics(first)["z"] ** 2
    )


def test_外生の説明変数があっても第1段階のF値を求められる() -> None:
    s = sample_with_control()
    test = first_stage_f(s["x"], s[["z", "z2"]], s[["w"]])
    assert test.statistic > 10
    assert test.p_value < 0.001


def test_第1段階のF値は外生の説明変数を含めた回帰から求める() -> None:
    s = sample_with_control()
    test = first_stage_f(s["x"], s[["z", "z2"]], s[["w"]])
    expected = f_test(s["x"], s[["w", "z", "z2"]], ["z", "z2"])
    assert test.statistic == pytest.approx(expected.statistic)
    assert test.p_value == pytest.approx(expected.p_value)
    without = f_test(s["x"], s[["z", "z2"]], ["z", "z2"])
    assert test.statistic != pytest.approx(without.statistic, rel=1e-6)


def test_標本の列と分散と相関() -> None:
    s = draw_iv_sample(50000, 1.0, 0.5, np.random.default_rng(0))
    assert list(s.columns) == ["y", "x", "z"]
    u = s["y"] - 1 - s["x"]
    assert np.cov(s["x"], u)[0, 1] == pytest.approx(0.5, abs=0.03)
    assert np.cov(s["z"], u)[0, 1] == pytest.approx(0, abs=0.03)
    assert np.cov(s["z"], s["x"])[0, 1] == pytest.approx(1.0, abs=0.03)
    assert np.var(u) == pytest.approx(1, rel=0.05)


def test_OLSは内生性で偏りIVは偏らない() -> None:
    s = draw_iv_sample(100000, 1.0, 0.5, np.random.default_rng(0))
    assert fit_simple(s["x"], s["y"]).slope == pytest.approx(1.25, abs=0.01)
    assert iv_estimate(s["y"], s["x"], s["z"]).slope == pytest.approx(1.0, abs=0.01)


def test_内生性がなければOLSも偏らない() -> None:
    s = draw_iv_sample(100000, 1.0, 0.0, np.random.default_rng(0))
    assert fit_simple(s["x"], s["y"]).slope == pytest.approx(1.0, abs=0.01)


def spread(values: pd.Series) -> float:
    return float(values.quantile(0.95) - values.quantile(0.05))


def test_強い操作変数ではF値が大きくIVは真の値に集まる() -> None:
    t = weak_instrument_experiment(100, 1.0, 1000, np.random.default_rng(0))
    assert list(t.columns) == ["ols", "iv", "f"]
    assert t["f"].mean() > 50
    assert t["iv"].median() == pytest.approx(1.0, abs=0.02)
    assert t["ols"].median() == pytest.approx(1.25, abs=0.03)


def test_弱い操作変数ではF値が小さくIVは広くばらつきOLSの方向に偏る() -> None:
    strong = weak_instrument_experiment(100, 1.0, 1000, np.random.default_rng(0))
    weak = weak_instrument_experiment(100, 0.1, 1000, np.random.default_rng(0))
    assert weak["f"].mean() < 5
    assert spread(weak["iv"]) > 5 * spread(strong["iv"])
    assert abs(weak["iv"].median() - 1) > abs(strong["iv"].median() - 1)
    assert weak["iv"].median() > 1.1
