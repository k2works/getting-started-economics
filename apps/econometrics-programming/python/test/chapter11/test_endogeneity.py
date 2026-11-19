"""第 11 章: 欠落変数・測定誤差・同時方程式のバイアスのテスト。"""

import numpy as np
import pytest

from lib.chapter02.simple import fit_simple
from lib.chapter11.endogeneity import (
    attenuation_factor,
    draw_market,
    draw_measurement_error,
    draw_omitted,
    ovb_decomposition,
    simulate_measurement_error,
    simulate_omitted,
    simulate_simultaneity,
    simultaneity_slope,
)

# x1 と x2 が正の相関を持ち、y = 1 + 2·x1 + 3·x2（誤差なし）
X1 = [1.0, 2.0, 3.0, 4.0, 5.0]
X2 = [2.0, 1.0, 4.0, 3.0, 6.0]
Y = [1 + 2 * a + 3 * b for a, b in zip(X1, X2, strict=True)]


def test_ちょうどの関係では長い回帰が真の係数を復元する() -> None:
    d = ovb_decomposition(Y, X1, X2)
    assert d.long == pytest.approx(2)
    assert d.beta2 == pytest.approx(3)


def test_手計算の補助回帰の傾き() -> None:
    d = ovb_decomposition(Y, X1, X2)
    assert d.delta == pytest.approx(fit_simple(X1, X2).slope)
    assert d.delta == pytest.approx(1.0)


def test_短い回帰の傾きは長い回帰の傾きにバイアスを足したものにちょうど等しい() -> None:
    d = ovb_decomposition(Y, X1, X2)
    assert d.short == pytest.approx(d.long + d.beta2 * d.delta)
    assert d.short == pytest.approx(2 + 3 * 1.0)


def test_恒等式は乱数の標本でも成り立つ() -> None:
    y, x1, x2 = draw_omitted(50, 0.5, np.random.default_rng(0))
    d = ovb_decomposition(y, x1, x2)
    assert d.short == pytest.approx(d.long + d.beta2 * d.delta, abs=1e-10)


def test_バイアスの符号は欠落変数の係数と相関の符号の積() -> None:
    for correlation in (0.6, -0.6):
        y, x1, x2 = draw_omitted(5000, correlation, np.random.default_rng(1))
        d = ovb_decomposition(y, x1, x2)
        assert np.sign(d.short - d.long) == np.sign(d.beta2 * correlation)


def test_標本の形と相関() -> None:
    y, x1, x2 = draw_omitted(20000, 0.5, np.random.default_rng(0))
    assert y.shape == x1.shape == x2.shape == (20000,)
    assert np.corrcoef(x1, x2)[0, 1] == pytest.approx(0.5, abs=0.02)
    assert np.var(x2) == pytest.approx(1, rel=0.05)


def test_x2を落とした回帰は平均して1プラス2ρに近く入れた回帰は真の値() -> None:
    table = simulate_omitted(200, 0.5, 1000, np.random.default_rng(0))
    se = table.std() / 1000**0.5
    assert list(table.columns) == ["short", "long"]
    assert abs(table["short"].mean() - 2.0) < 4 * se["short"]
    assert abs(table["long"].mean() - 1.0) < 4 * se["long"]


def test_相関がなければ欠落変数バイアスはない() -> None:
    table = simulate_omitted(200, 0.0, 1000, np.random.default_rng(0))
    se = table.std() / 1000**0.5
    assert abs(table["short"].mean() - 1.0) < 4 * se["short"]


def test_標本を増やしても短い回帰のバイアスは消えない() -> None:
    small = simulate_omitted(50, 0.5, 500, np.random.default_rng(0))["short"]
    large = simulate_omitted(2000, 0.5, 500, np.random.default_rng(0))["short"]
    assert large.mean() == pytest.approx(2.0, abs=0.02)
    assert large.std() < small.std() / 3
    assert abs(large.mean() - 1.0) > 0.9


def test_減衰係数() -> None:
    assert attenuation_factor(1, 1) == pytest.approx(0.5)
    assert attenuation_factor(1, 0.25) == pytest.approx(0.8)
    assert attenuation_factor(1, 0) == 1


def test_測定誤差のある標本の形() -> None:
    y, x = draw_measurement_error(20000, 1.0, np.random.default_rng(0))
    assert np.var(x) == pytest.approx(2, rel=0.05)
    assert np.var(y) == pytest.approx(2, rel=0.05)


def test_測定誤差があると傾きは0の方向に減衰する() -> None:
    for error_sd in (0.5, 1.0):
        slopes = simulate_measurement_error(
            500, error_sd, 1000, np.random.default_rng(0)
        )
        expected = attenuation_factor(1, error_sd**2)
        assert slopes.mean() == pytest.approx(
            expected, abs=4 * slopes.std() / 1000**0.5
        )


def test_誤差がなければ減衰しない() -> None:
    slopes = simulate_measurement_error(500, 0.0, 500, np.random.default_rng(0))
    assert slopes.mean() == pytest.approx(1, abs=4 * slopes.std() / 500**0.5)


def test_標本を増やしても減衰は消えない() -> None:
    slopes = simulate_measurement_error(5000, 1.0, 300, np.random.default_rng(0))
    assert slopes.mean() == pytest.approx(0.5, abs=0.02)


def test_市場の標本の式() -> None:
    market = draw_market(10, 0.0, 0.0, np.random.default_rng(0))
    assert market["p"].tolist() == [5] * 10
    assert market["q"].tolist() == [5] * 10


def test_均衡の価格と数量は需要と供給の両方の式を満たす() -> None:
    market = draw_market(100, 1.0, 1.0, np.random.default_rng(0))
    demand_shock = market["q"] - (10 - market["p"])
    supply_shock = market["q"] - market["p"]
    assert demand_shock.std() == pytest.approx(1, rel=0.3)
    assert supply_shock.std() == pytest.approx(1, rel=0.3)


def test_大標本での傾き() -> None:
    assert simultaneity_slope(1, 1) == 0
    assert simultaneity_slope(2, 1) == pytest.approx(0.6)
    assert simultaneity_slope(1, 2) == pytest.approx(-0.6)


def test_同時性があるとOLSの傾きは需要の傾きにも供給の傾きにも近づかない() -> None:
    for sd_demand, sd_supply in ((1, 1), (2, 1), (1, 2)):
        slopes = simulate_simultaneity(
            500, sd_demand, sd_supply, 1000, np.random.default_rng(0)
        )
        expected = simultaneity_slope(sd_demand, sd_supply)
        assert slopes.mean() == pytest.approx(
            expected, abs=4 * slopes.std() / 1000**0.5
        )
        assert abs(slopes.mean() - 1) > 0.3
        assert abs(slopes.mean() + 1) > 0.3


def test_1回分の同時性の推定は価格を説明変数に数量を被説明変数にする() -> None:
    market = draw_market(30, 2.0, 1.0, np.random.default_rng(5))
    expected = fit_simple(market["p"], market["q"]).slope
    slopes = simulate_simultaneity(30, 2.0, 1.0, 1, np.random.default_rng(5))
    assert slopes[0] == pytest.approx(expected)


def test_需要の変動が小さいと傾きは需要の傾きに近づく() -> None:
    slopes = simulate_simultaneity(500, 0.05, 1.0, 300, np.random.default_rng(0))
    assert slopes.mean() == pytest.approx(-1, abs=0.02)
