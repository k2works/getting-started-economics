"""第 9 章: 余剰分析と課税のテスト。"""

import pytest

from lib.chapter08.market import LinearMarket, equilibrium
from lib.chapter09.surplus import (
    choke_price,
    consumer_surplus,
    deadweight_loss_at_quantity,
    producer_surplus,
    reservation_price,
    tax_equilibrium,
    tax_incidence,
    total_surplus_at_quantity,
)

# 需要 Q = 100 − P、供給 Q = P − 10。均衡は P = 55、Q = 45
MARKET = LinearMarket(100, -1, -10, 1)
# 同じ均衡 (55, 45) で、需要が急な市場（需要の価格弾力性が小さい）と、供給が急な市場
STEEP_DEMAND = LinearMarket(72.5, -0.5, -10, 1)
STEEP_SUPPLY = LinearMarket(100, -1, 17.5, 0.5)


def test_需要がなくなる価格と供給が始まる価格() -> None:
    assert choke_price(MARKET) == 100
    assert reservation_price(MARKET) == 10


def test_消費者余剰は需要曲線と価格の間の三角形() -> None:
    assert consumer_surplus(MARKET, 55) == 1012.5
    assert consumer_surplus(MARKET, 30) == pytest.approx(0.5 * 70 * 70)


def test_価格が高いと消費者余剰は小さい() -> None:
    assert consumer_surplus(MARKET, 70) < consumer_surplus(MARKET, 55)
    assert consumer_surplus(MARKET, 100) == 0
    assert consumer_surplus(MARKET, 120) == 0


def test_生産者余剰は価格と供給曲線の間の三角形() -> None:
    assert producer_surplus(MARKET, 55) == 1012.5
    assert producer_surplus(MARKET, 70) == pytest.approx(0.5 * 60 * 60)


def test_価格が低いと生産者余剰は小さい() -> None:
    assert producer_surplus(MARKET, 40) < producer_surplus(MARKET, 55)
    assert producer_surplus(MARKET, 10) == 0
    assert producer_surplus(MARKET, 5) == 0


def test_総余剰は消費者余剰と生産者余剰の和() -> None:
    price, quantity = equilibrium(MARKET)
    total = consumer_surplus(MARKET, price) + producer_surplus(MARKET, price)
    assert total == 2025
    assert total_surplus_at_quantity(MARKET, quantity) == pytest.approx(total)


def test_傾きが違う市場でも総余剰は均衡で一致する() -> None:
    for market in (STEEP_DEMAND, STEEP_SUPPLY):
        price, quantity = equilibrium(market)
        total = consumer_surplus(market, price) + producer_surplus(market, price)
        assert total_surplus_at_quantity(market, quantity) == pytest.approx(total)


def test_総余剰は均衡の数量で最大() -> None:
    best = total_surplus_at_quantity(MARKET, 45)
    for q in (0, 10, 30, 44, 46, 60, 90):
        assert total_surplus_at_quantity(MARKET, q) < best


def test_均衡より少なくても多くても三角形の損失が出る() -> None:
    assert deadweight_loss_at_quantity(MARKET, 30) == pytest.approx(225)
    assert deadweight_loss_at_quantity(MARKET, 60) == pytest.approx(225)
    assert deadweight_loss_at_quantity(MARKET, 45) == pytest.approx(0, abs=1e-9)


def test_数量が負または需要の範囲外ならエラー() -> None:
    with pytest.raises(ValueError, match="数量"):
        total_surplus_at_quantity(MARKET, -1)
    with pytest.raises(ValueError, match="数量"):
        total_surplus_at_quantity(MARKET, 101)


def test_数量0の総余剰は0() -> None:
    assert total_surplus_at_quantity(MARKET, 0) == 0


def test_従量税のもとの価格と数量() -> None:
    result = tax_equilibrium(MARKET, 9)
    assert result.buyer_price == pytest.approx(59.5)
    assert result.seller_price == pytest.approx(50.5)
    assert result.quantity == pytest.approx(40.5)


def test_買い手の価格と売り手の手取りの差は税額() -> None:
    result = tax_equilibrium(MARKET, 9)
    assert result.buyer_price - result.seller_price == pytest.approx(9)


def test_税収は税額かける数量() -> None:
    assert tax_equilibrium(MARKET, 9).tax_revenue == pytest.approx(364.5)


def test_死荷重は三角形の面積() -> None:
    result = tax_equilibrium(MARKET, 9)
    assert result.deadweight_loss == pytest.approx(20.25)
    assert result.deadweight_loss == pytest.approx(0.5 * 9 * (45 - 40.5))


def test_課税後の消費者余剰と生産者余剰() -> None:
    result = tax_equilibrium(MARKET, 9)
    assert result.consumer_surplus == pytest.approx(820.125)
    assert result.producer_surplus == pytest.approx(820.125)


def test_総余剰は消費者余剰と生産者余剰と税収の和で死荷重だけ減る() -> None:
    result = tax_equilibrium(MARKET, 9)
    total = result.consumer_surplus + result.producer_surplus + result.tax_revenue
    assert total == pytest.approx(2025 - result.deadweight_loss)


def test_課税なしなら均衡と同じで死荷重は0() -> None:
    result = tax_equilibrium(MARKET, 0)
    assert (result.buyer_price, result.seller_price, result.quantity) == (55, 55, 45)
    assert result.tax_revenue == 0
    assert result.deadweight_loss == 0


def test_税額が負ならエラー() -> None:
    with pytest.raises(ValueError, match="税額"):
        tax_equilibrium(MARKET, -1)


def test_税が大きすぎて取引がなくなればエラー() -> None:
    with pytest.raises(ValueError, match="取引"):
        tax_equilibrium(MARKET, 90)


def test_税額が1未満の正の値でも求められる() -> None:
    result = tax_equilibrium(MARKET, 0.5)
    assert result.deadweight_loss == pytest.approx(0.5 * 0.5 * 0.25)


def test_需要が急な財ほど死荷重が小さい() -> None:
    steep = tax_equilibrium(STEEP_DEMAND, 9)
    assert steep.buyer_price == pytest.approx(61)
    assert steep.seller_price == pytest.approx(52)
    assert steep.quantity == pytest.approx(42)
    assert steep.deadweight_loss == pytest.approx(13.5)
    assert steep.deadweight_loss < tax_equilibrium(MARKET, 9).deadweight_loss


def test_供給が急でも死荷重は小さい() -> None:
    steep = tax_equilibrium(STEEP_SUPPLY, 9)
    assert steep.quantity == pytest.approx(42)
    assert steep.deadweight_loss == pytest.approx(13.5)


def test_税の負担は弾力性の小さい側が多く負担する() -> None:
    assert tax_incidence(MARKET, 9) == pytest.approx((4.5, 4.5))
    assert tax_incidence(STEEP_DEMAND, 9) == pytest.approx((6, 3))
    assert tax_incidence(STEEP_SUPPLY, 9) == pytest.approx((3, 6))


def test_税の負担の和は税額() -> None:
    for market in (MARKET, STEEP_DEMAND, STEEP_SUPPLY):
        buyer, seller = tax_incidence(market, 9)
        assert buyer + seller == pytest.approx(9)


# --- 独立した変異確認で見つかった穴を埋めるテスト ---


def test_数量が需要の切片に等しくても総余剰を求められる() -> None:
    assert total_surplus_at_quantity(MARKET, 100) == pytest.approx(90 * 100 - 100**2)


def test_取引がほとんどなくなる大きな税でも数量が正なら求められる() -> None:
    result = tax_equilibrium(MARKET, 89)
    assert result.quantity == pytest.approx(0.5)
    assert result.buyer_price == pytest.approx(99.5)
    with pytest.raises(ValueError, match="取引"):
        tax_equilibrium(MARKET, 90)
