"""第 3 章: 需要曲線と弾力性のテスト。"""

import pytest

from lib.chapter03.demand import (
    classify_by_income_elasticity,
    demand_curve,
    demand_x,
    elasticity_type,
    income_consumption_curve,
    income_elasticity,
    linear_demand_quantity,
    market_demand,
    market_demand_curve,
    price_elasticity,
    price_elasticity_linear,
)

# U = x·y、Py = 1。x の需要は m ÷ (2·Px)
M, PY = 80, 1


def test_価格が下がると需要は増える() -> None:
    assert demand_x(M, 2, PY) == 20
    assert demand_x(M, 1, PY) == 40
    assert demand_x(M, 0.5, PY) == 80


def test_需要曲線は価格と需要量の組() -> None:
    assert demand_curve(M, [2, 1, 0.5], PY) == [(2, 20), (1, 40), (0.5, 80)]


def test_需要曲線は右下がり() -> None:
    quantities = [q for _, q in demand_curve(M, [4, 2, 1, 0.5], PY)]
    assert quantities == pytest.approx([10, 20, 40, 80])
    assert all(a < b for a, b in zip(quantities, quantities[1:], strict=False))


def test_他の財の価格が上がると需要曲線は動かない() -> None:
    # コブ・ダグラス型では、財 x の需要は、財 y の価格に依らない
    assert demand_x(M, 2, 1) == demand_x(M, 2, 5)


def test_所得が増えると需要曲線は右へ動く() -> None:
    assert demand_x(160, 2, PY) > demand_x(80, 2, PY)
    assert demand_x(160, 2, PY) == 40


def test_市場需要は個人の需要を横に足したもの() -> None:
    assert market_demand([80, 80], 2, PY) == 40
    assert market_demand([40, 120], 2, PY) == 10 + 30


def test_市場需要は個人の数が増えると増える() -> None:
    assert market_demand([80, 80, 80], 2, PY) == 60


def test_市場需要曲線は各価格の合計() -> None:
    curve = market_demand_curve([40, 120], [2, 1], PY)
    assert curve == [(2, 40), (1, 80)]


def test_需要の価格は正でなければエラー() -> None:
    with pytest.raises(ValueError, match="価格"):
        demand_x(M, 0, PY)


def test_直線の需要曲線の需要量() -> None:
    assert linear_demand_quantity(100, -1, 25) == 75
    assert linear_demand_quantity(100, -1, 100) == 0


def test_直線の需要曲線の需要量は負にならない() -> None:
    assert linear_demand_quantity(100, -1, 150) == 0


def test_直線の需要曲線の弾力性は点の位置で変わる() -> None:
    assert price_elasticity_linear(100, -1, 25) == pytest.approx(1 / 3)
    assert price_elasticity_linear(100, -1, 50) == pytest.approx(1)
    assert price_elasticity_linear(100, -1, 75) == pytest.approx(3)


def test_グラフで緩やかな需要曲線ほど弾力的() -> None:
    # 同じ点 (P = 50, Q = 50) を通る 2 本の直線。価格を縦軸にしたグラフで、
    # 緩やかなほう（価格が少し動くと、需要量が大きく動く。傾き −2）が、弾力的
    gentle = price_elasticity_linear(150, -2, 50)
    steep = price_elasticity_linear(75, -0.5, 50)
    assert linear_demand_quantity(150, -2, 50) == 50
    assert linear_demand_quantity(75, -0.5, 50) == 50
    assert gentle == pytest.approx(2)
    assert steep == pytest.approx(0.5)
    assert gentle > steep


def test_需要量が0なら弾力性は求められない() -> None:
    with pytest.raises(ValueError, match="需要量"):
        price_elasticity_linear(100, -1, 100)


def test_ギッフェン財は右上がりで弾力性が負() -> None:
    # 価格が上がると需要が増える（傾きが正）。弾力性（−傾き × P ÷ Q）が負になる
    assert price_elasticity_linear(10, 0.5, 10) < 0


def test_コブ_ダグラス型の価格弾力性はいつも1() -> None:
    for price in (0.5, 1, 2, 4):
        e = price_elasticity(lambda p: demand_x(M, p, PY), price)
        assert e == pytest.approx(1, rel=1e-6)


def test_数値微分の価格弾力性は直線の需要曲線と一致する() -> None:
    e = price_elasticity(lambda p: linear_demand_quantity(100, -1, p), 25)
    assert e == pytest.approx(1 / 3, rel=1e-6)


def test_価格弾力性は需要量が0なら求められない() -> None:
    with pytest.raises(ValueError, match="需要量"):
        price_elasticity(lambda p: 0.0, 10)


def test_価格弾力性の価格は正でなければエラー() -> None:
    with pytest.raises(ValueError, match="価格"):
        price_elasticity(lambda p: 100 - p, 0)


def test_弾力性の種類() -> None:
    assert elasticity_type(3) == "弾力的"
    assert elasticity_type(1 / 3) == "非弾力的"
    assert elasticity_type(1) == "単位弾力的"
    assert elasticity_type(1 + 1e-12) == "単位弾力的"
    assert elasticity_type(-3) == "弾力的"


def test_所得弾力性はコブ_ダグラス型で1() -> None:
    e = income_elasticity(lambda m: demand_x(m, 2, PY), 80)
    assert e == pytest.approx(1, rel=1e-6)


def test_所得弾力性の符号は財の種類を表す() -> None:
    assert income_elasticity(lambda m: 100 - 0.1 * m, 500) == pytest.approx(-1)
    assert income_elasticity(lambda m: 10 * m**0.5, 100) == pytest.approx(0.5)
    assert income_elasticity(lambda m: 0.01 * m**2, 100) == pytest.approx(2)
    assert income_elasticity(lambda m: 30.0, 100) == pytest.approx(0, abs=1e-9)


def test_所得弾力性は需要量が0なら求められない() -> None:
    with pytest.raises(ValueError, match="需要量"):
        income_elasticity(lambda m: 0.0, 100)


def test_所得弾力性の所得は正でなければエラー() -> None:
    with pytest.raises(ValueError, match="所得"):
        income_elasticity(lambda m: m, 0)


def test_所得弾力性による財の分類() -> None:
    assert classify_by_income_elasticity(2) == "奢侈品"
    assert classify_by_income_elasticity(1) == "奢侈品"
    assert classify_by_income_elasticity(0.5) == "必需品"
    assert classify_by_income_elasticity(0) == "中立財"
    assert classify_by_income_elasticity(-1) == "下級財"


def test_所得弾力性の分類は許容誤差を持つ() -> None:
    assert classify_by_income_elasticity(1 - 1e-9) == "奢侈品"
    assert classify_by_income_elasticity(1e-9) == "中立財"
    assert classify_by_income_elasticity(-1e-9) == "中立財"
    assert classify_by_income_elasticity(0.01) == "必需品"
    assert classify_by_income_elasticity(-0.01) == "下級財"


def test_所得消費曲線は所得を動かしたときの最適点() -> None:
    assert income_consumption_curve([40, 80, 160], 2, PY) == [
        (10, 20),
        (20, 40),
        (40, 80),
    ]


def test_所得消費曲線はコブ_ダグラス型で原点を通る直線() -> None:
    curve = income_consumption_curve([40, 80, 160], 2, PY)
    assert all(y == pytest.approx(2 * x) for x, y in curve)
