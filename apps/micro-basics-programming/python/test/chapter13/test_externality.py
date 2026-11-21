"""第 13 章: 外部効果（ピグー税・コースの定理・排出権取引）のテスト。"""

import pytest

from lib.chapter13.externality import (
    ExternalityMarket,
    abatement_cost,
    coase_outcome,
    emissions_trading,
    externality_deadweight_loss,
    market_quantity,
    pigou_tax,
    quantity_with_tax,
    socially_optimal_quantity,
    uniform_reduction,
)

# 逆需要 P = 100 − Q、私的限界費用 MC = 10 + Q、外部費用は 1 単位あたり 20
POLLUTION = ExternalityMarket(
    demand_intercept=100,
    demand_slope=1,
    cost_intercept=10,
    cost_slope=1,
    external_cost=20,
)
# 外部便益は、外部費用が負の値（1 単位あたり 10 の便益）
BENEFIT = ExternalityMarket(100, 1, 10, 1, -10)


def test_市場の数量は私的限界費用で決まる() -> None:
    assert market_quantity(POLLUTION) == 45


def test_社会的に最適な数量は外部費用を含めた限界費用で決まる() -> None:
    assert socially_optimal_quantity(POLLUTION) == 35
    assert socially_optimal_quantity(POLLUTION) < market_quantity(POLLUTION)


def test_外部不経済があると市場は作りすぎる() -> None:
    assert market_quantity(POLLUTION) - socially_optimal_quantity(POLLUTION) == 10


def test_ピグー税は外部費用に等しい() -> None:
    assert pigou_tax(POLLUTION) == 20


def test_ピグー税をかけると市場の数量が最適な数量になる() -> None:
    assert quantity_with_tax(
        POLLUTION, pigou_tax(POLLUTION)
    ) == socially_optimal_quantity(POLLUTION)
    assert quantity_with_tax(POLLUTION, 0) == market_quantity(POLLUTION)
    assert quantity_with_tax(POLLUTION, 10) == 40


def test_税が大きすぎると作りすぎの逆になる() -> None:
    assert quantity_with_tax(POLLUTION, 30) < socially_optimal_quantity(POLLUTION)


def test_外部不経済の死荷重は三角形() -> None:
    assert externality_deadweight_loss(POLLUTION) == pytest.approx(0.5 * 20 * 10)


def test_外部経済は補助金で作りすぎの逆を直す() -> None:
    assert socially_optimal_quantity(BENEFIT) == 50
    assert market_quantity(BENEFIT) == 45
    assert pigou_tax(BENEFIT) == -10
    assert quantity_with_tax(BENEFIT, pigou_tax(BENEFIT)) == 50
    assert externality_deadweight_loss(BENEFIT) == pytest.approx(0.5 * 10 * 5)


def test_外部費用が0なら市場は効率的() -> None:
    clean = ExternalityMarket(100, 1, 10, 1, 0)
    assert socially_optimal_quantity(clean) == market_quantity(clean)
    assert externality_deadweight_loss(clean) == 0


def test_傾きが違う市場の最適な数量() -> None:
    market = ExternalityMarket(100, 2, 10, 1, 30)
    assert market_quantity(market) == pytest.approx(30)
    assert socially_optimal_quantity(market) == pytest.approx(20)
    assert externality_deadweight_loss(market) == pytest.approx(0.5 * 30 * 10)


def test_需要が小さすぎる市場はエラー() -> None:
    with pytest.raises(ValueError, match="最適な数量"):
        socially_optimal_quantity(ExternalityMarket(100, 1, 10, 1, 95))
    with pytest.raises(ValueError, match="需要の切片"):
        ExternalityMarket(10, 1, 10, 1, 0)


def test_傾きは正でなければエラー() -> None:
    with pytest.raises(ValueError, match="傾き"):
        ExternalityMarket(100, 0, 10, 1, 0)
    with pytest.raises(ValueError, match="傾き"):
        ExternalityMarket(100, 1, 10, 0, 0)


def test_税の後の数量は正でなければエラー() -> None:
    with pytest.raises(ValueError, match="税"):
        quantity_with_tax(POLLUTION, 100)


def test_コースの定理_被害者に権利があっても加害者に権利があっても効率的() -> None:
    # 汚染から得る利益 100、被害 60。汚染が効率的
    victim = coase_outcome(gain=100, damage=60, victim_has_right=True)
    polluter = coase_outcome(gain=100, damage=60, victim_has_right=False)
    assert victim.pollution and polluter.pollution
    assert victim.payment_range == (60, 100)
    assert polluter.payment_range is None


def test_コースの定理_被害が利益より大きいなら汚染しない() -> None:
    victim = coase_outcome(gain=40, damage=60, victim_has_right=True)
    polluter = coase_outcome(gain=40, damage=60, victim_has_right=False)
    assert not victim.pollution and not polluter.pollution
    assert victim.payment_range is None
    assert polluter.payment_range == (40, 60)


def test_コースの定理_利益と被害が等しいときは汚染しない() -> None:
    assert not coase_outcome(50, 50, True).pollution
    assert not coase_outcome(50, 50, False).pollution


def test_排出権取引は限界削減費用を等しくする() -> None:
    price, reductions = emissions_trading([1, 2, 4], 14)
    assert price == pytest.approx(8)
    assert reductions == pytest.approx([8, 4, 2])
    assert sum(reductions) == pytest.approx(14)
    for slope, reduction in zip([1, 2, 4], reductions, strict=True):
        assert slope * reduction == pytest.approx(price)


def test_排出権取引は一律規制より費用が小さい() -> None:
    slopes = [1, 2, 4]
    _, trading = emissions_trading(slopes, 14)
    assert abatement_cost(slopes, trading) == pytest.approx(56)
    uniform = uniform_reduction(slopes, 14)
    assert uniform == pytest.approx([14 / 3] * 3)
    assert abatement_cost(slopes, uniform) > abatement_cost(slopes, trading)


def test_企業の費用が同じなら取引しても一律でも同じ() -> None:
    _, trading = emissions_trading([2, 2], 10)
    assert trading == pytest.approx(uniform_reduction([2, 2], 10))


def test_排出権取引の入力のチェック() -> None:
    with pytest.raises(ValueError, match="傾き"):
        emissions_trading([1, 0], 10)
    with pytest.raises(ValueError, match="企業"):
        emissions_trading([], 10)
    with pytest.raises(ValueError, match="削減"):
        emissions_trading([1, 2], -1)
    with pytest.raises(ValueError, match="企業"):
        uniform_reduction([], 10)
