"""第 11 章: 需給ギャップとオークンの法則のテスト。"""

import pytest

from lib.chapter11.okun import (
    OkunFit,
    okun_breakeven_growth,
    okun_coefficients,
    output_gap_ratio,
    synthetic_unemployment_change,
)

# 成長率（%）。失業率の変化は、Δu = 1.2 − 0.4 × 成長率 で作る
GROWTH = [3.2, 1.5, 4.1, 0.8, 2.9, 5.0, -0.5, 3.6, 2.2, 4.5, 1.0, 3.0]


def test_需給ギャップは実際のGDPが潜在GDPを下回ると負() -> None:
    assert output_gap_ratio(950, 1000) == pytest.approx(-0.05)


def test_需給ギャップは実際のGDPが潜在GDPを上回ると正() -> None:
    assert output_gap_ratio(1050, 1000) == pytest.approx(0.05)


def test_需給ギャップは潜在GDPに等しければ0() -> None:
    assert output_gap_ratio(1000, 1000) == 0


def test_潜在GDPが0以下ならエラー() -> None:
    with pytest.raises(ValueError, match="潜在 GDP"):
        output_gap_ratio(950, 0)


def test_関係を満たすデータから傾きと切片が復元される() -> None:
    change = [1.2 - 0.4 * g for g in GROWTH]
    fit = okun_coefficients(GROWTH, change)
    assert fit.slope == pytest.approx(-0.4)
    assert fit.intercept == pytest.approx(1.2)


def test_成長率が高いほど失業率は下がる() -> None:
    change = [1.2 - 0.4 * g for g in GROWTH]
    assert okun_coefficients(GROWTH, change).slope < 0


def test_失業率が変わらない成長率は3() -> None:
    assert okun_breakeven_growth(OkunFit(slope=-0.4, intercept=1.2)) == pytest.approx(3)


def test_傾きが0なら失業率が変わらない成長率は求まらない() -> None:
    with pytest.raises(ValueError, match="傾き"):
        okun_breakeven_growth(OkunFit(slope=0, intercept=1.2))


def test_雑音のないデータは関係そのもの() -> None:
    change = synthetic_unemployment_change(GROWTH, -0.4, 1.2, noise=0, seed=0)
    assert change == pytest.approx([1.2 - 0.4 * g for g in GROWTH])


def test_種が同じなら同じデータ() -> None:
    first = synthetic_unemployment_change(GROWTH, -0.4, 1.2, noise=0.1, seed=7)
    again = synthetic_unemployment_change(GROWTH, -0.4, 1.2, noise=0.1, seed=7)
    assert first == again


def test_種が違えば雑音も違う() -> None:
    first = synthetic_unemployment_change(GROWTH, -0.4, 1.2, noise=0.1, seed=7)
    other = synthetic_unemployment_change(GROWTH, -0.4, 1.2, noise=0.1, seed=8)
    assert first != other


def test_雑音があっても傾きはおおよそ復元される() -> None:
    change = synthetic_unemployment_change(GROWTH, -0.4, 1.2, noise=0.1, seed=0)
    fit = okun_coefficients(GROWTH, change)
    assert fit.slope == pytest.approx(-0.4, abs=0.05)
    assert fit.intercept == pytest.approx(1.2, abs=0.2)


def test_長さが違えばエラー() -> None:
    with pytest.raises(ValueError, match="同じ長さ"):
        okun_coefficients([1, 2, 3], [1, 2])


def test_成長率のほうが短くてもエラー() -> None:
    with pytest.raises(ValueError, match="同じ長さ"):
        okun_coefficients([1, 2], [1, 2, 3])


def test_点が2つ未満ならエラー() -> None:
    with pytest.raises(ValueError, match="2 点以上"):
        okun_coefficients([1], [1])


def test_成長率がすべて同じなら傾きは求まらずエラー() -> None:
    with pytest.raises(ValueError, match="すべて同じ"):
        okun_coefficients([2, 2, 2], [1, 2, 3])


def test_2点だけでも直線が決まる() -> None:
    fit = okun_coefficients([1.0, 3.0], [1.0, -1.0])
    assert fit.slope == pytest.approx(-1.0)
    assert fit.intercept == pytest.approx(2.0)
