# creating-article — このプロジェクトの実構成

`SKILL.md` の汎用手順を、このリポジトリに当てはめた具体値。食い違うときは、こちらを正とする。

## 連載の一覧

| 連載 | 記事 | 実装 |
| :--- | :--- | :--- |
| 経済学のためのプログラミング | `docs/article/economics-programming/` | `apps/economics-programming/python/` |
| マクロ経済学のためのプログラミング（中級＋） | `docs/article/macro-programming/` | `apps/macro-programming/python/` |
| 計量経済学のためのプログラミング | `docs/article/econometrics-programming/` | `apps/econometrics-programming/python/` |
| マクロ経済学のためのプログラミング（初級） | `docs/article/macro-basics-programming/` | `apps/macro-basics-programming/python/` |

新しい連載の構成は、`macro-basics-programming` を雛形にする（新しいほど、規律が揃っている）。

## 配置

- 記事: `docs/article/{連載}/` — `outline.md`（計画。サイトに載せない。`mkdocs.yml` の `exclude_docs`）、`index.md`、`how-to-read.md`、`NN-*.md`、`images/`
- 実装: `apps/{連載}/python/` — `lib/chapterNN/`（実装と `plot.py`）、`test/chapterNN/`、`tools/`（連載固有のデータ）、`data/`、`practice/`（読者が写経する場所）、`pyproject.toml`、`tox.ini`、`.ruff.toml`
- 共通の検査ツール: `apps/article-tools/`（各連載の dev 依存に、編集可能なパス依存で入る）
- 計画・報告の置き場: `docs/review/{連載}_review_{日付}.md`（索引 `docs/review/index.md`）、`docs/log.md`
- サイト: `mkdocs.yml` の nav、`docs/article/index.md` の行、`docs/index.md`

## コマンド（連載の `apps/{連載}/python/` で実行）

| 目的 | コマンド |
| :--- | :--- |
| 環境 | `uv sync` |
| テスト + カバレッジ | `uv run pytest test --cov=lib --cov-fail-under=100` |
| lint・整形・型 | `uv run ruff check .`、`uv run ruff format .`、`uv run mypy lib test tools` |
| 全部 | `uv run tox -e all` |
| 記事の検査 | `uv run python -m article_tools.check_articles`（コードがフェンスの中・転記コードと実装の一致・`N passed` の件数・解答の実行） |
| 予想の答え合わせの検査 | `uv run python -m article_tools.check_predictions`（スクリプトを実行し、出力を許容誤差つきで照合） |
| 図の検査 | `uv run python -m article_tools.render_figures --check`（図を生成して指紋を比較。更新は `--check` なし） |
| サイトのビルド | リポジトリ直下で `npm run docs:build`（`mkdocs` はシェルに無い。実行して確かめる） |

Windows のシェルでは、日本語を扱うので `PYTHONUTF8=1` を付ける。別の連載の検査は、その連載のディレクトリで実行する（`ARTICLE_APP_DIR` または cwd で連載が決まる）。

## 連載固有のデータ（`tools/`）

- `figure_registry.py` — 章ごとの登録（`figures/chNN.py`）を合成する。図は、章のファイルに足す
- `answer_preludes.json` — 解答のコードの前置き
- `article_code_excerpts.json` — 抜粋の許可
- `figure_fingerprints.json` — 図の指紋
- `test/conftest.py` — matplotlib を Agg に固定する

## 規約

- 見出しの「プログラミング」小節は、Red → Green → Refactor の小節を含む（見出しに「Red → Green → Refactor」とは書かない）
- 「予想する」に答えを書かない。答えは「予想の答え合わせ」の出力にだけ置く
- 記事は、テンプレート（スクラッチ）+ ビルドスクリプトから生成する。大きく直すとき以外は、記事を直接編集してよいが、検査は必ず通す
- コミット: Conventional Commits（日本語）。`feat(連載)`・`docs(article)`・`ci(python)` を分ける。末尾に `Co-Authored-By` と `Claude-Session` を付ける
- `.claude/agent-memory/*` は、コミットしない
- CI: `.github/workflows/python-ci.yml`（連載ごとの matrix と `article-tools` ジョブ）。連載の追加時は、`paths` と matrix に足す
- 作業が完全に完了し、未解決がないときだけ、`CLAUDE.md` の合い言葉を報告する

## 作業の目安（初級連載での実績）

- 14 章を 4 つの Unit（雛形 + 第 1 章 / 第 2〜5 章 / 第 6〜9 章 / 第 10〜14 章）に分け、各 Unit を 1 Bolt で進めた。依存しない章は並列
- 全体レビューは Bolt 8。5 視点を並列。高 10 件に対応し、残りは報告書と outline に記録
