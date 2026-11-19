---
type: Article
title: "付録 A: 回帰分析への橋渡し"
description: "シミュレーションで作った需要データから、最小二乗法で需要曲線を推定する。計量経済学・マクロ経済学の姉妹サイトへの入口。"
tags: [article,economics-programming,python]
status: draft
generated: { by: claude-code/claude-sonnet-5-5, at: 2026-11-19T00:00:00Z }
---

# 付録 A: 回帰分析への橋渡し

## A.1 この付録の地図

第 8 章では、需要曲線 Q = 100 − 2P に、ばらつきを足して、観測値を作りました。この付録では、逆向きの問いを扱います。**観測値だけを見て、需要曲線の切片と傾きを、推定できるか**。この問いに答える方法が、回帰分析です。

| 項目 | 内容 |
| :--- | :--- |
| 経済学の題材 | 需要曲線の推定（計量経済学への入口） |
| 使う Python の機能 | 最小二乗法の式、`zip`、第 8 章のシミュレーションの再利用 |
| 完成形 | `fit_line`、`r_squared` |

回帰分析の本格的な内容（統計的推測、重回帰、検定、時系列など）は、この本の範囲を超えます。この付録は、その入口までです。

### 式とコードの対応

| 統計 | 式 | コード |
| :--- | :--- | :--- |
| 回帰直線 | y = 切片 + 傾き × x | `fit_line(x, y)` の戻り値 |
| 傾き | Σ(x − x̄)(y − ȳ) ÷ Σ(x − x̄)² | `slope` |
| 切片 | ȳ − 傾き × x̄ | `intercept` |
| 決定係数 R² | 1 − (残差の二乗和) ÷ (y の偏差の二乗和) | `r_squared(x, y)` |

最小二乗法は、直線と観測値の縦のずれ（残差）の二乗の和が、最小になる直線を選ぶ方法です。

## A.2 予想する

- 手計算できる 3 点 (0, 1)、(1, 3)、(2, 2) の回帰直線の、傾きと切片は、いくつでしょうか。ヒント: x の平均は 1、y の平均は 2 です
- 第 8 章の需要曲線 Q = 100 − 2P で、観測値のばらつき（標準偏差）を 5、10、30 と大きくしていくと、推定した傾きは、−2 からどのくらいずれるでしょうか。決定係数は、大きくなるでしょうか、小さくなるでしょうか

答えは、傾きが 0.5、切片が 1.5（x̄ = 1、ȳ = 2 を通り、傾き = (−1 × −1 + 0 × 1 + 1 × 0) ÷ 2 = 0.5）。決定係数は、ばらつきが大きいほど小さくなります。

## A.3 Red → Green → Refactor

### 回帰直線

```python
def test_直線上の点なら切片と傾きがそのまま求まる() -> None:
    x = [0.0, 1.0, 2.0, 3.0]
    y = [3 + 2 * v for v in x]
    intercept, slope = fit_line(x, y)
    assert intercept == pytest.approx(3)
    assert slope == pytest.approx(2)


def test_手計算できる3点の回帰直線() -> None:
    # 点 (0, 1)、(1, 3)、(2, 2): 平均は x = 1、y = 2。傾き = (−1×−1 + 0 + 1×0) ÷ 2 = 0.5
    intercept, slope = fit_line([0.0, 1.0, 2.0], [1.0, 3.0, 2.0])
    assert slope == pytest.approx(0.5)
    assert intercept == pytest.approx(1.5)


def test_すべて同じ値のxでは傾きは求められない() -> None:
    with pytest.raises(ValueError):
        fit_line([1.0, 1.0, 1.0], [1.0, 2.0, 3.0])


def test_点の数が合わなければ求められない() -> None:
    with pytest.raises(ValueError):
        fit_line([1.0, 2.0], [1.0])
```

```python
def fit_line(x: Sequence[float], y: Sequence[float]) -> tuple[float, float]:
    """最小二乗法で、(切片, 傾き) を返す。傾き = Σ(x - x̄)(y - ȳ) ÷ Σ(x - x̄)²。"""
    if len(x) != len(y):
        raise ValueError("x と y の点の数が合わない")
    mean_x = sum(x) / len(x)
    mean_y = sum(y) / len(y)
    spread_x = sum((xi - mean_x) ** 2 for xi in x)
    if spread_x == 0:
        raise ValueError("x がすべて同じ値なので、傾きは求められない")
    covariance = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y, strict=True))
    slope = covariance / spread_x
    return mean_y - slope * mean_x, slope
```

`x` がすべて同じ値だと、傾きを決められません（0 で割ることになります）。価格がずっと同じなら、価格と需要量の関係は、データから分かりません。

### 決定係数

決定係数 R² は、y のばらつきのうち、回帰直線で説明できた割合です。1 に近いほど、直線によく当てはまります。

```python
def test_直線上の点なら決定係数は1() -> None:
    x = [0.0, 1.0, 2.0, 3.0]
    y = [3 + 2 * v for v in x]
    assert r_squared(x, y) == pytest.approx(1)
```

```python
def r_squared(x: Sequence[float], y: Sequence[float]) -> float:
    """決定係数 R² = 1 - (残差の二乗和) ÷ (y の偏差の二乗和)。"""
    intercept, slope = fit_line(x, y)
    mean_y = sum(y) / len(y)
    residual = sum(
        (yi - (intercept + slope * xi)) ** 2 for xi, yi in zip(x, y, strict=True)
    )
    total = sum((yi - mean_y) ** 2 for yi in y)
    return 1 - residual / total
```

### シミュレーションで作ったデータから、需要曲線を推定する

第 8 章の `simulate_demand` で、価格 5〜20（16 通り）の各価格で 50 個ずつ、合計 800 個の観測値を作り、そこから需要曲線を推定します。

```python
def test_第8章のシミュレーションで作った需要データから需要曲線を推定できる() -> None:
    rng = random.Random(0)
    prices: list[float] = []
    quantities: list[float] = []
    for price in range(5, 21):
        observations = simulate_demand(price, 100, 2, 10, 50, rng)
        prices.extend([float(price)] * len(observations))
        quantities.extend(observations)
    intercept, slope = fit_line(prices, quantities)
    # 真の需要曲線は Q = 100 - 2P。標準誤差は、傾きが約 0.08、切片が約 1
    assert slope == pytest.approx(-2, abs=0.4)
    assert intercept == pytest.approx(100, abs=5)
```

標準偏差 10 のとき、推定結果は、切片 99.43、傾き −1.946 で、真の値（100、−2）に近くなります。許容誤差は、標準誤差（傾きが約 0.08、切片が約 1）の数倍にしてあります（第 8 章の考え方と同じです）。

ばらつきを変えると、次のようになります（種 0）。

| ばらつき（標準偏差） | 推定した切片 | 推定した傾き | 決定係数 R² |
| ---: | ---: | ---: | ---: |
| 5 | 99.714 | −1.973 | 0.7751 |
| 10 | 99.428 | −1.946 | 0.4561 |
| 30 | 98.284 | −1.839 | 0.0768 |

ばらつきが大きいほど、決定係数は小さくなります。ばらつき 30 では、決定係数が 0.08 しかなく、直線はデータのごく一部しか説明できません。それでも、傾きの推定値（−1.84）は、真の値（−2）の近くにあります。

```python
def test_ばらつきが大きいほど決定係数は小さい() -> None:
    def fit_r2(sigma: float) -> float:
        rng = random.Random(0)
        prices: list[float] = []
        quantities: list[float] = []
        for price in range(5, 21):
            observations = simulate_demand(price, 100, 2, sigma, 50, rng)
            prices.extend([float(price)] * len(observations))
            quantities.extend(observations)
        return r_squared(prices, quantities)

    assert fit_r2(5) > fit_r2(10) > fit_r2(30)
```

## A.4 実際のデータで推定するときの注意

この付録のデータは、シミュレーションで作ったので、「価格を、こちらで決めた」ものです。実際の市場データでは、そうはいきません。

| 注意点 | 内容 |
| :--- | :--- |
| 価格と数量は同時に決まる | 観測される（価格, 数量）の組は、需要曲線と供給曲線の**交点**です。価格に数量を回帰した直線は、需要曲線でも供給曲線でもなく、両者が混ざったものになることがあります（識別の問題） |
| 他の要因 | 所得、他の財の価格、嗜好の変化も、需要量に影響します（重回帰が必要） |
| 因果と相関 | 回帰直線の傾きは、2 つの変数の相関を表します。「価格を変えたら需要量が変わる」という因果とは、別の話です |
| 外れ値・欠損値 | 少数の極端な値が、傾きを大きく変えます |

第 7 章の需要曲線と供給曲線の交点（均衡）だけを観測して、需要曲線を推定しようとする場面を、想像してみてください。均衡の点は、需要や供給の変化に応じて動くので、その点を結んだ線は、需要曲線とは限りません。

## A.5 この先へ

回帰分析の本格的な内容は、次の 2 つの姉妹サイトで学べます。この本の内容は、どちらでも、Python の基本の使い方として、役立ちます。

- [Pythonで学ぶ入門計量経済学](https://py4etrics.github.io)（単回帰・重回帰、仮説検定、ダミー変数、パネルデータなど）
- [Pythonで学ぶマクロ経済学（中級＋レベル）](https://py4macro.github.io)（成長・景気循環・消費・投資などのマクロ経済学を、データで分析する）

この本で身につけた、「経済学の式を関数にして、テストで確かめる」型は、そこでも使えます。

## A.6 まとめ

- 最小二乗法で、観測値から、回帰直線（切片と傾き）を求めた
- 第 8 章のシミュレーションで作った需要データから、需要曲線を推定し、真の値に近いことを確かめた
- 実際のデータでは、価格と数量が同時に決まるので、回帰直線が、需要曲線とは限らないことを確認した
