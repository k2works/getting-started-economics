"""第 3 章: 回帰分析（最小二乗法）のテスト。

手計算の例: x = [1, 2, 3]、y = [2, 4, 5]。傾き 1.5、切片 2/3、決定係数 27/28。
"""

import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm

from lib.chapter01.accounting import load_countries
from lib.chapter03.regression import (
    development_accounting_regression,
    fit_ols,
)


def small_example() -> tuple[pd.Series, pd.DataFrame]:
    y = pd.Series([2.0, 4.0, 5.0], name="y")
    x = pd.DataFrame({"x": [1.0, 2.0, 3.0]})
    return y, x


def test_傾き1_5と切片2_3を求める() -> None:
    y, x = small_example()
    result = fit_ols(y, x)
    assert result.coefficients["x"] == pytest.approx(1.5)
    assert result.coefficients["const"] == pytest.approx(2 / 3)


def test_係数の名前は定数項が先で説明変数が続く() -> None:
    y, x = small_example()
    assert list(fit_ols(y, x).coefficients.index) == ["const", "x"]


def test_標準誤差を手計算と比べる() -> None:
    # 残差の二乗和 1/6、自由度 1。傾き: √((1/6) ÷ 2)、切片: √((1/6) × (1/3 + 4/2))
    y, x = small_example()
    result = fit_ols(y, x)
    assert result.standard_errors["x"] == pytest.approx(np.sqrt(1 / 12))
    assert result.standard_errors["const"] == pytest.approx(np.sqrt(7 / 18))


def test_決定係数は27_28() -> None:
    y, x = small_example()
    assert fit_ols(y, x).r_squared == pytest.approx(27 / 28)


def test_t値は係数を標準誤差で割った値() -> None:
    y, x = small_example()
    result = fit_ols(y, x)
    assert result.t_values()["x"] == pytest.approx(1.5 / np.sqrt(1 / 12))


def test_観測数と残差の自由度() -> None:
    y, x = small_example()
    result = fit_ols(y, x)
    assert result.n_obs == 3
    assert result.df_resid == 1


def test_直線上のデータなら決定係数は1で標準誤差は0() -> None:
    x = pd.DataFrame({"x": [0.0, 1.0, 2.0, 3.0]})
    y = pd.Series(1 + 2 * x["x"])
    result = fit_ols(y, x)
    assert result.coefficients.to_numpy() == pytest.approx([1, 2])
    assert result.r_squared == pytest.approx(1)
    assert result.standard_errors.to_numpy() == pytest.approx([0, 0], abs=1e-9)


def test_説明変数が2つでも既知の係数を復元できる() -> None:
    x = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0, 5.0], "b": [2.0, 1.0, 4.0, 3.0, 7.0]})
    y = 3 + 2 * x["a"] - 1 * x["b"]
    result = fit_ols(y, x)
    assert result.coefficients.to_numpy() == pytest.approx([3, 2, -1])


def test_statsmodelsの結果と一致する() -> None:
    df = load_countries()
    y = np.log(df["y"])
    x = pd.DataFrame({"ln_k": np.log(df["k"]), "ln_h": np.log(df["h"])})
    ours = fit_ols(y, x)
    theirs = sm.OLS(y, sm.add_constant(x)).fit()
    assert ours.coefficients.to_numpy() == pytest.approx(theirs.params.to_numpy())
    assert ours.standard_errors.to_numpy() == pytest.approx(theirs.bse.to_numpy())
    assert ours.r_squared == pytest.approx(theirs.rsquared)
    assert ours.t_values().to_numpy() == pytest.approx(theirs.tvalues.to_numpy())


def test_長さが違うときは受け付けない() -> None:
    y = pd.Series([1.0, 2.0, 3.0])
    x = pd.DataFrame({"x": [1.0, 2.0]})
    with pytest.raises(ValueError, match="長さ"):
        fit_ols(y, x)


def test_観測数が係数の数以下なら受け付けない() -> None:
    y = pd.Series([1.0, 2.0])
    x = pd.DataFrame({"x": [1.0, 2.0]})
    with pytest.raises(ValueError, match="観測"):
        fit_ols(y, x)


def test_説明変数が完全に共線形なら受け付けない() -> None:
    x = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0], "b": [2.0, 4.0, 6.0, 8.0]})
    y = pd.Series([1.0, 3.0, 2.0, 5.0])
    with pytest.raises(ValueError, match="共線形"):
        fit_ols(y, x)


def test_発展会計の回帰は対数の所得を対数の資本と人的資本に回帰する() -> None:
    df = load_countries()
    result = development_accounting_regression(df)
    assert list(result.coefficients.index) == ["const", "ln_k", "ln_h"]
    expected = fit_ols(
        np.log(df["y"]),
        pd.DataFrame({"ln_k": np.log(df["k"]), "ln_h": np.log(df["h"])}),
    )
    assert result.coefficients.to_numpy() == pytest.approx(
        expected.coefficients.to_numpy()
    )


def test_回帰で求めた資本の係数は真の資本分配率1_3を大きく上回る() -> None:
    # 同梱のデータでは、TFP が資本と相関しているので、係数は偏る（欠落変数バイアス）
    result = development_accounting_regression(load_countries())
    assert result.coefficients["ln_k"] == pytest.approx(0.878, abs=0.001)
    assert result.coefficients["ln_k"] > 1 / 3


def test_yがすべて同じなら決定係数は求められない() -> None:
    x = pd.DataFrame({"x": [1.0, 2.0, 3.0]})
    y = pd.Series([2.0, 2.0, 2.0])
    with pytest.raises(ValueError, match="差"):
        fit_ols(y, x)
