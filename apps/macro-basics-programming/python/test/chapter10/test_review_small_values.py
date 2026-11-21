"""全体レビュー（2026-11-21）の指摘: 0 より大きく 1 未満の有効な値と、0 の境界。"""

import pytest

from lib.chapter10.ad_as import keynesian_supply, shift_supply
from lib.chapter10.labor import (
    LaborCurves,
    best_efficiency_wage,
    labor_demand,
    labor_equilibrium,
    real_wage,
)

CURVES = LaborCurves(
    demand_intercept=100, demand_slope=0.5, supply_intercept=10, supply_slope=0.5
)


def test_物価が1未満の正の値でも総供給を求められる() -> None:
    assert keynesian_supply(0.5, 1000, 480, 400) == pytest.approx(680)


def test_総供給の傾きが1未満の正の値でも有効() -> None:
    assert keynesian_supply(1, 1000, 480, 0.5) == pytest.approx(480.5)


def test_動かしたあとの完全雇用所得が1未満の正でも有効() -> None:
    assert shift_supply(1000, 480, -999.5) == (
        pytest.approx(0.5),
        pytest.approx(-519.5),
    )


def test_労働の傾きが1未満の正の値でも有効() -> None:
    wage, employment = labor_equilibrium(CURVES)
    assert wage == pytest.approx(90)
    assert employment == pytest.approx(55)


def test_実質賃金0は許され負はエラー() -> None:
    assert labor_demand(CURVES, 0) == 100
    assert real_wage(0, 1) == 0
    with pytest.raises(ValueError, match="実質賃金"):
        labor_demand(CURVES, -0.1)


def test_賃金の候補が1未満の正の値でも有効() -> None:
    assert best_efficiency_wage([0.5, 0.8], 0.0) in (0.5, 0.8)
