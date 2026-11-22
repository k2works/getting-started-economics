"""アニメーション（lib/animations）のテスト。

フレームごとのデータは、各章の関数と一致すること。GIF の保存は、全フレームを描くので、
更新の関数が動くことの確認になる。
"""

from collections.abc import Callable
from pathlib import Path

import pytest
from matplotlib.animation import FuncAnimation

from lib.animations.common import linear_values
from lib.animations.consumer import animate_price_change, price_change_frames
from lib.animations.externality import animate_externality, externality_frames
from lib.animations.firm import (
    animate_monopoly_cost,
    animate_supply_curve,
    monopoly_frames,
    supply_frames,
)
from lib.animations.game import animate_trigger_threshold, threshold_frames
from lib.animations.market import (
    animate_price_adjustment,
    animate_tariff,
    animate_tax,
    tariff_frames,
    tax_frames,
)
from lib.chapter02.budget import optimal_bundle
from lib.chapter05.cost import CostCurve
from lib.chapter07.supply import profit_maximizing_output
from lib.chapter08.market import LinearMarket, equilibrium
from lib.chapter09.surplus import tax_equilibrium
from lib.chapter10.trade import tariff_deadweight_loss, tariff_result
from lib.chapter11.monopoly import Monopoly, monopoly_outcome
from lib.chapter14.externality import ExternalityMarket, socially_optimal_quantity

MARKET = LinearMarket(100, -1, -10, 1)
CURVE = CostCurve(1, -6, 15, 32)


def test_等間隔の値は両端を含む() -> None:
    assert linear_values(0, 10, 5) == [0, 2.5, 5, 7.5, 10]
    assert linear_values(4, 1, 4) == [4, 3, 2, 1]


def test_フレーム数は2以上() -> None:
    with pytest.raises(ValueError, match="フレーム数"):
        linear_values(0, 1, 1)


def test_価格が下がると最適点の財xが増える() -> None:
    data = price_change_frames(100, 1, 4, 1, 4)
    assert [f.price for f in data] == [4, 3, 2, 1]
    assert data[0].bundle == optimal_bundle(100, 4, 1)
    assert data[-1].bundle == (50, 50)
    assert [f.bundle[0] for f in data] == sorted(f.bundle[0] for f in data)
    assert data[0].intercepts == (25, 100)
    assert data[-1].level == pytest.approx(2500)


def test_供給の各フレームは利潤最大の生産量() -> None:
    data = supply_frames(CURVE, 40, 5)
    assert [f.price for f in data] == [0, 10, 20, 30, 40]
    assert data[0].quantity == 0
    assert data[0].profit == -32
    assert data[3].quantity == profit_maximizing_output(CURVE, 30)
    assert data[3].profit == pytest.approx(68)
    quantities = [f.quantity for f in data]
    assert quantities == sorted(quantities)


def test_独占の各フレームは限界費用に応じた結果() -> None:
    data = monopoly_frames(100, 1, 40, 5)
    assert [f.cost for f in data] == [0, 10, 20, 30, 40]
    assert data[1].monopoly == monopoly_outcome(Monopoly(100, 1, 10))
    assert data[0].monopoly.quantity == 50
    assert data[-1].monopoly.price == 70
    prices = [f.monopoly.price for f in data]
    assert prices == sorted(prices)


def test_課税の各フレームは税額に応じた結果() -> None:
    data = tax_frames(MARKET, 20, 5)
    assert data[0] == tax_equilibrium(MARKET, 0)
    assert data[0].deadweight_loss == 0
    assert data[-1] == tax_equilibrium(MARKET, 20)
    losses = [f.deadweight_loss for f in data]
    assert losses == sorted(losses)


def test_関税の各フレームは関税に応じた結果() -> None:
    data = tariff_frames(MARKET, 40, 15, 4)
    assert data[0] == tariff_result(MARKET, 40, 0)
    assert data[-1] == tariff_result(MARKET, 40, 15)
    assert data[-1].domestic_price == equilibrium(MARKET)[0]
    assert tariff_deadweight_loss(MARKET, 40, 15) == pytest.approx(225)


def test_割引因子の各フレームは閾値で協調が続く() -> None:
    data = threshold_frames(5, 3, 1, 0.9, 10)
    assert data[0].delta == 0
    assert data[-1].delta == pytest.approx(0.9)
    assert not data[0].sustained
    assert data[-1].sustained
    switch = next(f.delta for f in data if f.sustained)
    assert 0.4 < switch <= 0.6
    assert all(f.cooperate >= f.defect for f in data if f.sustained)


def test_外部費用の各フレームは最適な数量が減る() -> None:
    data = externality_frames((100, 1), (10, 1), 40, 5)
    assert [f.external_cost for f in data] == [0, 10, 20, 30, 40]
    assert data[0].loss == 0
    assert data[0].market == data[0].optimal
    assert data[2].optimal == socially_optimal_quantity(
        ExternalityMarket(100, 1, 10, 1, 20)
    )
    assert data[-1].loss == pytest.approx(400)
    optimal = [f.optimal for f in data]
    assert optimal == sorted(optimal, reverse=True)


BUILDERS: dict[str, Callable[[], FuncAnimation]] = {
    "price-change": lambda: animate_price_change(frames=4),
    "supply": lambda: animate_supply_curve(frames=4),
    "adjustment": lambda: animate_price_adjustment(steps=3),
    "tax": lambda: animate_tax(frames=4),
    "tariff": lambda: animate_tariff(frames=4),
    "monopoly": lambda: animate_monopoly_cost(frames=4),
    "trigger": lambda: animate_trigger_threshold(frames=4),
    "externality": lambda: animate_externality(frames=4),
}


@pytest.mark.parametrize("name", sorted(BUILDERS))
def test_アニメーションをGIFに保存できる(name: str, tmp_path: Path) -> None:
    animation = BUILDERS[name]()
    assert isinstance(animation, FuncAnimation)
    path = tmp_path / f"{name}.gif"
    animation.save(path, writer="pillow", fps=5, dpi=30)
    assert path.read_bytes()[:6] == b"GIF89a"
