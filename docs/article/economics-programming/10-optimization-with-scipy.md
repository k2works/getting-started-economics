---
type: Article
title: "第 10 章: SciPy による最適化"
description: "SciPy の最適化で、効用最大化・利潤最大化（P = MC と操業停止点）・費用最小化を数値で解き、手計算の解と突き合わせる。"
tags: [article,economics-programming,python]
status: draft
generated: { by: claude-code/claude-sonnet-5-5, at: 2026-11-19T00:00:00Z }
---

# 第 10 章: SciPy による最適化

## 10.1 この章の地図

経済学には、最大化や最小化の問題が、いたるところに出てきます。消費者は、予算の範囲で効用を最大にします。企業は、利潤を最大に、または費用を最小にします。この章では、そのための道具として、SciPy の最適化を使います。

| 項目 | 内容 |
| :--- | :--- |
| 経済学の題材 | 効用最大化、利潤最大化（P = MC、操業停止点）、費用最小化（マインドマップ [5-1](<../経済学・経済政策 トピック別マインドマップ.md#t1>), [5-2](<../経済学・経済政策 トピック別マインドマップ.md#t2>)） |
| 使う Python の機能 | `scipy.optimize` の `minimize`（制約付き）、`minimize_scalar`、`brentq`（解を求める）、無名関数（`lambda`） |
| 新しく導入するライブラリ | [SciPy](https://scipy.org/)（科学技術計算） |
| 完成形 | `maximize_utility`、`profit_maximizing_quantity`、`minimize_cost` |
| ファイル | 実装: `lib/chapter10/optimization.py`／テスト: `test/chapter10/test_optimization.py`（自分で書くときは、`practice/chapter10/` に、同じ名前で作ります） |

### 経済学の式とコードの対応

| 経済学 | 式 | コード |
| :--- | :--- | :--- |
| 効用最大化 | max x^α·y^(1−α)、予算 Px·x + Py·y = m | `maximize_utility` |
| 最適消費点の条件 | 限界代替率 MRS = Px ÷ Py | 第 4 章の `marginal_rate_of_substitution` |
| 利潤最大化 | P = MC（限界費用が右上がりの部分） | `profit_maximizing_quantity` |
| 操業停止点 | 価格が平均可変費用の最低値を下回ると生産しない | 同上 |
| 費用最小化 | min w·L + r·K、産出量 L^0.5·K^0.5 = Q | `minimize_cost` |

第 4 章で作った、費用関数と効用関数を、そのまま使います。

## 10.2 予想する

手計算で、次の問いに答えてください。

- 価格が Px = 2、Py = 4、所得が 40 で、効用が U = x^0.5 · y^0.5 のとき、最適な消費は、財 x と財 y をいくつずつ買う点ですか。ヒント: 予算の半分ずつを、それぞれの財に使います
- 第 4 章の費用関数で、価格が 15 のとき、利潤を最大にする生産量は、いくつですか。ヒント: MC = 3q² − 12q + 15 が 15 に等しくなる q を求めます
- 価格が 5 のとき、企業は生産しますか。平均可変費用の最低値は 6 です

答えは、(x, y) = (10, 5)、生産量 4（q = 0 の解もありますが、限界費用が右下がりの側なので、利潤は最大になりません）、価格 5 は 6 を下回るので、生産しません。

## 10.3 SciPy の最適化

### 1 変数の最小化

`minimize_scalar` は、1 つの変数の関数の、最小値を探します。範囲を `bounds` で指定します。

```python
from scipy.optimize import minimize_scalar

result = minimize_scalar(lambda q: (q - 3) ** 2 + 1, bounds=(0, 10), method="bounded")
result.x     # 3.0   最小になる q
result.fun   # 1.0   そのときの値
```

`lambda q: ...` は、名前を付けずに、その場で作る小さな関数です。

### 解を求める

`brentq` は、関数の値が 0 になる点を、範囲の中で探します。範囲の両端で、値の符号が逆でなければなりません。第 6 章の二分法と同じ考え方で、より速く収束します。

```python
from scipy.optimize import brentq

brentq(lambda q: q**2 - 4, 0, 10)    # 2.0   q² − 4 = 0 の解
```

### 制約付きの最小化

`minimize` は、複数の変数の関数を、制約のもとで最小にします。最大化したいときは、符号を逆にした関数を最小にします。

```python
from scipy.optimize import minimize

result = minimize(
    lambda v: v[0] ** 2 + v[1] ** 2,                                   # 最小にする関数
    x0=[1.0, 1.0],                                                      # 探し始める点
    constraints={"type": "eq", "fun": lambda v: v[0] + v[1] - 2},       # 制約: x + y = 2
    method="SLSQP",
)
result.x    # array([1., 1.])
```

`"eq"` は、制約の関数が 0 になる、という等式制約です。

## 10.4 Red → Green → Refactor

### 効用最大化

予想した答えを、テストにします。さらに、「最適な点では、限界代替率が価格比に等しい」という経済学の性質も、テストで確かめます。

```python
def test_効用最大化の消費点は所得の半分ずつを使う点() -> None:
    # 価格 (2, 4)、所得 40、alpha = 0.5。x* = 0.5 * 40 / 2 = 10、y* = 0.5 * 40 / 4 = 5
    x, y = maximize_utility(price_x=2, price_y=4, income=40)
    assert x == pytest.approx(10, abs=1e-4)
    assert y == pytest.approx(5, abs=1e-4)


def test_最適消費点では限界代替率が価格比に等しい() -> None:
    x, y = maximize_utility(price_x=2, price_y=4, income=40)
    assert marginal_rate_of_substitution(x, y) == pytest.approx(2 / 4, abs=1e-4)


def test_最適消費点は予算をちょうど使い切る() -> None:
    x, y = maximize_utility(price_x=2, price_y=4, income=40)
    assert 2 * x + 4 * y == pytest.approx(40, abs=1e-6)
```

```python
def maximize_utility(
    price_x: float, price_y: float, income: float, alpha: float = 0.5
) -> tuple[float, float]:
    """予算 price_x·x + price_y·y = income のもとで、効用を最大にする (x, y) を返す。"""
    result = minimize(
        lambda v: -cobb_douglas_utility(v[0], v[1], alpha),
        x0=[income / (2 * price_x), income / (2 * price_y)],
        bounds=[(_EPSILON, None), (_EPSILON, None)],
        constraints={
            "type": "eq",
            "fun": lambda v: price_x * v[0] + price_y * v[1] - income,
        },
        method="SLSQP",
        options={"ftol": 1e-12},
    )
    if not result.success:
        raise RuntimeError(f"効用最大化が収束しなかった: {result.message}")
    return float(result.x[0]), float(result.x[1])
```

効用を最大にするために、効用の符号を逆にした値（`-cobb_douglas_utility(...)`）を最小にしています。財の量が負にならないよう、`bounds` で下限を、ほぼ 0 の `_EPSILON`（1e-9）にしています。探し始める点 `x0` は、予算の半分ずつを使う点です。

結果は、価格 (2, 4)、所得 40 のとき (10.0, 5.0) で、手計算と一致します。財 x の比重 α を 0.75 にすると、手計算の (15, 2.5) に対して、(14.999999512744836, 2.5000002436275817) になります。数値計算の誤差が、小数点以下 7 桁目に出ています。

```python
def test_財xの比重が大きいと財xを多く買う() -> None:
    # alpha = 0.75: x* = 0.75 * 40 / 2 = 15、y* = 0.25 * 40 / 4 = 2.5
    x, y = maximize_utility(price_x=2, price_y=4, income=40, alpha=0.75)
    assert x == pytest.approx(15, abs=1e-4)
    assert y == pytest.approx(2.5, abs=1e-4)
```

最適な点の効用が、予算線上のほかの点より大きいことも、テストにします。

```python
def test_最適消費点の効用はほかの予算内の点より大きい() -> None:
    x, y = maximize_utility(price_x=2, price_y=4, income=40)
    best = cobb_douglas_utility(x, y)
    # 予算線上の別の点 (x, y) = (5, 7.5) と (15, 2.5)
    assert best > cobb_douglas_utility(5, 7.5)
    assert best > cobb_douglas_utility(15, 2.5)
```

### 利潤最大化と操業停止点

利潤最大化の条件 P = MC を、`brentq` で解きます。ただし、限界費用は U 字型なので、P = MC を満たす q が 2 つあります。利潤が最大になるのは、限界費用が右上がりの側（q ≥ 2）です。

```python
def test_価格が15のとき利潤を最大にする生産量は4() -> None:
    # P = MC: 15 = 3q^2 - 12q + 15 を解くと q = 4（q = 0 は MC が右下がりの側）
    quantity = profit_maximizing_quantity(price=15)
    assert quantity == pytest.approx(4)
    assert marginal_cost(quantity) == pytest.approx(15)


def test_価格が15のときの最大利潤は22() -> None:
    quantity = profit_maximizing_quantity(price=15)
    assert 15 * quantity - total_cost(quantity) == pytest.approx(22)


def test_価格が操業停止点の6を下回ると生産しない() -> None:
    assert profit_maximizing_quantity(price=5) == 0


def test_価格が操業停止点の6ちょうどなら生産量は3() -> None:
    assert profit_maximizing_quantity(price=6) == pytest.approx(3)
```

```python
# 限界費用が最低になる生産量。これより右では限界費用が右上がり
_MC_MINIMUM_QUANTITY = 2
# 生産量を探す範囲の上限
_MAX_QUANTITY = 10
# 数値計算の誤差を許す幅
_EPSILON = 1e-9


def profit_maximizing_quantity(price: float) -> float:
    """価格 price のとき、利潤を最大にする生産量を返す。

    価格が平均可変費用の最低値（操業停止点）を下回れば、生産しない。
    そうでなければ、P = MC（限界費用が右上がりの部分）を満たす生産量を求める。
    """
    shutdown_price = minimize_scalar(
        average_variable_cost, bounds=(0, _MAX_QUANTITY), method="bounded"
    ).fun
    if price < shutdown_price - _EPSILON:
        return 0
    return float(
        brentq(
            lambda q: marginal_cost(q) - price,
            _MC_MINIMUM_QUANTITY,
            _MAX_QUANTITY,
        )
    )
```

操業停止点の価格は、`minimize_scalar` で平均可変費用の最低値を探して求めています（結果は 6.0）。第 4 章では、q = 3 で MC と AVC が交わることを、テストで確かめました。ここでは、その値を式に書かずに、数値で探しています。

結果は、価格 15 のとき生産量 3.9999999999996683（≈ 4）、最大利潤は 22 です。第 4 章の練習問題「価格 15、生産量 4 のとき利潤 22」と一致します。価格 6 のとき 2.9999999999999996（≈ 3）、価格 30 のとき 4.999999999999528（≈ 5）、価格 5 のときは生産しないので 0 です。

価格が高いほど、生産量が増えます。マインドマップの「供給曲線は MC の右上がりの部分」が、数値で確かめられました。

### 費用最小化

産出量 Q を作る費用 w·L + r·K を最小にします。生産関数は、第 4 章の効用関数と同じ形の L^0.5 · K^0.5 で、産出量が Q に等しいことが制約です。賃金 w = 1、資本の価格 r = 4、産出量 10 のとき、手計算では L = 10 × √(4 ÷ 1) = 20、K = 10 × √(1 ÷ 4) = 5、費用は 20 + 20 = 40 です。

```python
def test_費用最小化では生産要素の価格が高い要素を少なく使う() -> None:
    # 賃金 1、資本の価格 4、産出量 10: L* = 10 * sqrt(4 / 1) = 20、K* = 10 * sqrt(1 / 4) = 5
    labor, capital, cost = minimize_cost(output=10, wage=1, rental=4)
    assert labor == pytest.approx(20, abs=1e-3)
    assert capital == pytest.approx(5, abs=1e-3)
    assert cost == pytest.approx(40, abs=1e-3)


def test_費用最小化の解は目標の産出量を満たす() -> None:
    labor, capital, _ = minimize_cost(output=10, wage=1, rental=4)
    assert cobb_douglas_utility(labor, capital) == pytest.approx(10, abs=1e-4)
```

```python
def minimize_cost(
    output: float, wage: float, rental: float
) -> tuple[float, float, float]:
    """産出量 output を作る費用 wage·L + rental·K を最小にする (L, K, 費用) を返す。

    生産関数は、コブ・ダグラス型 Q = L^0.5 · K^0.5（第 4 章の関数と同じ形）。
    """
    result = minimize(
        lambda v: wage * v[0] + rental * v[1],
        x0=[output, output],
        bounds=[(_EPSILON, None), (_EPSILON, None)],
        constraints={
            "type": "eq",
            "fun": lambda v: cobb_douglas_utility(v[0], v[1]) - output,
        },
        method="SLSQP",
        options={"ftol": 1e-12},
    )
    if not result.success:
        raise RuntimeError(f"費用最小化が収束しなかった: {result.message}")
    return float(result.x[0]), float(result.x[1]), float(result.fun)
```

結果は、(19.999999881893576, 5.00000002952655, 39.99999999999977) で、手計算の (20, 5, 40) と一致します。価格が高い資本（r = 4）を少なく、安い労働（w = 1）を多く使っています。

### 解がないときの扱い

実行可能な点がないとき（所得や産出量が負のとき）は、最適化が収束しません。その場合は、結果を返さず、`RuntimeError` にします。

```python
def test_所得が負なら効用最大化はできない() -> None:
    with pytest.raises(RuntimeError):
        maximize_utility(price_x=2, price_y=4, income=-40)


def test_産出量が負なら費用最小化はできない() -> None:
    with pytest.raises(RuntimeError):
        minimize_cost(output=-10, wage=1, rental=4)
```

最適化の結果が、見かけ上は数値でも、収束していないことがあります。そのため、`result.success` を、必ず確かめます。

### 実行結果

```bash
cd apps/economics-programming/python
uv run pytest test/chapter10
```

```text
13 passed
```

## 10.5 規則で言うと

1. **最大化は、符号を逆にして最小化する。** `minimize` は最小化の道具なので、効用の符号を逆にした値を渡す
2. **数値で解いた結果は、手計算の解と突き合わせる。** 許容誤差は、アルゴリズムの精度に合わせて決める（この章では 1e-3〜1e-4）
3. **最適化の結果は、収束したかどうかを必ず確かめる。** `result.success` が偽なら、例外にする

混同しやすい点を、表にまとめます。

| 混同しやすい点 | 違い |
| :--- | :--- |
| P = MC を満たす点が 2 つあるとき | 限界費用が右上がりの側が、利潤最大。右下がりの側は、利潤最小（またはその近く） |
| 操業停止点と損益分岐点 | 操業停止点は価格が AVC の最低値（固定費用は回収できなくても、生産した方が損が小さい）。損益分岐点は価格が AC の最低値（利潤が 0） |
| 最適消費点の条件 | 限界代替率 MRS = 価格比 Px ÷ Py。無差別曲線と予算線が接する点 |

### このモデルが成り立たない場面

数値の最適化は、探し始める点によって、違う解（局所的な最適解）に行き着くことがあります。この章の問題は、効用関数が凹で、制約が直線なので、解が 1 つしかありません。しかし、費用関数や効用関数が複雑になると、解が複数あり、探し始める点を変えて確かめる必要があります。また、この章の SLSQP は、関数が滑らかな場合に使えます。折れ線のような関数では、別の方法が必要です。

## 10.6 練習問題

| 種類 | 問題 |
| :--- | :--- |
| 想起 | 本文を閉じて、`minimize` を使い、「x + y = 2 のもとで x² + y² を最小にする」問題を書いてください |
| 生成 | 解説を見る前に、価格 20 のときの利潤を最大にする生産量を、手計算してから、テストを書いてください（3q² − 12q + 15 = 20 から q² − 4q − 5/3 = 0 になり、q = 2 + √(4 + 5/3) = 約 4.38 です） |
| 多様 | 賃金を 4、資本の価格を 1 に入れ替えて、`minimize_cost` を実行してください。労働と資本の使う量は、入れ替わります（L = 5、K = 20） |
| 交互 | 第 7 章の `equilibrium` と、この章の `profit_maximizing_quantity` を組み合わせて、企業が 1 社だけの市場の供給量が、市場の価格 20 のときいくつになるか求めてください（手計算で 3q² − 12q + 15 = 20 を解きます） |

## 10.7 振り返り

- 手計算の答えと、数値の答えは、どこまで一致しましたか。違いが出た桁は、何桁目でしたか
- P = MC の解が 2 つあるとき、どちらを選ぶか、どう判断しましたか
- 最適化が収束しなかったとき、何が原因だと思いますか

## 10.8 まとめ

- `minimize`、`minimize_scalar`、`brentq` で、最適化と、方程式の解を求めた
- 効用最大化・利潤最大化・費用最小化を、手計算の解と突き合わせて確かめた
- 最適化が収束したかどうかを確かめ、解がないときは例外にした

第 2 部はここまでです。次の第 3 部では、pandas で経済データを読み込み、GDP などの指標を計算します。

## 10.9 第 2 部の到達チェック

| できること | 検証の方法 | できた |
| :--- | :--- | :--- |
| 需要曲線・供給曲線を図に描き、余剰と死荷重を求める | 手計算の値と図が一致する | □ |
| 乱数でばらつきを作り、平均が安定することを示す | 理論値と、許容誤差の範囲で一致する | □ |
| 連立方程式と最適化で、均衡と最適点を求める | 手計算の解と一致する | □ |

### 時間を決めて書く課題

何も見ずに、時間を計って、次を書いてください。

1. 需要 Q = 120 − 2P、供給 Q = 20 + 3P の均衡を、`np.linalg.solve` で求める（10 分）
2. 所得 60、価格 (3, 2) の消費者が、U = x^0.5 · y^0.5 を最大にする点を、`minimize` で求め、手計算の (10, 15) と比べる（15 分）

### 誤りの原因の分類

| 原因 | 例 | 戻る章 |
| :--- | :--- | :--- |
| 知らない | `np.linalg.solve` や `minimize` の使い方が分からない | 第 9・10 章 |
| 見抜けない | 最大化の問題を、どう最小化に直すか決められない | 第 10 章 |
| 混同した | 操業停止点と損益分岐点を取り違えた | 第 4・10 章 |
| 手順の誤り | 収束の確認を忘れた | 第 10 章 |
