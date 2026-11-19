"""第 10 章: SciPy による最適化のテスト。"""

from types import SimpleNamespace

import pytest

from lib.chapter04.cost import marginal_cost, total_cost
from lib.chapter04.utility import cobb_douglas_utility, marginal_rate_of_substitution
from lib.chapter10 import optimization
from lib.chapter10.optimization import (
    maximize_utility,
    minimize_cost,
    production,
    profit_maximizing_quantity,
)


def test_効用最大化の消費点は所得の半分ずつを使う点() -> None:
    # 価格 (2, 4)、所得 40、alpha = 0.5。x* = 0.5 * 40 / 2 = 10、y* = 0.5 * 40 / 4 = 5
    x, y = maximize_utility(price_x=2, price_y=4, income=40)
    assert x == pytest.approx(10, abs=1e-4)
    assert y == pytest.approx(5, abs=1e-4)


def test_最適消費点では限界代替率が価格比に等しい() -> None:
    x, y = maximize_utility(price_x=2, price_y=4, income=40)
    assert marginal_rate_of_substitution(x, y) == pytest.approx(2 / 4, abs=1e-4)


def test_最適消費点は予算をちょうど使い切る() -> None:
    x, y = maximize_utility(price_x=2, price_y=4, income=40)
    assert 2 * x + 4 * y == pytest.approx(40, abs=1e-6)


def test_財xの比重が大きいと財xを多く買う() -> None:
    # alpha = 0.75: x* = 0.75 * 40 / 2 = 15、y* = 0.25 * 40 / 4 = 2.5
    x, y = maximize_utility(price_x=2, price_y=4, income=40, alpha=0.75)
    assert x == pytest.approx(15, abs=1e-4)
    assert y == pytest.approx(2.5, abs=1e-4)


def test_最適消費点の効用はほかの予算内の点より大きい() -> None:
    x, y = maximize_utility(price_x=2, price_y=4, income=40)
    best = cobb_douglas_utility(x, y)
    # 予算線上の別の点 (x, y) = (5, 7.5) と (15, 2.5)
    assert best > cobb_douglas_utility(5, 7.5)
    assert best > cobb_douglas_utility(15, 2.5)


def test_価格が15のとき利潤を最大にする生産量は4() -> None:
    # P = MC: 15 = 3q^2 - 12q + 15 を解くと q = 4（q = 0 は MC が右下がりの側）
    quantity = profit_maximizing_quantity(price=15)
    assert quantity == pytest.approx(4)
    assert marginal_cost(quantity) == pytest.approx(15)


def test_価格が15のときの最大利潤は22() -> None:
    quantity = profit_maximizing_quantity(price=15)
    assert 15 * quantity - total_cost(quantity) == pytest.approx(22)


def test_価格が操業停止点の6を下回ると生産しない() -> None:
    assert profit_maximizing_quantity(price=5) == 0


def test_価格が操業停止点の6ちょうどなら生産量は3() -> None:
    assert profit_maximizing_quantity(price=6) == pytest.approx(3)


def test_費用最小化では生産要素の価格が高い要素を少なく使う() -> None:
    # 賃金 1、資本の価格 4、産出量 10: L* = 10 * sqrt(4 / 1) = 20、K* = 10 * sqrt(1 / 4) = 5
    labor, capital, cost = minimize_cost(output=10, wage=1, rental=4)
    assert labor == pytest.approx(20, abs=1e-3)
    assert capital == pytest.approx(5, abs=1e-3)
    assert cost == pytest.approx(40, abs=1e-3)


def test_費用最小化の解は目標の産出量を満たす() -> None:
    labor, capital, _ = minimize_cost(output=10, wage=1, rental=4)
    assert production(labor, capital) == pytest.approx(10, abs=1e-4)


def test_所得が0以下なら効用最大化はできない() -> None:
    with pytest.raises(ValueError, match="所得"):
        maximize_utility(price_x=2, price_y=4, income=-40)
    with pytest.raises(ValueError, match="所得"):
        maximize_utility(price_x=2, price_y=4, income=0)


def test_財の価格が0以下なら効用最大化はできない() -> None:
    with pytest.raises(ValueError, match="価格"):
        maximize_utility(price_x=0, price_y=4, income=40)
    with pytest.raises(ValueError, match="価格"):
        maximize_utility(price_x=2, price_y=-4, income=40)


def test_産出量が0以下なら費用最小化はできない() -> None:
    with pytest.raises(ValueError, match="産出量"):
        minimize_cost(output=-10, wage=1, rental=4)
    with pytest.raises(ValueError, match="産出量"):
        minimize_cost(output=0, wage=1, rental=4)


def test_生産要素の価格が0以下なら費用最小化はできない() -> None:
    with pytest.raises(ValueError, match="価格"):
        minimize_cost(output=10, wage=0, rental=4)


def test_価格が探索範囲の上限での限界費用を超えると利潤最大化の生産量を探せない() -> (
    None
):
    with pytest.raises(ValueError, match="探索範囲"):
        profit_maximizing_quantity(300)


def test_費用最小化の生産関数は労働と資本の幾何平均() -> None:
    assert production(4, 9) == pytest.approx(6)


def test_生産要素の量が負なら生産関数は求められない() -> None:
    with pytest.raises(ValueError, match="生産要素"):
        production(-1, 4)


def test_価格が限界費用の最低値以下なら生産しない() -> None:
    assert profit_maximizing_quantity(price=2) == 0


def test_ソルバーが収束しなかったときは実行時エラーにする(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    failed = SimpleNamespace(success=False, message="失敗した")
    monkeypatch.setattr(optimization, "minimize", lambda *args, **kwargs: failed)
    with pytest.raises(RuntimeError, match="効用最大化"):
        maximize_utility(price_x=2, price_y=4, income=40)
    with pytest.raises(RuntimeError, match="費用最小化"):
        minimize_cost(output=10, wage=1, rental=4)
