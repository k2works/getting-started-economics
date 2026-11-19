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

数値計算とデータ分析のライブラリ（NumPy・pandas・SciPy・matplotlib）は、初めて使う章で導入します。

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
| 第 2 章 | データ型と変数 | 計画中 |
| 第 3 章 | コンテナとデータの操作 | 計画中 |
| 第 4 章 | 関数とメソッド | 計画中 |
| 第 5 章 | 制御フロー | 計画中 |
| 第 6 章 | モジュール・エラー・アルゴリズム | 計画中 |

第 2 部以降は、[執筆計画アウトライン](outline.md) の章構成を参照してください。

## 参照

- [Python 入門（py4basics）](https://py4basics.github.io/)・書籍『経済学のためのPython入門』（新世社）— 学ぶ順序の参考にしました。本文とコードは、本シリーズで新たに書いています
- [経済学・経済政策 トピック別マインドマップ](<../経済学・経済政策 トピック別マインドマップ.md>) — 経済学の題材の出典です
