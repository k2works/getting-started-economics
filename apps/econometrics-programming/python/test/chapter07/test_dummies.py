"""第 7 章: ダミー変数・カテゴリー変数・交差項のテスト。"""

import numpy as np
import pandas as pd
import pytest

from lib.chapter03.multiple import fit_ols
from lib.chapter07.dummies import (
    draw_wage_sample,
    group_means,
    has_dummy_trap,
    make_dummies,
    with_interaction,
)

Y = pd.Series([10.0, 12.0, 14.0, 20.0, 22.0], name="y")
GROUP = pd.Series(["a", "a", "a", "b", "b"], name="group")
FULL = pd.DataFrame({"a": (GROUP == "a") * 1.0, "b": (GROUP == "b") * 1.0})


def wage_sample(n: int = 20000) -> pd.DataFrame:
    return draw_wage_sample(n, np.random.default_rng(0))


def test_グループごとの平均() -> None:
    means = group_means(Y, GROUP)
    assert means["a"] == pytest.approx(12)
    assert means["b"] == pytest.approx(21)


def test_ダミー変数は基準のカテゴリーを除いて作る() -> None:
    d = make_dummies(GROUP)
    assert list(d.columns) == ["group_b"]
    assert d["group_b"].tolist() == [0, 0, 0, 1, 1]


def test_基準のカテゴリーを指定できる() -> None:
    d = make_dummies(GROUP, base="b")
    assert list(d.columns) == ["group_a"]
    assert d["group_a"].tolist() == [1, 1, 1, 0, 0]


def test_カテゴリーが3つならダミー変数は2つ() -> None:
    region = pd.Series(["north", "south", "west", "south"], name="region")
    d = make_dummies(region)
    assert list(d.columns) == ["region_south", "region_west"]
    assert d.sum(axis=1).tolist() == [0, 1, 1, 1]


def test_存在しない基準のカテゴリーは受け付けない() -> None:
    with pytest.raises(ValueError, match="基準"):
        make_dummies(GROUP, base="c")


def test_名前のないデータにも名前が付く() -> None:
    d = make_dummies(pd.Series(["x", "y", "x"]))
    assert list(d.columns) == ["d_y"]


def test_定数項だけの回帰の係数は標本平均() -> None:
    result = fit_ols(Y, np.empty((5, 0)))
    assert result.coefficients["const"] == pytest.approx(Y.mean())


def test_ダミー変数の係数は2つの群の平均の差() -> None:
    result = fit_ols(Y, make_dummies(GROUP))
    assert result.coefficients["const"] == pytest.approx(12)
    assert result.coefficients["group_b"] == pytest.approx(21 - 12)


def test_基準を入れ替えると符号が変わるが当てはめ値は同じ() -> None:
    a = fit_ols(Y, make_dummies(GROUP, base="a"))
    b = fit_ols(Y, make_dummies(GROUP, base="b"))
    assert b.coefficients["const"] == pytest.approx(21)
    assert b.coefficients["group_a"] == pytest.approx(-9)
    assert a.residuals == pytest.approx(b.residuals)


def test_カテゴリーのダミー変数の係数は基準との平均の差() -> None:
    y = pd.Series([1.0, 3.0, 5.0, 6.0, 10.0, 12.0])
    g = pd.Series(["p", "p", "q", "q", "r", "r"], name="g")
    result = fit_ols(y, make_dummies(g))
    assert result.coefficients["const"] == pytest.approx(2)
    assert result.coefficients["g_q"] == pytest.approx(5.5 - 2)
    assert result.coefficients["g_r"] == pytest.approx(11 - 2)


def test_ダミー変数の罠() -> None:
    assert has_dummy_trap(FULL)
    assert not has_dummy_trap(make_dummies(GROUP))
    assert not has_dummy_trap(FULL, constant=False)
    with pytest.raises(ValueError, match="多重共線性"):
        fit_ols(Y, FULL)


def test_定数項を外すと全カテゴリーの係数が群の平均になる() -> None:
    result = fit_ols(Y, FULL, constant=False)
    assert result.coefficients["a"] == pytest.approx(12)
    assert result.coefficients["b"] == pytest.approx(21)


def test_交差項は2つの変数の積() -> None:
    x = pd.Series([1.0, 2.0, 3.0, 4.0], name="x")
    d = pd.Series([0.0, 1.0, 0.0, 1.0], name="d")
    z = with_interaction(x, d)
    assert z.name == "x:d"
    assert z.tolist() == [0, 2, 0, 4]


def test_交差項つきの回帰は群ごとの回帰と一致する() -> None:
    df = wage_sample(400)
    x = pd.DataFrame(
        {
            "educ": df["educ"],
            "female": df["female"],
            "educ:female": with_interaction(df["educ"], df["female"]),
        }
    )
    pooled = fit_ols(df["lwage"], x).coefficients
    male = df[df["female"] == 0]
    female = df[df["female"] == 1]
    m = fit_ols(male["lwage"], male[["educ"]]).coefficients
    f = fit_ols(female["lwage"], female[["educ"]]).coefficients
    assert pooled["const"] == pytest.approx(m["const"])
    assert pooled["educ"] == pytest.approx(m["educ"])
    assert pooled["const"] + pooled["female"] == pytest.approx(f["const"])
    assert pooled["educ"] + pooled["educ:female"] == pytest.approx(f["educ"])


def test_標本の列とカテゴリー() -> None:
    df = wage_sample(300)
    assert list(df.columns) == ["lwage", "educ", "female", "region"]
    assert set(df["region"]) == {"north", "south", "west"}
    assert set(df["female"]) == {0, 1}
    assert df["educ"].min() == 8
    assert df["educ"].max() == 18


def full_design(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "educ": df["educ"],
            "female": df["female"],
            "educ:female": with_interaction(df["educ"], df["female"]),
        }
    ).join(make_dummies(df["region"]))


def test_誤差項の標準偏差は0点3に近い() -> None:
    df = wage_sample()
    result = fit_ols(df["lwage"], full_design(df))
    sigma = float(np.sqrt(result.residuals @ result.residuals / result.df_resid))
    assert sigma == pytest.approx(0.3, rel=0.03)


def test_真の係数は標準誤差の4倍以内で復元される() -> None:
    df = wage_sample()
    result = fit_ols(df["lwage"], full_design(df))
    truth = {
        "const": 1.0,
        "educ": 0.08,
        "female": -0.25,
        "educ:female": 0.02,
        "region_south": -0.1,
        "region_west": 0.15,
    }
    for name, value in truth.items():
        assert abs(result.coefficients[name] - value) < 4 * result.standard_errors[name]


def test_同じ種なら同じ標本() -> None:
    a = draw_wage_sample(50, np.random.default_rng(2))
    b = draw_wage_sample(50, np.random.default_rng(2))
    pd.testing.assert_frame_equal(a, b)
