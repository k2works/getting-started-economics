---
type: Article
title: "経済学のためのプログラミング入門"
description: "経済学の基本モデルを題材に、Python の基礎・数値計算・データ分析をテストを書きながら学ぶ記事シリーズ。"
tags: [article,economics-programming,python]
status: draft
generated: { by: claude-code/claude-sonnet-5-5, at: 2026-11-19T00:00:00Z }
---

# 経済学のためのプログラミング入門

経済学の基本モデル（需要と供給、市場均衡、IS-LM など）を題材に、Python の基礎とデータ分析を学ぶ記事シリーズです。式や曲線を自分の手でコードにして、テストで確かめながら、経済学とプログラミングを同時に身につけます。

執筆計画は [執筆計画アウトライン](outline.md) を参照してください。

## この記事の読み方

### 対象読者と前提

- 経済学を学び始めた学部生・社会人で、ミクロ・マクロ経済学の入門（需要曲線・供給曲線、IS-LM の図を見たことがある程度）を学んだ方
- プログラミングの経験は、不要です。第 1 章で、環境の準備から説明します

### 進め方

各章は、次の順で進みます。

1. **予想する**: コードを見る前に、紙で、手計算の答えを予想します
2. **自分で書く**: `practice/` に、テストを先に書いて、実装を書きます（Red → Green → Refactor）
3. **答え合わせ**: 完成形（`lib/` と `test/`）と見比べます
4. **練習問題・振り返り**: 条件を変えて試し、つまずいた所を確かめます

完成形が、手元に入っているので、写すだけで終わらないように、**先に自分で考えて、書いてから、答え合わせをしてください**。

### 使う道具

読者が使うのは、**uv**（Python とライブラリの用意）と、**pytest**（テストの実行）だけです。インストールの手順は、[第 1 章](01-preparation-and-first-test.md) にあります。

| ツール | 用途 | 読者が使うか |
| :--- | :--- | :--- |
| [uv](https://docs.astral.sh/uv/) | Python とライブラリの用意 | 使う |
| [pytest](https://docs.pytest.org/) | テストの実行 | 使う |
| [Ruff](https://docs.astral.sh/ruff/)・[mypy](https://mypy-lang.org/)・[tox](https://tox.wiki/) | コードの検査（静的解析）、タスクの実行 | 使わない（サンプルコードの品質を保つための道具です） |

数値計算とデータ分析のライブラリは、初めて使う章で導入します（matplotlib は第 7 章、NumPy と SciPy は第 9・10 章、pandas は第 11 章）。第 11・12 章のデータは、`apps/economics-programming/python/data/` にある架空の国の統計です。

## サンプルコード

サンプルコードは `apps/economics-programming/python/` にあります。

| ディレクトリ | 中身 |
| :--- | :--- |
| `practice/chapterNN/` | **自分のコードを書く場所**（章ごとに、自分で作ります） |
| `lib/chapterNN/` | 各章の完成した実装（答え合わせ用） |
| `test/chapterNN/` | 各章の完成したテスト（答え合わせ用） |
| `data/` | 第 11・12 章で使う、架空の国の統計 |

準備と、最初のテストの実行は、[第 1 章](01-preparation-and-first-test.md) の 1.2 節を参照してください。

## 章構成

### 第 1 部: Python の基礎と最初のテスト

| 章 | テーマ | 状況 |
| :--- | :--- | :--- |
| [第 1 章](01-preparation-and-first-test.md) | 準備とはじめてのテスト | 執筆済み |
| [第 2 章](02-data-types-and-variables.md) | データ型と変数 | 執筆済み |
| [第 3 章](03-containers-and-data-operations.md) | コンテナとデータの操作 | 執筆済み |
| [第 4 章](04-functions-and-methods.md) | 関数とメソッド | 執筆済み |
| [第 5 章](05-control-flow.md) | 制御フロー | 執筆済み |
| [第 6 章](06-modules-errors-and-algorithms.md) | モジュール・エラー・アルゴリズム | 執筆済み |

### 第 2 部: 図示と数値計算

| 章 | テーマ | 状況 |
| :--- | :--- | :--- |
| [第 7 章](07-plotting-with-matplotlib.md) | Matplotlib による図示 | 執筆済み |
| [第 8 章](08-random-numbers-and-simulation.md) | 乱数とシミュレーション | 執筆済み |
| [第 9 章](09-numpy-arrays.md) | NumPy による配列計算 | 執筆済み |
| [第 10 章](10-optimization-with-scipy.md) | SciPy による最適化 | 執筆済み |

### 第 3 部: 経済データの分析

| 章 | テーマ | 状況 |
| :--- | :--- | :--- |
| [第 11 章](11-data-analysis-with-pandas.md) | Pandas によるデータ分析 | 執筆済み |
| [第 12 章](12-plotting-with-pandas.md) | Pandas による図示 | 執筆済み |

### 第 4 部: マクロ経済モデルの実装

| 章 | テーマ | 状況 |
| :--- | :--- | :--- |
| [第 13 章](13-is-lm-analysis.md) | IS-LM 分析 | 執筆済み |
| [第 14 章](14-ad-as-and-major-theories.md) | AD-AS 分析と主要理論 | 執筆済み |
| [第 15 章](15-imperfect-competition-and-game-theory.md) | 不完全競争とゲーム理論 | 執筆済み |

### 付録

| 付録 | テーマ | 状況 |
| :--- | :--- | :--- |
| [付録 A](appendix-a-bridge-to-regression.md) | 回帰分析への橋渡し | 執筆済み |

全 15 章と付録 A が、執筆済みです。学び終えたら、姉妹サイト（[Pythonで学ぶ入門計量経済学](https://py4etrics.github.io)、[Pythonで学ぶマクロ経済学](https://py4macro.github.io)）に進んでください。

## 参照

- [Python 入門（py4basics）](https://py4basics.github.io/)・書籍『経済学のためのPython入門』（新世社）— 学ぶ順序の参考にしました。本文とコードは、本シリーズで新たに書いています
- [経済学・経済政策 全体マインドマップ](<../経済学・経済政策 全体マインドマップ.md>) — 7 冊のテキストの全体像です。各章の題材が、どのテキストに対応するかを、章末の表で確かめられます
- [経済学・経済政策 トピック別マインドマップ](<../経済学・経済政策 トピック別マインドマップ.md>) — 経済学の題材の出典です。各トピックから、実装した章へ移れます
