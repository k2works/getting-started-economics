---
type: ADR
title: "ADR-003: pytest-timeout の導入"
description: "無限ループになる不具合や変異で、テストが止まらなくなるのを防ぐため、開発用の依存に pytest-timeout を足し、1 件 60 秒で打ち切る。"
tags: [adr,micro-basics-programming]
status: draft
generated: { by: claude-code/claude-sonnet-5-5, at: 2026-11-22T00:00:00Z }
---

# ADR-003: pytest-timeout の導入

日付: 2026-11-22

## ステータス

承認（ユーザーの承認: 2026-11-22）。実施済み（ミクロ初級のみ）。

## コンテキスト

テスターの変異確認で、`lib/chapter13/public.py`（当時）の演算子を変えると、無限ループになり、pytest が止まらず、CI は、ジョブのタイムアウト（20 分）まで止まらないことが分かった。

## 決定

`pytest-timeout` を、ミクロ初級の開発用の依存に足し、`pyproject.toml` に `timeout = 60`（1 件 60 秒）を置く。他の連載への展開は、必要になったときに、個別に判断する。

## 影響

`uv.lock` が更新される（`pytest-timeout 2.4.0`）。通常のテストは、全体で 10 秒程度で、影響はない。

## コンプライアンス

`uv sync --locked` が CI で通ること。

## 備考

提案: クロード（テスターの指摘）。承認: ユーザー。
