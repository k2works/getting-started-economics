"""全体レビュー（2026-11-21）の指摘: 無限大・負の均衡値を、黙って返さない。"""

import math
from dataclasses import replace

import pytest

from lib.chapter14.mundell_fleming import (
    SmallOpenEconomy,
    fixed_rate_equilibrium,
    floating_rate_equilibrium,
)

ECONOMY = SmallOpenEconomy(
    mpc=0.6,
    b=20,
    intercept=400,
    n=50,
    k=0.5,
    h=100,
    real_money=250,
    world_rate=2.5,
    exchange_rate=1,
)


def test_hが無限大なら有限でないとしてエラー() -> None:
    with pytest.raises(ValueError, match="有限"):
        replace(ECONOMY, h=math.inf)


def test_変動相場で為替レートが負になる条件も範囲外の値としてそのまま返す() -> None:
    # M/P を小さくすると、LM から所得が小さくなり、IS から逆算する e が負になる（モデルの範囲外）
    assert floating_rate_equilibrium(replace(ECONOMY, real_money=100)).exchange_rate < 0


def test_固定相場で実質貨幣供給が負になる条件も範囲外の値としてそのまま返す() -> None:
    assert fixed_rate_equilibrium(replace(ECONOMY, intercept=-100)).real_money < 0


def test_感応度が1未満の正の値でも有効() -> None:
    economy = replace(ECONOMY, h=0.5, n=0.5, intercept=450 - 0.5)
    assert fixed_rate_equilibrium(economy).income > 0
