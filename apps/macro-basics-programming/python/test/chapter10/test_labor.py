"""第 10 章: 労働市場のテスト。"""

import pytest

from lib.chapter10.labor import (
    LaborCurves,
    best_efficiency_wage,
    effort_level,
    involuntary_unemployment,
    labor_demand,
    labor_equilibrium,
    labor_supply,
    real_wage,
)

# 労働需要 Ld = 100 − 10w、労働供給 Ls = 20 + 10w
CURVES = LaborCurves(
    demand_intercept=100, demand_slope=10, supply_intercept=20, supply_slope=10
)


def test_労働需要は実質賃金の減少関数() -> None:
    assert labor_demand(CURVES, 4) == pytest.approx(60)
    assert labor_demand(CURVES, 6) == pytest.approx(40)
    assert labor_demand(CURVES, 6) < labor_demand(CURVES, 4)


def test_労働供給は実質賃金の増加関数() -> None:
    assert labor_supply(CURVES, 4) == pytest.approx(60)
    assert labor_supply(CURVES, 6) == pytest.approx(80)
    assert labor_supply(CURVES, 6) > labor_supply(CURVES, 4)


def test_均衡では実質賃金4で雇用60() -> None:
    wage, employment = labor_equilibrium(CURVES)
    assert wage == pytest.approx(4)
    assert employment == pytest.approx(60)
    assert labor_demand(CURVES, wage) == pytest.approx(labor_supply(CURVES, wage))


def test_均衡より高い賃金では非自発的失業が生まれる() -> None:
    assert involuntary_unemployment(CURVES, 6) == pytest.approx(40)


def test_均衡の賃金では非自発的失業はない() -> None:
    assert involuntary_unemployment(CURVES, 4) == pytest.approx(0)


def test_均衡より低い賃金は超過需要で失業ではない() -> None:
    assert labor_demand(CURVES, 3) > labor_supply(CURVES, 3)
    assert involuntary_unemployment(CURVES, 3) == 0


def test_実質賃金は名目賃金を物価で割った値() -> None:
    assert real_wage(4, 1) == pytest.approx(4)
    assert real_wage(4, 0.5) == pytest.approx(8)


def test_名目賃金が硬直的だと物価の下落が失業を生む() -> None:
    nominal_wage = 4
    assert involuntary_unemployment(CURVES, real_wage(nominal_wage, 1)) == 0
    unemployment = involuntary_unemployment(CURVES, real_wage(nominal_wage, 0.5))
    assert unemployment == pytest.approx(80)


def test_物価が0以下ならエラー() -> None:
    with pytest.raises(ValueError, match="物価"):
        real_wage(4, 0)


def test_負の名目賃金はエラー() -> None:
    with pytest.raises(ValueError, match="名目賃金"):
        real_wage(-1, 1)


def test_労働需要の傾きが0以下ならエラー() -> None:
    with pytest.raises(ValueError, match="需要"):
        labor_equilibrium(LaborCurves(100, 0, 20, 10))


def test_労働供給の傾きが0以下ならエラー() -> None:
    with pytest.raises(ValueError, match="供給"):
        labor_equilibrium(LaborCurves(100, 10, 20, 0))


def test_均衡の賃金が負になる設定はエラー() -> None:
    with pytest.raises(ValueError, match="負"):
        labor_equilibrium(LaborCurves(10, 10, 20, 10))


def test_負の賃金で需要を求めるとエラー() -> None:
    with pytest.raises(ValueError, match="実質賃金"):
        labor_demand(CURVES, -1)


def test_努力水準は生存水準を超えた賃金の平方根() -> None:
    assert effort_level(8, 4) == pytest.approx(2)
    assert effort_level(13, 4) == pytest.approx(3)


def test_生存水準以下の賃金では努力は0() -> None:
    assert effort_level(3, 4) == 0
    assert effort_level(4, 4) == 0


def test_賃金あたりの効率を最大にする賃金は8() -> None:
    wages = [5, 6, 7, 8, 9, 10, 12]
    assert best_efficiency_wage(wages, 4) == 8


def test_効率賃金は市場の均衡賃金より高く失業が残る() -> None:
    wage = best_efficiency_wage([5, 6, 7, 8, 9, 10, 12], 4)
    assert wage > labor_equilibrium(CURVES)[0]
    assert involuntary_unemployment(CURVES, wage) == pytest.approx(80)


def test_賃金の候補が空ならエラー() -> None:
    with pytest.raises(ValueError, match="候補"):
        best_efficiency_wage([], 4)


def test_賃金の候補に0以下があればエラー() -> None:
    with pytest.raises(ValueError, match="正"):
        best_efficiency_wage([0, 5], 4)
