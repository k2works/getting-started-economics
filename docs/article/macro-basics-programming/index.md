---
type: Article
title: "マクロ経済学のためのプログラミング（初級）"
description: "GDP・45 度線・IS-LM・AD-AS・フィリップス曲線・貨幣数量説・開放経済を、式を関数にして、テストで確かめながら学ぶ記事シリーズ。"
tags: [article,macro-basics-programming,python]
status: draft
generated: { by: claude-code/claude-sonnet-5-5, at: 2026-11-21T00:00:00Z }
---

# マクロ経済学のためのプログラミング（初級）

教科書的なマクロ経済学（国民所得の計算、財市場、貨幣市場、IS-LM、AD-AS、物価と失業、消費・投資の理論、貨幣数量説、開放経済）を、Python のコードとテストで学ぶ記事シリーズです。**式を関数にして、テストで確かめ**、曲線の動きを**図で見ます**。

[経済学のためのプログラミング入門](../economics-programming/index.md)（以下、「第 1 シリーズ」）の前半を終えた方が、続けて読めます。データ分析と動学モデルを扱う [マクロ経済学のためのプログラミング（中級＋）](../macro-programming/index.md) の、**前に読む**位置の記事です。

各章の構成と、練習問題・到達チェックの使い方は、[この記事の読み方](how-to-read.md) を参照してください。章によって意味が変わる記号の一覧は、[記号について](how-to-read.md#symbols) にあります。

> 全 14 章（3 部）が公開されています。各部の終わり（第 5・9・14 章）に、到達チェックがあります。

## この記事の読み方

### 対象読者と前提

- 第 1 シリーズの第 1〜8 章（関数・pytest・リストと辞書・制御構文・モジュール・Matplotlib・乱数）を終えた方
- 経済学の入門（ミクロ・マクロの基本用語）を学んだ、または学んでいる方

NumPy と pandas は、前提にしません。必要な章（NumPy は第 2 章、pandas は第 3 章）で、必要な分だけ、導入します。準備（uv のインストール）は、[第 1 シリーズの第 1 章](../economics-programming/01-preparation-and-first-test.md) の 1.2 節にあります。

第 1 シリーズ・中級＋・計量経済学の連載と題材が重なる章がありますが、各章は、**この連載だけで独立して読めます**（必要な前提は、各章の冒頭に表で示します）。

この連載の**範囲**は、教科書の静学モデル（GDP・IS-LM・AD-AS・マンデル・フレミング）を、関数とテストにして、比較静学を行うところまでです。実際の統計データ、時間を通じた動き（動学）、ミクロ的基礎づけ、ニューケインジアンは、扱いません。実データと動学は[中級＋](../macro-programming/index.md)、統計的な推定は[計量経済学](../econometrics-programming/index.md)の連載で続けられます。

### 進め方

1. **予想する**: コードを見る前に、紙で、手計算の答えを予想します。**答えは書いてありません。**
2. **自分で書く**: `practice/` に、テストを先に書いて、実装を書きます（Red → Green → Refactor）
3. **答え合わせ**: 「プログラミング」の節の小節「予想の答え合わせ」で、予想の答えを、プログラムを動かして確かめます。完成形（`lib/` と `test/`）とも、見比べます
4. **練習問題・振り返り**: 条件を変えて試します。解答は、各章の練習問題の下に、折りたたんで置いてあります。先に自分で取り組んでから、開いてください

## サンプルコード

サンプルコードは `apps/macro-basics-programming/python/` にあります。

| ディレクトリ | 中身 |
| :--- | :--- |
| `practice/chapterNN/` | **自分のコードを書く場所**（章ごとに、自分で作ります） |
| `lib/chapterNN/` | 各章の完成した実装（答え合わせ用） |
| `test/chapterNN/` | 各章の完成したテスト（答え合わせ用） |
| `data/` | 各章で使う、架空のデータ（実在の統計ではありません） |

```bash
cd apps/macro-basics-programming/python
uv sync
uv run pytest test/chapter01
```

## 章構成

### 第 1 部: 経済指標と財市場

| 章 | テーマ | 状況 |
| :--- | :--- | :--- |
| [第 1 章](01-gdp-and-value-added.md) | GDP と付加価値 | 執筆済み |
| [第 2 章](02-three-way-equivalence.md) | 三面等価と産業連関表 | 執筆済み |
| [第 3 章](03-price-indexes-and-indicators.md) | 物価指数と景気・雇用の指標 | 執筆済み |
| [第 4 章](04-45-degree-line-and-multiplier.md) | 45 度線分析と乗数 | 執筆済み |
| [第 5 章](05-gaps-and-stabilization.md) | ギャップと安定化政策（第 1 部の到達チェック） | 執筆済み |

### 第 2 部: 貨幣市場と IS-LM

| 章 | テーマ | 状況 |
| :--- | :--- | :--- |
| [第 6 章](06-money-supply.md) | 貨幣供給と貨幣乗数 | 執筆済み |
| [第 7 章](07-money-demand-and-lm.md) | 貨幣需要と LM 曲線 | 執筆済み |
| [第 8 章](08-is-curve-and-is-lm.md) | IS 曲線と IS-LM の均衡 | 執筆済み |
| [第 9 章](09-fiscal-and-monetary-policy.md) | 財政政策と金融政策の効果（第 2 部の到達チェック） | 執筆済み |

### 第 3 部: 労働市場と主要理論

| 章 | テーマ | 状況 |
| :--- | :--- | :--- |
| [第 10 章](10-labor-market-and-ad-as.md) | 労働市場と AD-AS 分析 | 執筆済み |
| [第 11 章](11-phillips-curve-and-okun.md) | 物価・失業とフィリップス曲線 | 執筆済み |
| [第 12 章](12-consumption-and-investment.md) | 消費と投資の理論 | 執筆済み |
| [第 13 章](13-quantity-theory-and-exchange-rate.md) | 貨幣数量説と為替・国際収支 | 執筆済み |
| [第 14 章](14-mundell-fleming.md) | マンデル・フレミング・モデル（第 3 部の到達チェック） | 執筆済み |

## 参照

- [経済学・経済政策 トピック別マインドマップ](<../経済学・経済政策 トピック別マインドマップ.md>)・[全体マインドマップ](<../経済学・経済政策 全体マインドマップ.md>) — 章立てと、式・数値の出典です
- [経済学のためのプログラミング入門](../economics-programming/index.md) — 前提とする、第 1 シリーズです
- [マクロ経済学のためのプログラミング（中級＋）](../macro-programming/index.md) — この記事の次に読む、データ分析と動学モデルの連載です
- [経済学で出る数学プログラミング](../math-for-economics-programming/index.md) — 数学の復習は、こちらへ。複利・割引現在価値（[第 3 章](../math-for-economics-programming/03-exponents-logarithms-and-interest.md)）、等比数列・無限級数（乗数の土台。[第 4 章](../math-for-economics-programming/04-sequences-and-saving.md)）、漸化式（[第 12 章](../math-for-economics-programming/12-recurrence-and-economic-growth.md)）
