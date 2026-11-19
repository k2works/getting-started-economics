"""第 3 章: 重回帰分析（行列による最小二乗法）のテスト。"""

import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import OLSInfluence
from statsmodels.stats.outliers_influence import (
    variance_inflation_factor as reference_vif,
)

from lib.chapter03.multiple import (
    fit_ols,
    fwl_coefficient,
    leverage,
    multicollinearity_experiment,
    partial_out,
    percent_effect,
    variance_inflation_factor,
)

X1 = [1, 2, 3, 4, 5]
X2 = [2, 1, 4, 3, 6]


def random_data(n: int = 40, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    x1 = rng.standard_normal(n)
    x2 = 0.5 * x1 + rng.standard_normal(n)
    y = 1 + 2 * x1 - x2 + rng.standard_normal(n)
    return pd.DataFrame({"y": y, "x1": x1, "x2": x2})


def test_ちょうどの関係から係数を復元する() -> None:
    x = pd.DataFrame({"x1": X1, "x2": X2})
    y = [1 + 2 * a + 3 * b for a, b in zip(X1, X2, strict=True)]
    result = fit_ols(y, x)
    assert result.coefficients.tolist() == pytest.approx([1, 2, 3])
    assert result.standard_errors.tolist() == pytest.approx([0, 0, 0], abs=1e-9)
    assert result.r_squared == pytest.approx(1)


def test_係数の名前は列の名前と定数項() -> None:
    df = random_data()
    result = fit_ols(df["y"], df[["x1", "x2"]])
    assert list(result.coefficients.index) == ["const", "x1", "x2"]
    assert list(result.standard_errors.index) == ["const", "x1", "x2"]


def test_配列を渡すと名前はx1から始まる() -> None:
    df = random_data()
    result = fit_ols(df["y"].to_numpy(), df[["x1", "x2"]].to_numpy())
    assert list(result.coefficients.index) == ["const", "x1", "x2"]


def test_列の名前がある1次元のデータは名前を引き継ぐ() -> None:
    df = random_data()
    result = fit_ols(df["y"], df["x2"])
    assert list(result.coefficients.index) == ["const", "x2"]


def test_1次元の配列も説明変数にできる() -> None:
    df = random_data()
    result = fit_ols(df["y"], df["x1"].to_numpy())
    assert list(result.coefficients.index) == ["const", "x1"]


def test_定数項なしにできる() -> None:
    df = random_data()
    result = fit_ols(df["y"], df[["x1", "x2"]], constant=False)
    assert list(result.coefficients.index) == ["x1", "x2"]


def test_statsmodelsと一致する() -> None:
    df = random_data()
    result = fit_ols(df["y"], df[["x1", "x2"]])
    reference = sm.OLS(df["y"], sm.add_constant(df[["x1", "x2"]])).fit()
    assert result.coefficients.to_numpy() == pytest.approx(reference.params.to_numpy())
    assert result.standard_errors.to_numpy() == pytest.approx(reference.bse.to_numpy())
    assert result.r_squared == pytest.approx(reference.rsquared)
    assert result.n_obs == reference.nobs
    assert result.df_resid == reference.df_resid


def test_残差の和は0で説明変数と直交する() -> None:
    df = random_data()
    result = fit_ols(df["y"], df[["x1", "x2"]])
    assert np.sum(result.residuals) == pytest.approx(0, abs=1e-10)
    for name in ("x1", "x2"):
        assert np.dot(df[name], result.residuals) == pytest.approx(0, abs=1e-10)


def test_同じ列を2つ入れると推定できない() -> None:
    df = random_data()
    x = pd.DataFrame({"a": df["x1"], "b": df["x1"]})
    with pytest.raises(ValueError, match="多重共線性"):
        fit_ols(df["y"], x)


def test_定数倍の列を入れても推定できない() -> None:
    df = random_data()
    x = pd.DataFrame({"a": df["x1"], "b": 2 * df["x1"]})
    with pytest.raises(ValueError, match="多重共線性"):
        fit_ols(df["y"], x)


def test_観測値が係数の数以下だと推定できない() -> None:
    x = pd.DataFrame({"x1": [1, 2, 4], "x2": [2, 1, 5]})
    with pytest.raises(ValueError, match="観測値の数"):
        fit_ols([1, 2, 3], x)


def test_てこ比の和は係数の数でありstatsmodelsと一致する() -> None:
    df = random_data()
    h = leverage(df[["x1", "x2"]])
    assert h.sum() == pytest.approx(3)
    assert h.min() >= 1 / len(df) - 1e-12
    assert h.max() <= 1
    reference = OLSInfluence(
        sm.OLS(df["y"], sm.add_constant(df[["x1", "x2"]])).fit()
    ).hat_matrix_diag
    assert h == pytest.approx(reference)


def test_偏りを除いた回帰の傾きは重回帰の係数と一致する() -> None:
    df = random_data()
    full = fit_ols(df["y"], df[["x1", "x2"]])
    assert fwl_coefficient(df["y"], df["x1"], df[["x2"]]) == pytest.approx(
        full.coefficients["x1"]
    )
    assert fwl_coefficient(df["y"], df["x2"], df[["x1"]]) == pytest.approx(
        full.coefficients["x2"]
    )


def test_偏りを除いた変数は他の変数と直交する() -> None:
    df = random_data()
    z = partial_out(df["x1"], df[["x2"]])
    assert np.sum(z) == pytest.approx(0, abs=1e-10)
    assert np.dot(z, df["x2"]) == pytest.approx(0, abs=1e-10)


def test_分散拡大係数は相関から決まる() -> None:
    df = random_data()
    r = np.corrcoef(df["x1"], df["x2"])[0, 1]
    vif = variance_inflation_factor(df[["x1", "x2"]], "x1")
    assert vif == pytest.approx(1 / (1 - r**2))
    assert vif == pytest.approx(variance_inflation_factor(df[["x1", "x2"]], "x2"))


def test_分散拡大係数はstatsmodelsと一致する() -> None:
    df = random_data()
    exog = sm.add_constant(df[["x1", "x2"]]).to_numpy()
    assert variance_inflation_factor(df[["x1", "x2"]], "x1") == pytest.approx(
        reference_vif(exog, 1)
    )


def test_相関のない変数の分散拡大係数は1に近い() -> None:
    x = pd.DataFrame({"a": [1, 2, 3, 4], "b": [1, -1, -1, 1]})
    assert variance_inflation_factor(x, "a") == pytest.approx(1)


def test_対数の係数の割合への換算() -> None:
    assert percent_effect(0.1) == pytest.approx(10.5171, abs=1e-4)
    assert percent_effect(0) == 0
    assert percent_effect(-0.1) == pytest.approx(-9.5163, abs=1e-4)
    assert percent_effect(0.1, change=2) == pytest.approx(22.1403, abs=1e-4)


def test_相関が強くても推定値は不偏() -> None:
    table = multicollinearity_experiment(0.9, 50, 1000, np.random.default_rng(0))
    assert list(table.columns) == ["x1", "x2"]
    assert table.mean().to_numpy() == pytest.approx([1, 1], abs=0.05)


def test_1回分の推定を手で再現すると列の順序はx1とx2() -> None:
    rng = np.random.default_rng(7)
    z1, z2, u = rng.standard_normal((3, 20))
    x2 = 0.6 * z1 + 0.8 * z2
    expected = fit_ols(1 + z1 + x2 + u, np.column_stack([z1, x2])).coefficients
    table = multicollinearity_experiment(0.6, 20, 1, np.random.default_rng(7))
    assert table.loc[0, "x1"] == pytest.approx(expected["x1"])
    assert table.loc[0, "x2"] == pytest.approx(expected["x2"])
    assert table.loc[0, "x1"] != pytest.approx(table.loc[0, "x2"])


def test_相関が強いほど係数はばらつく() -> None:
    low = multicollinearity_experiment(0.0, 50, 1000, np.random.default_rng(0))
    high = multicollinearity_experiment(0.9, 50, 1000, np.random.default_rng(0))
    ratio = high["x1"].std() / low["x1"].std()
    assert ratio == pytest.approx((1 / (1 - 0.9**2)) ** 0.5, rel=0.15)


def test_名前のない系列を渡すと係数名は_x1() -> None:
    x = pd.Series([1.0, 2.0, 3.0, 4.0, 6.0])
    y = [2.0, 4.1, 5.9, 8.2, 12.1]
    assert list(fit_ols(y, x).coefficients.index) == ["const", "x1"]


def test_名前のある系列を渡すと係数名はその名前() -> None:
    x = pd.Series([1.0, 2.0, 3.0, 4.0, 6.0], name="educ")
    y = [2.0, 4.1, 5.9, 8.2, 12.1]
    assert list(fit_ols(y, x).coefficients.index) == ["const", "educ"]
