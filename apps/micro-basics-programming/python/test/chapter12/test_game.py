"""第 12 章: 利得表・支配戦略・ナッシュ均衡のテスト。"""

import pytest

from lib.chapter12.game import (
    Game,
    best_responses_for_column,
    best_responses_for_row,
    dominant_strategy_for_column,
    dominant_strategy_for_row,
    is_pareto_dominated,
    is_prisoners_dilemma,
    prisoners_dilemma,
    pure_nash_equilibria,
)

# 戦略 0 = 協調、戦略 1 = 裏切り。誘惑 T = 5、報酬 R = 3、罰 P = 1、愚か者 S = 0
DILEMMA = prisoners_dilemma(temptation=5, reward=3, punishment=1, sucker=0)
# 協調ゲーム: 同じ戦略をそろえると得（均衡が 2 つ）
COORDINATION = Game(
    (
        ((2, 2), (0, 0)),
        ((0, 0), (1, 1)),
    )
)
# 一致ゲーム: 純粋戦略の均衡がない
MATCHING = Game(
    (
        ((1, -1), (-1, 1)),
        ((-1, 1), (1, -1)),
    )
)


def test_囚人のジレンマの利得表() -> None:
    assert DILEMMA.payoffs[0][0] == (3, 3)
    assert DILEMMA.payoffs[0][1] == (0, 5)
    assert DILEMMA.payoffs[1][0] == (5, 0)
    assert DILEMMA.payoffs[1][1] == (1, 1)


def test_囚人のジレンマの条件が崩れるとエラー() -> None:
    with pytest.raises(ValueError, match="T > R > P > S"):
        prisoners_dilemma(temptation=3, reward=3, punishment=1, sucker=0)
    with pytest.raises(ValueError, match="T > R > P > S"):
        prisoners_dilemma(temptation=5, reward=1, punishment=3, sucker=0)
    with pytest.raises(ValueError, match="T > R > P > S"):
        prisoners_dilemma(temptation=5, reward=3, punishment=1, sucker=1)


def test_利得表の形のチェック() -> None:
    with pytest.raises(ValueError, match="空"):
        Game(())
    with pytest.raises(ValueError, match="長方形"):
        Game((((1, 1), (2, 2)), ((3, 3),)))


def test_相手の戦略に対する最適反応() -> None:
    assert best_responses_for_row(DILEMMA, 0) == [1]
    assert best_responses_for_row(DILEMMA, 1) == [1]
    assert best_responses_for_column(DILEMMA, 0) == [1]
    assert best_responses_for_column(DILEMMA, 1) == [1]


def test_最適反応は同点なら両方() -> None:
    tie = Game((((1, 1), (1, 1)), ((0, 0), (0, 0))))
    assert best_responses_for_row(tie, 0) == [0]
    flat = Game((((1, 1), (1, 1)), ((1, 1), (1, 1))))
    assert best_responses_for_row(flat, 0) == [0, 1]
    assert best_responses_for_column(flat, 1) == [0, 1]


def test_最適反応の相手の戦略は範囲内だけ() -> None:
    with pytest.raises(ValueError, match="戦略"):
        best_responses_for_row(DILEMMA, 2)
    with pytest.raises(ValueError, match="戦略"):
        best_responses_for_column(DILEMMA, -1)


def test_囚人のジレンマでは裏切りが支配戦略() -> None:
    assert dominant_strategy_for_row(DILEMMA) == 1
    assert dominant_strategy_for_column(DILEMMA) == 1


def test_支配戦略がないゲーム() -> None:
    assert dominant_strategy_for_row(COORDINATION) is None
    assert dominant_strategy_for_column(MATCHING) is None


def test_列の支配戦略は行とは別に求める() -> None:
    game = Game((((1, 3), (1, 0)), ((0, 2), (0, 1))))
    assert dominant_strategy_for_column(game) == 0
    assert dominant_strategy_for_row(game) == 0
    flipped = Game((((1, 0), (1, 3)), ((0, 1), (0, 2))))
    assert dominant_strategy_for_row(flipped) == 0
    assert dominant_strategy_for_column(flipped) == 1


def test_囚人のジレンマのナッシュ均衡は裏切りと裏切りだけ() -> None:
    assert pure_nash_equilibria(DILEMMA) == [(1, 1)]


def test_協調ゲームの均衡は2つ() -> None:
    assert pure_nash_equilibria(COORDINATION) == [(0, 0), (1, 1)]


def test_一致ゲームに純粋戦略の均衡はない() -> None:
    assert pure_nash_equilibria(MATCHING) == []


def test_ナッシュ均衡は2人とも最適反応() -> None:
    for i, j in pure_nash_equilibria(COORDINATION):
        assert i in best_responses_for_row(COORDINATION, j)
        assert j in best_responses_for_column(COORDINATION, i)


def test_囚人のジレンマの均衡はパレート劣位() -> None:
    assert is_pareto_dominated(DILEMMA, (1, 1))
    assert not is_pareto_dominated(DILEMMA, (0, 0))


def test_パレート劣位は片方だけ良くなるなら劣位() -> None:
    game = Game((((1, 1), (2, 1)), ((0, 0), (0, 0))))
    assert is_pareto_dominated(game, (0, 0))
    assert not is_pareto_dominated(game, (0, 1))


def test_囚人のジレンマの判定() -> None:
    assert is_prisoners_dilemma(DILEMMA)
    assert not is_prisoners_dilemma(COORDINATION)
    assert not is_prisoners_dilemma(MATCHING)


def test_囚人のジレンマの判定は列の利得も見る() -> None:
    asymmetric = Game((((3, 3), (0, 0)), ((5, 5), (1, 1))))
    assert not is_prisoners_dilemma(asymmetric)


def test_大きさが2かける2でなければ囚人のジレンマではない() -> None:
    big = Game((((1, 1), (1, 1), (1, 1)), ((1, 1), (1, 1), (1, 1))))
    assert not is_prisoners_dilemma(big)


def test_戦略が1つだけの行のゲーム() -> None:
    single = Game((((1, 1), (2, 2)),))
    assert (single.rows, single.columns) == (1, 2)


def test_同点の戦略は支配戦略ではない() -> None:
    weak_row = Game((((1, 0), (1, 0)), ((1, 0), (0, 0))))
    assert dominant_strategy_for_row(weak_row) is None
    weak_column = Game((((1, 1), (0, 1)), ((0, 0), (0, 1))))
    assert dominant_strategy_for_column(weak_column) is None


def test_パレート劣位は列だけが良くなる場合も劣位() -> None:
    assert is_pareto_dominated(Game((((1, 1), (1, 2)),)), (0, 0))


def test_パレート劣位は行と列の利得を取り違えない() -> None:
    assert not is_pareto_dominated(Game((((1, 5), (2, 3)),)), (0, 0))
    assert not is_pareto_dominated(Game((((3, 1), (1, 3)),)), (0, 0))


def test_2かける3のゲームは囚人のジレンマではない() -> None:
    wide = Game((((3, 3), (0, 5), (0, 0)), ((5, 0), (1, 1), (0, 0))))
    assert not is_prisoners_dilemma(wide)
    tall = Game((((3, 3), (0, 5)), ((5, 0), (1, 1)), ((0, 0), (0, 0))))
    assert not is_prisoners_dilemma(tall)


def test_囚人のジレンマの判定は報酬と罰の列の利得も見る() -> None:
    assert not is_prisoners_dilemma(Game((((3, 4), (0, 5)), ((5, 0), (1, 1)))))
    assert not is_prisoners_dilemma(Game((((3, 3), (0, 5)), ((5, 0), (1, 2)))))


def _symmetric(
    temptation: float, reward: float, punishment: float, sucker: float
) -> Game:
    return Game(
        (
            ((reward, reward), (sucker, temptation)),
            ((temptation, sucker), (punishment, punishment)),
        )
    )


def test_囚人のジレンマの不等式は厳密() -> None:
    assert is_prisoners_dilemma(_symmetric(5, 3, 1, 0))
    assert not is_prisoners_dilemma(_symmetric(3, 3, 1, 0))
    assert not is_prisoners_dilemma(_symmetric(5, 1, 1, 0))
    assert not is_prisoners_dilemma(_symmetric(5, 3, 0, 0))


def test_報酬と罰が等しければ囚人のジレンマではない() -> None:
    with pytest.raises(ValueError, match="T > R > P > S"):
        prisoners_dilemma(temptation=5, reward=3, punishment=3, sucker=0)


def test_最適反応は浮動小数点の誤差を同点と見なす() -> None:
    rows = Game((((0.1 + 0.2, 0),), ((0.3, 0),)))
    assert best_responses_for_row(rows, 0) == [0, 1]
    columns = Game((((0, 0.1 + 0.2), (0, 0.3)),))
    assert best_responses_for_column(columns, 0) == [0, 1]
