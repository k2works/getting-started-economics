"""第 4 章: スルツキー分解と財の種類のテスト。"""

import pytest

from lib.chapter01.utility import cobb_douglas_utility
from lib.chapter02.budget import optimal_bundle
from lib.chapter04.slutsky import (
    classify_by_effects,
    compensated_bundle,
    cross_price_relation,
    demand_perfect_complements,
    demand_perfect_substitutes,
    slutsky_decomposition,
)

# U = x·y、所得 80、Py = 1。Px が 2 から 0.5 に下がる
M, PY = 80, 1


def test_補償された消費点は元の効用を保つ() -> None:
    x, y = compensated_bundle(800, 0.5, PY)
    assert (x, y) == pytest.approx((40, 20))
    assert cobb_douglas_utility(x, y) == pytest.approx(800)


def test_補償された消費点で限界代替率は新しい価格比と等しい() -> None:
    x, y = compensated_bundle(800, 0.5, PY)
    assert y / x == pytest.approx(0.5 / PY)


def test_補償された消費点のべき指数が違う場合() -> None:
    x, y = compensated_bundle(800, 0.5, PY, 1, 2)
    assert cobb_douglas_utility(x, y, 1, 2) == pytest.approx(800)
    assert y / (2 * x) == pytest.approx(0.5 / PY)


def test_補償された消費点の価格は正でなければエラー() -> None:
    with pytest.raises(ValueError, match="価格"):
        compensated_bundle(800, 0, PY)
    with pytest.raises(ValueError, match="効用"):
        compensated_bundle(0, 0.5, PY)


def test_値下げの価格効果は代替効果と所得効果の和() -> None:
    result = slutsky_decomposition(M, 2, 0.5, PY)
    assert result.original == (20, 40)
    assert result.substitution == pytest.approx((40, 20))
    assert result.final == pytest.approx((80, 40))
    assert result.substitution_effect == pytest.approx(20)
    assert result.income_effect == pytest.approx(40)
    assert result.price_effect == pytest.approx(60)


def test_価格効果は元の点と最終の点の差() -> None:
    result = slutsky_decomposition(M, 2, 0.5, PY)
    assert result.price_effect == pytest.approx(result.final[0] - result.original[0])


def test_最終の点は新しい価格の最適消費点() -> None:
    result = slutsky_decomposition(M, 2, 0.5, PY)
    assert result.final == pytest.approx(optimal_bundle(M, 0.5, PY))


def test_代替効果のあとの点の支出は元の所得より少ない() -> None:
    result = slutsky_decomposition(M, 2, 0.5, PY)
    x, y = result.substitution
    assert 0.5 * x + PY * y == pytest.approx(40)


def test_値上げでは効果の符号が逆() -> None:
    result = slutsky_decomposition(M, 0.5, 2, PY)
    assert result.original == pytest.approx((80, 40))
    assert result.substitution_effect == pytest.approx(-40)
    assert result.income_effect == pytest.approx(-20)
    assert result.price_effect == pytest.approx(-60)


def test_代替効果は値下げで必ず正() -> None:
    for a, b in ((1, 1), (1, 2), (2, 1), (0.5, 0.5)):
        for old, new in ((2, 1), (4, 1), (2, 1.9), (1, 0.1)):
            effect = slutsky_decomposition(M, old, new, PY, a, b).substitution_effect
            assert effect > 0


def test_価格が変わらなければ効果は0() -> None:
    result = slutsky_decomposition(M, 2, 2, PY)
    assert result.substitution_effect == pytest.approx(0)
    assert result.income_effect == pytest.approx(0)


def test_価格が1未満の正の値でも分解できる() -> None:
    result = slutsky_decomposition(M, 0.5, 0.25, PY)
    assert result.price_effect > 0


def test_上級財は代替効果も所得効果も正() -> None:
    assert classify_by_effects(20, 40) == "上級財"


def test_下級財は所得効果が負で代替効果のほうが大きい() -> None:
    assert classify_by_effects(20, -5) == "下級財"


def test_ギッフェン財は所得効果の負が代替効果より大きい() -> None:
    assert classify_by_effects(20, -30) == "ギッフェン財"
    # 値下げで、需要が減る（価格効果 = 20 − 30 < 0）
    assert 20 + (-30) < 0


def test_所得効果が代替効果と同じ大きさなら下級財() -> None:
    assert classify_by_effects(20, -20) == "下級財"


def test_所得効果が0なら中立財() -> None:
    assert classify_by_effects(20, 0) == "中立財"


def test_代替効果が正でなければエラー() -> None:
    with pytest.raises(ValueError, match="代替効果"):
        classify_by_effects(0, 10)
    with pytest.raises(ValueError, match="代替効果"):
        classify_by_effects(-1, 10)


def test_完全補完財の需要は所得を価格の和で割った値() -> None:
    assert demand_perfect_complements(M, 2, 1) == pytest.approx(80 / 3)
    assert demand_perfect_complements(M, 2, 2) == pytest.approx(20)


def test_完全代替財は安いほうだけを買う() -> None:
    assert demand_perfect_substitutes(M, 2, 1) == 0
    assert demand_perfect_substitutes(M, 2, 3) == 40
    assert demand_perfect_substitutes(M, 2, 2) == 40


def test_代替財は相手の値上げで需要が増える() -> None:
    change = demand_perfect_substitutes(M, 2, 3) - demand_perfect_substitutes(M, 2, 1)
    assert cross_price_relation(change) == "代替財"


def test_補完財は相手の値上げで需要が減る() -> None:
    change = demand_perfect_complements(M, 2, 2) - demand_perfect_complements(M, 2, 1)
    assert cross_price_relation(change) == "補完財"


def test_コブ_ダグラス型は相手の価格に影響されず独立財() -> None:
    change = optimal_bundle(M, 2, 5)[0] - optimal_bundle(M, 2, 1)[0]
    assert cross_price_relation(change) == "独立財"


def test_交差価格効果の許容誤差() -> None:
    assert cross_price_relation(1e-12) == "独立財"
    assert cross_price_relation(-1e-12) == "独立財"
    assert cross_price_relation(1e-6) == "代替財"
    assert cross_price_relation(-1e-6) == "補完財"


def test_完全補完財と完全代替財の価格は正でなければエラー() -> None:
    with pytest.raises(ValueError, match="価格"):
        demand_perfect_complements(M, 0, 1)
    with pytest.raises(ValueError, match="価格"):
        demand_perfect_substitutes(M, 2, 0)
    with pytest.raises(ValueError, match="所得"):
        demand_perfect_substitutes(-1, 2, 1)
