"""Jupyter Notebook（notebooks/）のテスト。

- すべてのノートブックが、上から順に、エラーなく実行できる（数字を書き換えて使う前提の確認）
- 実行結果を保存していない（差分がきれい）
- 先頭のコードのセルが、「Parameters」（数字を書き換えるセル）の印を持つ
- 登録したノートブックだけがあり、記事から案内されている
"""

import glob
from pathlib import Path
from typing import cast

import nbformat
import pytest
from nbclient import NotebookClient

from tools.build_notebooks import NOTEBOOKS, NOTEBOOKS_DIR

APP_DIR = NOTEBOOKS_DIR.parent
ARTICLES_DIR = APP_DIR.parents[2] / "docs" / "article" / "economics-programming"
PATHS = sorted(NOTEBOOKS_DIR.glob("*.ipynb"))


def _read(path: Path) -> nbformat.NotebookNode:
    return cast(nbformat.NotebookNode, nbformat.read(path, as_version=4))


def test_登録したノートブックだけがある() -> None:
    assert [p.stem for p in PATHS] == sorted(NOTEBOOKS)


@pytest.mark.parametrize("path", PATHS, ids=lambda p: p.stem)
def test_ノートブックは実行結果を保存していない(path: Path) -> None:
    for cell in _read(path).cells:
        if cell.cell_type == "code":
            assert cell.outputs == []
            assert cell.execution_count is None


@pytest.mark.parametrize("path", PATHS, ids=lambda p: p.stem)
def test_最初のコードのセルは数字を書き換えるセル(path: Path) -> None:
    first = next(c for c in _read(path).cells if c.cell_type == "code")
    assert first.metadata.get("tags") == ["parameters"]


@pytest.mark.parametrize("path", PATHS, ids=lambda p: p.stem)
def test_ノートブックは上から順にエラーなく実行できる(path: Path) -> None:
    notebook = _read(path)
    client = NotebookClient(
        notebook,
        timeout=60,
        kernel_name="python3",
        resources={"metadata": {"path": str(NOTEBOOKS_DIR)}},
    )
    client.execute()
    outputs = [o for c in notebook.cells if c.cell_type == "code" for o in c.outputs]
    assert outputs, f"{path.name}: 出力がない"
    assert all(o.output_type != "error" for o in outputs)


@pytest.mark.parametrize("path", PATHS, ids=lambda p: p.stem)
def test_ノートブックは記事から案内されている(path: Path) -> None:
    if path.stem.startswith("appendix"):
        pattern = path.stem.replace("_", "-") + ".md"
    else:
        pattern = f"{path.stem[2:4]}-*.md"
    articles = glob.glob(str(ARTICLES_DIR / pattern))
    assert articles, f"{path.name}: 対応する記事がない"
    assert path.name in Path(articles[0]).read_text(encoding="utf-8")


@pytest.mark.parametrize("path", PATHS, ids=lambda p: p.stem)
def test_Parametersの次は準備のセル(path: Path) -> None:
    """`jupyter lab notebooks/` で開いても、lib を読めるようにする準備のセル。"""
    codes = [c for c in _read(path).cells if c.cell_type == "code"]
    assert "sys.path" in codes[1].source
