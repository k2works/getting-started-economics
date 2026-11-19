"""第 13 章: IS-LM 分析のテスト。

標準のモデル: 消費 C = 100 + 0.8(Y - 50)、投資 I = 140 - 10r、政府支出 G = 100、
貨幣需要 L = 0.5Y - 20r、実質貨幣供給 M/P = 525。
IS 曲線は 0.2Y + 10r = 300、LM 曲線は 0.5Y - 20r = 525。
"""

import dataclasses
from typing import Any

import pytest
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from lib.chapter13.islm import (
    IsLmModel,
    is_income,
    lm_interest,
    plot_islm,
    solve_equilibrium,
)


def curve_points(line: Line2D) -> dict[float, float]:
    """線の (横軸, 縦軸) の組を、横軸をキーにした辞書にする。"""
    points: Any = line.get_xydata()
    return {float(x): float(y) for x, y in points}


def test_標準のモデルの均衡は所得1250で利子率5() -> None:
    income, rate = solve_equilibrium(IsLmModel())
    assert income == pytest.approx(1250)
    assert rate == pytest.approx(5)


def test_IS曲線は利子率が5のとき所得1250で利子率が0のとき所得1500() -> None:
    model = IsLmModel()
    assert is_income(model, 5) == pytest.approx(1250)
    assert is_income(model, 0) == pytest.approx(1500)


def test_LM曲線は所得が1250のとき利子率5で所得が1050のとき利子率0() -> None:
    model = IsLmModel()
    assert lm_interest(model, 1250) == pytest.approx(5)
    assert lm_interest(model, 1050) == pytest.approx(0)


def test_利子率に下限があるとLM曲線は下限で水平になる() -> None:
    trap = IsLmModel(interest_floor=2)
    # 所得 1050 では、下限がなければ利子率は 0。下限があれば 2 になる
    assert lm_interest(trap, 1050) == pytest.approx(2)
    assert lm_interest(trap, 1250) == pytest.approx(5)


def test_均衡はIS曲線とLM曲線の両方の上にある() -> None:
    model = IsLmModel()
    income, rate = solve_equilibrium(model)
    assert is_income(model, rate) == pytest.approx(income)
    assert lm_interest(model, income) == pytest.approx(rate)


def test_財政支出を増やすと所得と利子率が上がる() -> None:
    before = solve_equilibrium(IsLmModel())
    after = solve_equilibrium(IsLmModel(government=120))
    assert after[0] == pytest.approx(1294.4444, abs=1e-3)
    assert after[1] == pytest.approx(6.1111, abs=1e-3)
    assert after[0] > before[0]
    assert after[1] > before[1]


def test_クラウディングアウトで所得の増加は乗数効果より小さい() -> None:
    before_income, _ = solve_equilibrium(IsLmModel())
    after_income, _ = solve_equilibrium(IsLmModel(government=120))
    # 利子率が一定なら、所得は 20 / (1 - 0.8) = 100 増える
    assert after_income - before_income == pytest.approx(44.444, abs=1e-3)
    assert after_income - before_income < 100


def test_貨幣供給を増やすと所得が増え利子率が下がる() -> None:
    before = solve_equilibrium(IsLmModel())
    after = solve_equilibrium(IsLmModel(money_supply=575))
    assert after[0] == pytest.approx(1305.5556, abs=1e-3)
    assert after[1] == pytest.approx(3.8889, abs=1e-3)
    assert after[0] > before[0]
    assert after[1] < before[1]


def test_IS曲線が緩やかなほど金融政策は有効() -> None:
    # 投資の利子率感応度 b を 10 から 20 にすると、IS 曲線は緩やかになる
    gentle = IsLmModel(investment_sensitivity=20)
    steep_gain = (
        solve_equilibrium(IsLmModel(money_supply=575))[0]
        - solve_equilibrium(IsLmModel())[0]
    )
    gentle_gain = (
        solve_equilibrium(dataclasses.replace(gentle, money_supply=575))[0]
        - solve_equilibrium(gentle)[0]
    )
    assert gentle_gain == pytest.approx(71.4286, abs=1e-3)
    assert gentle_gain > steep_gain


def test_LM曲線が緩やかなほど財政政策は有効() -> None:
    # 貨幣需要の利子率感応度 h を 20 から 40 にすると、LM 曲線は緩やかになる
    gentle = IsLmModel(money_interest_sensitivity=40)
    steep_gain = (
        solve_equilibrium(IsLmModel(government=120))[0]
        - solve_equilibrium(IsLmModel())[0]
    )
    gentle_gain = (
        solve_equilibrium(dataclasses.replace(gentle, government=120))[0]
        - solve_equilibrium(gentle)[0]
    )
    assert gentle_gain == pytest.approx(61.5385, abs=1e-3)
    assert gentle_gain > steep_gain


def test_流動性のわなで金融政策を強めても所得は増えない() -> None:
    trap = IsLmModel(interest_floor=2)
    # 通常の範囲では、下限は効かない
    assert solve_equilibrium(trap) == pytest.approx((1250, 5))
    # 貨幣供給を大きく増やすと、利子率は下限の 2 に張り付き、所得は 1400 で止まる
    big = solve_equilibrium(dataclasses.replace(trap, money_supply=2000))
    bigger = solve_equilibrium(dataclasses.replace(trap, money_supply=3000))
    assert big == pytest.approx((1400, 2))
    assert bigger == pytest.approx((1400, 2))


def test_流動性のわなで財政政策は乗数どおりの効果がある() -> None:
    trap = IsLmModel(interest_floor=2, money_supply=2000)
    before = solve_equilibrium(trap)[0]
    after = solve_equilibrium(dataclasses.replace(trap, government=120))[0]
    # クラウディングアウトがないので、20 / (1 - 0.8) = 100 だけ増える
    assert after - before == pytest.approx(100)


@pytest.mark.parametrize(
    "overrides",
    [
        {"mpc": 1.0},
        {"mpc": -0.1},
        {"investment_sensitivity": 0},
        {"money_interest_sensitivity": 0},
        {"money_income_sensitivity": 0},
        {"price_level": 0},
    ],
)
def test_モデルの係数が不正なら作れない(overrides: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        IsLmModel(**overrides)


def test_IS_LMの図にはIS曲線とLM曲線と均衡点がある() -> None:
    fig = plot_islm(IsLmModel())
    ax = fig.axes[0]
    assert isinstance(fig, Figure)
    assert [line.get_label() for line in ax.lines] == ["IS", "LM", "Equilibrium"]


def test_図の均衡点は所得1250利子率5() -> None:
    ax = plot_islm(IsLmModel()).axes[0]
    ((income, rate),) = curve_points(ax.lines[2]).items()
    assert income == pytest.approx(1250)
    assert rate == pytest.approx(5)


def test_政策後のモデルを渡すと移動後の曲線も描く() -> None:
    after = IsLmModel(government=120)
    ax = plot_islm(IsLmModel(), after=after).axes[0]
    labels = [line.get_label() for line in ax.lines]
    assert labels == [
        "IS",
        "LM",
        "Equilibrium",
        "IS (after)",
        "LM (after)",
        "Equilibrium (after)",
    ]


def test_IS曲線上の点はすべて財市場の均衡を表す() -> None:
    model = IsLmModel()
    ax = plot_islm(model).axes[0]
    points = curve_points(ax.lines[0])
    assert len(points) > 10
    for income, rate in points.items():
        assert is_income(model, rate) == pytest.approx(income)


def test_LM曲線上の点はすべて貨幣市場の均衡を表す() -> None:
    model = IsLmModel()
    ax = plot_islm(model).axes[0]
    points = curve_points(ax.lines[1])
    assert len(points) > 10
    for income, rate in points.items():
        assert lm_interest(model, income) == pytest.approx(rate)


def test_政策後のIS曲線は政策後のモデルの上にある() -> None:
    before = IsLmModel()
    after = IsLmModel(government=120)
    ax = plot_islm(before, after=after).axes[0]
    after_points = curve_points(ax.lines[3])
    for income, rate in after_points.items():
        assert is_income(after, rate) == pytest.approx(income)
    # 政策前の IS 曲線とは、別の線になっている
    assert is_income(before, 6) != pytest.approx(is_income(after, 6))


def test_政策後のLM曲線と均衡点は政策後のモデルのもの() -> None:
    after = IsLmModel(money_supply=575)
    ax = plot_islm(IsLmModel(), after=after).axes[0]
    for income, rate in curve_points(ax.lines[4]).items():
        assert lm_interest(after, income) == pytest.approx(rate)
    ((income, rate),) = curve_points(ax.lines[5]).items()
    assert (income, rate) == pytest.approx(solve_equilibrium(after))
