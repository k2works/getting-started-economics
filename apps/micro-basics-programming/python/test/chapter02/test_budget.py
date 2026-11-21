"""第 2 章: 予算制約と最適消費のテスト。"""

import pytest

from lib.chapter01.utility import (
    cobb_douglas_utility,
    marginal_rate_of_substitution,
)
from lib.chapter02.budget import (
    budget_intercepts,
    budget_line_y,
    budget_slope,
    is_affordable,
    optimal_bundle,
    optimal_bundle_by_grid,
    tangency_gap,
)

# U = x·y、所得 80、Px = 2、Py = 1。最適消費点は (20, 40)
M, PX, PY = 80, 2, 1


def test_予算線は所得を使い切る点を結ぶ() -> None:
    assert budget_line_y(M, PX, PY, 0) == 80
    assert budget_line_y(M, PX, PY, 20) == 40
    assert budget_line_y(M, PX, PY, 40) == 0


def test_予算線の傾きは価格比のマイナス() -> None:
    assert budget_slope(PX, PY) == -2
    assert budget_slope(1, 2) == pytest.approx(-0.5)


def test_予算線の切片は所得を価格で割った値() -> None:
    assert budget_intercepts(M, PX, PY) == (40, 80)


def test_財xが値下がりするとx切片だけが右へ動く() -> None:
    assert budget_intercepts(M, 1, PY) == (80, 80)
    assert budget_slope(1, PY) == -1


def test_所得が増えると予算線は平行に動く() -> None:
    assert budget_intercepts(160, PX, PY) == (80, 160)
    assert budget_slope(PX, PY) == -2


def test_予算線の価格は正でなければエラー() -> None:
    with pytest.raises(ValueError, match="価格"):
        budget_line_y(M, 0, PY, 1)
    with pytest.raises(ValueError, match="価格"):
        budget_intercepts(M, PX, 0)
    with pytest.raises(ValueError, match="価格"):
        budget_slope(-1, PY)


def test_価格が1未満の正の値でも予算線を引ける() -> None:
    assert budget_intercepts(M, 0.5, 0.25) == (160, 320)


def test_所得が負ならエラー() -> None:
    with pytest.raises(ValueError, match="所得"):
        budget_intercepts(-1, PX, PY)


def test_所得0は許される() -> None:
    assert budget_intercepts(0, PX, PY) == (0, 0)


def test_買える組み合わせは予算線の内側() -> None:
    assert is_affordable(20, 40, M, PX, PY)
    assert is_affordable(10, 10, M, PX, PY)
    assert not is_affordable(30, 40, M, PX, PY)


def test_予算線の上の点は買えるが誤差を許す() -> None:
    assert is_affordable(20, 40 + 1e-12, M, PX, PY)
    assert not is_affordable(20, 40 + 1e-6, M, PX, PY)


def test_最適消費点は予算を半分ずつ使う() -> None:
    assert optimal_bundle(M, PX, PY) == (20, 40)


def test_最適消費点は予算線の上にある() -> None:
    x, y = optimal_bundle(M, PX, PY)
    assert PX * x + PY * y == pytest.approx(M)


def test_最適点では限界代替率が価格比と等しい() -> None:
    x, y = optimal_bundle(M, PX, PY)
    assert marginal_rate_of_substitution(x, y) == pytest.approx(PX / PY)
    assert tangency_gap(x, y, PX, PY) == pytest.approx(0, abs=1e-12)


def test_最適点でない点は限界代替率と価格比が食い違う() -> None:
    assert tangency_gap(10, 60, PX, PY) == pytest.approx(6 - 2)
    assert tangency_gap(30, 20, PX, PY) == pytest.approx(2 / 3 - 2)


def test_予算線の上の他の点は効用が低い() -> None:
    best = cobb_douglas_utility(*optimal_bundle(M, PX, PY))
    assert best == 800
    for x in (5, 10, 15, 25, 30, 35):
        y = budget_line_y(M, PX, PY, x)
        assert cobb_douglas_utility(x, y) < best


def test_格子点の探索は閉じた式と一致する() -> None:
    x, y = optimal_bundle_by_grid(M, PX, PY)
    assert x == pytest.approx(20)
    assert y == pytest.approx(40)


def test_格子点の探索は別の価格でも一致する() -> None:
    assert optimal_bundle_by_grid(90, 3, 2) == pytest.approx((15, 22.5))
    assert optimal_bundle(90, 3, 2) == pytest.approx((15, 22.5))


def test_べき指数が違う効用でも格子点の探索は閉じた式に近い() -> None:
    closed = optimal_bundle(M, PX, PY, 1, 2)
    assert closed == pytest.approx((80 / 3 / 2, 160 / 3))
    grid = optimal_bundle_by_grid(M, PX, PY, 1, 2)
    assert grid == pytest.approx(closed, abs=0.1)


def test_べき指数が違えば支出の割合が変わる() -> None:
    x, y = optimal_bundle(M, PX, PY, 1, 3)
    assert PX * x == pytest.approx(M * 1 / 4)
    assert PY * y == pytest.approx(M * 3 / 4)


def test_所得が2倍なら最適消費点も2倍() -> None:
    assert optimal_bundle(160, PX, PY) == (40, 80)


def test_財xが値下がりするとxは増えyは変わらない() -> None:
    assert optimal_bundle(M, 1, PY) == (40, 40)
    assert optimal_bundle(M, 0.5, PY) == (80, 40)


def test_所得0なら何も買わない() -> None:
    assert optimal_bundle(0, PX, PY) == (0, 0)
    assert optimal_bundle_by_grid(0, PX, PY) == (0, 0)


def test_最適消費点の価格は正でなければエラー() -> None:
    with pytest.raises(ValueError, match="価格"):
        optimal_bundle(M, 0, PY)
    with pytest.raises(ValueError, match="価格"):
        optimal_bundle_by_grid(M, PX, 0)


def test_最適消費点のべき指数は正でなければエラー() -> None:
    with pytest.raises(ValueError, match="指数"):
        optimal_bundle(M, PX, PY, 0, 1)
    with pytest.raises(ValueError, match="指数"):
        optimal_bundle_by_grid(M, PX, PY, 1, -1)


def test_格子の分割数が2未満ならエラー() -> None:
    with pytest.raises(ValueError, match="分割"):
        optimal_bundle_by_grid(M, PX, PY, steps=1)


def test_格子の分割数が2なら端点と中点だけを調べる() -> None:
    assert optimal_bundle_by_grid(M, PX, PY, steps=2) == (20, 40)
