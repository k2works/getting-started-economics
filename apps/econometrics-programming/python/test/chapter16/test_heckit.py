"""第 16 章: 標本選択とヘックマンの 2 段階推定のテスト。"""

import math

import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm
from scipy import stats

from lib.chapter03.multiple import fit_ols
from lib.chapter16.heckit import (
    HeckitFit,
    draw_selection_sample,
    heckit_bootstrap_standard_errors,
    heckit_two_step,
    inverse_mills_ratio,
    selection_bias_experiment,
)


def sample(correlation: float = 0.7, n: int = 5000, seed: int = 0) -> pd.DataFrame:
    return draw_selection_sample(n, correlation, np.random.default_rng(seed))


def test_逆ミルズ比の手計算() -> None:
    assert inverse_mills_ratio(0.0) == pytest.approx(math.sqrt(2 / math.pi))
    assert inverse_mills_ratio(0.0) == pytest.approx(0.7979, abs=1e-4)
    expected = stats.norm.pdf(1.0) / stats.norm.cdf(1.0)
    assert inverse_mills_ratio(1.0) == pytest.approx(expected)
    assert inverse_mills_ratio(1.0) == pytest.approx(0.2876, abs=1e-4)


def test_逆ミルズ比は常に正で_c_が大きいほど小さい() -> None:
    values = inverse_mills_ratio(np.linspace(-5, 5, 41))
    assert (values > 0).all()
    assert (np.diff(values) < 0).all()


def test_cが非常に小さいと逆ミルズ比はcの符号を変えた値に近づく() -> None:
    assert inverse_mills_ratio(-10.0) == pytest.approx(10.098, abs=0.01)
    assert inverse_mills_ratio(5.0) < 1e-5


def test_配列を渡すと配列が返る() -> None:
    assert inverse_mills_ratio([0.0, 1.0]).shape == (2,)


def test_標本は乱数列から決まる式で作られる() -> None:
    x, z, v, w = np.random.default_rng(11).standard_normal((4, 300))
    u = 0.7 * v + math.sqrt(1 - 0.7**2) * w
    selected = (0.5 + x + z + v > 0).astype(float)
    df = draw_selection_sample(300, 0.7, np.random.default_rng(11))
    assert df["x"].to_numpy() == pytest.approx(x)
    assert df["selected"].to_numpy() == pytest.approx(selected)
    chosen = selected == 1
    assert df["y"].to_numpy()[chosen] == pytest.approx((1 + 2 * x + u)[chosen])


def test_標本の形() -> None:
    df = sample(n=50000)
    assert list(df.columns) == ["x", "z", "selected", "y"]
    assert df["selected"].mean() == pytest.approx(
        stats.norm.cdf(0.5 / 3**0.5), abs=0.01
    )
    assert (df["y"].isna() == (df["selected"] == 0)).all()


def test_選択された人の結果は選択の誤差と相関するときだけ偏る() -> None:
    biased = sample(0.7, 50000)
    independent = sample(0.0, 50000)
    for df, expect_bias in ((biased, True), (independent, False)):
        chosen = df[df["selected"] == 1]
        residual = chosen["y"] - 1 - 2 * chosen["x"]
        assert (abs(residual.mean()) > 0.2) == expect_bias


def test_2段階推定はstatsmodelsのプロビットとOLSで作った値に一致する() -> None:
    df = sample()
    fit = heckit_two_step(df, ["x"], ["x", "z"])
    probit = sm.Probit(df["selected"], sm.add_constant(df[["x", "z"]])).fit(disp=0)
    linear = probit.params["const"] + df[["x", "z"]] @ probit.params[["x", "z"]]
    chosen = df["selected"] == 1
    columns = df.loc[chosen, ["x"]].assign(
        **{"lambda": inverse_mills_ratio(linear[chosen])}
    )
    reference = fit_ols(df.loc[chosen, "y"], columns)
    assert fit.coefficients.to_numpy() == pytest.approx(
        reference.coefficients.to_numpy()
    )
    assert fit.naive_standard_errors.to_numpy() == pytest.approx(
        reference.standard_errors.to_numpy()
    )
    assert fit.n_selected == int(chosen.sum())
    assert list(fit.coefficients.index) == ["const", "x", "lambda"]


def test_第1段階の選択の係数は真の値に近い() -> None:
    fit = heckit_two_step(sample(), ["x"], ["x", "z"])
    truth = {"const": 0.5, "x": 1.0, "z": 1.0}
    for name, value in truth.items():
        error = fit.selection.standard_errors[name]
        assert abs(fit.selection.coefficients[name] - value) < 4 * error


def test_選択された標本のOLSは偏りヘックマンは真の値を復元する() -> None:
    df = sample()
    chosen = df[df["selected"] == 1]
    ols = fit_ols(chosen["y"], chosen[["x"]]).coefficients["x"]
    fit = heckit_two_step(df, ["x"], ["x", "z"])
    errors = heckit_bootstrap_standard_errors(
        df, ["x"], ["x", "z"], 200, np.random.default_rng(1)
    )
    assert ols < 1.9
    truth = {"const": 1.0, "x": 2.0, "lambda": 0.7}
    for name, value in truth.items():
        assert abs(fit.coefficients[name] - value) < 4 * errors[name]


def test_相関がなければ選択のバイアスもなくlambdaの係数は0に近い() -> None:
    df = sample(0.0, 20000, seed=2)
    chosen = df[df["selected"] == 1]
    ols = fit_ols(chosen["y"], chosen[["x"]])
    fit = heckit_two_step(df, ["x"], ["x", "z"])
    assert abs(ols.coefficients["x"] - 2.0) < 4 * ols.standard_errors["x"]
    assert abs(fit.coefficients["lambda"]) < 4 * fit.naive_standard_errors["lambda"]


def test_ブートストラップ標準誤差は標本標準偏差_n_引く1で割る() -> None:
    df = sample(n=500)
    errors = heckit_bootstrap_standard_errors(
        df, ["x"], ["x", "z"], 2, np.random.default_rng(5)
    )
    rng = np.random.default_rng(5)
    rows = []
    for _ in range(2):
        resampled = df.iloc[rng.integers(0, len(df), len(df))].reset_index(drop=True)
        rows.append(heckit_two_step(resampled, ["x"], ["x", "z"]).coefficients)
    expected = pd.DataFrame(rows).std(ddof=1)
    assert errors.to_numpy() == pytest.approx(expected.to_numpy())


def test_ブートストラップは全標本から復元抽出する(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    df = sample(n=400)
    seen: list[pd.DataFrame] = []
    original = heckit_two_step

    def spy(
        frame: pd.DataFrame, x_columns: list[str], selection_columns: list[str]
    ) -> HeckitFit:
        seen.append(frame)
        return original(frame, x_columns, selection_columns)

    monkeypatch.setattr("lib.chapter16.heckit.heckit_two_step", spy)
    heckit_bootstrap_standard_errors(df, ["x"], ["x", "z"], 3, np.random.default_rng(0))
    second_half = set(df["x"].iloc[200:])
    assert len(seen) == 3
    for frame in seen:
        assert len(frame) == 400
        assert set(frame["x"]) & second_half


def test_ブートストラップ標準誤差は同じ種なら同じ() -> None:
    df = sample(n=500)
    a = heckit_bootstrap_standard_errors(
        df, ["x"], ["x", "z"], 30, np.random.default_rng(3)
    )
    b = heckit_bootstrap_standard_errors(
        df, ["x"], ["x", "z"], 30, np.random.default_rng(3)
    )
    assert a.tolist() == b.tolist()
    assert list(a.index) == ["const", "x", "lambda"]


def test_ブートストラップ標準誤差は第2段階のOLSの標準誤差と違う() -> None:
    df = sample(n=2000)
    fit = heckit_two_step(df, ["x"], ["x", "z"])
    errors = heckit_bootstrap_standard_errors(
        df, ["x"], ["x", "z"], 100, np.random.default_rng(3)
    )
    assert errors["x"] != pytest.approx(fit.naive_standard_errors["x"], rel=1e-3)


def test_ブートストラップ標準誤差は推定値の実際のばらつきに近い() -> None:
    table = selection_bias_experiment(1000, 0.7, 150, np.random.default_rng(0))
    errors = heckit_bootstrap_standard_errors(
        sample(n=1000), ["x"], ["x", "z"], 150, np.random.default_rng(1)
    )
    assert errors["x"] == pytest.approx(table["heckit"].std(), rel=0.3)


def test_相関があるとOLSは偏りヘックマンは偏らない() -> None:
    table = selection_bias_experiment(1000, 0.7, 200, np.random.default_rng(0))
    se = table.std() / 200**0.5
    assert list(table.columns) == ["ols_selected", "heckit"]
    assert abs(table["heckit"].mean() - 2.0) < 4 * se["heckit"]
    assert table["ols_selected"].mean() < 1.9
    assert abs(table["ols_selected"].mean() - 2.0) > 4 * se["ols_selected"]


def test_相関がなければOLSも偏らない() -> None:
    table = selection_bias_experiment(1000, 0.0, 200, np.random.default_rng(0))
    se = table.std() / 200**0.5
    assert abs(table["ols_selected"].mean() - 2.0) < 4 * se["ols_selected"]
    assert abs(table["heckit"].mean() - 2.0) < 4 * se["heckit"]
