import pytest

from lib.chapter04.sequence import (
    affine_fixed_point,
    annuity_present_value,
    coupon_bond_price,
    geometric_partial_sum,
    geometric_series_limit,
    geometric_term,
    gordon_stock_price,
    iterate_map,
    partial_sums,
    perpetuity_present_value,
    savings_future_value,
    terms_until_within,
)


def test_等比数列の第n項は初項に公比をnマイナス1回掛ける() -> None:
    assert [geometric_term(3, 2, n) for n in (1, 2, 3, 4)] == [3, 6, 12, 24]


def test_初項1公比2分の1の10項の和() -> None:
    assert geometric_partial_sum(1, 0.5, 10) == 1.998046875


def test_部分和の公式は項を順に足した値と一致する() -> None:
    for first, ratio, n in [(1, 0.5, 10), (3, 2, 5), (5, 1 / 1.04, 3), (2, -0.5, 7)]:
        added = sum(geometric_term(first, ratio, k) for k in range(1, n + 1))
        assert geometric_partial_sum(first, ratio, n) == pytest.approx(added)


def test_公比1の部分和は初項のn倍() -> None:
    assert geometric_partial_sum(4, 1, 6) == 24


def test_初項1公比2分の1の無限級数は2() -> None:
    assert geometric_series_limit(1, 0.5) == 2


@pytest.mark.parametrize("ratio", [1, -1, 1.5, -2])
def test_公比の絶対値が1以上なら無限級数は収束しない(ratio: float) -> None:
    with pytest.raises(ValueError):
        geometric_series_limit(1, ratio)


def test_部分和は無限級数に近づいていく() -> None:
    limit = geometric_series_limit(1, 0.5)
    sums = partial_sums(1, 0.5, 30)
    gaps = [abs(limit - s) for s in sums]
    assert all(g1 > g2 for g1, g2 in zip(gaps, gaps[1:], strict=False))
    assert gaps[-1] < 1e-8


def test_無限級数との差が許容誤差より小さくなるまでの項数() -> None:
    # 初項 1・公比 0.5 の差は 2 × 0.5^n。0.01 より小さくなるのは n = 8（0.0078125）
    assert terms_until_within(1, 0.5, 0.01) == 8
    assert terms_until_within(1, 0.5, 0.001) == 11


def test_公比が0に近いほど少ない項数で近づく() -> None:
    assert terms_until_within(1, 0.1, 0.001) < terms_until_within(1, 0.9, 0.001)


def test_毎期1を3期受け取る年金の利子率5パーセントでの現在価値() -> None:
    expected = 1 / 1.05 + 1 / 1.05**2 + 1 / 1.05**3
    assert annuity_present_value(1, 0.05, 3) == pytest.approx(expected)


def test_年金の現在価値は等比数列の部分和() -> None:
    discount = 1 / 1.04
    for n in (1, 2, 10):
        assert annuity_present_value(5, 0.04, n) == pytest.approx(
            geometric_partial_sum(5 * discount, discount, n)
        )


def test_毎年5の永久債_利子率5パーセントで100() -> None:
    assert perpetuity_present_value(5, 0.05) == pytest.approx(100)


def test_年金の期間を延ばすと永久債の価値に近づく() -> None:
    perpetuity = perpetuity_present_value(5, 0.05)
    values = [annuity_present_value(5, 0.05, n) for n in (10, 50, 200, 1000)]
    assert all(v1 < v2 < perpetuity for v1, v2 in zip(values, values[1:], strict=False))
    assert values[-1] == pytest.approx(perpetuity)


@pytest.mark.parametrize("rate", [0, -0.01])
def test_利子率が正でなければ永久債の価値は決まらない(rate: float) -> None:
    with pytest.raises(ValueError):
        perpetuity_present_value(5, rate)


def test_毎年10を3パーセントで5年積み立てた将来価値() -> None:
    expected = sum(10 * 1.03**k for k in range(5))
    assert savings_future_value(10, 0.03, 5) == pytest.approx(expected)
    assert savings_future_value(10, 0.03, 5) == pytest.approx(53.0913581)


def test_額面100_クーポン5_利子率4パーセント_3年の利付債() -> None:
    expected = 5 / 1.04 + 5 / 1.04**2 + 105 / 1.04**3
    assert coupon_bond_price(100, 5, 0.04, 3) == pytest.approx(expected)
    assert coupon_bond_price(100, 5, 0.04, 3) == pytest.approx(102.775091)


def test_クーポンの利回りと利子率が等しければ価格は額面() -> None:
    for rate, years in [(0.05, 3), (0.02, 10), (0.08, 1)]:
        assert coupon_bond_price(100, 100 * rate, rate, years) == pytest.approx(100)


def test_利子率が上がると債券の価格は下がる() -> None:
    prices = [coupon_bond_price(100, 5, r, 10) for r in (0.01, 0.03, 0.05, 0.07)]
    assert all(p1 > p2 for p1, p2 in zip(prices, prices[1:], strict=False))


def test_漸化式を反復すると初期値から順に値が並ぶ() -> None:
    assert iterate_map(0.5, 10, 0, 3) == [0, 10, 15, 17.5]


def test_xの次は0点5x足す10の不動点は20() -> None:
    point = affine_fixed_point(0.5, 10)
    assert point == 20
    assert 0.5 * point + 10 == point


def test_傾きの絶対値が1より小さければ反復は不動点に近づく() -> None:
    for a, b, start in [(0.5, 10, 0), (0.5, 10, 100), (-0.5, 30, 0), (0.9, 2, 50)]:
        path = iterate_map(a, b, start, 300)
        assert path[-1] == pytest.approx(affine_fixed_point(a, b))


def test_傾きの絶対値が1より大きければ反復は不動点から離れる() -> None:
    path = iterate_map(2, -10, 11, 5)
    gaps = [abs(x - affine_fixed_point(2, -10)) for x in path]
    assert gaps == [1, 2, 4, 8, 16, 32]


def test_傾きが1なら不動点はない() -> None:
    with pytest.raises(ValueError):
        affine_fixed_point(1, 10)


def test_配当2_利子率7パーセント_成長率2パーセントで株価40() -> None:
    assert gordon_stock_price(2, 0.07, 0.02) == pytest.approx(40)


def test_配当割引モデルは成長する配当の割引現在価値の無限級数() -> None:
    for dividend, rate, growth in [(2, 0.07, 0.02), (3, 0.1, -0.05), (1, 0.04, 0)]:
        series = geometric_series_limit(
            dividend / (1 + rate), (1 + growth) / (1 + rate)
        )
        assert gordon_stock_price(dividend, rate, growth) == pytest.approx(series)


@pytest.mark.parametrize("growth", [0.07, 0.1])
def test_成長率が利子率以上なら株価は決まらない(growth: float) -> None:
    with pytest.raises(ValueError):
        gordon_stock_price(2, 0.07, growth)


def test_0項の和は0で1項の和は初項() -> None:
    assert geometric_partial_sum(3, 0.2, 0) == 0
    assert geometric_partial_sum(3, 0.2, 1) == pytest.approx(3)
    assert geometric_partial_sum(3, 0.2, 2) == pytest.approx(3.6)


def test_項数が負なら和は決まらない() -> None:
    with pytest.raises(ValueError):
        geometric_partial_sum(1, 0.5, -1)


def test_公比が負なら部分和は無限級数の上下を行き来する() -> None:
    limit = geometric_series_limit(1, -0.5)
    assert limit == pytest.approx(2 / 3)
    sums = partial_sums(1, -0.5, 6)
    assert [s > limit for s in sums] == [True, False, True, False, True, False]


def test_公比0と初項が負の無限級数() -> None:
    assert geometric_series_limit(7, 0) == 7
    assert geometric_series_limit(-3, 0.25) == -4


def test_許容誤差が差より大きければ1項で足りる() -> None:
    assert terms_until_within(1, 0.5, 1.5) == 1


@pytest.mark.parametrize("tolerance", [0, -0.1])
def test_許容誤差が正でなければ項数は決まらない(tolerance: float) -> None:
    with pytest.raises(ValueError):
        terms_until_within(1, 0.5, tolerance)


def test_利子率0の年金と積立は単純な合計() -> None:
    assert annuity_present_value(5, 0, 4) == 20
    assert savings_future_value(5, 0, 4) == 20


def test_0期の年金と積立は0で1期の積立は1回分() -> None:
    assert annuity_present_value(5, 0.05, 0) == 0
    assert savings_future_value(5, 0.05, 0) == 0
    assert savings_future_value(5, 0.05, 1) == 5


def test_利子率が負でも年金の現在価値は受け取る合計より大きい() -> None:
    assert annuity_present_value(10, -0.5, 2) == pytest.approx(20 + 40)


@pytest.mark.parametrize("rate", [-1, -1.5])
def test_利子率がマイナス100パーセント以下なら割引できない(rate: float) -> None:
    with pytest.raises(ValueError):
        annuity_present_value(5, rate, 3)


def test_満期0年の利付債は額面で1年なら額面とクーポンの割引() -> None:
    assert coupon_bond_price(100, 5, 0.04, 0) == 100
    assert coupon_bond_price(100, 5, 0.25, 1) == pytest.approx(105 / 1.25)


def test_小さい利子率の永久債と大きい額() -> None:
    assert perpetuity_present_value(0.3, 0.5) == pytest.approx(0.6)
    assert perpetuity_present_value(2, 0.001) == pytest.approx(2000)


def test_反復0回は初期値だけ() -> None:
    assert iterate_map(0.5, 10, 7, 0) == [7]


def test_傾き0と負の傾きの不動点() -> None:
    assert affine_fixed_point(0, 4) == 4
    assert affine_fixed_point(-1, 6) == 3
    assert iterate_map(-1, 6, 1, 4) == [1, 5, 1, 5, 1]


def test_成長率がわずかに利子率より小さいと株価は大きい() -> None:
    assert gordon_stock_price(1, 0.05, 0.04) == pytest.approx(100)
    assert gordon_stock_price(3, 0.5, 0.25) == pytest.approx(12)


def test_差が許容誤差とちょうど等しければもう1項足す() -> None:
    # 7 項までの差は 2 × 0.5^7 = 0.015625（等しいので「小さい」ではない）
    assert terms_until_within(1, 0.5, 0.015625) == 8
