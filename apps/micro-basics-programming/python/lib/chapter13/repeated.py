"""繰り返しゲーム（囚人のジレンマの、しっぺ返しとトリガー戦略）。

戦略は、自分と相手の過去の手（0 = 協調、1 = 裏切り）から、次の手を決める関数。
無限に繰り返すときの価値は、公比 δ（割引因子）の、無限等比級数の、閉じた式で求める。
"""

from collections.abc import Callable, Sequence

from lib.chapter12.game import Game

Strategy = Callable[[Sequence[int], Sequence[int]], int]

COOPERATE = 0
DEFECT = 1
_TOLERANCE = 1e-9  # 閾値ちょうどの判定を、浮動小数点の誤差に左右させない


def _check_delta(delta: float) -> None:
    if not 0 <= delta < 1:
        raise ValueError("割引因子は、0 以上 1 未満にする")


def discounted_sum(payoffs: Sequence[float], delta: float) -> float:
    """割引現在価値 Σ δ^t × 利得_t（t = 0, 1, …）。"""
    _check_delta(delta)
    return sum(payoff * delta**t for t, payoff in enumerate(payoffs))


def cooperation_value(reward: float, delta: float) -> float:
    """毎期、報酬 R を得続ける価値 R ÷ (1 − δ)（無限回）。"""
    _check_delta(delta)
    return reward / (1 - delta)


def deviation_value(temptation: float, punishment: float, delta: float) -> float:
    """今期だけ裏切り、以後は罰 P を受け続ける価値 T + δ·P ÷ (1 − δ)。"""
    _check_delta(delta)
    return temptation + delta * punishment / (1 - delta)


def cooperation_threshold(temptation: float, reward: float, punishment: float) -> float:
    """トリガー戦略で協調が続く、最低の割引因子 δ* = (T − R) ÷ (T − P)。"""
    if not temptation > reward > punishment:
        raise ValueError("T > R > P にする")
    return (temptation - reward) / (temptation - punishment)


def trigger_sustains_cooperation(
    temptation: float, reward: float, punishment: float, delta: float
) -> bool:
    """割引因子が閾値以上なら、トリガー戦略で、協調を保てる。"""
    threshold = cooperation_threshold(temptation, reward, punishment)
    return delta >= threshold - _TOLERANCE


def always_cooperate(own: Sequence[int], opponent: Sequence[int]) -> int:
    """いつも協調する。"""
    return COOPERATE


def always_defect(own: Sequence[int], opponent: Sequence[int]) -> int:
    """いつも裏切る。"""
    return DEFECT


def tit_for_tat(own: Sequence[int], opponent: Sequence[int]) -> int:
    """しっぺ返し。最初は協調し、以後は、相手の前の手をまねる。"""
    return opponent[-1] if opponent else COOPERATE


def grim_trigger(own: Sequence[int], opponent: Sequence[int]) -> int:
    """トリガー戦略。相手が一度でも裏切ったら、永久に裏切る。"""
    return DEFECT if DEFECT in opponent else COOPERATE


def play(
    game: Game, row_strategy: Strategy, column_strategy: Strategy, rounds: int
) -> list[tuple[int, int]]:
    """rounds 回、繰り返して、各期の（行の手、列の手）を返す。"""
    if rounds < 1:
        raise ValueError("回数は、1 以上にする")
    row_moves: list[int] = []
    column_moves: list[int] = []
    for _ in range(rounds):
        row = row_strategy(row_moves, column_moves)
        column = column_strategy(column_moves, row_moves)
        row_moves.append(row)
        column_moves.append(column)
    return list(zip(row_moves, column_moves, strict=True))


def total_payoffs(
    game: Game, history: Sequence[tuple[int, int]]
) -> tuple[float, float]:
    """各期の利得の合計（割り引かない）。"""
    row_total = sum(game.payoffs[i][j][0] for i, j in history)
    column_total = sum(game.payoffs[i][j][1] for i, j in history)
    return row_total, column_total
