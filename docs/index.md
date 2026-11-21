---
okf_version: "0.2"
---

# 経済学入門

経済学（ミクロ・マクロ・計量経済学）の式とモデルを、Python のコードとテストで確かめながら学び、よいソフトウェアの作り方も身につけるプロジェクトです。

## 記事

- [記事の一覧](./article/index.md) - 学習用の記事シリーズ（公開サイトへのリンクを含む）
- [経済学・経済政策 全体マインドマップ](<./article/経済学・経済政策 全体マインドマップ.md>) - 経済学・経済政策の 7 冊のテキストの章立てを、1 枚にまとめた図
- [経済学・経済政策 トピック別マインドマップ](<./article/経済学・経済政策 トピック別マインドマップ.md>) - トピックごとの式・曲線・混同しやすい対比

### 連載の入口

| 連載 | 水準・題材 | 章 | 入口 | 読み方 |
| :--- | :--- | :--- | :--- | :--- |
| 経済学のためのプログラミング入門 | 経済モデルを軸にした Python 入門（需要曲線・市場均衡・IS-LM・ゲーム理論など） | 15 章と付録 A | [概要](./article/economics-programming/index.md) | [読み方](./article/economics-programming/how-to-read.md) |
| ミクロ経済学のためのプログラミング（初級） | 教科書的なミクロ（無差別曲線・費用曲線・市場均衡・余剰・独占・ゲーム理論・外部効果・情報の非対称性） | 14 章（4 部。執筆中。第 3 部まで公開） | [概要](./article/micro-basics-programming/index.md) | [読み方](./article/micro-basics-programming/how-to-read.md) |
| マクロ経済学のためのプログラミング（初級） | 教科書的なマクロ（GDP・45 度線・IS-LM・AD-AS・フィリップス曲線・貨幣数量説・開放経済） | 14 章（3 部） | [概要](./article/macro-basics-programming/index.md) | [読み方](./article/macro-basics-programming/how-to-read.md) |
| マクロ経済学のためのプログラミング（中級＋） | 成長・景気循環・貨幣・為替の分析と、動学モデルの数値計算 | 18 章（4 部） | [概要](./article/macro-programming/index.md) | [読み方](./article/macro-programming/how-to-read.md) |
| 計量経済学のためのプログラミング | 回帰・推論・パネル・操作変数法・ロジット・トービット・ヘックマンの推定量 | 16 章（4 部） | [概要](./article/econometrics-programming/index.md) | [読み方](./article/econometrics-programming/how-to-read.md) |

読む順序の目安は、入門 → マクロ（初級）→ マクロ（中級＋）、計量経済学は、入門のあとに、独立して読めます。各連載は、「予想する → プログラミング（予想の答え合わせを含む）→ 練習問題 → 到達チェック」の型で進みます。

### その他の記事シリーズ

プログラミング言語・関数型・データベース・コンテナなどの学習用シリーズは、[記事の一覧](./article/index.md) にまとめています（公開サイトへのリンクです）。

## 開発

- [開発](./development/index.md) - リリース計画、イテレーション計画、進捗管理の入口
- [ADR](./adr/index.md) - アーキテクチャに関する決定の記録
- [ジャーナル](./journal/index.md) - 開発ジャーナル（判断と学びの記録）

## 分析・設計

- [戦略](./strategy/index.md) - ビジネス構造やプロジェクトの方向性を整理します。
- [要件](./requirements/index.md) - RDRA 2.0 ベースで要件を定義します。
- [設計](./design/index.md) - アーキテクチャ、モデル、品質方針を整理します。
- [レビュー](./review/index.md) - 分析・開発レビュー結果の記録です。

## 運用

- [運用](./operation/index.md) - 環境構築、デプロイ、運用手順の入口です。

## リファレンス

- [よいソフトウェアとは](./reference/よいソフトウェアとは.md) - ソフトウェアの価値と品質
- [ロジカルシンキング](./reference/ロジカルシンキング.md) - 論理的に考えるための道具立て
- [開発ガイド](./reference/開発ガイド.md) - 開発ライフサイクルの全体像
- [開発ガイド（AI-DLC 版）](./reference/開発ガイド_AI-DLC版.md) - AI が計画・生成し、人が承認ゲートで検証する開発ライフサイクル
- [AI-DLC 導入ガイド](./reference/AI-DLC導入ガイド.md) - AI-DLC の原則・成果物・フェーズと、本プロジェクトへの組み込み方
- [コーディングとテストガイド](./reference/コーディングとテストガイド.md) - TDD の実践ガイド
- [アーキテクチャ設計ガイド](./reference/アーキテクチャ設計ガイド.md) - アーキテクチャ設計の指針
- [テスト戦略ガイド](./reference/テスト戦略ガイド.md) - テスト計画と戦略
- [リリース・イテレーション計画ガイド](./reference/リリース・イテレーション計画ガイド.md) - 計画策定の指針
- [リファレンス一覧](./reference/index.md) - その他のガイド

## その他

- [テンプレート](./template/index.md) - 各種ドキュメントの作成テンプレート
- [更新履歴](./log.md) - ドキュメントの作成・更新の記録
- `strategy/` は企業で 1 つの統合戦略として管理し、プロジェクト別のサブディレクトリは作りません。
- `requirements/`、`design/`、`development/`、`operation/`、`adr/`、`journal/`、`review/` はプロジェクト別に管理します。カテゴリ直下の `index.md` はプロジェクト一覧の索引で、実ドキュメントとその一覧は `<category>/<project>/index.md` 配下に置きます。
- プロジェクトの追加は `apply-docs-structure` スキル（add-project）で行います。構成の規約は [ドキュメント構成ガイド](./reference/ドキュメント構成ガイド.md) を参照してください。
- `assets/` は MkDocs 用のスタイル・スクリプトを格納しています。
