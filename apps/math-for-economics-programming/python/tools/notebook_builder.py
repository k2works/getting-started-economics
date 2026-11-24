"""Jupyter Notebook を、セルの並びから作る（実行結果は、保存しない）。

ノートブックの中身は、`tools/build_notebooks.py` に、セルのデータとして書く。
JSON を手で編集せず、スクリプトから作り直すので、差分が小さく、きれいに保てる。
"""

from pathlib import Path
from typing import cast

import nbformat
from nbformat.notebooknode import NotebookNode

# カーネル名は、連載のディレクトリ名（npm run setup:* が登録する）。
# JupyterLab で開くと、連載の .venv（numpy など入り）で動く。
KERNEL_NAME = Path(__file__).resolve().parents[2].name

BOOTSTRAP = """
# --- 準備（変更しません）: lib を読み込めるようにします ---
import sys
from pathlib import Path

_root = next(p for p in (Path.cwd(), *Path.cwd().parents) if (p / "lib").is_dir())
if str(_root) in sys.path:
    sys.path.remove(str(_root))
sys.path.insert(0, str(_root))
_lib = sys.modules.get("lib")
if _lib is not None and Path(getattr(_lib, "__file__", "") or "").resolve().parent \
!= _root / "lib":
    for _name in list(sys.modules):
        if _name == "lib" or _name.startswith("lib."):
            del sys.modules[_name]
"""


def markdown(text: str) -> NotebookNode:
    """説明のセル。"""
    return cast(NotebookNode, nbformat.v4.new_markdown_cell(text.strip("\n")))


def code(source: str, parameters: bool = False) -> NotebookNode:
    """コードのセル。parameters=True なら、「数字を書き換える」セルの印を付ける。"""
    cell = cast(NotebookNode, nbformat.v4.new_code_cell(source.strip("\n")))
    if parameters:
        cell.metadata["tags"] = ["parameters"]
    return cell


def write(path: Path, cells: list[NotebookNode]) -> None:
    """セルの並びを、ノートブックのファイルに書く。

    最初のコードのセル（Parameters）の次に、準備のセルを入れる。`jupyter lab` で開くと、
    カーネルの作業場所が notebooks/ になり、lib が読めないため。セルの id は、通し番号。
    """
    first = next(i for i, c in enumerate(cells) if c.cell_type == "code")
    cells = [*cells[: first + 1], code(BOOTSTRAP), *cells[first + 1 :]]
    for index, cell in enumerate(cells):
        cell["id"] = f"cell-{index + 1:02d}"
    notebook = nbformat.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {
                "display_name": KERNEL_NAME,
                "language": "python",
                "name": KERNEL_NAME,
            },
            "language_info": {"name": "python"},
        },
    )
    nbformat.validate(notebook)
    path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(notebook, path)
