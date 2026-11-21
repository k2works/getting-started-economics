"""第 7 章: 貨幣需要の分解・シフト・流動性のわなのテスト。"""

import math

import pytest

from lib.chapter07.liquidity import (
    asset_demand,
    excess_money_demand,
    lm_interest_with_trap,
    lm_shift,
    money_demand_shift,
    money_demand_with_trap,
    money_market_state,
    transaction_demand,
    trap_income,
)
from lib.chapter07.money_market import (
    lm_income,
    lm_interest,
    lm_slope,
    money_demand,
)

K = 0.5  # 所得に対する貨幣需要の感応度
H = 100.0  # 利子率に対する貨幣需要の感応度
FLOOR = 2.0  # 利子率の下限


def test_取引需要は所得の増加関数() -> None:
    assert transaction_demand(1000, K) == pytest.approx(500)
    assert transaction_demand(1200, K) > transaction_demand(1000, K)


def test_資産需要は利子率の減少関数() -> None:
    assert asset_demand(2.5, H) == pytest.approx(-250)
    assert asset_demand(4.0, H) < asset_demand(2.5, H)


def test_取引需要と資産需要の和は貨幣需要() -> None:
    total = transaction_demand(1000, K) + asset_demand(2.5, H)
    assert total == pytest.approx(money_demand(1000, 2.5, K, H))


def test_所得が増えると貨幣需要曲線は右にシフトする() -> None:
    assert money_demand_shift(1000, 1200, K) == pytest.approx(100)
    gap = money_demand(1200, 2.5, K, H) - money_demand(1000, 2.5, K, H)
    assert gap == pytest.approx(money_demand_shift(1000, 1200, K))


def test_所得が減ると貨幣需要曲線は左にシフトする() -> None:
    assert money_demand_shift(1000, 800, K) == pytest.approx(-100)


def test_マネーサプライが増えるとLM曲線は右にシフトする() -> None:
    assert lm_shift(250, 300, K) == pytest.approx(100)
    gap = lm_income(2.5, 300, K, H) - lm_income(2.5, 250, K, H)
    assert gap == pytest.approx(lm_shift(250, 300, K))


def test_マネーサプライが減ると左にシフトする() -> None:
    assert lm_shift(250, 200, K) == pytest.approx(-100)


def test_所得への感応度が大きいほどLM曲線は急() -> None:
    assert lm_slope(1.0, H) > lm_slope(K, H)
    assert lm_slope(1.0, H) == pytest.approx(0.01)


def test_傾きは所得を1増やしたときの利子率の上昇に等しい() -> None:
    rise = lm_interest(1001, 250, K, H) - lm_interest(1000, 250, K, H)
    assert rise == pytest.approx(lm_slope(K, H))


def test_利子率への感応度が大きいほどLM曲線は水平に近づく() -> None:
    assert lm_slope(K, 1e6) < 1e-6
    assert lm_slope(K, 1e6) > 0


def test_下限より上ではわなの影響を受けない() -> None:
    assert lm_interest_with_trap(1000, 250, K, H, FLOOR) == pytest.approx(2.5)


def test_下限より低くなるはずの所得では利子率は下限で水平() -> None:
    assert lm_interest(600, 250, K, H) == pytest.approx(0.5)
    for income in (0, 600, 900):
        assert lm_interest_with_trap(income, 250, K, H, FLOOR) == pytest.approx(2.0)


def test_わなの端の所得は下限の利子率に対応する所得() -> None:
    assert trap_income(250, K, H, FLOOR) == pytest.approx(900)
    assert lm_interest(900, 250, K, H) == pytest.approx(FLOOR)


def test_わなでは貨幣供給を増やしても利子率は下がらない() -> None:
    assert lm_interest_with_trap(600, 250, K, H, FLOOR) == pytest.approx(
        lm_interest_with_trap(600, 270, K, H, FLOOR)
    )
    assert lm_interest_with_trap(1000, 300, K, H, FLOOR) < lm_interest_with_trap(
        1000, 250, K, H, FLOOR
    )


def test_下限の利子率では貨幣需要は無限大() -> None:
    assert math.isinf(money_demand_with_trap(1000, FLOOR, K, H, FLOOR))
    assert money_demand_with_trap(1000, 2.5, K, H, FLOOR) == pytest.approx(250)


def test_利子率が下限を下回ればエラー() -> None:
    with pytest.raises(ValueError, match="下限"):
        money_demand_with_trap(1000, 1.0, K, H, FLOOR)


def test_LM曲線上では貨幣の超過需要は0() -> None:
    assert excess_money_demand(1000, 2.5, 250, K, H) == pytest.approx(0)


def test_LM曲線の上側は供給超過で下側は需要超過() -> None:
    assert excess_money_demand(1000, 3.5, 250, K, H) == pytest.approx(-100)
    assert excess_money_demand(1000, 1.5, 250, K, H) == pytest.approx(100)


def test_貨幣市場の状態の判定() -> None:
    assert money_market_state(1000, 3.5, 250, K, H) == "供給超過（利子率が下がる）"
    assert money_market_state(1000, 1.5, 250, K, H) == "需要超過（利子率が上がる）"
    assert money_market_state(1000, 2.5, 250, K, H) == "均衡"


def test_取引需要の感応度が正でなければエラー() -> None:
    with pytest.raises(ValueError, match="所得への感応度"):
        transaction_demand(1000, 0.0)
    with pytest.raises(ValueError, match="所得への感応度"):
        lm_shift(250, 300, -1.0)
    with pytest.raises(ValueError, match="所得への感応度"):
        money_demand_shift(1000, 1200, 0.0)
    with pytest.raises(ValueError, match="利子率への感応度"):
        asset_demand(2.5, 0.0)
