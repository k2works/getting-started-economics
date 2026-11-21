"""第 14 章: マンデル・フレミング・モデルのテスト。"""

import pytest

from lib.chapter14.mundell_fleming import (
    PolicyEffect,
    SmallOpenEconomy,
    fixed_rate_devaluation_effect,
    fixed_rate_equilibrium,
    fixed_rate_fiscal_effect,
    fixed_rate_monetary_effect,
    floating_rate_equilibrium,
    floating_rate_fiscal_effect,
    floating_rate_monetary_effect,
    open_economy_residuals,
    policy_effects_table,
)

# c = 0.6、b = 20、IS: (1 − c)Y + b·r = 400 + 50·e、LM: 0.5·Y − 100·r = 250、r* = 2.5
# 為替レート e = 1 で、第 8 章と同じ均衡 Y = 1000、r = 2.5 になる。


def make_economy(**changes: float) -> SmallOpenEconomy:
    base = {
        "mpc": 0.6,
        "b": 20,
        "intercept": 400,
        "n": 50,
        "k": 0.5,
        "h": 100,
        "real_money": 250,
        "world_rate": 2.5,
        "exchange_rate": 1,
    }
    return SmallOpenEconomy(**{**base, **changes})


def test_固定相場の均衡は世界の利子率と一致する() -> None:
    eq = fixed_rate_equilibrium(make_economy())
    assert eq.income == pytest.approx(1000)
    assert eq.interest == pytest.approx(2.5)
    assert eq.exchange_rate == pytest.approx(1)
    assert eq.real_money == pytest.approx(250)


def test_固定相場では為替レートを動かすと所得が動く() -> None:
    eq = fixed_rate_equilibrium(make_economy(exchange_rate=1.2))
    assert eq.income == pytest.approx(1025)
    assert eq.real_money == pytest.approx(0.5 * 1025 - 100 * 2.5)


def test_変動相場の均衡は貨幣供給で所得が決まる() -> None:
    eq = floating_rate_equilibrium(make_economy())
    assert eq.income == pytest.approx(1000)
    assert eq.interest == pytest.approx(2.5)
    assert eq.exchange_rate == pytest.approx(1)
    assert eq.real_money == pytest.approx(250)


def test_変動相場では貨幣供給を変えると所得と為替レートが動く() -> None:
    eq = floating_rate_equilibrium(make_economy(real_money=260))
    assert eq.income == pytest.approx(1020)
    assert eq.exchange_rate == pytest.approx((0.4 * 1020 + 50 - 400) / 50)


def test_均衡はISとLMとBPをすべて満たす() -> None:
    # 固定相場の LM と変動相場の IS の残差は、M/P と e を、その式から逆算するので、作り方から 0 になる。
    # 意味のある照合は、固定相場の IS（Y を決めた式の確認）と、変動相場の LM（Y の式の確認）
    economy = make_economy(exchange_rate=1.1, real_money=240, world_rate=3)
    for eq in (fixed_rate_equilibrium(economy), floating_rate_equilibrium(economy)):
        assert open_economy_residuals(economy, eq) == pytest.approx((0, 0, 0))


def test_均衡でない点は残差が0にならない() -> None:
    economy = make_economy()
    eq = fixed_rate_equilibrium(economy)
    moved = type(eq)(eq.income + 10, eq.interest + 1, eq.exchange_rate, eq.real_money)
    is_res, lm_res, bp_res = open_economy_residuals(economy, moved)
    assert is_res == pytest.approx(0.4 * 10 + 20 * 1)
    assert lm_res == pytest.approx(0.5 * 10 - 100 * 1)
    assert bp_res == pytest.approx(1)


def test_固定相場で財政政策は有効() -> None:
    economy = make_economy()
    assert fixed_rate_fiscal_effect(economy, 10) == pytest.approx(25)


def test_固定相場で金融政策は無効() -> None:
    assert fixed_rate_monetary_effect(make_economy(), 10) == 0


def test_変動相場で財政政策は無効() -> None:
    assert floating_rate_fiscal_effect(make_economy(), 10) == 0


def test_変動相場で金融政策は有効() -> None:
    assert floating_rate_monetary_effect(make_economy(), 10) == pytest.approx(20)


def test_固定相場の切り下げは所得を増やす() -> None:
    assert fixed_rate_devaluation_effect(make_economy(), 0.1) == pytest.approx(12.5)


def test_4通りの効果の表() -> None:
    rows = policy_effects_table(make_economy(), 10, 10)
    assert [(r.regime, r.policy) for r in rows] == [
        ("固定相場", "財政政策"),
        ("固定相場", "金融政策"),
        ("変動相場", "財政政策"),
        ("変動相場", "金融政策"),
    ]
    assert [r.income_change for r in rows] == pytest.approx([25, 0, 0, 20])
    assert [r.exchange_rate_change for r in rows] == pytest.approx([0, 0, -0.2, 0.16])
    assert [r.real_money_change for r in rows] == pytest.approx([12.5, 0, 0, 10])


def test_表の効果は閉じた式と一致する() -> None:
    economy = make_economy()
    rows = policy_effects_table(economy, 10, 10)
    assert rows[0].income_change == pytest.approx(fixed_rate_fiscal_effect(economy, 10))
    assert rows[1].income_change == pytest.approx(
        fixed_rate_monetary_effect(economy, 10)
    )
    assert rows[2].income_change == pytest.approx(
        floating_rate_fiscal_effect(economy, 10)
    )
    assert rows[3].income_change == pytest.approx(
        floating_rate_monetary_effect(economy, 10)
    )


@pytest.mark.parametrize("n", [10, 50, 500])
@pytest.mark.parametrize("c", [0.3, 0.6, 0.9])
def test_どの条件でも符号の組み合わせが変わらない(c: float, n: float) -> None:
    rows = policy_effects_table(make_economy(mpc=c, n=n, intercept=450 - n), 10, 10)
    fixed_fiscal, fixed_money, float_fiscal, float_money = (
        r.income_change for r in rows
    )
    assert fixed_fiscal > 0
    assert fixed_money == pytest.approx(0)
    assert float_fiscal == pytest.approx(0)
    assert float_money > 0


def test_政策の効果は型を持つ() -> None:
    row = policy_effects_table(make_economy(), 10, 10)[0]
    assert isinstance(row, PolicyEffect)


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"mpc": 1}, "限界消費性向"),
        ({"mpc": -0.1}, "限界消費性向"),
        ({"b": -1}, "投資の利子感応度"),
        ({"n": 0}, "為替レートへの純輸出の感応度"),
        ({"n": -1}, "為替レートへの純輸出の感応度"),
        ({"k": 0}, "貨幣需要の所得への感応度"),
        ({"h": 0}, "貨幣需要の利子率への感応度"),
        ({"world_rate": -1}, "世界の利子率"),
        ({"exchange_rate": 0}, "為替レート"),
    ],
)
def test_退化した入力は分かるエラーにする(
    changes: dict[str, float], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        make_economy(**changes)


def test_境界の値は許される() -> None:
    # b = 0（投資が利子率に反応しない）と r* = 0 は、退化ではない
    assert fixed_rate_equilibrium(make_economy(b=0)).income == pytest.approx(1125)
    assert floating_rate_equilibrium(make_economy(world_rate=0)).income == (
        pytest.approx(500)
    )
