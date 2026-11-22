"""アニメーション（lib/animations）のテスト。

フレームごとのデータは、各章の関数と一致すること。GIF の保存は、全フレームを描くので、
更新の関数が動くことの確認になる。
"""

from collections.abc import Callable
from dataclasses import replace
from pathlib import Path

import pytest
from matplotlib.animation import FuncAnimation

from lib.animations.ad_as import ad_as_frames, animate_ad_as
from lib.animations.common import linear_values
from lib.animations.income import animate_mpc_change, mpc_frames
from lib.animations.is_lm import (
    animate_crowding_out,
    animate_fiscal_shift,
    crowding_frames,
    fiscal_shift_frames,
)
from lib.animations.money import (
    animate_credit_creation,
    animate_lm_shift,
    credit_frames,
    lm_shift_frames,
)
from lib.animations.open_economy import animate_regimes, regime_frames
from lib.animations.phillips import animate_accelerating_inflation, phillips_frames
from lib.chapter04.multiplier import equilibrium_income, spending_multiplier
from lib.chapter06.money_supply import credit_creation_path, money_stock
from lib.chapter07.liquidity import lm_interest_with_trap
from lib.chapter07.money_market import lm_interest
from lib.chapter08.is_lm import solve_is_lm
from lib.chapter09.policy import crowding_out, fiscal_effect
from lib.chapter10.ad_as import (
    AdEconomy,
    aggregate_demand_income,
    expand_demand,
    keynesian_supply,
    solve_ad_as,
)
from lib.chapter11.phillips import accelerating_inflation_path, short_run_inflation
from lib.chapter14.mundell_fleming import (
    SmallOpenEconomy,
    fixed_rate_equilibrium,
    floating_rate_equilibrium,
)

AD_ECONOMY = AdEconomy(mpc=0.6, b=20, intercept=450, k=0.5, h=100, nominal_money=250)
OPEN_ECONOMY = SmallOpenEconomy(
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


def test_等間隔の値は両端を含む() -> None:
    assert linear_values(0, 10, 5) == [0, 2.5, 5, 7.5, 10]
    assert linear_values(4, 1, 4) == [4, 3, 2, 1]


def test_フレーム数は2以上() -> None:
    with pytest.raises(ValueError, match="フレーム数"):
        linear_values(0, 1, 1)


def test_限界消費性向が上がると均衡所得と乗数が増える() -> None:
    data = mpc_frames(40, 30, 30, 0, 0.5, 0.9, 5)
    assert [f.mpc for f in data] == pytest.approx([0.5, 0.6, 0.7, 0.8, 0.9])
    assert data[0].income == pytest.approx(equilibrium_income(0.5, 40, 30, 30, 0))
    assert data[0].income == pytest.approx(200)
    assert data[-1].income == pytest.approx(1000)
    assert data[-1].multiplier == pytest.approx(spending_multiplier(0.9))
    incomes = [f.income for f in data]
    assert incomes == sorted(incomes)


def test_信用創造は最終的なマネーストックへ近づく() -> None:
    data = credit_frames(110, 0.1, 0.01, 5)
    assert [f.round for f in data] == [1, 2, 3, 4, 5]
    assert [f.stock for f in data] == credit_creation_path(110, 0.1, 0.01, 5)
    assert all(f.limit == money_stock(0.1, 0.01, 110) for f in data)
    assert data[-1].stock < data[-1].limit
    assert [f.stock for f in data] == sorted(f.stock for f in data)


def test_実質貨幣供給が増えるとLM曲線が下へ動く() -> None:
    incomes = [600.0, 800.0, 1000.0]
    data = lm_shift_frames(250, 350, 0.5, 100, 2.5, incomes, 3)
    assert [f.real_money for f in data] == [250, 300, 350]
    assert data[0].curve == [lm_interest(y, 250, 0.5, 100) for y in incomes]
    assert data[1].trap_curve == [
        lm_interest_with_trap(y, 300, 0.5, 100, 2.5) for y in incomes
    ]
    assert data[-1].trap_curve[0] == 2.5
    assert data[-1].curve[0] < data[0].curve[0]


def test_政府支出が増えるとISが右へ動き均衡所得が増える() -> None:
    data = fiscal_shift_frames(0.6, 20, 450, 0.5, 100, 250, 40, 5)
    assert [f.delta_government for f in data] == [0, 10, 20, 30, 40]
    assert (data[0].income, data[0].interest) == pytest.approx((1000, 2.5))
    assert (data[2].income, data[2].interest) == pytest.approx(
        solve_is_lm(0.6, 20, 470, 0.5, 100, 250)
    )
    assert data[-1].intercept == 490
    incomes = [f.income for f in data]
    assert incomes == sorted(incomes)


def test_貨幣需要の利子感応度が上がるとクラウディングアウトが減る() -> None:
    data = crowding_frames(0.6, 20, 450, 0.5, 20, 400, 10, 250, 5)
    assert data[0].h == 20
    assert data[-1].h == 400
    for frame in data:
        assert frame.effect == pytest.approx(fiscal_effect(0.6, 20, 0.5, frame.h, 10))
        assert frame.crowding_out == pytest.approx(
            crowding_out(0.6, 20, 0.5, frame.h, 10)
        )
        assert frame.income_after - frame.income_before == pytest.approx(frame.effect)
    effects = [f.effect for f in data]
    assert effects == sorted(effects)
    assert data[-1].crowding_out < data[0].crowding_out


def test_政府支出が増えるとADが右へ動き物価も上がる() -> None:
    prices = [0.8, 1.2, 1.6]
    data = ad_as_frames(AD_ECONOMY, 1000, 480, 400, 40, prices, 3)
    assert [f.delta_government for f in data] == [0, 20, 40]
    assert data[1].curve == [
        aggregate_demand_income(expand_demand(AD_ECONOMY, 20), p) for p in prices
    ]
    for frame in data:
        economy = expand_demand(AD_ECONOMY, frame.delta_government)
        price, income = solve_ad_as(
            economy, lambda p: keynesian_supply(p, 1000, 480, 400)
        )
        assert (frame.price, frame.income) == pytest.approx((price, income))
    assert data[-1].price > data[0].price
    assert data[-1].income >= data[0].income


def test_失業率を自然失業率より低く保つとインフレ率が上がり続ける() -> None:
    data = phillips_frames(4, 5, 2, 0.5, 4)
    assert [f.period for f in data] == [0, 1, 2, 3, 4]
    assert [f.inflation for f in data] == accelerating_inflation_path(4, 5, 2, 0.5, 4)
    assert data[-1].inflation == pytest.approx(4)
    assert data[0].expected == 2
    for before, after in zip(data, data[1:], strict=False):
        assert after.expected == before.inflation
        assert after.inflation == short_run_inflation(4, 5, after.expected, 0.5)


def test_為替制度ごとの財政政策の効果() -> None:
    data = regime_frames(OPEN_ECONOMY, 20, 5)
    assert [f.delta_government for f in data] == [0, 5, 10, 15, 20]
    base = fixed_rate_equilibrium(OPEN_ECONOMY).income
    assert data[0].fixed_income == pytest.approx(base)
    assert data[0].floating_income == pytest.approx(
        floating_rate_equilibrium(OPEN_ECONOMY).income
    )
    after = replace(OPEN_ECONOMY, intercept=OPEN_ECONOMY.intercept + 20)
    assert data[-1].fixed_income == pytest.approx(fixed_rate_equilibrium(after).income)
    assert data[-1].fixed_income - base == pytest.approx(50)
    assert data[-1].floating_income == pytest.approx(data[0].floating_income)
    assert data[-1].exchange_rate < data[0].exchange_rate


BUILDERS: dict[str, Callable[[], FuncAnimation]] = {
    "mpc": lambda: animate_mpc_change(frames=4),
    "credit": lambda: animate_credit_creation(rounds=4),
    "lm": lambda: animate_lm_shift(frames=4),
    "fiscal": lambda: animate_fiscal_shift(frames=4),
    "crowding": lambda: animate_crowding_out(frames=4),
    "ad-as": lambda: animate_ad_as(frames=4),
    "phillips": lambda: animate_accelerating_inflation(periods=3),
    "regimes": lambda: animate_regimes(frames=4),
}


@pytest.mark.parametrize("name", sorted(BUILDERS))
def test_アニメーションをGIFに保存できる(name: str, tmp_path: Path) -> None:
    animation = BUILDERS[name]()
    assert isinstance(animation, FuncAnimation)
    path = tmp_path / f"{name}.gif"
    animation.save(path, writer="pillow", fps=5, dpi=30)
    assert path.read_bytes()[:6] == b"GIF89a"
