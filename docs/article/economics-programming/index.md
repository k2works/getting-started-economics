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

## 開発環境

| ツール | 用途 |
| :--- | :--- |
| [uv](https://docs.astral.sh/uv/) | パッケージ管理 |
| [pytest](https://docs.pytest.org/) | テスト |
| [Ruff](https://docs.astral.sh/ruff/)・[mypy](https://mypy-lang.org/) | 静的解析 |
| [tox](https://tox.wiki/) | タスクランナー |

数値計算とデータ分析のライブラリは、初めて使う章で導入します（matplotlib は第 7 章、NumPy と SciPy は第 9・10 章、pandas は第 11 章）。第 11・12 章のデータは、`apps/python/data/` にある架空の国の統計です。

## サンプルコード

サンプルコードは `apps/python/` にあります。

```bash
cd apps/python
uv sync
uv run pytest
```

各章の実装は `lib/chapterNN/`、テストは `test/chapterNN/` にあります。

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
- [経済学・経済政策 トピック別マインドマップ](<../経済学・経済政策 トピック別マインドマップ.md>) — 経済学の題材の出典です
