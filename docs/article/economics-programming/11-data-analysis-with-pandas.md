---
type: Article
title: "第 11 章: Pandas によるデータ分析"
description: "pandas で経済統計の表を読み込み、GDP の三面等価、実質 GDP と成長率、支出の構成比、物価指数を計算する。"
tags: [article,economics-programming,python]
status: draft
generated: { by: claude-code/claude-sonnet-5-5, at: 2026-11-19T00:00:00Z }
---

# 第 11 章: Pandas によるデータ分析

## 11.1 この章の地図

第 3 部の最初の章です。ここまでは、手で作った数値を使ってきました。この章では、表の形をした経済統計を読み込み、GDP や物価指数を計算します。

| 項目 | 内容 |
| :--- | :--- |
| 経済学の題材 | GDP の三面等価、名目と実質、成長率、支出の構成比、物価指数（マインドマップ [5-5](<../経済学・経済政策 トピック別マインドマップ.md#t5>)） |
| 使う Python の機能 | pandas の `DataFrame` と `Series`、CSV の読み込み、列と行の選択、条件による行の抽出、`pytest.fixture` |
| 新しく導入するライブラリ | [pandas](https://pandas.pydata.org/)（表形式のデータ分析） |
| 完成形 | `load_economy`、`production_gdp`、`income_gdp`、`expenditure_gdp`、`statistical_discrepancy`、`real_gdp`、`growth_rates`、`recession_years`、`expenditure_shares`、`laspeyres_index`、`paasche_index` |

### この章のデータについて

使うデータは、`apps/economics-programming/python/data/economy.csv` にある、**架空の国**の 2010〜2021 年の統計です。実在の国や年の統計ではありません。構造だけを、実際の国民経済計算（生産・分配・支出の 3 面、統計上の不突合、GDP デフレーター）にそろえてあります。

実際の公開統計（内閣府の国民経済計算など）で試したいときは、同じ列の形に整えれば、この章の関数がそのまま使えます（`apps/economics-programming/python/data/README.md` と練習問題を参照）。

### 経済学の式とコードの対応

| 経済学 | 式 | コード |
| :--- | :--- | :--- |
| 生産面の GDP | 産業ごとの付加価値の合計 | `production_gdp` |
| 分配面の GDP | 雇用者報酬 + 営業余剰 + 固定資本減耗と間接税 | `income_gdp` |
| 支出面の GDP | 消費 + 投資 + 政府支出 + (輸出 − 輸入) | `expenditure_gdp` |
| 統計上の不突合 | 生産面 − 支出面 | `statistical_discrepancy` |
| 実質 GDP | 名目 GDP ÷ GDP デフレーター × 100 | `real_gdp` |
| 成長率 | (今年 − 前年) ÷ 前年 × 100 | `growth_rates` |
| ラスパイレス指数 | Σ(比較年の価格 × 基準年の数量) ÷ Σ(基準年の価格 × 基準年の数量) × 100 | `laspeyres_index` |
| パーシェ指数 | Σ(比較年の価格 × 比較年の数量) ÷ Σ(基準年の価格 × 比較年の数量) × 100 | `paasche_index` |

## 11.2 予想する

データを開く前に、次の問いに答えてください。

- 2010 年の第 1 次・第 2 次・第 3 次産業の付加価値が、14・130・336 のとき、生産面の GDP はいくつですか
- 三面等価が成り立つなら、分配面の GDP（雇用者報酬 250、営業余剰 124、固定資本減耗と間接税 106）は、いくつになりますか
- 支出面の GDP（消費 264、投資 110、政府支出 96、輸出 82、輸入 72）は、いくつになりますか。生産面と同じになるでしょうか

答えは、生産面が 480、分配面も 250 + 124 + 106 = 480 です。支出面は 264 + 110 + 96 + (82 − 72) = 480 で、2010 年は一致します。ただし、年によっては、1 や 3 の差が出ます（統計上の不突合）。

## 11.3 Pandas の基本

### DataFrame と Series

pandas では、表を `DataFrame`、表の 1 列（または 1 行）を `Series` と呼びます。CSV ファイルは、`pd.read_csv` で読み込みます。`index_col="year"` で、年の列を、行の名前（インデックス）にします。

```python
import pandas as pd

df = pd.read_csv("data/economy.csv", index_col="year")
df.shape       # (12, 12)   12 行 12 列
df.columns     # 列の名前
df.index       # 行の名前（年）
```

先頭の数行は、`df.head(3)` で見られます。

```text
      primary  secondary  tertiary  wages  profits  depreciation_and_tax  ...  deflator
year
2010       14        130       336    250      124                   106  ...      96.1
2011       15        133       344    256      128                   108  ...      96.5
2012       15        138       357    265      133                   112  ...      97.1
```

### 列と行を選ぶ

```python
df["consumption"]                          # 1 列（Series）
df.loc[2015]                               # 2015 年の 1 行（Series）
df.loc[2015, "consumption"]                # 298   行と列を指定する
df.loc[2015:2017, ["consumption", "investment"]]   # 2015〜2017 年の 2 列
```

`.loc[2015:2017]` のように範囲を書くと、**終わりの 2017 年も含まれます**（Python のリストの切り出しとは違います）。

### 表どうしの計算

列（Series）どうしを足すと、同じ行の名前（年）の値どうしが足されます。

```python
df["primary"] + df["secondary"] + df["tertiary"]    # 年ごとの合計（生産面の GDP）
```

### 条件で行を選ぶ

比較の結果（`True` か `False` の列）で、行を選べます。

```python
df[df["deflator"] >= 103].index.tolist()    # [2019, 2020, 2021]   デフレーターが 103 以上の年
df["deflator"].idxmax()                      # 2021                  最大の年
df.sort_values("exports", ascending=False).head(2).index.tolist()    # [2019, 2021]
```

### 変化率と欠損値

`pct_change()` は、前の行からの変化率を計算します。最初の行は、前がないので、欠損値（`NaN`、値がないこと）になります。この表には欠損値がありません（`df.isna().sum().sum()` は 0 です）。

## 11.4 Red → Green → Refactor

### データを読み込む

```python
@pytest.fixture
def economy() -> pd.DataFrame:
    return load_economy()


def test_データは2010年から2021年までの12年分() -> None:
    df = load_economy()
    assert df.shape == (12, 12)
    assert list(df.index) == list(range(2010, 2022))
```

`@pytest.fixture` は、テストで使う部品（ここでは読み込んだ表）を用意する印です。テスト関数の引数に、同じ名前（`economy`）を書くと、pytest が渡してくれます。

```python
DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "economy.csv"


def load_economy(path: Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """CSV を読み込み、年を行の名前（インデックス）にした表を返す。"""
    return pd.read_csv(path, index_col="year")
```

`Path(__file__)` は、このファイルの場所です。そこから、`data` ディレクトリのファイルの場所を求めているので、どのディレクトリから実行しても読めます。

### GDP の三面等価

予想した値を、テストにします。

```python
def test_生産面のGDPは3つの産業の付加価値の合計(economy: pd.DataFrame) -> None:
    # 2010 年: 14 + 130 + 336、2015 年: 16 + 146 + 379
    assert production_gdp(economy)[2010] == 480
    assert production_gdp(economy)[2015] == 541


def test_生産面と分配面のGDPは全年で一致する(economy: pd.DataFrame) -> None:
    assert (production_gdp(economy) == income_gdp(economy)).all()


def test_支出面のGDPは消費と投資と政府支出と純輸出の合計(
    economy: pd.DataFrame,
) -> None:
    # 2010 年: 264 + 110 + 96 + (82 - 72)
    assert expenditure_gdp(economy)[2010] == 480
```

```python
def production_gdp(df: pd.DataFrame) -> pd.Series:
    """生産面の GDP: 産業ごとの付加価値の合計。"""
    return df["primary"] + df["secondary"] + df["tertiary"]


def income_gdp(df: pd.DataFrame) -> pd.Series:
    """分配面の GDP: 雇用者報酬・営業余剰・固定資本減耗と間接税の合計。"""
    return df["wages"] + df["profits"] + df["depreciation_and_tax"]


def expenditure_gdp(df: pd.DataFrame) -> pd.Series:
    """支出面の GDP: 消費・投資・政府支出・純輸出（輸出 - 輸入）の合計。"""
    return (
        df["consumption"]
        + df["investment"]
        + df["government"]
        + df["exports"]
        - df["imports"]
    )
```

`.all()` は、すべてが `True` のときだけ `True` になります。全年で、生産面と分配面が一致しました。

### 統計上の不突合

支出面は、年によって生産面と一致しません。実際の統計でも、3 面は別々の資料から集計するので、ぴったり一致しません。その差が、統計上の不突合です。

```python
def test_統計上の不突合は生産面から支出面を引いた差(economy: pd.DataFrame) -> None:
    gap = statistical_discrepancy(economy)
    assert gap[2010] == 0
    # 2011 年: 生産面 492、支出面 271 + 113 + 98 + (84 - 75) = 491
    assert gap[2011] == 1


def test_統計上の不突合はGDPの1パーセント未満(economy: pd.DataFrame) -> None:
    ratio = statistical_discrepancy(economy).abs() / production_gdp(economy)
    assert (ratio < 0.01).all()
```

```python
def statistical_discrepancy(df: pd.DataFrame) -> pd.Series:
    """統計上の不突合: 生産面の GDP から支出面の GDP を引いた差。"""
    return production_gdp(df) - expenditure_gdp(df)
```

年ごとの不突合は、2010 年から順に、0、1、−1、0、2、−1、0、0、−3、0、1、−1 です。最大でも 3（2018 年）で、GDP の 1% 未満に収まっています。

### 名目 GDP と実質 GDP

名目 GDP には、物価の変化が含まれます。実質 GDP は、デフレーター（基準年 2015 年 = 100）で割って、物価の変化を除いた値です。

```python
def test_基準年の実質GDPは名目GDPと等しい(economy: pd.DataFrame) -> None:
    # デフレーターは 2015 年が 100
    assert real_gdp(economy)[2015] == pytest.approx(production_gdp(economy)[2015])


def test_名目GDPが同じでも物価が上がれば実質GDPは減る(
    economy: pd.DataFrame,
) -> None:
    nominal = production_gdp(economy)
    real = real_gdp(economy)
    assert nominal[2013] == nominal[2012]
    assert real[2013] < real[2012]
```

```python
def real_gdp(df: pd.DataFrame) -> pd.Series:
    """実質 GDP = 名目 GDP ÷ GDP デフレーター × 100（基準年はデフレーターが 100）。"""
    return production_gdp(df) / df["deflator"] * 100
```

2012 年と 2013 年は、名目 GDP がどちらも 510 で同じです。しかし、デフレーターが 97.1 から 98.0 に上がっているので、実質 GDP は 525.2 から 520.4 に減っています。名目の数字だけを見ると、この減少に気づけません。

### 成長率と景気後退の年

```python
def test_成長率の最初の年は計算できない(economy: pd.DataFrame) -> None:
    assert math.isnan(growth_rates(real_gdp(economy))[2010])


def test_2020年の実質成長率はおよそマイナス3パーセント(
    economy: pd.DataFrame,
) -> None:
    # 実質 GDP は 2019 年が 599 / 1.032、2020 年が 580 / 1.030
    assert growth_rates(real_gdp(economy))[2020] == pytest.approx(-3.0, abs=0.1)


def test_実質成長率がマイナスの年は2013年と2020年(economy: pd.DataFrame) -> None:
    assert recession_years(economy) == [2013, 2020]
```

```python
def growth_rates(series: pd.Series) -> pd.Series:
    """前の年からの変化率（%）。最初の年は計算できないので欠損値になる。"""
    return series.pct_change() * 100


def recession_years(df: pd.DataFrame) -> list[int]:
    """実質成長率がマイナスの年を、古い順に返す。"""
    growth = growth_rates(real_gdp(df))
    return [int(year) for year in growth.index[growth < 0]]
```

`growth < 0` は、欠損値（最初の年）に対しては `False` になるので、最初の年は含まれません。実質成長率は、2011 年から順に 2.08、3.02、−0.92、1.50、2.42、1.99、1.02、2.19、1.90、−2.98、2.46（%）で、マイナスの年は 2013 年と 2020 年です。

### 支出の構成比

```python
def test_2015年の支出の構成比(economy: pd.DataFrame) -> None:
    shares = expenditure_shares(economy, 2015)
    # GDP 541 のうち、消費 298、投資 124、政府支出 108、純輸出 92 - 80
    assert shares["consumption"] == pytest.approx(298 / 541 * 100)
    assert shares["investment"] == pytest.approx(124 / 541 * 100)
    assert shares["government"] == pytest.approx(108 / 541 * 100)
    assert shares["net_exports"] == pytest.approx(12 / 541 * 100)


def test_存在しない年の構成比は求められない(economy: pd.DataFrame) -> None:
    with pytest.raises(KeyError):
        expenditure_shares(economy, 1999)
```

```python
def expenditure_shares(df: pd.DataFrame, year: int) -> pd.Series:
    """指定した年の、支出の構成比（GDP に対する %）を返す。"""
    row = df.loc[year]
    shares = pd.Series(
        {
            "consumption": row["consumption"],
            "investment": row["investment"],
            "government": row["government"],
            "net_exports": row["exports"] - row["imports"],
        }
    )
    gdp = production_gdp(df)[year]
    result: pd.Series = shares / gdp * 100
    return result
```

2015 年の構成比は、消費 55.08%、投資 22.92%、政府支出 19.96%、純輸出 2.22% です。合計は 100.18% で、100% からずれる分は、この年の統計上の不突合（−1）によるものです。

### 物価指数: ラスパイレスとパーシェ

物価指数は、いくつかの財の価格の変化を、1 つの数にまとめます。どの年の数量を重みにするかで、2 種類あります。

```python
def test_ラスパイレス指数は基準年の数量で価格の変化を測る() -> None:
    # (110 * 10 + 190 * 5) / (100 * 10 + 200 * 5) = 2050 / 2000
    result = laspeyres_index(
        base_prices=[100, 200], base_quantities=[10, 5], current_prices=[110, 190]
    )
    assert result == pytest.approx(102.5)


def test_パーシェ指数は比較年の数量で価格の変化を測る() -> None:
    # (110 * 8 + 190 * 6) / (100 * 8 + 200 * 6) = 2020 / 2000
    result = paasche_index(
        base_prices=[100, 200], current_prices=[110, 190], current_quantities=[8, 6]
    )
    assert result == pytest.approx(101.0)
```

```python
def laspeyres_index(
    base_prices: Sequence[float],
    base_quantities: Sequence[float],
    current_prices: Sequence[float],
) -> float:
    """ラスパイレス指数: 基準年の数量を使って、価格の変化を測る（基準年 = 100）。"""
    _check_same_length(base_prices, base_quantities, current_prices)
    current = sum(p * q for p, q in zip(current_prices, base_quantities, strict=True))
    base = sum(p * q for p, q in zip(base_prices, base_quantities, strict=True))
    return current / base * 100


def paasche_index(
    base_prices: Sequence[float],
    current_prices: Sequence[float],
    current_quantities: Sequence[float],
) -> float:
    """パーシェ指数: 比較年の数量を使って、価格の変化を測る（基準年 = 100）。"""
    _check_same_length(base_prices, current_prices, current_quantities)
    current = sum(
        p * q for p, q in zip(current_prices, current_quantities, strict=True)
    )
    base = sum(p * q for p, q in zip(base_prices, current_quantities, strict=True))
    return current / base * 100
```

2 つの財の価格が 100 → 110 と 200 → 190 に変わったとき、ラスパイレス指数は 102.5、パーシェ指数は 101.0 です。値が違うのは、重みの数量が違うからです。この例では、値上がりした財 1 の数量が、基準年（10）から比較年（8）に減り、値下がりした財 2 の数量が増えた（5 → 6）ので、パーシェ指数の方が小さくなっています。

### 実行結果

```bash
cd apps/economics-programming/python
uv run pytest
```

```text
131 passed
```

この 131 件には、第 1〜12 章のテストを含みます。

## 11.5 規則で言うと

1. **表の列は、列の名前で選ぶ。** 列の番号ではなく名前で選べば、列の順序が変わっても壊れない
2. **同じ年の値どうしを足し引きするときは、Series どうしで計算する。** pandas は、行の名前（年）をそろえて計算する
3. **データの性質（三面等価、基準年で実質 = 名目）は、テストで確かめる。** データを読み込んだあとに、まず確かめる

混同しやすい点を、表にまとめます。

| 混同しやすい点 | 違い |
| :--- | :--- |
| 名目 GDP と実質 GDP | 名目は、その年の価格で測る。実質は、基準年の価格で測り直して、物価の変化を除く |
| 経済成長率の「名目」と「実質」 | 景気を見るには、実質成長率を使う。名目の増加には、物価上昇が含まれる |
| ラスパイレスとパーシェ | ラスパイレスは基準年の数量、パーシェは比較年の数量を重みにする。一般に、ラスパイレスは物価上昇を大きめに、パーシェは小さめに出す |
| `.loc[a:b]` と `list[a:b]` | `.loc` は、終わりの b を含む。リストは含まない |

### このデータと実際の統計の違い

この章のデータは、生産面と分配面が全年で一致します。実際の統計は、そうではありません。分配面にも、別の資料の誤差が入ります。また、この章の GDP デフレーターは、1 つの数ですが、実際には、財・サービスの種類ごとに、別々のデフレーターを使って、実質化します。さらに、実際の統計は、後から改訂されます。同じ年の値が、公表のたびに変わることがあるので、分析の日付と、データの取得日を、記録しておく必要があります。

## 11.6 練習問題

| 種類 | 問題 |
| :--- | :--- |
| 想起 | 本文を閉じて、`production_gdp` と `real_gdp` を自分で書いてください |
| 生成 | 解説を見る前に、名目 GDP の成長率の関数を、テストから書いてください。2013 年は、名目が 510 で前年と同じなので、成長率は 0 です |
| 多様 | `.loc` を使って、2018〜2021 年の `consumption` の列だけを取り出し、前年からの増加率を求めてください（2020 年は 319 ÷ 329 − 1 = −3.0%） |
| 交互 | 第 6 章の考え方で、`recession_years` の結果が正しいか、手計算で確かめてください。さらに、内閣府などの公開統計から、実際の GDP のデータを取得し、`data/README.md` の列の形に整えて、この章の関数を動かしてみてください（利用条件と出典を、確認してください） |

## 11.7 振り返り

- 三面等価が成り立つかどうかの予想は、当たりましたか
- 名目 GDP が同じ年に、実質 GDP が減ることを、どう説明しますか
- 実際のデータを使うときは、どんな点に注意が必要だと思いますか

## 11.8 まとめ

- pandas の `DataFrame`・`Series`、CSV の読み込み、列と行の選択、条件による抽出を学んだ
- GDP の三面等価、統計上の不突合、実質 GDP、成長率、支出の構成比、物価指数を、テストで確かめながら計算した
- 名目 GDP が同じでも、物価が上がれば、実質 GDP が減ることを確かめた

次の章では、同じデータを、図にして、移動平均と景気動向指数で、景気の動きを見ます。
