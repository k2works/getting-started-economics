---
type: Article
title: "第 9 章: NumPy による配列計算"
description: "NumPy の配列で、乗数効果の波及と国民所得の決定、需要・供給の連立方程式を計算する。"
tags: [article,economics-programming,python]
status: draft
generated: { by: claude-code/claude-sonnet-5-5, at: 2026-11-19T00:00:00Z }
---

# 第 9 章: NumPy による配列計算

## 9.1 この章の地図

この章では、数値計算のライブラリ NumPy を導入します。たくさんの数を、まとめて計算する方法と、連立方程式を解く方法を学びます。

| 項目 | 内容 |
| :--- | :--- |
| 経済学の題材 | 乗数効果、45 度線分析（国民所得の決定）、需要・供給の連立方程式（マインドマップ [5-5](<../経済学・経済政策 トピック別マインドマップ.md#t5>), [5-3](<../経済学・経済政策 トピック別マインドマップ.md#t3>)） |
| 使う Python の機能 | NumPy の配列（`array`）、形（`shape`）、添字と切り出し、配列どうしの計算、`np.linalg.solve` |
| 新しく導入するライブラリ | [NumPy](https://numpy.org/)（配列と線形代数） |
| 完成形 | `multiplier`、`spending_rounds`、`income_determination`、`equilibrium_by_linear_algebra`、`demand_quantities` |

### 経済学の式とコードの対応

| 経済学 | 式 | コード |
| :--- | :--- | :--- |
| 乗数 | 1 ÷ (1 − c)（c は限界消費性向） | `multiplier(mpc)` |
| 支出の波及 | 初期支出 × c の 0 乗、1 乗、2 乗、… | `spending_rounds(initial_spending, mpc, count)` |
| 45 度線分析 | Y = C + I、C = C0 + cY | `income_determination(...)` |
| 需要・供給の均衡 | Q + bP = a、Q − dP = c | `equilibrium_by_linear_algebra(...)` |

マインドマップの「45 度線分析：乗数 1 ÷ (1 − c)」を、2 通りで確かめます。1 つは、支出が波及する様子を足し合わせる方法、もう 1 つは、連立方程式を解く方法です。

## 9.2 予想する

限界消費性向 c = 0.8 のとき、政府が 100 の支出を増やしたとします。

- この 100 は、誰かの所得になり、その 80% が消費に回ります。2 回目の増加は、いくつですか。3 回目は
- これを足し続けると、合計はいくつに近づきますか
- 乗数 1 ÷ (1 − 0.8) は、いくつですか。上の合計と、どう関係しますか

答えは、2 回目が 80、3 回目が 64 で、合計は 100 × 5 = 500 に近づきます。乗数 5 は、支出 1 が最終的に所得を 5 増やすことを表します。

## 9.3 NumPy の配列

### 配列を作る

リストと違い、NumPy の配列は、すべての要素が同じ型で、まとめて計算できます。

```python
import numpy as np

prices = np.array([0, 10, 20, 30])
100 - 2 * prices        # array([100,  80,  60,  40])
```

第 3 章では、リストの内包表記で、価格ごとに需要量を計算しました。配列なら、式を 1 回書くだけで、全部の価格に適用されます。

### 形・添字・切り出し

2 次元の配列（行と列を持つ表）も作れます。

```python
a = np.array([[1, 2], [3, 4]])
a.shape        # (2, 2)   2 行 2 列
a[1, 0]        # 3        1 行目（0 から数える）の 0 列目
a[:, 1]        # array([2, 4])   1 列目すべて
a.T            # 転置（行と列を入れ替える）
```

### 配列どうしの計算

配列どうしの計算は、要素ごとに行います。行列の積は、`@` で書きます。

```python
a @ np.array([1, 1])    # array([3, 7])   [1*1 + 2*1, 3*1 + 4*1]
```

### リストと配列の違い

| 項目 | リスト | NumPy の配列 |
| :--- | :--- | :--- |
| 要素の型 | 混ぜられる | すべて同じ |
| `2 * x` | 要素を 2 回繰り返す | 全要素を 2 倍する |
| 用途 | 汎用のデータの入れ物 | 数値計算 |

`2 * [1, 2]` は `[1, 2, 1, 2]` ですが、`2 * np.array([1, 2])` は `array([2, 4])` です。

### 連立方程式を解く

未知数が複数ある連立方程式は、係数の行列と、定数の配列にして、`np.linalg.solve` で解きます。

```python
# x + 2y = 5、3x + 4y = 11
coefficients = np.array([[1, 2], [3, 4]])
constants = np.array([5, 11])
np.linalg.solve(coefficients, constants)    # array([1., 2.])  x = 1、y = 2
```

## 9.4 Red → Green → Refactor

### 乗数と支出の波及

予想した値を、テストにします。

```python
def test_限界消費性向が0_8なら乗数は5() -> None:
    assert multiplier(0.8) == pytest.approx(5)


@pytest.mark.parametrize("mpc", [-0.1, 1.0, 1.5])
def test_限界消費性向は0以上1未満でなければならない(mpc: float) -> None:
    with pytest.raises(ValueError):
        multiplier(mpc)


def test_支出の波及は各回で限界消費性向倍になる() -> None:
    rounds = spending_rounds(initial_spending=100, mpc=0.8, count=3)
    assert rounds.tolist() == pytest.approx([100, 80, 64])


def test_波及を足し合わせると初期支出かける乗数に近づく() -> None:
    rounds = spending_rounds(initial_spending=100, mpc=0.8, count=100)
    assert rounds.sum() == pytest.approx(100 * multiplier(0.8), abs=1e-6)
```

```python
def _check_mpc(mpc: float) -> None:
    if not 0 <= mpc < 1:
        raise ValueError("限界消費性向は 0 以上 1 未満でなければならない")


def multiplier(mpc: float) -> float:
    """乗数 1 / (1 - c) を返す。c は限界消費性向。"""
    _check_mpc(mpc)
    return 1 / (1 - mpc)


def spending_rounds(
    initial_spending: float, mpc: float, count: int
) -> NDArray[np.float64]:
    """初期支出が各回で限界消費性向倍になって波及する様子を、count 回分返す。"""
    _check_mpc(mpc)
    return (initial_spending * mpc ** np.arange(count)).astype(np.float64)
```

`np.arange(count)` は、0, 1, 2, … と並ぶ配列です。`mpc ** np.arange(count)` で、c の 0 乗、1 乗、2 乗、… を、一度に作ります。限界消費性向が 1 以上だと、支出が減らずに波及し続けて、合計が決まりません。そのため、0 以上 1 未満に限っています。

実際に動かすと、波及は 100、80、64、51.2、40.96 と減り、累積は 100、180、244、295.2、336.16 と増えます。100 回分を足すと 499.9999998981483 で、100 × 5 = 500 にほぼ一致します。

### 連立方程式で国民所得を決める

国民所得 Y と消費 C を、連立方程式として解きます。Y = C + I と C = C0 + cY を、未知数 Y と C について整理します。

```text
 Y −  C = I
−c·Y +  C = C0
```

```python
def test_国民所得は消費と投資の和と等しくなる() -> None:
    # 消費 C = 20 + 0.8Y、投資 I = 30、Y = C + I を解くと Y = 250、C = 220
    income, consumption = income_determination(
        autonomous_consumption=20, mpc=0.8, investment=30
    )
    assert income == pytest.approx(250)
    assert consumption == pytest.approx(220)
    assert income == pytest.approx(consumption + 30)
```

```python
def income_determination(
    autonomous_consumption: float, mpc: float, investment: float
) -> tuple[float, float]:
    """国民所得 Y と消費 C を求める。

    Y = C + I と C = C0 + cY を、Y と C についての連立方程式として解く。
        Y -  C = I
     -c·Y +  C = C0
    """
    _check_mpc(mpc)
    coefficients = np.array([[1.0, -1.0], [-mpc, 1.0]])
    constants = np.array([investment, autonomous_consumption])
    income, consumption = np.linalg.solve(coefficients, constants)
    return float(income), float(consumption)
```

結果は、Y = 250.00000000000006、C = 220.00000000000006 です。第 2 章で学んだとおり、小数の計算には誤差があるので、`pytest.approx` で確かめます。Y = (C0 + I) ÷ (1 − c) = (20 + 30) × 5 = 250 と、乗数の式で求めた値と一致します。

### 需要・供給の連立方程式

第 7 章では、均衡の式を、手で P について解きました。連立方程式にすると、係数（切片や傾き）が変わっても、式を解き直さずに、同じ関数で解けます（ただし、直線の式に限ります）。

```python
def test_連立方程式で均衡価格20と均衡数量60を求める() -> None:
    price, quantity = equilibrium_by_linear_algebra(
        demand_intercept=100, demand_slope=2, supply_intercept=0, supply_slope=3
    )
    assert price == pytest.approx(20)
    assert quantity == pytest.approx(60)
```

```python
def equilibrium_by_linear_algebra(
    demand_intercept: float,
    demand_slope: float,
    supply_intercept: float,
    supply_slope: float,
) -> tuple[float, float]:
    """均衡価格と均衡数量を、連立方程式として解いて返す。

    Q + bP = a（需要曲線）
    Q - dP = c（供給曲線）

    第 7 章の `equilibrium` と同じく、価格が負、または数量が 0 以下になる市場には、
    均衡がないので、NoEquilibriumError にする。
    """
    coefficients = np.array([[1.0, demand_slope], [1.0, -supply_slope]])
    constants = np.array([demand_intercept, supply_intercept])
    quantity, price = np.linalg.solve(coefficients, constants)
    check_equilibrium_exists(float(price), float(quantity))
    return float(price), float(quantity)
```

第 7 章の `equilibrium` と同じ答え（価格 20、数量 60）になります。均衡がない市場（価格が負、または数量が 0 以下）では、第 7 章の `check_equilibrium_exists` を呼んで、同じ `NoEquilibriumError` にします。連立方程式は、解けさえすれば値を返してしまうので、「その値が経済学の意味を持つか」の確認を、自分で足す必要があります。

求め方の違う実装が、同じ答えになることは、テストで固定します。

```python
@pytest.mark.parametrize("supply_intercept", [0, 10, -30])
def test_連立方程式の解は第7章の閉形式の解と一致する(supply_intercept: float) -> None:
    market = {
        "demand_intercept": 100,
        "demand_slope": 2,
        "supply_intercept": supply_intercept,
        "supply_slope": 3,
    }
    assert equilibrium_by_linear_algebra(**market) == pytest.approx(
        equilibrium(**market)
    )


def test_価格が負になる市場では3つの方法がそろって均衡なしと判断する() -> None:
    market = {
        "demand_intercept": 100,
        "demand_slope": 2,
        "supply_intercept": 120,
        "supply_slope": 3,
    }
    with pytest.raises(NoEquilibriumError):
        equilibrium(**market)
    with pytest.raises(NoEquilibriumError):
        equilibrium_by_linear_algebra(**market)
    with pytest.raises(NoEquilibriumError):
        find_equilibrium_price(make_excess_demand(**market), low=0, high=100)
```

供給曲線の切片が 0・10・−30 の 3 つの市場で、連立方程式の解が、第 7 章の閉形式の解と一致します。そして、価格が負になる市場では、閉形式、連立方程式、第 6 章の二分法の 3 つが、そろって `NoEquilibriumError` になります。

ただし、二分法は、数量が負になる市場（需要が価格 10 でなくなり、供給が価格 30 まで始まらない）では、均衡なしと判断できません。需要も供給も 0 になる価格の範囲では、超過需要が 0 なので、その中の 1 点（価格 10）を「均衡」として返します。二分法は、価格だけから超過需要を計算する、汎用の方法なので、取引量が 0 であることには気づけません。

### 配列で需要量をまとめて計算する

第 3 章の需要表（辞書と内包表記）を、配列で書き直します。結果が、1 つずつ計算した結果と一致することを、テストで確かめます。

```python
def test_配列で需要量をまとめて計算できる() -> None:
    prices = np.array([0, 10, 20, 30])
    result = demand_quantities(prices, intercept=100, slope=2)
    assert result.tolist() == [100, 80, 60, 40]


def test_配列の計算結果は1つずつ計算した結果と一致する() -> None:
    prices = np.array([0, 10, 20, 30, 60])
    expected = [quantity_demanded(float(p), 100, 2) for p in prices]
    assert demand_quantities(prices, intercept=100, slope=2).tolist() == expected


def test_配列でも負の価格は受け付けない() -> None:
    with pytest.raises(ValueError):
        demand_quantities(np.array([10, -1]), intercept=100, slope=2)
```

```python
def demand_quantities(
    prices: NDArray[np.float64], intercept: float, slope: float
) -> NDArray[np.float64]:
    """価格の配列から、需要量の配列を一度に計算する。需要量は負にならない。"""
    if np.any(prices < 0):
        raise ValueError("価格は 0 以上でなければならない")
    return np.maximum(intercept - slope * prices.astype(float), 0)
```

`np.maximum` は、配列の各要素と 0 の大きい方を取ります。第 1 章の `max(..., 0)` を、配列に広げたものです。`np.any(prices < 0)` は、1 つでも負の価格があれば `True` です。

### 実行結果

```bash
cd apps/economics-programming/python
uv run pytest
```

```text
103 passed
```

この 103 件には、第 1〜10 章のテストを含みます。

## 9.5 規則で言うと

1. **たくさんの数の同じ計算は、配列にして、式を 1 回だけ書く。** 繰り返しの `for` を書かずに済む
2. **未知数が複数ある連立方程式は、係数の行列と定数の配列にして `solve` で解く。** 係数が変わっても、同じ関数で解ける。ただし、直線（線形）の式に限る
3. **同じ答えを、別の方法で求めて、突き合わせる。** 手で解いた式と、連立方程式で解いた答えが一致すれば、どちらも正しい可能性が高い

混同しやすい点を、表にまとめます。

| 混同しやすい点 | 違い |
| :--- | :--- |
| 乗数 5 と、波及の合計 | 乗数は、波及の合計（無限に足した値）を、初期支出で割った値 |
| リストの `*` と配列の `*` | リストは繰り返し、配列は要素ごとの掛け算 |
| 乗数効果が大きい / 小さい | 限界消費性向 c が大きいほど、乗数は大きい（c = 0.9 なら 10、c = 0.5 なら 2） |

### このモデルが成り立たない場面

連立方程式で解く方法は、式が直線（線形）のときに使えます。曲線の式には、第 6 章の二分法や、第 10 章の SciPy の方法が必要です。乗数効果は、供給能力に余裕があり、物価が変わらない前提です。完全雇用に近い経済では、需要が増えても、生産が増えずに、物価が上がります。また、国民所得の決定のモデルは、税や輸入を考えていません。税や輸入があると、所得が増えたときに、消費に回る割合が下がり、乗数が小さくなります。

## 9.6 練習問題

| 種類 | 問題 |
| :--- | :--- |
| 想起 | 本文を閉じて、`np.linalg.solve` で、x + 2y = 5、3x + 4y = 11 を解いてください |
| 生成 | 解説を見る前に、税率 t を加えて、乗数が 1 ÷ (1 − c(1 − t)) になる `multiplier_with_tax(mpc, tax_rate)` を、テストから書いてください。c = 0.8、t = 0.25 のとき、乗数は 1 ÷ 0.4 = 2.5 です |
| 多様 | 限界消費性向を 0.5 と 0.9 に変えて、波及の合計（100 回分）が 200 と 1000 に近づくことを確かめてください |
| 交互 | 第 6 章の二分法と、この章の連立方程式で、同じ均衡価格を求め、どちらが式の形に依存するかを説明してください（二分法は式の形に依存せず、連立方程式は、直線の式でしか使えません） |

## 9.7 振り返り

- 波及の合計と乗数の関係を、予想できましたか
- 配列と、第 3 章のリスト・辞書とでは、何が書きやすく、何が書きにくかったですか
- 連立方程式の行列を作るとき、どこで間違えやすいですか

## 9.8 まとめ

- NumPy の配列、形、添字と切り出し、配列どうしの計算を学んだ
- 乗数効果を、波及の足し合わせと連立方程式の 2 通りで確かめた
- 需要・供給の均衡を、連立方程式として解いた

次の章では、SciPy で最適化を学び、効用最大化と利潤最大化を数値で解きます。
