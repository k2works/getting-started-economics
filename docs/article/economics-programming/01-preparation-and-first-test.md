---
type: Article
title: "第 1 章: 準備とはじめてのテスト"
description: "需要曲線 Q = a − bP を関数にして、pytest でテストを先に書きながら最初のプログラムを作る。"
tags: [article,economics-programming,python]
status: draft
generated: { by: claude-code/claude-sonnet-5-5, at: 2026-11-19T00:00:00Z }
---

# 第 1 章: 準備とはじめてのテスト

## 1.1 この章の地図

この章では、経済学の最初の式である需要曲線を、Python の関数にします。そして、テストを先に書いてから関数を作る手順（テスト駆動開発、TDD）を体験します。

| 項目 | 内容 |
| :--- | :--- |
| 経済学の題材 | 需要曲線 Q = a − bP（マインドマップ [5-1](<../経済学・経済政策 トピック別マインドマップ.md#t1>)） |
| 使う Python の機能 | 関数、`if`、`max`、例外、型ヒント |
| 完成形 | 価格を入れると需要量を返す `quantity_demanded` 関数と、5 つのテスト |

### 既に知っていることとの対応

表計算ソフトで「価格」の列から「需要量」の列を式で計算したことがあれば、関数はその式に名前を付けたものです。

| 表計算 | Python |
| :--- | :--- |
| セルの式 `=100-2*A2` | 関数 `quantity_demanded(price, intercept, slope)` |
| セル `A2` の値 | 引数 `price` |
| 式を書き換えて結果を目で確かめる | テストを書いて、結果を自動で確かめる |

### 経済学の式とコードの対応

需要曲線 Q = a − bP は、価格 P が 1 上がると需要量 Q が b だけ減る関係を表します。

| 式の記号 | 意味 | コードの名前 |
| :--- | :--- | :--- |
| P | 価格 | `price` |
| Q | 需要量 | 関数の戻り値 |
| a | 切片（価格が 0 のときの需要量） | `intercept` |
| b | 傾き（価格が 1 上がると減る量） | `slope` |

## 1.2 環境を準備する

必要なものは、Python のパッケージ管理ツール [uv](https://docs.astral.sh/uv/) です。次のコマンドで、サンプルコードのテストが動く状態にします。

```bash
cd apps/economics-programming/python
uv sync
uv run pytest
```

サンプルコードは `apps/economics-programming/python/` にあります。実装は `lib/chapter01/`、テストは `test/chapter01/` です。

## 1.3 予想する

コードを読む前に、次の問いに自分で答えてみてください。紙に書くのがお勧めです。

- 需要曲線が Q = 100 − 2P のとき、価格が 0 のとき、需要量はいくつですか
- 価格が 10 のとき、需要量はいくつですか
- 価格が 60 のとき、需要量はいくつですか。式のとおりに計算すると、困ったことになりませんか

3 つ目で「マイナスになる」と気づいたら、経済学の感覚が働いています。需要量は負にならないので、コードでこの場面を扱う必要があります。

## 1.4 Red → Green → Refactor

### Red: 最初のテストを書く

最初に、実装がまだない関数のテストを書きます。価格が 0 なら、需要量は切片 a と等しいはずです。

```python
def test_価格が0なら需要量は切片と等しい() -> None:
    assert quantity_demanded(price=0, intercept=100, slope=2) == 100
```

実行すると、関数がないので失敗します。失敗を確かめることが大切です。

```text
ModuleNotFoundError: No module named 'lib.chapter01.demand'
```

### Green: 最小の実装で通す

テストを通す最小の実装は、式をそのまま書くことです。

```python
def quantity_demanded(price: float, intercept: float, slope: float) -> float:
    return intercept - slope * price
```

### 次のテストを足す

予想した 2 つ目と 3 つ目の問いを、テストにします。

```python
def test_価格が上がると需要量は傾きの分だけ減る() -> None:
    assert quantity_demanded(price=10, intercept=100, slope=2) == 80


def test_価格が高すぎると需要量は0になる() -> None:
    assert quantity_demanded(price=60, intercept=100, slope=2) == 0
```

3 つ目のテストは、式のとおりだと −20 になるので失敗します。需要量が負にならないよう、`max` で 0 を下限にします。

```python
def quantity_demanded(price: float, intercept: float, slope: float) -> float:
    return max(intercept - slope * price, 0)
```

価格が負の入力は、経済学の意味がありません。これもテストで先に決めます。

```python
def test_負の価格は受け付けない() -> None:
    with pytest.raises(ValueError):
        quantity_demanded(price=-1, intercept=100, slope=2)
```

### Refactor: 完成した実装

テストがすべて通ったら、名前と説明を整えます。需要量がちょうど 0 になる価格（`choke_price`）も、同じ手順で追加します。

```python
def quantity_demanded(price: float, intercept: float, slope: float) -> float:
    """価格 P のときの需要量 Q = a - bP を返す。需要量は負にならない。"""
    if price < 0:
        raise ValueError("価格は 0 以上でなければならない")
    return max(intercept - slope * price, 0)


def choke_price(intercept: float, slope: float) -> float:
    """需要量がちょうど 0 になる価格 P = a / b を返す。"""
    return intercept / slope
```

```python
def test_需要が0になる最低の価格を求める() -> None:
    assert choke_price(intercept=100, slope=2) == 50
```

テストを実行すると、5 つのテストがすべて通ります。

```bash
cd apps/economics-programming/python
uv run pytest test/chapter01
```

```text
5 passed
```

章ごとにテストを実行するときは、`uv run pytest test/chapter02` のように、章のディレクトリを指定します。全章分をまとめて実行するときは、ディレクトリを指定せずに `uv run pytest` とします。

## 1.5 規則で言うと

この章で身につけたことを、原則にまとめます。

1. **式は関数にする。** 経済学の式 1 つを、名前の付いた関数 1 つにする。引数の名前は、式の記号の意味に合わせる
2. **先にテストを書く。** 手で計算できる値（ここでは 100、80、0、50）を期待値にして、関数が正しいことを確かめる
3. **経済学の制約をコードにする。** 「需要量は負にならない」「価格は負にならない」といった、式に書かれていない前提を、テストで先に決める

混同しやすい点を、表にまとめます。

| 混同しやすい点 | 違い |
| :--- | :--- |
| 需要の変化と需要量の変化 | 価格が変わって曲線上を動くのは「需要量の変化」。切片 a が変わって曲線が動くのは「需要の変化」 |
| 傾き b と曲線の見た目 | 式 Q = a − bP では b が大きいほど、価格が上がったときの需要量の減り方が大きい。グラフ（縦軸が P）では傾きが緩やかに見える |

## 1.6 練習問題

| 種類 | 問題 |
| :--- | :--- |
| 想起 | 本文を閉じて、`quantity_demanded` を自分で書いてください。その後、本文と見比べて違いを確かめます |
| 生成 | 供給曲線 Q = c + dP の関数 `quantity_supplied` を、解説を見る前に、テストから書いてください。価格が 0 のときの供給量は c です |
| 多様 | `intercept=100, slope=2` を `intercept=50, slope=5` に変えて、5 つのテストの期待値を手計算で作り直してください |
| 交互 | 需要曲線と供給曲線を使って、需要量と供給量が等しくなる価格を、紙の上で求めてください（第 5 章で、コードで求めます） |

## 1.7 振り返り

次の 3 つを、短くノートに書いてください。

- 予想した値と、テストの期待値は一致しましたか。違っていたら、何が原因でしたか
- 詰まった所はどこでしたか
- 次の章までに試してみたいことは何ですか

## 1.8 まとめ

- 需要曲線 Q = a − bP を、`quantity_demanded` 関数にした
- テストを先に書いて失敗を確かめ、最小の実装で通し、整える手順（Red → Green → Refactor）を体験した
- 経済学の制約（需要量・価格は負にならない）は、式に書かれていなくてもテストで決める

次の章では、データ型と変数を学び、価格弾力性と所得弾力性を計算します。
