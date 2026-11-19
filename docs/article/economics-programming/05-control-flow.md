---
type: Article
title: "第 5 章: 制御フロー"
description: "条件分岐と繰り返しで、ワルラス調整とマーシャル調整が均衡に向かう様子をコードで動かす。"
tags: [article,economics-programming,python]
status: draft
generated: { by: claude-code/claude-sonnet-5-5, at: 2026-11-19T00:00:00Z }
---

# 第 5 章: 制御フロー

## 5.1 この章の地図

この章では、`if` による条件分岐と、`for` による繰り返しを学びます。第 3 章では、価格の表に均衡がないと見つけられませんでした。この章では、価格を少しずつ動かして、均衡に近づける方法を使います。

| 項目 | 内容 |
| :--- | :--- |
| 経済学の題材 | ワルラス調整（価格で調整）とマーシャル調整（数量で調整）（マインドマップ [5-3](<../経済学・経済政策 トピック別マインドマップ.md#t3>)） |
| 使う Python の機能 | `if` / `elif` / `else`、`for`、`range`、`return` での途中終了、関数を引数に渡す |
| 完成形 | `market_state`、`walras_path`、`marshall_path` |

### 経済学の式とコードの対応

| 経済学 | 式 | コード |
| :--- | :--- | :--- |
| ワルラス調整 | 価格の変化 = k × 超過需要 | `price += step * excess` |
| マーシャル調整 | 数量の変化 = k × (需要価格 − 供給価格) | `quantity += step * gap` |
| 調整の速さ k | 調整の 1 回で、どれだけ動かすか | 引数 `step` |
| 均衡 | 超過需要（または価格の差）が 0 | `abs(excess) < tolerance` |

需要曲線 Q = 100 − 2P と供給曲線 Q = 3P を、引き続き使います。

## 5.2 予想する

ワルラス調整で、価格を 0 から始め、調整の速さ k = 0.1 とします。

- 価格 0 のとき、超過需要はいくつですか。1 回調整すると、価格はいくつになりますか
- 2 回目の調整の後、価格はいくつになりますか
- k = 0.5 にすると、価格は均衡の 20 に近づくでしょうか

答えは、超過需要 100 なので 1 回後の価格は 0 + 0.1 × 100 = 10、2 回目は超過需要 50 なので 10 + 0.1 × 50 = 15 です。3 つ目は、手で数回計算してみてください。20 に近づかず、行き過ぎて振動が大きくなります。

## 5.3 制御フロー

### 条件分岐: if

条件によって、実行する処理を分けます。

```python
if excess_demand > 0:
    state = "品不足"
elif excess_demand < 0:
    state = "売れ残り"
else:
    state = "均衡"
```

### 繰り返し: for

決まった回数だけ、処理を繰り返します。`range(5)` は 0 から 4 までの 5 個の数を作ります。

```python
for i in range(5):
    print(i)    # 0 1 2 3 4
```

### 関数を引数に渡す

調整のコードでは、需要と供給の式を、引数として受け取ります。関数も、数や文字列と同じように、引数に渡せます。

```python
def demand(price: float) -> float:
    return 100 - 2 * price


walras_path(demand, supply, initial_price=0, step=0.1)
```

これで、需要曲線や供給曲線の式を変えても、調整のコードは変えずに済みます。

## 5.4 Red → Green → Refactor

### 市場の状態

```python
@pytest.mark.parametrize(
    ("excess", "expected"),
    [(50, "品不足"), (-50, "売れ残り"), (0, "均衡"), (1e-12, "均衡")],
)
def test_超過需要から市場の状態を判定する(excess: float, expected: str) -> None:
    assert market_state(excess) == expected
```

```python
def market_state(excess_demand: float, tolerance: float = 1e-9) -> str:
    """超過需要から市場の状態（品不足・売れ残り・均衡）を返す。"""
    if abs(excess_demand) <= tolerance:
        return "均衡"
    if excess_demand > 0:
        return "品不足"
    return "売れ残り"
```

第 2 章で学んだとおり、小数の 0 は誤差を含むので、「0 に十分近い」を許容誤差 `tolerance` で判定します。

### ワルラス調整

テストでは、予想した手計算の値を使います。

```python
def demand(price: float) -> float:
    return 100 - 2 * price


def supply(price: float) -> float:
    return 3 * price


def test_ワルラス調整の最初の2回は手計算と一致する() -> None:
    path = walras_path(demand, supply, initial_price=0, step=0.1)
    # 超過需要 100 のとき、価格は 0 + 0.1 * 100 = 10。次は 10 + 0.1 * 50 = 15
    assert path[:3] == pytest.approx([0, 10, 15])


def test_ワルラス調整は均衡価格20に収束する() -> None:
    path = walras_path(demand, supply, initial_price=0, step=0.1)
    assert path[-1] == pytest.approx(20, abs=1e-6)


def test_ワルラス調整は初期価格が均衡価格なら動かない() -> None:
    assert walras_path(demand, supply, initial_price=20, step=0.1) == [20]


def test_調整の速さが大きすぎるとワルラス調整は収束しない() -> None:
    with pytest.raises(RuntimeError):
        walras_path(demand, supply, initial_price=0, step=0.5)
```

```python
def walras_path(
    demand: Callable[[float], float],
    supply: Callable[[float], float],
    initial_price: float,
    step: float,
    tolerance: float = 1e-6,
    max_iterations: int = 1000,
) -> list[float]:
    """ワルラス調整: 超過需要に比例して価格を動かし、価格の推移を返す。"""
    price = initial_price
    path = [price]
    for _ in range(max_iterations):
        excess = demand(price) - supply(price)
        if abs(excess) < tolerance:
            return path
        price += step * excess
        path.append(price)
    raise RuntimeError("価格が収束しなかった。調整の速さ step を小さくする")
```

`for` の繰り返しの中で、均衡に達したら `return` で途中で終わります。`max_iterations` で回数に上限を付けているのは、収束しない場合に、永久に終わらなくなるのを避けるためです。

実際に動かすと、価格は 0 → 10 → 15 → 17.5 → 18.75 と近づき、27 回の調整で 19.999999850988388 になります。

### マーシャル調整

ワルラス調整が「価格を動かす」のに対して、マーシャル調整は「数量を動かす」方法です。需要価格（その数量で買い手が払ってよい価格）が供給価格（売り手が受け取りたい価格）より高いと、数量が増えます。

```python
def demand_price(quantity: float) -> float:
    # 需要曲線 Q = 100 - 2P を P について解いた逆需要曲線
    return (100 - quantity) / 2


def supply_price(quantity: float) -> float:
    # 供給曲線 Q = 3P を P について解いた逆供給曲線
    return quantity / 3


def test_マーシャル調整は均衡数量60に収束する() -> None:
    path = marshall_path(demand_price, supply_price, initial_quantity=0, step=0.1)
    assert path[-1] == pytest.approx(60, abs=1e-4)
```

```python
def marshall_path(
    demand_price: Callable[[float], float],
    supply_price: Callable[[float], float],
    initial_quantity: float,
    step: float,
    tolerance: float = 1e-6,
    max_iterations: int = 1000,
) -> list[float]:
    """マーシャル調整: 需要価格と供給価格の差に比例して数量を動かし、推移を返す。"""
    quantity = initial_quantity
    path = [quantity]
    for _ in range(max_iterations):
        gap = demand_price(quantity) - supply_price(quantity)
        if abs(gap) < tolerance:
            return path
        quantity += step * gap
        path.append(quantity)
    raise RuntimeError("数量が収束しなかった。調整の速さ step を小さくする")
```

同じ k = 0.1 でも、数量が 0 → 5 → 9.58 → 13.78 と動き、収束まで 204 回かかり、最後の値は 59.99999882703561 です。ワルラス調整の 27 回より、ずっと遅くなります。

### 実行結果

```bash
cd apps/economics-programming/python
uv run pytest
```

```text
52 passed
```

## 5.5 規則で言うと

1. **繰り返しには、必ず終わりの条件と上限を付ける。** 「十分に近づいたら終わり」と「回数の上限」の両方を書く
2. **収束するかどうかは、調整の速さ k で決まる。** この例では、ワルラス調整は 0 < k < 0.4、マーシャル調整は 0 < k < 2.4 のときだけ収束する
3. **式が変わっても調整のコードを変えないよう、式を関数として引数に渡す**

収束の条件は、式から分かります。ワルラス調整の 1 回の更新は、p ← p + k(100 − 5p) = (1 − 5k)p + 100k です。均衡との差が毎回 (1 − 5k) 倍になるので、|1 − 5k| < 1、つまり 0 < k < 0.4 のときだけ、差が縮みます。k = 0.5 では、1 − 5k = −1.5 となり、差が毎回 1.5 倍になって広がります。

混同しやすい点を、表にまとめます。

| 混同しやすい点 | 違い |
| :--- | :--- |
| ワルラス調整とマーシャル調整 | ワルラスは超過需要で価格を動かす。マーシャルは需要価格と供給価格の差で数量を動かす |
| 超過需要が正のとき、価格は | 上がる（品不足）。負のときは下がる（売れ残り） |

### このモデルが成り立たない場面

この章の調整は、価格が毎回、均衡に近づく前提です。需要と供給の傾きによっては、均衡のまわりを行き来して近づかない（または遠ざかる）ことがあります。また、現実の市場は、毎回同じ速さで調整するとは限りません。収束するかどうかは、実際に動かして確かめる必要があります。

## 5.6 練習問題

| 種類 | 問題 |
| :--- | :--- |
| 想起 | 本文を閉じて、`market_state` を自分で書いてください |
| 生成 | 解説を見る前に、価格が均衡の 20 に最初に近づく（差が 1 未満になる）までの回数を返す関数を、テストから書いてください。初期価格 0、k = 0.1 のとき、手計算で 5 回です（0 → 10 → 15 → 17.5 → 18.75 → 19.375） |
| 多様 | k を 0.2 と 0.4 にしたとき、何回で収束するか、または収束しないか、実行して確かめてください（k = 0.4 は境界で、1 − 5k = −1 なので収束しません） |
| 交互 | 第 3 章の需要表と、この章のワルラス調整の違いを、「均衡の価格が表にないとき」を例に説明してください |

## 5.7 振り返り

- k = 0.5 の予想は当たりましたか。当たらなかったなら、どこで計算が違いましたか
- ワルラス調整とマーシャル調整の収束の速さの違いを、どう説明しますか
- 繰り返しに上限を付けなかったら、何が起きるでしょうか

## 5.8 まとめ

- `if`・`elif`・`else` と `for`、途中終了の `return` を学んだ
- 価格を動かすワルラス調整と、数量を動かすマーシャル調整を実装した
- 調整の速さが大きすぎると収束しないことを、式とテストで確かめた

次の章では、モジュール、エラー、アルゴリズムを学び、二分法で均衡価格を求めます。
