---
type: Article
title: "マクロ経済学のためのプログラミング（中級＋）"
description: "成長・景気循環・貨幣・為替の分析を、データ分析と動学モデルの数値計算で、テストを書きながら学ぶ記事シリーズ。"
tags: [article,macro-programming,python]
status: draft
generated: { by: claude-code/claude-sonnet-5-5, at: 2026-11-19T00:00:00Z }
---

# マクロ経済学のためのプログラミング（中級＋）

学部中級より少し進んだマクロ経済学（成長、景気循環、貨幣、為替）を、Python のコードとテストで学ぶ記事シリーズです。**データの分析**（国際比較・日本のマクロ時系列）と、**動学モデルの数値計算**（ソロー・モデル、AD-AS、IS-MP-PC、RBC）を、関数にして、テストで確かめます。

[経済学のためのプログラミング入門](../economics-programming/index.md)（以下、「第 1 シリーズ」）の続編です。

各章の構成と、練習問題・到達チェックの使い方は、[この記事の読み方](how-to-read.md) を参照してください。章によって意味が変わる記号（α・A・k・h など）の一覧は、[記号について](how-to-read.md#symbols) にあります。

> 全 18 章（4 部）が公開されています。各部の終わり（第 7・12・14・18 章）に、到達チェックがあります。

## この記事の読み方

### 対象読者と前提

- [第 1 シリーズ](../economics-programming/index.md)を終えた方、または、同等の Python（関数・pytest・NumPy・pandas・Matplotlib）の経験がある方
- 学部中級レベルのマクロ経済学（IS-LM、AD-AS、ソロー・モデル）を学んだ、または学んでいる方

Python の基礎は、繰り返しません。準備（uv のインストール）は、[第 1 シリーズの第 1 章](../economics-programming/01-preparation-and-first-test.md) の 1.2 節にあります。

### 進め方

第 1 シリーズと同じです。

1. **予想する**: コードを見る前に、紙で、手計算の答えを予想します
2. **自分で書く**: `practice/` に、テストを先に書いて、実装を書きます（Red → Green → Refactor）
3. **答え合わせ**: 完成形（`lib/` と `test/`）と見比べます
4. **練習問題・振り返り**: 条件を変えて試します。解答は、各章の練習問題の下に、折りたたんで置いてあります。先に自分で取り組んでから、開いてください

## サンプルコード

サンプルコードは `apps/macro-programming/python/` にあります。

| ディレクトリ | 中身 |
| :--- | :--- |
| `practice/chapterNN/` | **自分のコードを書く場所**（章ごとに、自分で作ります） |
| `lib/chapterNN/` | 各章の完成した実装（答え合わせ用） |
| `test/chapterNN/` | 各章の完成したテスト（答え合わせ用） |
| `data/` | 各章で使う、架空のデータ（実在の統計ではありません） |

```bash
cd apps/macro-programming/python
uv sync
uv run pytest test/chapter01
```

## 章構成

### 第 1 部: 長期分析（成長と国際比較）

| 章 | テーマ | 状況 |
| :--- | :--- | :--- |
| [第 1 章](01-development-accounting.md) | 発展会計 | 執筆済み |
| [第 2 章](02-growth-accounting.md) | 成長会計 | 執筆済み |
| [第 3 章](03-regression.md) | 回帰分析 | 執筆済み |
| [第 4 章](04-difference-equations.md) | 差分方程式と経済分析 | 執筆済み |
| [第 5 章](05-solow-model.md) | ソロー・モデル | 執筆済み |
| [第 6 章](06-income-convergence.md) | 所得分布と所得収斂 | 執筆済み |
| [第 7 章](07-purchasing-power-parity.md) | 一物一価と購買力平価（第 1 部の到達チェック、実際の統計で試す） | 執筆済み |

### 第 2 部: 短期データ分析（景気循環と貨幣）

| 章 | テーマ | 状況 |
| :--- | :--- | :--- |
| [第 8 章](08-random-variables.md) | ランダム変数と確率過程 | 執筆済み |
| [第 9 章](09-macro-data-features.md) | 主なマクロ・データの特徴 | 執筆済み |
| [第 10 章](10-okun-and-phillips.md) | オークンの法則とフィリップス曲線 | 執筆済み |
| [第 11 章](11-inflation-and-money-stock.md) | インフレとマネーストック | 執筆済み |
| [第 12 章](12-money-neutrality.md) | 貨幣の中立性と金融政策（第 2 部の到達チェック・実際の統計で試す） | 執筆済み |

### 第 3 部: 短期定量分析（AD-AS モデルのカリブレーション）

| 章 | テーマ | 状況 |
| :--- | :--- | :--- |
| [第 13 章](13-adas-calibration.md) | 動学的 AD-AS モデルとカリブレーション | 執筆済み |
| [第 14 章](14-adas-simulation.md) | インパルス反応と確率的シミュレーション（第 3 部の到達チェック・実際の統計で試す） | 執筆済み |

### 第 4 部: 短期モデル分析（景気循環モデル）

| 章 | テーマ | 状況 |
| :--- | :--- | :--- |
| [第 15 章](15-is-mp-pc.md) | IS-MP-PC モデル | 執筆済み |
| [第 16 章](16-stochastic-solow.md) | 確率的ソロー・モデル | 執筆済み |
| [第 17 章](17-log-linearization.md) | 対数線形近似 | 執筆済み |
| [第 18 章](18-rbc-model.md) | 実物的景気循環（RBC）モデル（第 4 部の到達チェック・実際の統計で試す） | 執筆済み |

## 参照

- [Pythonで学ぶマクロ経済学（中級＋レベル）](https://py4macro.github.io/)（春山鉄源氏）— 章の順序と題材の選び方の参考にしました。本文・コード・図・データは、本シリーズで新たに書いています
- [経済学のためのプログラミング入門](../economics-programming/index.md) — 前提とする、第 1 シリーズです
- [経済学・経済政策 トピック別マインドマップ](<../経済学・経済政策 トピック別マインドマップ.md>) — 経済学の題材の出典です
- [経済学で出る数学プログラミング](../math-for-economics-programming/index.md) — 数学の復習は、こちらへ。漸化式・ソロー・モデル（[第 12 章](../math-for-economics-programming/12-recurrence-and-economic-growth.md)）、数列（[第 4 章](../math-for-economics-programming/04-sequences-and-saving.md)）、行列と回帰（[第 9 章](../math-for-economics-programming/09-matrices-and-regression.md)）
