"""全体レビュー（2026-11-21）の指摘: 許容誤差と、公開した検証関数のテスト。"""

import math

import pytest

from lib.chapter07.liquidity import money_demand_with_trap, money_market_state
from lib.chapter07.money_market import lm_slope, money_demand, validate_h, validate_k


def test_下限が0のとき浮動小数点の誤差でも下限に等しいと見なす() -> None:
    tiny = 0.1 + 0.2 - 0.3  # 5.55e-17
    assert money_demand_with_trap(1000, tiny, 0.5, 100, 0.0) == math.inf
    assert money_demand_with_trap(1000, -tiny, 0.5, 100, 0.0) == math.inf


def test_下限を明らかに下回ればエラー() -> None:
    with pytest.raises(ValueError, match="下限を下回らない"):
        money_demand_with_trap(1000, -1e-3, 0.5, 100, 0.0)


def test_超過需要が小さくても符号で状態が決まる() -> None:
    # L = kY − hr = 250。M/P = 250 ∓ 1e-6 なら、超過需要は ±1e-6（許容誤差 1e-9 より大きい）
    assert money_market_state(1000, 2.5, 250 - 1e-6, 0.5, 100).startswith("需要超過")
    assert money_market_state(1000, 2.5, 250 + 1e-6, 0.5, 100).startswith("供給超過")


def test_感応度が1未満の正の値でも有効() -> None:
    assert money_demand(1000, 2.5, 0.5, 0.5) == pytest.approx(498.75)
    assert lm_slope(0.5, 0.5) == pytest.approx(1.0)


def test_公開した検証関数は正の値を通し正でなければエラー() -> None:
    validate_k(0.5)
    validate_h(0.5)
    with pytest.raises(ValueError, match="所得への感応度"):
        validate_k(0.0)
    with pytest.raises(ValueError, match="利子率への感応度"):
        validate_h(-1.0)
