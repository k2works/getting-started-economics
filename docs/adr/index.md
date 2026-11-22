# ADR (Architecture Decision Records)

技術的意思決定を記録した ADR です。

## プロジェクト一覧

| プロジェクト | 概要 | 状況 |
| :--- | :--- | :--- |
| [ミクロ経済学のためのプログラミング（初級）](micro-basics-programming/index.md) | 章の分割・共通ツール・テストのタイムアウトの決定 | ADR 3 件 |
| [記事検査の共通ツール（article-tools）](article-tools/index.md) | 検査の厳格化・図の指紋の拡張・変異確認ツールの決定 | ADR 2 件 |

## 補足

- プロジェクトの追加は `apply-docs-structure` スキル（add-project）で行い、この一覧と `docs/index.md` を更新します。
- 実ドキュメントは `adr/<project>/` に置き、プロジェクトの `index.md` で一覧を管理します。
- ADR の作成には `creating-adr` スキルを使用してください。
- テンプレートは [template/ADR.md](../template/ADR.md) です。
