"""第 4 章: 45 度線分析と乗数のテスト。"""

import pytest

from lib.chapter04.multiplier import (
    aggregate_demand,
    balanced_budget_multiplier,
    consumption,
    equilibrium_income,
    income_change,
    saving,
    spending_multiplier,
    tax_multiplier,
)

# 限界消費性向 0.6、独立消費 40、投資 30、政府支出 30、純輸出 0（独立支出 A = 100）
BASE = {
    "mpc": 0.6,
    "autonomous_consumption": 40,
    "investment": 30,
    "government": 30,
    "net_exports": 0,
}


def test_消費は限界消費性向と所得の積に独立消費を足した値() -> None:
    assert consumption(100, mpc=0.6, autonomous_consumption=40) == pytest.approx(100)


def test_課税で消費関数はc掛けるTだけ下へ動く() -> None:
    before = consumption(250, mpc=0.6, autonomous_consumption=40)
    after = consumption(250, mpc=0.6, autonomous_consumption=40, tax=50)
    assert before - after == pytest.approx(0.6 * 50)


def test_貯蓄は可処分所得から消費を引いた値() -> None:
    assert saving(100, mpc=0.6, autonomous_consumption=40) == pytest.approx(0)
    assert saving(250, mpc=0.6, autonomous_consumption=40) == pytest.approx(60)


def test_貯蓄関数は1引くcの傾きと負の切片() -> None:
    assert saving(0, mpc=0.6, autonomous_consumption=40) == pytest.approx(-40)
    slope = saving(11, 0.6, 40) - saving(10, 0.6, 40)
    assert slope == pytest.approx(0.4)


def test_総需要は消費と投資と政府支出と純輸出の和() -> None:
    demand = aggregate_demand(100, **BASE)
    assert demand == pytest.approx(100 + 30 + 30 + 0)


def test_純輸出が増えると総需要は同額だけ増える() -> None:
    base = aggregate_demand(100, **BASE)
    exports = aggregate_demand(100, **{**BASE, "net_exports": 10})
    assert exports - base == pytest.approx(10)


def test_均衡国民所得は独立支出を1引くcで割った値() -> None:
    assert equilibrium_income(**BASE) == pytest.approx(250)


def test_均衡では総需要が総供給に等しい() -> None:
    y = equilibrium_income(**BASE)
    assert aggregate_demand(y, **BASE) == pytest.approx(y)


def test_均衡より所得が低いと総需要が大きく高いと小さい() -> None:
    y = equilibrium_income(**BASE)
    assert aggregate_demand(y - 10, **BASE) > y - 10
    assert aggregate_demand(y + 10, **BASE) < y + 10


def test_均衡では貯蓄が投資と政府赤字と純輸出の和に等しい() -> None:
    kwargs = {**BASE, "net_exports": 10, "tax": 20}
    y = equilibrium_income(**kwargs)
    s = saving(y, 0.6, 40, tax=20)
    assert s == pytest.approx(30 + (30 - 20) + 10)


def test_閉鎖経済で政府がなければ貯蓄は投資に等しい() -> None:
    kwargs = {**BASE, "government": 0, "net_exports": 0}
    y = equilibrium_income(**kwargs)
    assert saving(y, 0.6, 40) == pytest.approx(30)


def test_定額税は均衡所得を下げる() -> None:
    assert equilibrium_income(**BASE, tax=0) == pytest.approx(250)
    assert equilibrium_income(**BASE, tax=10) == pytest.approx(235)


def test_政府支出乗数は1を1引くcで割った値() -> None:
    assert spending_multiplier(0.6) == pytest.approx(2.5)
    assert spending_multiplier(0.8) == pytest.approx(5)


def test_租税乗数は負でcを1引くcで割った大きさ() -> None:
    assert tax_multiplier(0.6) == pytest.approx(-1.5)
    assert tax_multiplier(0.8) == pytest.approx(-4)


def test_均衡予算乗数は常に1() -> None:
    for mpc in (0.0, 0.3, 0.6, 0.8, 0.95):
        total = spending_multiplier(mpc) + tax_multiplier(mpc)
        assert total == pytest.approx(1)
        assert balanced_budget_multiplier(mpc) == pytest.approx(1)


def test_政府支出を増やすと所得は乗数倍に増える() -> None:
    assert income_change(0.6, delta_government=10) == pytest.approx(25)


def test_減税は所得を増やし増税は減らす() -> None:
    assert income_change(0.6, delta_tax=-10) == pytest.approx(15)
    assert income_change(0.6, delta_tax=10) == pytest.approx(-15)


def test_減税より公共投資が効く() -> None:
    spending = income_change(0.6, delta_government=10)
    tax_cut = income_change(0.6, delta_tax=-10)
    assert spending > tax_cut


def test_同額の政府支出と増税で所得は同額だけ増える() -> None:
    assert income_change(0.6, delta_government=10, delta_tax=10) == pytest.approx(10)


def test_変化は均衡所得の差と一致する() -> None:
    before = equilibrium_income(**BASE)
    after = equilibrium_income(**{**BASE, "government": 40}, tax=5)
    assert after - before == pytest.approx(income_change(0.6, 10, 5))


def test_限界消費性向が1以上はエラー() -> None:
    with pytest.raises(ValueError, match="1 未満"):
        spending_multiplier(1.0)
    with pytest.raises(ValueError, match="1 未満"):
        equilibrium_income(**{**BASE, "mpc": 1.2})


def test_限界消費性向が負はエラー() -> None:
    with pytest.raises(ValueError, match="0 以上"):
        tax_multiplier(-0.1)


def test_限界消費性向が0なら乗数は1() -> None:
    assert spending_multiplier(0.0) == pytest.approx(1)
    assert tax_multiplier(0.0) == pytest.approx(0)
