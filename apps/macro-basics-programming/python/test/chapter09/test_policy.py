"""第 9 章: 財政政策と金融政策の効果のテスト。"""

import math
from dataclasses import astuple

import pytest

from lib.chapter04.multiplier import spending_multiplier
from lib.chapter08.is_lm import solve_is_lm
from lib.chapter09.policy import (
    PolicyRow,
    crowding_out,
    fiscal_effect,
    fiscal_effect_solved,
    monetary_effect,
    monetary_effect_solved,
    policy_effectiveness,
    policy_interest_change,
)

# c = 0.6、b = 20、IS の切片 A = 450、LM は k = 0.5、h = 100、M/P = 250
MPC = 0.6
B = 20
A = 450
K = 0.5
H = 100
M = 250


def test_財政政策の効果は単純な乗数より小さい() -> None:
    assert spending_multiplier(MPC) * 10 == pytest.approx(25)
    assert fiscal_effect(MPC, B, K, H, 10) == pytest.approx(20)
    assert fiscal_effect(MPC, B, K, H, 10) < spending_multiplier(MPC) * 10


def test_クラウディングアウトは単純な乗数との差() -> None:
    assert crowding_out(MPC, B, K, H, 10) == pytest.approx(5)


def test_金融政策の効果() -> None:
    assert monetary_effect(MPC, B, K, H, 10) == pytest.approx(4)


def test_政府支出の減少は所得を減らす() -> None:
    assert fiscal_effect(MPC, B, K, H, -10) == pytest.approx(-20)


def test_財政政策の効果は連立方程式を解いた結果と一致する() -> None:
    y0, _ = solve_is_lm(MPC, B, A, K, H, M)
    y1, _ = solve_is_lm(MPC, B, A + 10, K, H, M)
    assert y1 - y0 == pytest.approx(fiscal_effect(MPC, B, K, H, 10))
    assert fiscal_effect_solved(MPC, B, A, K, H, M, 10) == pytest.approx(20)


def test_金融政策の効果は連立方程式を解いた結果と一致する() -> None:
    assert monetary_effect_solved(MPC, B, A, K, H, M, 10) == pytest.approx(4)
    assert monetary_effect_solved(MPC, B, A, K, H, M, 10) == pytest.approx(
        monetary_effect(MPC, B, K, H, 10)
    )


@pytest.mark.parametrize("h", [10, 1000])
@pytest.mark.parametrize("b", [0, 40])
def test_どの条件でも閉じた式と連立方程式が一致する(h: float, b: float) -> None:
    fiscal = fiscal_effect(MPC, b, K, h, 10)
    monetary = monetary_effect(MPC, b, K, h, 10)
    assert fiscal == pytest.approx(fiscal_effect_solved(MPC, b, A, K, h, M, 10))
    assert monetary == pytest.approx(monetary_effect_solved(MPC, b, A, K, h, M, 10))


def test_財政政策は利子率を上げ金融政策は利子率を下げる() -> None:
    fiscal = fiscal_effect(MPC, B, K, H, 10)
    assert policy_interest_change(K, H, fiscal) == pytest.approx(0.1)
    monetary = monetary_effect(MPC, B, K, H, 10)
    assert policy_interest_change(K, H, monetary, 10) == pytest.approx(-0.08)


def test_利子率の変化は連立方程式の解の変化と一致する() -> None:
    _, r0 = solve_is_lm(MPC, B, A, K, H, M)
    _, r1 = solve_is_lm(MPC, B, A + 10, K, H, M)
    fiscal = fiscal_effect(MPC, B, K, H, 10)
    assert r1 - r0 == pytest.approx(policy_interest_change(K, H, fiscal))


def test_LMが緩やかなほど財政政策は有効() -> None:
    steep = fiscal_effect(MPC, B, K, 10, 10)
    base = fiscal_effect(MPC, B, K, 100, 10)
    flat = fiscal_effect(MPC, B, K, 1000, 10)
    assert steep == pytest.approx(10 / 1.4)
    assert flat == pytest.approx(10 / 0.41)
    assert steep < base < flat


def test_LMの傾きが大きいほど財政政策は小さい() -> None:
    assert fiscal_effect(MPC, B, 1.0, H, 10) < fiscal_effect(MPC, B, 0.5, H, 10)


def test_LMが垂直に近いと完全なクラウディングアウト() -> None:
    assert fiscal_effect(MPC, B, K, 1e-6, 10) == pytest.approx(0, abs=1e-4)
    assert crowding_out(MPC, B, K, 1e-6, 10) == pytest.approx(25, abs=1e-4)


def test_ISが緩やかなほど金融政策は有効() -> None:
    steep = monetary_effect(MPC, 20, K, H, 10)
    flat = monetary_effect(MPC, 40, K, H, 10)
    assert flat == pytest.approx(10 * 0.4 / 0.6)
    assert steep < flat


def test_ISが緩やかなほど財政政策は小さい() -> None:
    assert fiscal_effect(MPC, 40, K, H, 10) < fiscal_effect(MPC, 20, K, H, 10)


def test_ISが垂直なら金融政策は効かず財政政策は単純な乗数() -> None:
    assert monetary_effect(MPC, 0, K, H, 10) == 0
    assert fiscal_effect(MPC, 0, K, H, 10) == pytest.approx(25)
    assert crowding_out(MPC, 0, K, H, 10) == pytest.approx(0)


def test_流動性のわなでは財政政策は単純な乗数で金融政策は無効() -> None:
    assert fiscal_effect(MPC, B, K, math.inf, 10) == pytest.approx(25)
    assert monetary_effect(MPC, B, K, math.inf, 10) == 0
    assert crowding_out(MPC, B, K, math.inf, 10) == pytest.approx(0)
    assert policy_interest_change(K, math.inf, 25) == 0


def test_十分大きいhで流動性のわなの閉じた式に近づく() -> None:
    big = 1e9
    assert fiscal_effect(MPC, B, K, big, 10) == pytest.approx(25, rel=1e-6)
    assert monetary_effect(MPC, B, K, big, 10) == pytest.approx(0, abs=1e-6)
    assert fiscal_effect_solved(MPC, B, A, K, big, M, 10) == pytest.approx(25, rel=1e-6)
    assert monetary_effect_solved(MPC, B, A, K, big, M, 10) == pytest.approx(
        0, abs=1e-6
    )


def test_政策の効果の表() -> None:
    rows = policy_effectiveness(MPC, K, [(100, 20), (math.inf, 20), (100, 0)], 10, 10)
    assert [row.h for row in rows] == [100, math.inf, 100]
    assert [row.b for row in rows] == [20, 20, 0]
    expected = PolicyRow(100, 20, 20, 4, 5)
    assert astuple(rows[0]) == pytest.approx(astuple(expected))
    assert rows[1].fiscal == pytest.approx(25)
    assert rows[1].monetary == 0
    assert rows[2].monetary == 0
    assert rows[2].crowding_out == pytest.approx(0)


def test_表の列は閉じた式と一致する() -> None:
    row = policy_effectiveness(MPC, K, [(1000, 40)], 10, 10)[0]
    assert row.fiscal == pytest.approx(fiscal_effect(MPC, 40, K, 1000, 10))
    assert row.monetary == pytest.approx(monetary_effect(MPC, 40, K, 1000, 10))
    assert row.crowding_out == pytest.approx(crowding_out(MPC, 40, K, 1000, 10))


def test_限界消費性向が1ならエラー() -> None:
    with pytest.raises(ValueError, match="限界消費性向"):
        fiscal_effect(1, B, K, H, 10)


def test_bが負ならエラー() -> None:
    with pytest.raises(ValueError, match="利子感応度"):
        monetary_effect(MPC, -1, K, H, 10)


def test_kとhは正でなければエラー() -> None:
    with pytest.raises(ValueError, match="k は"):
        fiscal_effect(MPC, B, 0, H, 10)
    with pytest.raises(ValueError, match="h は"):
        fiscal_effect(MPC, B, K, 0, 10)
