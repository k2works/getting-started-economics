---
type: Article
title: "第 12 章: 寡占とゲーム理論（1）: 利得表とナッシュ均衡"
description: "利得表から最適反応・支配戦略・ナッシュ均衡を求め、囚人のジレンマで均衡が非効率になる（パレート劣位）ことを確かめる。協調ゲームと一致ゲームで、均衡が 2 つある場合と、純粋戦略の均衡がない場合も見る。"
tags: [article,micro-basics-programming,python]
status: draft
generated: { by: claude-code/claude-sonnet-5-5, at: 2026-11-22T00:00:00Z }
---

# 第 12 章: 寡占とゲーム理論（1）: 利得表とナッシュ均衡

## 12.1 この章の地図

売り手が**少数**の市場（**寡占**）では、自分の最善の行動が、**相手の行動**に依存します。相手の出方を読み合う状況を、**ゲーム**として扱います。この章では、次のことを関数にします。

- **利得表**から、相手の戦略に対する**最適反応**、どんな相手にも最善の**支配戦略**、2 人とも最適反応になっている**ナッシュ均衡**を求める
- **囚人のジレンマ**: 均衡（裏切り、裏切り）が、協調（協調、協調）より、**2 人とも悪い**（パレート劣位）
- **協調ゲーム・一致ゲーム**: 均衡が 2 つある場合と、純粋戦略の均衡がない場合

次の章（第 13 章）では、同じゲームを**繰り返し**、協調が続く条件（割引因子の閾値）と、寡占の**屈折需要曲線**を扱います。

| | 列: 協調 | 列: 裏切り |
| :---: | :---: | :---: |
| **行: 協調** | (3, 3) | (0, 5) |
| **行: 裏切り** | (5, 0) | (1, 1) |

この章で扱う囚人のジレンマの利得表です（括弧の中は、(行の利得, 列の利得)）。

| 項目 | 内容 |
| :--- | :--- |
| 経済学の題材 | 利得表、最適反応、支配戦略、ナッシュ均衡、パレート劣位、囚人のジレンマ、協調ゲーム・一致ゲーム |
| 使う Python の機能 | `dataclass`、タプルの入れ子、関数、内包表記、テスト（`pytest`） |
| 新しく導入するライブラリ | なし |
| 完成形 | `Game`、`prisoners_dilemma`、`best_responses_for_row`、`best_responses_for_column`、`dominant_strategy_for_row`、`dominant_strategy_for_column`、`pure_nash_equilibria`、`is_pareto_dominated`、`is_prisoners_dilemma` |
| ファイル | 実装: `lib/chapter12/game.py`／テスト: `test/chapter12/test_game.py`（自分で書くときは、`practice/chapter12/` に、同じ名前で作ります） |
| データ | なし（手計算できる小さな例だけ） |

### 経済学の式とコードの対応

| 経済学 | 式 | コード |
| :--- | :--- | :--- |
| 利得表 | payoffs[i][j] = (行の利得, 列の利得) | `Game(payoffs)` |
| 最適反応 | 相手の戦略を与えて、自分の利得が最大の戦略 | `best_responses_for_row(game, column)` |
| 支配戦略 | 相手が何をしても、他より厳密に良い戦略 | `dominant_strategy_for_row(game)` |
| ナッシュ均衡 | 2 人とも、相手の戦略への最適反応 | `pure_nash_equilibria(game)` |
| 囚人のジレンマ | T > R > P > S | `prisoners_dilemma(T, R, P, S)` |

> **記号の注意**: この章の T・R・P・S は、囚人のジレンマの利得（誘惑・報酬・罰・愚か者）です。第 7・9・10 章の T（税額・関税）や、P（価格）とは、別の意味です。

### 前提とする章

| できること | 場所 |
| :--- | :--- |
| 独占の限界収入と、完全競争との比較 | この連載の[第 11 章](11-monopoly-and-monopolistic-competition.md) |
| 関数・タプル・内包表記 | [第 1 シリーズ](../economics-programming/index.md)の第 3 章。ゲーム理論は、第 15 章でも扱っています（この連載は、関数にして、テストで確かめます） |

## 12.2 準備

```bash
cd apps/micro-basics-programming/python
uv sync
uv run pytest test/chapter12
```

```text
26 passed
```

自分でコードを書くときは、`practice/chapter12/` に、`game.py` と、そのテスト（`test_game.py`）を作ります。

## 12.3 予想する

囚人のジレンマです。2 人が、協調（0）か裏切り（1）を選びます。利得は、誘惑 T = 5、報酬 R = 3、罰 P = 1、愚か者 S = 0（相手が裏切り、自分が協調したときの利得）です。**紙で、手計算で**答えてください。答えは、この節には書いてありません。「プログラミング」の節の「予想の答え合わせ」で、プログラムを動かして確かめます。

- 相手が協調するとき・裏切るとき、自分の**最適反応**は、それぞれ、何ですか。**支配戦略**は、ありますか
- **ナッシュ均衡**は、どの組ですか。それは、2 人にとって、**最善の組**ですか（パレート劣位か）

## 12.4 寡占とゲーム理論（1）の考え方

### 利得表

2 人の戦略と利得を、表にします。行の人が戦略 i、列の人が戦略 j を選んだときの利得を、(行の利得, 列の利得) と書きます。

| | 列: 協調 | 列: 裏切り |
| :---: | :---: | :---: |
| **行: 協調** | (3, 3) | (0, 5) |
| **行: 裏切り** | (5, 0) | (1, 1) |

### 最適反応・支配戦略・ナッシュ均衡

- **最適反応**: 相手の戦略を与えられたとき、自分の利得が最大になる戦略
- **支配戦略**: 相手が**何をしても**、他のどの戦略より、厳密に良い戦略。あれば、それを選ぶ
- **ナッシュ均衡**: 2 人とも、相手の戦略に対して、**最適反応になっている**組。誰も、一人では、戦略を変えたくない

### 囚人のジレンマ

上の表では、相手が何をしても、**裏切りが最適反応**（支配戦略）です。だから、均衡は（裏切り、裏切り）で、利得は (1, 1)。（協調、協調）の (3, 3) の方が、**2 人とも良い**のに、そこへは行けません。個人の合理性が、全体の非効率を生みます。寡占企業の**カルテル**（価格を高く保つ約束）が、破られやすい理由です。

## 12.5 プログラミング

### Red: 囚人のジレンマの利得表

最初のテストを書きます。戦略 0 が協調、戦略 1 が裏切りで、利得表は、上の表のとおりです。

```python
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
```

```python
DILEMMA = prisoners_dilemma(temptation=5, reward=3, punishment=1, sucker=0)


COORDINATION = Game(
    (
        ((2, 2), (0, 0)),
        ((0, 0), (1, 1)),
    )
)


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
```

`Game` などがまだないので、テストは失敗します（**Red**）。テストの import は、書いた関数だけを、1 つずつ足してかまいません（[第 5 章](05-cost-curves.md)の注意を参照）。

### Green: 利得表と囚人のジレンマ

利得表は、`payoffs[i][j] = (行の利得, 列の利得)` の入れ子のタプルです。形が長方形で、空でないことは、`__post_init__` で、作るときに検査します。

```python
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
```

??? note "import と補助関数（写すときに足す）"

    記事の抜粋には、import と、先頭が `_` の補助関数・定数を、省いています。完成形のファイルの先頭にある、次の部分を、写してください。

    **lib/chapter12/game.py**

    ```python
    from dataclasses import dataclass
    ```

    ```python
    def _check_strategy(index: int, count: int) -> None:
        if not 0 <= index < count:
            raise ValueError("戦略の番号が、範囲外です")
    ```

    ```python
    def _best(values: list[float]) -> list[int]:
        top = max(values)
        return [i for i, value in enumerate(values) if value == top]
    ```

### 最適反応・支配戦略

```python
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
```

```python
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
```

最適反応は、同点なら、**すべて**返します（利得が等しい戦略は、どれも最適）。支配戦略は、**厳密に**良い戦略だけで、なければ `None` です。

### ナッシュ均衡とパレート劣位

```python
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
```

```python
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
```

協調ゲーム（同じ戦略をそろえると得）では、均衡が 2 つあり、一致ゲーム（行は手をそろえたく、列は違う手を出したい）では、**純粋戦略の均衡がありません**（混合戦略が必要ですが、この章は扱いません）。

### 予想の答え合わせ

予想した答えを、プログラムで確かめます。

> このスクリプトは、**完成形**（`lib/`）を読みます。**自分のコードで確かめる**ときは、import を、`from practice.chapterNN...` に書き換えてください。

```python
from lib.chapter12.game import (
    Game,
    best_responses_for_column,
    best_responses_for_row,
    dominant_strategy_for_row,
    is_pareto_dominated,
    is_prisoners_dilemma,
    prisoners_dilemma,
    pure_nash_equilibria,
)

game = prisoners_dilemma(temptation=5, reward=3, punishment=1, sucker=0)
print("囚人のジレンマか:", is_prisoners_dilemma(game))
print("行の最適反応 列が協調・裏切り:", best_responses_for_row(game, 0), best_responses_for_row(game, 1))
print("列の最適反応 行が協調・裏切り:", best_responses_for_column(game, 0), best_responses_for_column(game, 1))
print("行の支配戦略:", dominant_strategy_for_row(game))
print("ナッシュ均衡:", pure_nash_equilibria(game), "パレート劣位 (裏切り, 裏切り):", is_pareto_dominated(game, (1, 1)))
coordination = Game((((2, 2), (0, 0)), ((0, 0), (1, 1))))
print("協調ゲームの均衡:", pure_nash_equilibria(coordination))
```

```text
囚人のジレンマか: True
行の最適反応 列が協調・裏切り: [1] [1]
列の最適反応 行が協調・裏切り: [1] [1]
行の支配戦略: 1
ナッシュ均衡: [(1, 1)] パレート劣位 (裏切り, 裏切り): True
協調ゲームの均衡: [(0, 0), (1, 1)]
```

- **1 つ目の問い**: 相手が協調でも裏切りでも、最適反応は**裏切り**（支配戦略）です
- **2 つ目の問い**: ナッシュ均衡は（裏切り、裏切り）だけで、(1, 1) は、（協調、協調）の (3, 3) に、**パレート劣位**です
- **協調ゲーム**（同じ戦略をそろえると得）では、均衡が 2 つあります（[(0, 0), (1, 1)]）

### 実行結果

```bash
uv run pytest test/chapter12
```

```text
26 passed
```

## 12.6 規則で言うと

1. **相手の戦略を所与として、最適反応を選ぶ。** 2 人とも最適反応の組が、ナッシュ均衡
2. **囚人のジレンマでは、支配戦略の均衡が、パレート劣位になる。** 個人の合理性が、全体の非効率を生む

混同しやすい点を、表にまとめます。

| 混同しやすい点 | 違い |
| :--- | :--- |
| 支配戦略とナッシュ均衡 | 支配戦略は、相手が**何をしても**最善。ナッシュ均衡は、相手の**その戦略**に対して最善。支配戦略の組は、必ず均衡だが、逆は成り立たない |
| ナッシュ均衡と効率 | 均衡は、一人で変えたくない組であって、**全体で最善**とは限らない（囚人のジレンマ） |
| 最適反応が複数 | 利得が同点なら、最適反応は**すべて**。支配戦略は、**厳密に**良いものだけ |

### このモデルが成り立たない場面

- **純粋戦略だけを扱いました。** 混合戦略（確率的に選ぶ）の均衡は、扱っていません。一致ゲームの均衡は、混合戦略にあります
- **2 人・同時手番だけです。** 順番に選ぶゲーム（先手・後手）や、3 人以上は、扱っていません
- **利得は、すべて分かっている（完備情報）と仮定しました。** 相手の利得を知らない場合は、扱っていません

## 12.7 練習問題

| 種類 | 問題 |
| :--- | :--- |
| 想起 | 本文を閉じて、囚人のジレンマのナッシュ均衡が（裏切り、裏切り）だけであるテストを書いてください |
| 生成 | 解説を見る前に、組 (i, j) が**ナッシュ均衡かどうか**を返す `is_nash_equilibrium(game, cell)` を、テストから書いてください。囚人のジレンマで (1, 1) は真、(0, 0) は偽です |
| 多様 | 誘惑 T を 5 から 7 に上げても、ナッシュ均衡は、変わりますか。先に予想してから、確かめてください |
| 交互 | [第 1 シリーズ](../economics-programming/index.md)の第 3 章のリスト内包表記で、T = 4〜10 のナッシュ均衡を、一度に求めてください（R = 3、P = 1、S = 0）。T が大きいと、均衡は、どうなりますか |

??? note "解答（先に自分で取り組んでから、開いてください）"

    **想起**:

    ```python
    def test_練習問題のナッシュ均衡() -> None:
        game = prisoners_dilemma(5, 3, 1, 0)
        assert pure_nash_equilibria(game) == [(1, 1)]
    ```

    **生成**: 行も列も、最適反応になっているかを、調べます。

    ```python
    def is_nash_equilibrium(game, cell):
        row, column = cell
        return row in best_responses_for_row(game, column) and column in best_responses_for_column(game, row)
    ```

    ```python
    def test_練習問題のナッシュ均衡の判定() -> None:
        game = prisoners_dilemma(5, 3, 1, 0)
        assert is_nash_equilibrium(game, (1, 1))
        assert not is_nash_equilibrium(game, (0, 0))
    ```

    **多様**: T = 7 でも、裏切りは、相手が何をしても最適反応のままで、均衡は（裏切り、裏切り）だけです。T > R > P > S が成り立つ限り、均衡は変わりません。

    ```python
    def test_練習問題の誘惑が大きい場合() -> None:
        assert pure_nash_equilibria(prisoners_dilemma(7, 3, 1, 0)) == [(1, 1)]
    ```

    **交互**: T = 4〜10 のどれでも、均衡は同じです。

    ```python
    def test_練習問題の誘惑とナッシュ均衡() -> None:
        results = [pure_nash_equilibria(prisoners_dilemma(t, 3, 1, 0)) for t in range(4, 11)]
        assert results == [[(1, 1)]] * 7
    ```

## 12.8 振り返り

- うまくいったこと:
- 詰まったこと:
- 次に試すこと:

## 12.9 まとめ

- 利得表から、最適反応・支配戦略・ナッシュ均衡を求められる。囚人のジレンマでは、均衡（裏切り、裏切り）が、協調よりパレート劣位になる
- 協調ゲームでは、均衡が 2 つあり、一致ゲームでは、純粋戦略の均衡がない

次の章では、同じゲームを**繰り返し**ます。将来の報復があると、協調が続くことがあります。トリガー戦略で協調が続く**割引因子の閾値**と、しっぺ返し、寡占の**屈折需要曲線**（価格の硬直性）を、確かめます。
