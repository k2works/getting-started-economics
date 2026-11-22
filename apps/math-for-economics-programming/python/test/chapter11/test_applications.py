import functools
import math

import pytest

from lib.chapter01.market import consumer_surplus, demand_quantity
from lib.chapter03.interest import continuous_compound_amount
from lib.chapter04.sequence import annuity_present_value, perpetuity_present_value
from lib.chapter05.derivative import Polynomial
from lib.chapter11.applications import area_under_demand, continuous_present_value
from lib.chapter11.integral import midpoint_rule_integral, polynomial_definite_integral


def test_直線の需要の消費者余剰は積分でも第1章の三角形と同じ400() -> None:
    demand = functools.partial(demand_quantity, a=120, b=2)
    # 需要がちょうど 0 になる価格 60 まで、需要曲線の下を積分する
    assert area_under_demand(demand, 40, 60) == pytest.approx(400)
    assert consumer_surplus(40, 120, 2) == pytest.approx(400)
    for a, b, price in [(90, 3, 10), (50, 0.5, 64)]:
        demand = functools.partial(demand_quantity, a=a, b=b)
        area = area_under_demand(demand, price, a / b)
        assert area == pytest.approx(consumer_surplus(price, a, b))


def test_曲線の需要の消費者余剰は三角形では求まらない() -> None:
    # q = 100 − p²。価格 6 で q = 64、需要が 0 になる価格は 10
    demand = Polynomial((100, 0, -1))
    exact = polynomial_definite_integral(demand, 6, 10)
    assert exact == pytest.approx(416 / 3)
    assert area_under_demand(demand, 6, 10) == pytest.approx(exact)
    triangle = (10 - 6) * demand(6) / 2
    assert triangle == 128
    assert exact - triangle == pytest.approx(32 / 3)


def test_価格が上がったときの余剰の減少は価格の区間の積分() -> None:
    # q = 100/p は、需要が 0 になる価格がない。2 から 4 への値上げの減少は 100·ln 2
    loss = area_under_demand(lambda p: 100 / p, 2, 4)
    assert loss == pytest.approx(100 * math.log(2), rel=1e-6)
    # 上端を 4 倍にするたびに、面積は 100·ln 4 ずつ増え続け、上限がない
    highs = (8, 32, 128)
    areas = [area_under_demand(lambda p: 100 / p, 2, high) for high in highs]
    assert areas == pytest.approx([100 * math.log(h / 2) for h in highs], rel=1e-3)


def test_連続時間の割引現在価値は割引かけた流れの積分() -> None:
    # 毎年 10 の流れを 20 年、割引率 5%: 10(1 − e^(−1)) ÷ 0.05 ≈ 126.42
    value = continuous_present_value(10, 0.05, 20)
    assert value == pytest.approx(200 * (1 - math.exp(-1)))
    assert round(value, 2) == 126.42

    def discounted(t: float) -> float:
        return 10 / continuous_compound_amount(1, 0.05, t)

    assert midpoint_rule_integral(discounted, 0, 20, 1000) == pytest.approx(value)
    assert continuous_present_value(4, 0.1, 5) == pytest.approx(
        40 * (1 - math.exp(-0.5))
    )


def test_連続の流れは期末払いの年金より早く受け取るので価値が高く永久なら同じ() -> None:
    annuity = annuity_present_value(10, 0.05, 20)
    assert round(annuity, 2) == 124.62
    assert continuous_present_value(10, 0.05, 20) > annuity
    long = continuous_present_value(10, 0.05, 1000)
    assert long == pytest.approx(perpetuity_present_value(10, 0.05))


def test_割引率0なら流れの合計で期間は0以上で価格の区間は下から上() -> None:
    assert continuous_present_value(10, 0, 20) == 200
    assert continuous_present_value(10, 0.05, 0) == 0
    # 割引率がごく小さくても、桁落ちせず、流れの合計に近い
    for rate in (1e-13, 1e-17):
        assert continuous_present_value(100, rate, 10) == pytest.approx(1000, rel=1e-9)
    with pytest.raises(ValueError):
        continuous_present_value(10, 0.05, -1)
    with pytest.raises(ValueError):
        area_under_demand(lambda p: 100 / p, 4, 2)
    assert area_under_demand(lambda p: 100 / p, 3, 3) == 0
