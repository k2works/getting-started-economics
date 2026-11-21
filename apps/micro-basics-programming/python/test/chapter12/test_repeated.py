"""第 12 章: 繰り返しゲーム（しっぺ返し・トリガー戦略）のテスト。"""

import pytest

from lib.chapter12.game import prisoners_dilemma
from lib.chapter12.repeated import (
    always_cooperate,
    always_defect,
    cooperation_threshold,
    cooperation_value,
    deviation_value,
    discounted_sum,
    grim_trigger,
    play,
    tit_for_tat,
    total_payoffs,
    trigger_sustains_cooperation,
)

# 誘惑 T = 5、報酬 R = 3、罰 P = 1、愚か者 S = 0（戦略 0 = 協調、1 = 裏切り）
GAME = prisoners_dilemma(temptation=5, reward=3, punishment=1, sucker=0)


def test_割引現在価値の合計() -> None:
    assert discounted_sum([3, 3, 3], 0.5) == pytest.approx(3 + 1.5 + 0.75)
    assert discounted_sum([], 0.5) == 0
    assert discounted_sum([10], 0.9) == 10


def test_割引因子は0以上1未満() -> None:
    with pytest.raises(ValueError, match="割引因子"):
        discounted_sum([1], -0.1)
    with pytest.raises(ValueError, match="割引因子"):
        discounted_sum([1], 1)


def test_協調を続ける価値は報酬を割引因子で割った値() -> None:
    assert cooperation_value(3, 0.5) == pytest.approx(6)
    assert cooperation_value(3, 0.9) == pytest.approx(30)
    assert cooperation_value(3, 0) == 3


def test_裏切る価値は誘惑に以後の罰を足した値() -> None:
    assert deviation_value(5, 1, 0.5) == pytest.approx(5 + 0.5 * 1 / 0.5)
    assert deviation_value(5, 1, 0) == 5


def test_協調が続く最低の割引因子() -> None:
    assert cooperation_threshold(5, 3, 1) == pytest.approx(0.5)
    assert cooperation_threshold(4, 3, 1) == pytest.approx(1 / 3)
    assert cooperation_threshold(10, 3, 1) == pytest.approx(7 / 9)


def test_閾値の条件が崩れるとエラー() -> None:
    with pytest.raises(ValueError, match="T > R > P"):
        cooperation_threshold(3, 3, 1)
    with pytest.raises(ValueError, match="T > R > P"):
        cooperation_threshold(5, 1, 1)


def test_トリガー戦略は割引因子が閾値以上なら協調を保てる() -> None:
    assert trigger_sustains_cooperation(5, 3, 1, 0.6)
    assert trigger_sustains_cooperation(5, 3, 1, 0.5)
    assert not trigger_sustains_cooperation(5, 3, 1, 0.4)


def test_閾値の上下で協調と裏切りの価値が入れ替わる() -> None:
    for delta in (0.4, 0.49, 0.6, 0.9):
        stays = cooperation_value(3, delta) >= deviation_value(5, 1, delta)
        assert stays == trigger_sustains_cooperation(5, 3, 1, delta)
    assert cooperation_value(3, 0.5) == pytest.approx(deviation_value(5, 1, 0.5))


def test_戦略は過去の手から次の手を決める() -> None:
    assert always_cooperate([], []) == 0
    assert always_defect([], []) == 1
    assert tit_for_tat([], []) == 0
    assert tit_for_tat([0], [1]) == 1
    assert tit_for_tat([1], [0]) == 0
    assert grim_trigger([], []) == 0
    assert grim_trigger([0, 0], [0, 0]) == 0
    assert grim_trigger([0, 0], [0, 1]) == 1
    assert grim_trigger([0, 1, 1], [0, 1, 0]) == 1


def test_しっぺ返し同士は協調が続く() -> None:
    history = play(GAME, tit_for_tat, tit_for_tat, 5)
    assert history == [(0, 0)] * 5
    assert total_payoffs(GAME, history) == (15, 15)


def test_しっぺ返しは裏切りに裏切りで返す() -> None:
    history = play(GAME, tit_for_tat, always_defect, 4)
    assert history == [(0, 1), (1, 1), (1, 1), (1, 1)]
    assert total_payoffs(GAME, history) == (0 + 1 + 1 + 1, 5 + 1 + 1 + 1)


def test_裏切り同士は罰のまま() -> None:
    history = play(GAME, always_defect, always_defect, 3)
    assert total_payoffs(GAME, history) == (3, 3)


def test_協調しつづけると裏切りに搾取される() -> None:
    history = play(GAME, always_cooperate, always_defect, 3)
    assert total_payoffs(GAME, history) == (0, 15)


def test_トリガー戦略は一度の裏切りで永久に裏切る() -> None:
    history = play(GAME, grim_trigger, tit_for_tat, 4)
    assert history == [(0, 0)] * 4
    history = play(GAME, grim_trigger, always_defect, 4)
    assert history == [(0, 1), (1, 1), (1, 1), (1, 1)]


def test_回数は1以上() -> None:
    with pytest.raises(ValueError, match="回数"):
        play(GAME, tit_for_tat, tit_for_tat, 0)


def test_有限回で近似した価値は閾値の判定と同じ向き() -> None:
    delta = 0.6
    rounds = 200
    cooperate = discounted_sum([3] * rounds, delta)
    deviate = discounted_sum([5] + [1] * (rounds - 1), delta)
    assert cooperate == pytest.approx(cooperation_value(3, delta), rel=1e-6)
    assert deviate == pytest.approx(deviation_value(5, 1, delta), rel=1e-6)
    assert cooperate > deviate
