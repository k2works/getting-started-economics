"""アニメーション（lib/animations）のテスト。

フレームごとのデータは、各章の関数と一致すること。GIF の保存は、全フレームを描くので、
更新の関数が動くことの確認になる。
"""

from collections.abc import Callable
from pathlib import Path

import pytest
from matplotlib.animation import FuncAnimation

from lib.animations.common import linear_values
from lib.animations.firm import (
    animate_cournot_steps,
    animate_monopoly_cost,
    animate_profit_price,
    cournot_steps,
    monopoly_frames,
    profit_frames,
)
from lib.animations.macro import (
    adas_frames,
    animate_adas_fiscal,
    animate_islm_fiscal,
    animate_multiplier,
    fiscal_models,
    multiplier_frames,
)
from lib.animations.market import (
    animate_tax_wedge,
    animate_walras,
    tax_frames,
    walras_frames,
)
from lib.chapter04.cost import average_cost
from lib.chapter05.adjustment import walras_path
from lib.chapter07.surplus import equilibrium_with_tax
from lib.chapter09.linear import income_determination
from lib.chapter10.optimization import profit_maximizing_quantity
from lib.chapter13.islm import IsLmModel, solve_equilibrium
from lib.chapter14.adas import aggregate_demand
from lib.chapter15.monopoly import competitive_quantity, monopoly_outcome
from lib.chapter15.oligopoly import best_response, cournot_by_iteration


def test_等間隔の値は両端を含む() -> None:
    assert linear_values(0, 10, 5) == [0, 2.5, 5, 7.5, 10]
    assert linear_values(4, 1, 4) == [4, 3, 2, 1]


def test_フレーム数は2以上() -> None:
    with pytest.raises(ValueError, match="フレーム数"):
        linear_values(0, 1, 1)


def test_ワルラス調整のフレームは価格の推移() -> None:
    data = walras_frames(100, 2, 0, 3, 40, 0.3)
    assert data == walras_path(lambda p: 100 - 2 * p, lambda p: 3 * p, 40, 0.3)
    assert data[0] == 40
    assert data[-1] == pytest.approx(20, abs=1e-5)
    assert data[1] < 20 < data[2]


def test_課税の各フレームは税額に応じた結果() -> None:
    data = tax_frames(100, 2, 0, 3, 15, 4)
    assert data[0] == equilibrium_with_tax(100, 2, 0, 3, 0)
    assert data[0].deadweight_loss == 0
    assert data[-1] == equilibrium_with_tax(100, 2, 0, 3, 15)
    losses = [f.deadweight_loss for f in data]
    assert losses == sorted(losses)


def test_投資が増えると均衡所得が乗数倍で増える() -> None:
    data = multiplier_frames(20, 0.8, 30, 50, 3)
    assert [i for i, _ in data] == [30, 40, 50]
    assert data[0][1] == income_determination(20, 0.8, 30)[0]
    assert data[-1][1] == pytest.approx(350)
    assert data[1][1] - data[0][1] == pytest.approx(50)


def test_政府支出を増やすとISが右へ動く() -> None:
    base = IsLmModel()
    models = fiscal_models(base, 160, 4)
    assert [m.government for m in models] == [100, 120, 140, 160]
    assert models[0] == base
    assert solve_equilibrium(models[0]) == pytest.approx((1250, 5))
    incomes = [solve_equilibrium(m)[0] for m in models]
    assert incomes == sorted(incomes)


def test_総需要の各フレームは完全雇用所得で垂直な総供給と交わる() -> None:
    data = adas_frames(IsLmModel(), 1250, 140, 3)
    assert [f.model.government for f in data] == [100, 120, 140]
    assert data[0].price == pytest.approx(1)
    assert all(f.income == pytest.approx(1250) for f in data)
    assert [round(f.price, 6) for f in data] == sorted(round(f.price, 6) for f in data)
    assert data[-1].price > 1.05
    assert aggregate_demand(data[-1].model, data[-1].price) == pytest.approx(1250)


def test_利潤の各フレームは価格に応じた生産量() -> None:
    data = profit_frames(4, 24, 5)
    assert [f.price for f in data] == [4, 9, 14, 19, 24]
    assert data[0].quantity == 0
    assert data[0].profit == 0
    assert data[1].quantity == profit_maximizing_quantity(9)
    assert data[1].profit < 0
    expected = (14 - average_cost(data[2].quantity)) * data[2].quantity
    assert data[2].profit == pytest.approx(expected)
    quantities = [f.quantity for f in data]
    assert quantities == sorted(quantities)


def test_独占の各フレームは限界費用に応じた結果() -> None:
    data = monopoly_frames(100, 2, 40, 5)
    assert [f.cost for f in data] == [0, 10, 20, 30, 40]
    assert data[1].outcome == monopoly_outcome(100, 2, 10)
    assert data[1].competitive == competitive_quantity(100, 2, 10)
    prices = [f.outcome.price for f in data]
    assert prices == sorted(prices)
    assert data[0].outcome.quantity == 50


def test_クールノーの最適反応を交互にたどる() -> None:
    path = cournot_steps(100, 2, 10, 4)
    assert len(path) == 9
    assert path[0] == (0, 0)
    assert path[1] == (best_response(0, 100, 2, 10), 0)
    assert path[2] == (path[1][0], best_response(path[1][0], 100, 2, 10))
    assert path[3][1] == path[2][1]
    long_path = cournot_steps(100, 2, 10, 40)
    assert long_path[-1] == pytest.approx(cournot_by_iteration(100, 2, 10))


BUILDERS: dict[str, Callable[[], FuncAnimation]] = {
    "walras": lambda: animate_walras(),
    "tax": lambda: animate_tax_wedge(frames=4),
    "multiplier": lambda: animate_multiplier(frames=4),
    "islm": lambda: animate_islm_fiscal(frames=4),
    "adas": lambda: animate_adas_fiscal(frames=4),
    "profit": lambda: animate_profit_price(frames=4),
    "monopoly": lambda: animate_monopoly_cost(frames=4),
    "cournot": lambda: animate_cournot_steps(rounds=3),
}


@pytest.mark.parametrize("name", sorted(BUILDERS))
def test_アニメーションをGIFに保存できる(name: str, tmp_path: Path) -> None:
    animation = BUILDERS[name]()
    assert isinstance(animation, FuncAnimation)
    path = tmp_path / f"{name}.gif"
    animation.save(path, writer="pillow", fps=5, dpi=30)
    assert path.read_bytes()[:6] == b"GIF89a"
