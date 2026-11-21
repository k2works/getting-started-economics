"""第 14 章: 逆選択・シグナル・モラルハザードのテスト。"""

import pytest

from lib.chapter14.information import (
    agent_works,
    expected_value_of_unknown_quality,
    good_quality_sells,
    minimum_bonus,
    principal_profit_with_bonus,
    separating_education_range,
    signal_separates,
    unraveling,
    worth_paying_bonus,
)


def test_質が分からない買い手の支払意思額は期待値() -> None:
    assert expected_value_of_unknown_quality(0.5, 100, 40) == pytest.approx(70)
    assert expected_value_of_unknown_quality(1, 100, 40) == 100
    assert expected_value_of_unknown_quality(0, 100, 40) == 40


def test_良い品の割合は0から1() -> None:
    with pytest.raises(ValueError, match="割合"):
        expected_value_of_unknown_quality(1.1, 100, 40)
    with pytest.raises(ValueError, match="割合"):
        expected_value_of_unknown_quality(-0.1, 100, 40)


def test_良い品が売られるのは期待値が売り手の最低価格以上のとき() -> None:
    assert good_quality_sells(0.5, 100, 40, seller_reservation=60)
    assert good_quality_sells(0.5, 100, 40, seller_reservation=70)
    assert not good_quality_sells(0.5, 100, 40, seller_reservation=80)


def test_良い品の割合が低いと良い品が市場から消える() -> None:
    assert good_quality_sells(0.8, 100, 40, 70)
    assert not good_quality_sells(0.3, 100, 40, 70)


def test_逆選択は市場が崩れる() -> None:
    # 質 20〜100 の 5 種類。売り手の最低価格 = 質、買い手の支払意思額 = 質の平均 × 1.2
    assert unraveling([20, 40, 60, 80, 100], 1.2) == [20]


def test_買い手の評価が高いと一部だけが残る() -> None:
    assert unraveling([20, 40, 60, 80, 100], 1.5) == [20, 40, 60]


def test_買い手の評価が十分高ければ全部が売られる() -> None:
    assert unraveling([20, 40, 60, 80, 100], 2.0) == [20, 40, 60, 80, 100]


def test_質が1種類だけなら崩れない() -> None:
    assert unraveling([50], 1.0) == [50]


def test_市場が崩れる入力のチェック() -> None:
    with pytest.raises(ValueError, match="質"):
        unraveling([], 1.2)
    with pytest.raises(ValueError, match="評価"):
        unraveling([20, 40], 0)


def test_買い手が質を見分けられない市場では売り手の順序は入力の順に依らない() -> None:
    assert unraveling([100, 20, 80, 40, 60], 1.5) == [20, 40, 60]


def test_シグナルで高い能力の人だけが選ぶ教育年数の範囲() -> None:
    low, high = separating_education_range(
        wage_high=100, wage_low=60, cost_high=10, cost_low=20
    )
    assert (low, high) == (pytest.approx(2), pytest.approx(4))


def test_範囲の中の教育年数なら高い能力の人だけが教育を選ぶ() -> None:
    args = {"wage_high": 100, "wage_low": 60, "cost_high": 10, "cost_low": 20}
    assert signal_separates(3, **args)
    assert signal_separates(2, **args)
    assert signal_separates(4, **args)
    assert not signal_separates(1, **args)
    assert not signal_separates(5, **args)


def test_シグナルの費用が同じなら区別できない() -> None:
    with pytest.raises(ValueError, match="費用"):
        separating_education_range(100, 60, 20, 20)
    with pytest.raises(ValueError, match="費用"):
        separating_education_range(100, 60, 30, 20)


def test_シグナルの賃金は高い能力の方が高い() -> None:
    with pytest.raises(ValueError, match="賃金"):
        separating_education_range(60, 100, 10, 20)
    with pytest.raises(ValueError, match="賃金"):
        separating_education_range(100, 100, 10, 20)


def test_教育の費用が負ならエラー() -> None:
    with pytest.raises(ValueError, match="費用"):
        separating_education_range(100, 60, 0, 20)


def test_努力させるのに必要な最低の成果報酬() -> None:
    assert minimum_bonus(0.8, 0.4, effort_cost=10) == pytest.approx(25)
    assert minimum_bonus(0.9, 0.3, effort_cost=12) == pytest.approx(20)


def test_成果報酬が最低額以上なら努力する() -> None:
    assert agent_works(25, 0.8, 0.4, 10)
    assert agent_works(30, 0.8, 0.4, 10)
    assert not agent_works(24, 0.8, 0.4, 10)
    assert not agent_works(0, 0.8, 0.4, 10)


def test_努力しても成功確率が変わらないなら報酬で動かせない() -> None:
    with pytest.raises(ValueError, match="確率"):
        minimum_bonus(0.5, 0.5, 10)
    with pytest.raises(ValueError, match="確率"):
        minimum_bonus(0.4, 0.8, 10)
    with pytest.raises(ValueError, match="確率"):
        minimum_bonus(1.1, 0.4, 10)


def test_努力させたときの依頼人の期待利潤() -> None:
    assert principal_profit_with_bonus(100, 0.8, 0.4, 10) == pytest.approx(
        0.8 * (100 - 25)
    )


def test_努力させる価値があるのは利潤が努力なしを上回るとき() -> None:
    assert worth_paying_bonus(100, 0.8, 0.4, 10)
    assert not worth_paying_bonus(100, 0.8, 0.4, 50)


def test_努力の費用が負ならエラー() -> None:
    with pytest.raises(ValueError, match="費用"):
        minimum_bonus(0.8, 0.4, -1)


def test_買い手の評価が低すぎると市場が消える() -> None:
    assert unraveling([20, 40], 0.5) == []
