"""第 9 章: 差分の差分と、1 階差分推定のテスト。"""

import numpy as np
import pandas as pd
import pytest

from lib.chapter09.did import (
    did_estimate,
    did_regression,
    draw_did_sample,
    draw_panel,
    first_difference,
    first_difference_estimate,
    group_period_means,
    panel_estimators,
    pooled_estimate,
)

# 処置群 10 → 15、対照群 8 → 10（各セルに 2 個の観測値）
CELLS = pd.DataFrame(
    {
        "y": [7, 9, 9, 11, 9, 11, 14, 16],
        "treated": [0, 0, 0, 0, 1, 1, 1, 1],
        "post": [0, 0, 1, 1, 0, 0, 1, 1],
    },
    dtype=float,
)

# 個人 0・1・2 の x と y（y = a + 2x。a は 1・6・−1）
PANEL = pd.DataFrame(
    {
        "entity": [0, 0, 1, 1, 2, 2],
        "time": [0, 1] * 3,
        "x": [1, 2, 2, 4, 0, 3],
        "y": [3, 5, 10, 14, -1, 5],
    },
    dtype=float,
)


def test_2_x_2の平均() -> None:
    means = group_period_means(CELLS)
    assert means.to_numpy().tolist() == [[8, 10], [10, 15]]
    assert list(means.index) == ["control", "treated"]
    assert list(means.columns) == ["before", "after"]


def test_差分の差分の手計算() -> None:
    assert did_estimate(CELLS) == pytest.approx((15 - 10) - (10 - 8))


def test_回帰の交差項の係数はDiDにちょうど等しい() -> None:
    coefficients = did_regression(CELLS).coefficients
    assert coefficients["treated:post"] == pytest.approx(3)
    assert coefficients["const"] == pytest.approx(8)
    assert coefficients["treated"] == pytest.approx(10 - 8)
    assert coefficients["post"] == pytest.approx(10 - 8)


def test_乱数の標本でも回帰の交差項はDiDに等しい() -> None:
    sample = draw_did_sample(100, 1.5, np.random.default_rng(1))
    assert did_regression(sample).coefficients["treated:post"] == pytest.approx(
        did_estimate(sample)
    )


def test_標本の形() -> None:
    sample = draw_did_sample(10, 1.5, np.random.default_rng(0))
    assert len(sample) == 40
    assert sample.groupby(["treated", "post"]).size().tolist() == [10, 10, 10, 10]


def test_標本の行は対照前_対照後_処置前_処置後の順() -> None:
    sample = draw_did_sample(3, 1.5, np.random.default_rng(0))
    assert sample[["treated", "post"]].to_numpy().tolist() == (
        [[0, 0]] * 3 + [[0, 1]] * 3 + [[1, 0]] * 3 + [[1, 1]] * 3
    )


def test_処置の効果は標準誤差の4倍以内で復元される() -> None:
    sample = draw_did_sample(500, 1.5, np.random.default_rng(0))
    result = did_regression(sample)
    assert (
        abs(result.coefficients["treated:post"] - 1.5)
        < 4 * (result.standard_errors["treated:post"])
    )
    assert (
        abs(result.coefficients["treated"] - 3) < 4 * result.standard_errors["treated"]
    )
    assert abs(result.coefficients["post"] - 2) < 4 * result.standard_errors["post"]


def test_効果が0なら差分の差分は0に近い() -> None:
    sample = draw_did_sample(2000, 0.0, np.random.default_rng(0))
    assert did_estimate(sample) == pytest.approx(0, abs=0.1)


def test_群の差と共通の時間変化だけでは差分の差分は0() -> None:
    df = CELLS.copy()
    df["y"] = 5 + 3 * df["treated"] + 2 * df["post"]
    assert did_estimate(df) == pytest.approx(0)


def test_1階差分は個人ごとの前期との差() -> None:
    d = first_difference(PANEL.sample(frac=1, random_state=0))
    assert d["dx"].tolist() == [1, 2, 3]
    assert d["dy"].tolist() == [2, 4, 6]
    assert list(d.columns) == ["dx", "dy"]


def test_1階差分推定は個人の効果を除いて真の傾きを復元する() -> None:
    assert first_difference_estimate(PANEL) == pytest.approx(2)


def test_プーリングOLSは個人の効果のため偏る() -> None:
    assert pooled_estimate(PANEL) == pytest.approx(3.2)


def test_パネルの形() -> None:
    panel = draw_panel(10, 4, 0.5, np.random.default_rng(0))
    assert len(panel) == 40
    assert list(panel.columns) == ["entity", "time", "x", "y"]
    assert panel["entity"].nunique() == 10
    assert panel.groupby("entity")["time"].apply(list).iloc[0] == [0, 1, 2, 3]


def test_個人の効果は期をまたいで同じ() -> None:
    a = draw_panel(5, 3, 1.0, np.random.default_rng(0))
    b = draw_panel(5, 3, 1.0, np.random.default_rng(0))
    pd.testing.assert_frame_equal(a, b)


def test_相関があるとプーリングは偏り差分は偏らない() -> None:
    table = panel_estimators(200, 2, 1.0, 500, np.random.default_rng(0))
    se = table.std() / 500**0.5
    assert abs(table["pooled"].mean() - 1.5) < 4 * se["pooled"]
    assert abs(table["first_difference"].mean() - 1.0) < 4 * se["first_difference"]


def test_相関がなければプーリングも偏らない() -> None:
    table = panel_estimators(200, 2, 0.0, 500, np.random.default_rng(0))
    se = table.std() / 500**0.5
    assert abs(table["pooled"].mean() - 1.0) < 4 * se["pooled"]
    assert abs(table["first_difference"].mean() - 1.0) < 4 * se["first_difference"]


def test_期が多くても1階差分は偏らない() -> None:
    table = panel_estimators(100, 5, 1.0, 200, np.random.default_rng(0))
    se = table.std() / 200**0.5
    assert abs(table["first_difference"].mean() - 1.0) < 4 * se["first_difference"]
