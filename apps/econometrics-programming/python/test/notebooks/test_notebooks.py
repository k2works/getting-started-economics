"""Jupyter Notebook（notebooks/）のテスト。

- すべてのノートブックが、上から順に、エラーなく実行できる（数字を書き換えて使う前提の確認）
- 実行結果を保存していない（差分がきれい）
- 先頭のコードのセルが、「Parameters」（数字を書き換えるセル）の印を持つ
- 登録したノートブックだけがあり、記事から案内されている
"""

import glob
import subprocess
import sys
from pathlib import Path
from typing import cast

import nbformat
import pytest
from nbclient import NotebookClient

from tools.build_notebooks import NOTEBOOKS, NOTEBOOKS_DIR
from tools.notebook_builder import BOOTSTRAP

APP_DIR = NOTEBOOKS_DIR.parent
ARTICLES_DIR = APP_DIR.parents[2] / "docs" / "article" / "econometrics-programming"
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
    chapter = path.stem[2:4]
    articles = glob.glob(str(ARTICLES_DIR / f"{chapter}-*.md"))
    assert articles, f"{path.name}: 第 {chapter} 章の記事がない"
    assert path.name in Path(articles[0]).read_text(encoding="utf-8")


@pytest.mark.parametrize("path", PATHS, ids=lambda p: p.stem)
def test_Parametersの次は準備のセル(path: Path) -> None:
    """`jupyter lab notebooks/` で開いても、lib を読めるようにする準備のセル。"""
    codes = [c for c in _read(path).cells if c.cell_type == "code"]
    assert "sys.path" in codes[1].source


@pytest.mark.parametrize("path", PATHS, ids=lambda p: p.stem)
def test_準備セルは競合するlibより自分のlibを優先する(path: Path) -> None:
    source = [c for c in _read(path).cells if c.cell_type == "code"][1].source
    assert source == BOOTSTRAP.strip("\n")
    script = f'''import sys, types
sys.path.append({str(APP_DIR)!r})
foreign = types.ModuleType("lib")
foreign.__file__ = "foreign/lib/__init__.py"
foreign.__path__ = ["foreign/lib"]
sys.modules["lib"] = foreign
sys.modules["lib.chapter01"] = types.ModuleType("lib.chapter01")
exec({source!r})
import lib
from pathlib import Path
assert Path(lib.__file__).resolve() == Path({str(APP_DIR / "lib" / "__init__.py")!r}).resolve()
assert "lib.chapter01" not in sys.modules
assert sys.path[0] == {str(APP_DIR)!r}
'''
    subprocess.run([sys.executable, "-c", script], cwd=NOTEBOOKS_DIR, check=True)
