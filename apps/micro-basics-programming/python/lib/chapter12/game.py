"""2 人ゲーム（利得表）。

利得表 payoffs[i][j] = (行の利得, 列の利得)。行が戦略 i、列が戦略 j を選ぶ。
- 最適反応: 相手の戦略を与えられたとき、自分の利得が最大になる戦略
- 支配戦略: 相手が何をしても、他のどの戦略より、厳密に良い戦略
- ナッシュ均衡: 2 人とも、相手の戦略に対して、最適反応になっている組
"""

from dataclasses import dataclass

Payoffs = tuple[tuple[tuple[float, float], ...], ...]


@dataclass(frozen=True)
class Game:
    """2 人ゲーム。payoffs[i][j] = (行の利得, 列の利得)。"""

    payoffs: Payoffs

    def __post_init__(self) -> None:
        if not self.payoffs or not self.payoffs[0]:
            raise ValueError("利得表が空です")
        width = len(self.payoffs[0])
        if any(len(row) != width for row in self.payoffs):
            raise ValueError("利得表は、長方形にする")

    @property
    def rows(self) -> int:
        """行の戦略の数。"""
        return len(self.payoffs)

    @property
    def columns(self) -> int:
        """列の戦略の数。"""
        return len(self.payoffs[0])


def prisoners_dilemma(
    temptation: float, reward: float, punishment: float, sucker: float
) -> Game:
    """囚人のジレンマ。戦略 0 = 協調、戦略 1 = 裏切り。T > R > P > S が条件。"""
    if not temptation > reward > punishment > sucker:
        raise ValueError("囚人のジレンマは、T > R > P > S にする")
    return Game(
        (
            ((reward, reward), (sucker, temptation)),
            ((temptation, sucker), (punishment, punishment)),
        )
    )


def _check_strategy(index: int, count: int) -> None:
    if not 0 <= index < count:
        raise ValueError("戦略の番号が、範囲外です")


def _best(values: list[float]) -> list[int]:
    top = max(values)
    return [i for i, value in enumerate(values) if value == top]


def best_responses_for_row(game: Game, column: int) -> list[int]:
    """列が戦略 column のとき、行の最適反応（同点なら、すべて）。"""
    _check_strategy(column, game.columns)
    return _best([game.payoffs[i][column][0] for i in range(game.rows)])


def best_responses_for_column(game: Game, row: int) -> list[int]:
    """行が戦略 row のとき、列の最適反応（同点なら、すべて）。"""
    _check_strategy(row, game.rows)
    return _best([game.payoffs[row][j][1] for j in range(game.columns)])


def dominant_strategy_for_row(game: Game) -> int | None:
    """行の支配戦略（列が何をしても、他より厳密に良い戦略）。なければ None。"""
    for i in range(game.rows):
        if all(
            game.payoffs[i][j][0] > game.payoffs[k][j][0]
            for k in range(game.rows)
            if k != i
            for j in range(game.columns)
        ):
            return i
    return None


def dominant_strategy_for_column(game: Game) -> int | None:
    """列の支配戦略。なければ None。"""
    for j in range(game.columns):
        if all(
            game.payoffs[i][j][1] > game.payoffs[i][k][1]
            for k in range(game.columns)
            if k != j
            for i in range(game.rows)
        ):
            return j
    return None


def pure_nash_equilibria(game: Game) -> list[tuple[int, int]]:
    """純粋戦略のナッシュ均衡（2 人とも、相手の戦略への最適反応になっている組）。"""
    return [
        (i, j)
        for i in range(game.rows)
        for j in range(game.columns)
        if i in best_responses_for_row(game, j)
        and j in best_responses_for_column(game, i)
    ]


def is_pareto_dominated(game: Game, cell: tuple[int, int]) -> bool:
    """別の組で、2 人とも悪くならず、少なくとも 1 人が良くなるなら、劣位。"""
    row, column = cell
    mine = game.payoffs[row][column]
    for i in range(game.rows):
        for j in range(game.columns):
            other = game.payoffs[i][j]
            if (
                other[0] >= mine[0]
                and other[1] >= mine[1]
                and (other[0] > mine[0] or other[1] > mine[1])
            ):
                return True
    return False


def is_prisoners_dilemma(game: Game) -> bool:
    """2×2 で T > R > P > S（行・列とも）なら、囚人のジレンマ。0 = 協調、1 = 裏切り。"""
    if game.rows != 2 or game.columns != 2:
        return False
    p = game.payoffs
    r, s, t, pun = p[0][0][0], p[0][1][0], p[1][0][0], p[1][1][0]
    row_ok = t > r > pun > s
    column_ok = (
        p[0][0][1] == r and p[1][0][1] == s and p[0][1][1] == t and p[1][1][1] == pun
    )
    return row_ok and column_ok
