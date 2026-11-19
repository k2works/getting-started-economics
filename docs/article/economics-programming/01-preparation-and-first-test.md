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
| ファイル | 実装: `lib/chapter01/demand.py`／テスト: `test/chapter01/test_demand.py`（自分で書くときは、`practice/chapter01/` に、同じ名前で作ります） |

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

> **記号について**: この記事では、需要曲線を Q = a − bP、供給曲線を Q = c + dP と書きます（第 3 章以降で使います）。ただし、a・b・c などの記号は、章によって、別の意味で使うものがあります（たとえば、第 9 章の c は、限界消費性向です）。そのときは、その章の表の下に、注記があります。一覧は、[記号について](how-to-read.md#symbols) を参照してください。

## 1.2 環境を準備する

### 必要なもの

| 必要なもの | 説明 |
| :--- | :--- |
| ターミナル | コマンドを打ち込む画面。Windows は「PowerShell」、macOS は「ターミナル」を、検索して開きます |
| Git | サンプルコードを入手するための道具。無いときは、ZIP ファイルでも入手できます（後述） |
| uv | Python と、必要なライブラリを用意する道具。次の手順でインストールします |
| エディタ | コードを書くための道具。メモ帳でも書けますが、[VS Code](https://code.visualstudio.com/) などをお勧めします |

Python 本体を、先に入れておく必要はありません。uv が、必要な版（Python 3.12）を、自動で用意します。初回は、ダウンロードのために、インターネットへの接続が必要で、時間がかかります。

### コマンドの実行のしかた

この本のコマンドは、コードブロックの内容を、そのままターミナルに貼り付けて、Enter キーを押して実行します。`$` や `>` のようなプロンプトの記号は、書いていません。

### uv をインストールする

Windows の PowerShell では、次のコマンドを実行します。

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

macOS と Linux では、次のコマンドを実行します。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

インストールしたら、ターミナルを開き直して、バージョンが表示されることを確かめます。

```bash
uv --version
```

最新のインストール方法は、公式の案内（<https://docs.astral.sh/uv/getting-started/installation/>）で確認できます。インターネット上のスクリプトを実行するコマンドなので、実行する前に、公式の案内に、同じコマンドが書かれていることを確かめてください。

### サンプルコードを入手する

```bash
git clone https://github.com/k2works/getting-started-economics.git
cd getting-started-economics
```

Git が無いときは、GitHub のリポジトリのページ（<https://github.com/k2works/getting-started-economics>）で、「Code」ボタンから「Download ZIP」を選んで入手します。ZIP を展開したフォルダを、ターミナルで開きます（`cd 展開したフォルダの名前`）。

### テストが動くことを確かめる

サンプルコードは、リポジトリの `apps/economics-programming/python/` にあります。そこで、ライブラリを用意して、第 1 章の完成形のテストを実行します。

```bash
cd apps/economics-programming/python
uv sync
uv run pytest test/chapter01
```

```text
5 passed
```

`uv sync` は、必要なライブラリを用意します（初回は、時間がかかります）。5 つのテストが通れば、準備は完了です。

各章のコマンドの最初の行 `cd apps/economics-programming/python` は、リポジトリの最上位（`getting-started-economics`）からの道のりです。すでにこのディレクトリにいるときは、その行を省略してください。

### 完成形と、自分のコード

準備の確認で、テストが**最初から通った**のは、リポジトリに、完成した実装とテストが入っているからです。

| ディレクトリ | 中身 | 使い方 |
| :--- | :--- | :--- |
| `lib/chapterNN/` | 各章の完成した実装 | 答え合わせ用。自分のコードを書き終えてから開く |
| `test/chapterNN/` | 各章の完成したテスト | 答え合わせ用。`uv run pytest test/chapterNN` で、完成形が動くことを確かめる |
| `practice/chapterNN/` | **自分のコードを書く場所** | 章ごとに、自分で作る |

この本の「予想する」「Red → Green → Refactor」「練習問題」は、**自分で `practice/` に書いて体験する**ための手順です。完成形を写すだけでは、テストを先に書く体験になりません。先に自分で考えて、書いてから、`lib/` と `test/` を開いて、答え合わせをしてください。

前の章の関数を使うときは、自分で作ったもの（`practice.chapter01.demand` など）でも、用意してある完成形（`lib.chapter01.demand` など）でも、かまいません。

### 対話モードで試す

コードを 1 行ずつ打ち込んで、結果をすぐに見る方法があります。`apps/economics-programming/python/` で、次のコマンドを実行します。

```bash
uv run python
```

`>>>` という記号が表示されたら、式や関数の呼び出しを打ち込んで、Enter キーを押します。

```text
>>> 1 + 1
2
>>> from lib.chapter01.demand import quantity_demanded
>>> quantity_demanded(price=10, intercept=100, slope=2)
80
>>> exit()
```

`#` から後ろは、コメント（人間への注釈）なので、打ち込まなくてかまいません。終わるときは、`exit()` と打ち込みます（Windows では、Ctrl キーを押しながら Z を押して Enter、macOS・Linux では、Ctrl キーを押しながら D でも終われます）。

この本のコード片は、対話モードに 1 行ずつ打ち込んで、試せます。テストに書く前に、「この式は、どんな値になるか」を確かめたいときに、便利です。

## 1.3 予想する

コードを読む前に、次の問いに自分で答えてみてください。紙に書くのがお勧めです。

- 需要曲線が Q = 100 − 2P のとき、価格が 0 のとき、需要量はいくつですか
- 価格が 10 のとき、需要量はいくつですか
- 価格が 60 のとき、需要量はいくつですか。式のとおりに計算すると、困ったことになりませんか

3 つ目で「マイナスになる」と気づいたら、経済学の感覚が働いています。需要量は負にならないので、コードでこの場面を扱う必要があります。

## 1.4 Red → Green → Refactor

### コードの読み方（最小限）

これから、Python のコードが出てきます。読むために、最低限の対応を、先に表にします。**全部を覚える必要はありません。** コードを読んでいて、分からなくなったときに、この表に戻ってきてください。詳しい説明は、表の右の章にあります。

| 書き方 | 意味 | 詳しくは |
| :--- | :--- | :--- |
| `def 名前(引数):` | 関数を作る。「引数を受け取って、結果を返す処理」に、名前を付ける | 第 4 章 |
| `return 値` | 関数の結果を返す | 第 4 章 |
| `price: float` | 引数 `price` は、小数（`float`）を渡す、という**型ヒント**。Python は、実行するときには、チェックしない。エディタや検査の道具が、間違いに気づく助けにする。今は、読み飛ばしてかまいません | 第 2 章 |
| `-> float` | 関数が返す値の型ヒント。`-> None` は、「何も返さない」。テストの関数には、`-> None` を付ける | 第 2 章 |
| `if 条件:` | 条件が成り立つときだけ、字下げした中の処理を実行する | 第 5 章 |
| `raise ValueError(...)` | 「この入力は、おかしい」と、エラーを起こして知らせる | 第 6 章 |
| `max(a, b)` | 2 つの値の、大きい方を返す（Python に最初から入っている関数） | 第 4 章 |
| `import` / `from ... import ...` | 他のファイルで作った関数や、道具を、読み込む | 第 6 章 |
| `# ...` | コメント。人間への注釈で、実行には影響しない | — |

テストのコードには、次の書き方が出てきます。

| 書き方 | 意味 |
| :--- | :--- |
| `def test_名前() -> None:` | テストを 1 つ作る。pytest は、`test_` で始まる名前の関数を、テストとして見つけて、実行する。名前は日本語でよい。「何を確かめるか」を、文章で書く |
| `assert 式` | 式が成り立つ（`True` になる）ことを、確かめる。成り立たなければ、そのテストは失敗する |
| `==` | 左と右が、等しいかどうかを調べる（`=` は、値を名前に結び付ける別の意味なので、混同しない） |
| `with pytest.raises(ValueError):` | 「この中の処理で、`ValueError` が起きること」を、確かめる。起きれば成功で、起きなければ、テストは失敗する |

### Red: 最初のテストを書く

最初に、実装がまだない関数のテストを書きます。価格が 0 なら、需要量は切片 a と等しいはずです。次の手順で、自分のコードを書く場所を作ります。

1. `apps/economics-programming/python/` で、章のディレクトリを作ります。

    ```bash
    mkdir practice/chapter01
    ```

2. `practice/chapter01/test_demand.py` を作って、次の内容を書きます。ファイル名は、`test_` で始めます（pytest が、この名前のファイルを、テストとして見つけます）。

    ```python
    import pytest

    from practice.chapter01.demand import quantity_demanded


    def test_価格が0なら需要量は切片と等しい() -> None:
        assert quantity_demanded(price=0, intercept=100, slope=2) == 100
    ```

    1 行目の `pytest` は、テストの道具です（後の節で使います）。3 行目は、これから作る関数 `quantity_demanded` を、`practice/chapter01/demand.py` から読み込む、という意味です。まだ、そのファイルがありません。

3. テストを実行します。

    ```bash
    uv run pytest practice/chapter01
    ```

実行すると、関数がないので失敗します。失敗を確かめることが大切です。

```text
ModuleNotFoundError: No module named 'practice.chapter01.demand'
```

画面には、`ERROR practice/chapter01/test_demand.py` と、`1 error` も表示されます。

### Green: 最小の実装で通す

テストを通す最小の実装は、式をそのまま書くことです。`practice/chapter01/demand.py` を作って、次の内容を書きます。

```python
def quantity_demanded(price: float, intercept: float, slope: float) -> float:
    return intercept - slope * price
```

もう一度、テストを実行します。

```bash
uv run pytest practice/chapter01
```

```text
1 passed
```

### 次のテストを足す

予想した 2 つ目と 3 つ目の問いを、テストにします。`test_demand.py` の末尾に、次のテストを書き足します。

```python
def test_価格が上がると需要量は傾きの分だけ減る() -> None:
    assert quantity_demanded(price=10, intercept=100, slope=2) == 80


def test_価格が高すぎると需要量は0になる() -> None:
    assert quantity_demanded(price=60, intercept=100, slope=2) == 0
```

3 つ目のテストは、式のとおりだと −20 になるので失敗します（実行して、確かめてください）。需要量が負にならないよう、`demand.py` を、`max` で 0 を下限にする形に書き換えます。

```python
def quantity_demanded(price: float, intercept: float, slope: float) -> float:
    return max(intercept - slope * price, 0)
```

価格が負の入力は、経済学の意味がありません。これもテストで先に決めます。次のテストを、`test_demand.py` の末尾に書き足します。

```python
def test_負の価格は受け付けない() -> None:
    with pytest.raises(ValueError):
        quantity_demanded(price=-1, intercept=100, slope=2)
```

### Refactor: 完成した実装

テストがすべて通ったら、名前と説明を整えます。需要量がちょうど 0 になる価格（`choke_price`）も、同じ手順（テストを先に書く）で追加します。`demand.py` を、次の完成形にします。

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

テストの追加では、`test_demand.py` の `import` の行を、`from practice.chapter01.demand import choke_price, quantity_demanded` に書き換えます。また、`ValueError` のテストで使う `pytest` を、この `import` で読み込んでいます。

自分のコードで、テストを実行します。5 つのテストがすべて通ります。

```bash
uv run pytest practice/chapter01
```

```text
5 passed
```

最後に、答え合わせをします。`lib/chapter01/demand.py` を開いて、自分の実装と見比べてください。完成形のテストも、実行できます。

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
| 想起 | 本文を閉じて、`quantity_demanded` を、`practice/chapter01/demand.py` に、自分で書いてください。その後、本文と見比べて違いを確かめます |
| 生成 | 供給曲線 Q = c + dP の関数 `quantity_supplied` を、解説を見る前に、`practice/chapter01/` に、テストから書いてください。価格が 0 のときの供給量は c です |
| 多様 | `intercept=100, slope=2` を `intercept=50, slope=5` に変えて、5 つのテストの期待値を手計算で作り直してください |
| 交互 | 需要曲線 Q = 100 − 2P と、供給曲線 Q = 3P を使って、需要量と供給量が等しくなる価格を、紙の上で求めてください（第 5 章で、コードで求めます） |

??? note "解答（先に自分で取り組んでから、開いてください）"

    **想起**: 本文の完成形（`lib/chapter01/demand.py`）と見比べます。次の 3 点を確かめてください。

    - 価格が負のときに `ValueError` を出しているか
    - `max(..., 0)` で、需要量が負にならないようにしているか
    - 引数と戻り値に、型ヒントを付けているか

    **生成**: 実装は、`quantity_demanded` の `-` を `+` にした形です。

    ```python
    def quantity_supplied(price: float, intercept: float, slope: float) -> float:
        if price < 0:
            raise ValueError("価格は 0 以上でなければならない")
        return max(intercept + slope * price, 0)
    ```

    テストの例です（先に書きます）。

    ```python
    def test_価格が0なら供給量は切片と等しい() -> None:
        assert quantity_supplied(price=0, intercept=10, slope=3) == 10


    def test_価格が上がると供給量は傾きの分だけ増える() -> None:
        assert quantity_supplied(price=10, intercept=10, slope=3) == 40
    ```

    同じ関数が、第 3 章の `lib/chapter03/schedule.py` にあります。

    **多様**: 需要曲線 Q = 50 − 5P の期待値です。

    | テスト | 価格 | 需要量 |
    | :--- | ---: | ---: |
    | 価格が 0 | 0 | 50（切片と等しい） |
    | 価格が上がる | 5 | 25 |
    | 価格 10 | 10 | 0（本文の例では 80 だった所が 0 に変わる） |
    | 価格が高すぎる | 60 | 0（式のとおりでは −250） |
    | 需要が 0 になる最低の価格 `choke_price` | — | 10（= 50 ÷ 5） |

    **交互**: 100 − 2P = 3P から、5P = 100 で、P = 20 です。そのとき、需要量は 100 − 2 × 20 = 60、供給量は 3 × 20 = 60 で、等しくなります。

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
