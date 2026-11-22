"""章ごとのノートブックに共通する部分（使い方の説明・先頭のセル）。"""

from nbformat.notebooknode import NotebookNode

from tools.notebook_builder import markdown

HOW_TO_RUN = (
    "**使い方**: 「Parameters」のセルの数字を書き換えて、上から順に実行します"
    "（メニューの Run → Run All Cells）。数字を変えるたびに、結果と図が変わります。\n\n"
    "起動: アプリのディレクトリで `uv run --with jupyterlab jupyter lab notebooks/` "
    "を実行します。"
)


def title(number: int, name: str, article: str) -> NotebookNode:
    """先頭の説明のセル（章のタイトル、使い方、記事のパス）。"""
    return markdown(
        f"# 第 {number} 章 {name}: 数字を変えて確かめる\n\n"
        + HOW_TO_RUN
        + f"\n\n記事: `docs/article/math-for-economics-programming/{article}.md`"
    )
