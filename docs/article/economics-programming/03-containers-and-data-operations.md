---
type: Article
title: "第 3 章: コンテナとデータの操作"
description: "リスト・辞書・内包表記で需要表と供給表を表し、超過需要と市場均衡の価格を求める。"
tags: [article,economics-programming,python]
status: draft
generated: { by: claude-code/claude-sonnet-5-5, at: 2026-11-19T00:00:00Z }
---

# 第 3 章: コンテナとデータの操作

## 3.1 この章の地図

この章では、複数の値をまとめて扱うリストと辞書を学びます。需要表と供給表を作り、価格ごとの超過需要から、市場均衡の価格を探します。

| 項目 | 内容 |
| :--- | :--- |
| 経済学の題材 | 需要表・供給表、超過需要、市場均衡（マインドマップ 5-3） |
| 使う Python の機能 | リスト、辞書、内包表記、`in`、`Mapping` の型ヒント |
| 完成形 | `demand_schedule`、`supply_schedule`、`excess_demand`、`market_clearing_prices` |

### 経済学の式とコードの対応

| 経済学 | 意味 | コード |
| :--- | :--- | :--- |
| 需要曲線 Q = a − bP | 価格ごとの需要量 | 辞書 `{価格: 需要量}`（需要表） |
| 供給曲線 Q = c + dP | 価格ごとの供給量 | 辞書 `{価格: 供給量}`（供給表） |
| 超過需要 = 需要量 − 供給量 | 正なら品不足、負なら売れ残り | 辞書 `{価格: 超過需要}` |
| 市場均衡 | 超過需要が 0 になる価格 | 値が 0 の価格のリスト |

マインドマップの「調整過程」のとおり、超過需要が正なら価格は上がり、負なら下がります。

## 3.2 予想する

需要曲線を Q = 100 − 2P、供給曲線を Q = 3P として、価格が 0・10・20・30 のときの表を、紙に書いてください。

- 各価格の需要量と供給量は、いくつですか
- 超過需要が 0 になるのは、価格がいくつのときですか

答えは、需要量が 100・80・60・40、供給量が 0・30・60・90 で、価格 20 で超過需要が 0 です。式で 100 − 2P = 3P を解いても、P = 20 になります。

## 3.3 コンテナ

### リスト

順番に並んだ値の集まりが、リストです。価格を並べるのに使います。

```python
prices = [0, 10, 20, 30]
prices[1]    # 10   0 から数えて 2 番目
len(prices)  # 4
```

### 辞書

キーと値の組を持つのが、辞書です。「価格 → 数量」の対応を表すのに向いています。

```python
demand = {0: 100, 10: 80, 20: 60, 30: 40}
demand[20]      # 60
20 in demand    # True   キー 20 があるか
```

### 内包表記

リストや辞書を、1 行で作る書き方です。繰り返しの値から、新しい辞書を作ります。

```python
{p: 100 - 2 * p for p in [0, 10, 20, 30]}
# {0: 100, 10: 80, 20: 60, 30: 40}
```

## 3.4 Red → Green → Refactor

### Red: 供給量のテスト

供給関数 Q = c + dP は、第 1 章の練習問題で作った需要関数と同じ形です。

```python
def test_供給量は価格に比例して増える() -> None:
    assert quantity_supplied(price=10, intercept=0, slope=3) == 30


def test_負の価格は受け付けない() -> None:
    with pytest.raises(ValueError):
        quantity_supplied(price=-1, intercept=0, slope=3)
```

```python
def quantity_supplied(price: float, intercept: float, slope: float) -> float:
    """価格 P のときの供給量 Q = c + dP を返す。供給量は負にならない。"""
    if price < 0:
        raise ValueError("価格は 0 以上でなければならない")
    return max(intercept + slope * price, 0)
```

### 需要表と供給表

予想した表を、テストの期待値にします。

```python
PRICES = [0, 10, 20, 30]


def test_需要表は価格ごとの需要量を並べた辞書() -> None:
    assert demand_schedule(PRICES, intercept=100, slope=2) == {
        0: 100,
        10: 80,
        20: 60,
        30: 40,
    }
```

実装は、第 1 章の `quantity_demanded` を内包表記で繰り返すだけです。

```python
def demand_schedule(
    prices: list[int], intercept: float, slope: float
) -> dict[int, float]:
    """価格ごとの需要量を並べた需要表を返す。"""
    return {p: quantity_demanded(p, intercept, slope) for p in prices}


def supply_schedule(
    prices: list[int], intercept: float, slope: float
) -> dict[int, float]:
    """価格ごとの供給量を並べた供給表を返す。"""
    return {p: quantity_supplied(p, intercept, slope) for p in prices}
```

### 超過需要

2 つの表から、価格ごとに引き算をします。

```python
def test_超過需要は需要量から供給量を引いたもの() -> None:
    demand = demand_schedule(PRICES, intercept=100, slope=2)
    supply = supply_schedule(PRICES, intercept=0, slope=3)
    assert excess_demand(demand, supply) == {0: 100, 10: 50, 20: 0, 30: -50}
```

2 つの表で価格が違う場合は、両方にある価格だけを扱うことも、テストで決めます。

```python
def test_需要表と供給表で価格が共通でなければ超過需要は共通の価格だけ求める() -> None:
    demand = {10: 80, 20: 60}
    supply = {20: 60, 30: 90}
    assert excess_demand(demand, supply) == {20: 0}
```

```python
def excess_demand(
    demand: Mapping[int, float], supply: Mapping[int, float]
) -> dict[int, float]:
    """価格ごとの超過需要（需要量 - 供給量）を返す。両方の表にある価格だけを扱う。"""
    return {p: demand[p] - supply[p] for p in demand if p in supply}
```

引数の型を `dict` ではなく `Mapping`（読み取り専用の辞書）にしているのは、値が整数の辞書 `dict[int, int]` も渡せるようにするためです。

### 市場均衡の価格

超過需要が 0 になる価格だけを取り出します。

```python
def test_超過需要が0になる価格が市場均衡の価格() -> None:
    demand = demand_schedule(PRICES, intercept=100, slope=2)
    supply = supply_schedule(PRICES, intercept=0, slope=3)
    assert market_clearing_prices(demand, supply) == [20]
```

```python
def market_clearing_prices(
    demand: Mapping[int, float], supply: Mapping[int, float]
) -> list[int]:
    """超過需要が 0 になる価格（市場均衡の価格）を返す。"""
    return [p for p, gap in excess_demand(demand, supply).items() if gap == 0]
```

### 実行結果

```bash
cd apps/python
uv run pytest
```

```text
22 passed
```

## 3.5 規則で言うと

1. **「A ごとの B」は辞書にする。** 価格ごとの数量のように、対応を表すものは `{キー: 値}` にする
2. **順序のある並びはリスト、対応は辞書。** 選ぶ基準は「順番が大事か、キーで引きたいか」
3. **繰り返しで新しい表を作るときは、内包表記を使う。** `{p: f(p) for p in prices}` の形が、表の変換の基本形になる

混同しやすい点を、表にまとめます。

| 混同しやすい点 | 違い |
| :--- | :--- |
| 超過需要が正と負 | 正は需要が多すぎる（品不足）ので価格が上がる。負は供給が多すぎる（売れ残り）ので価格が下がる |
| 需要表を 1 本の表にまとめるか | 需要量と供給量を別々の辞書にしておくと、後から片方だけを変えて比較できる |

### このモデルが成り立たない場面

この章の方法は、均衡の価格が、表に載せた価格の中にあるときだけ見つかります。たとえば価格を 0・10・30 の 3 つにすると、均衡の 20 は表にないので、`market_clearing_prices` は空のリストを返します。実際には、均衡価格が表の価格と一致するとは限りません。第 5 章で、価格を少しずつ動かして均衡を探す方法を学びます。

## 3.6 練習問題

| 種類 | 問題 |
| :--- | :--- |
| 想起 | 本文を閉じて、`demand_schedule` を内包表記で書いてください |
| 生成 | 解説を見る前に、超過需要が正の価格だけを取り出す `shortage_prices` を、テストから書いてください（上の例では `[0, 10]`） |
| 多様 | 需要を Q = 120 − 2P に変えて、均衡の価格を手計算し、テストで確かめてください（P = 24 は価格 `[0, 12, 24, 36]` に含まれます） |
| 交互 | 第 2 章の `price_elasticity` を使い、需要表の隣り合う 2 点（価格 10 → 20）の価格弾力性を求めてください |

## 3.7 振り返り

- 予想した表と、テストの期待値は一致しましたか
- 内包表記と、繰り返しの書き方（第 5 章）の違いは、何だと思いますか
- 価格を 3 つだけにしたとき、何が起きましたか

## 3.8 まとめ

- リスト、辞書、内包表記を学んだ
- 需要表・供給表を辞書で表し、超過需要と市場均衡の価格を求めた
- 表に載せた価格の中にしか均衡は見つからない、という限界を確認した

次の章では、関数とメソッドを学び、効用関数と費用関数を作ります。
