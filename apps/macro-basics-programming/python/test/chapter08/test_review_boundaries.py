"""全体レビュー（2026-11-21）の指摘: 許容誤差と、小さい正の値のテスト。"""

import pytest

from lib.chapter08.is_lm import (
    goods_market_state,
    is_interest,
    is_slope,
    solve_is_lm,
    validate_b,
)


def test_超過供給が小さくても符号で状態が決まる() -> None:
    # (1 − c)Y + b·r = 450。IS の切片 A を 450 ± 1e-6 にすると、超過供給は ∓1e-6
    assert goods_market_state(1000, 2.5, 450 - 1e-6, 0.6, 20) == "供給超過"
    assert goods_market_state(1000, 2.5, 450 + 1e-6, 0.6, 20) == "需要超過"


def test_投資の感応度が1未満の正の値でも有効() -> None:
    assert is_interest(1000, 450, 0.6, 0.5) == pytest.approx(100)
    assert is_slope(0.6, 0.5) == pytest.approx(-0.8)


def test_貨幣需要の感応度が1未満の正の値でも連立方程式を解ける() -> None:
    income, interest = solve_is_lm(0.6, 20, 450, 0.5, 0.5, 250)
    assert 0.4 * income + 20 * interest == pytest.approx(450)
    assert 0.5 * income - 0.5 * interest == pytest.approx(250)


def test_公開した検証関数は0以上を通し負ならエラー() -> None:
    validate_b(0.0)
    validate_b(0.5)
    with pytest.raises(ValueError, match="0 以上"):
        validate_b(-0.1)
