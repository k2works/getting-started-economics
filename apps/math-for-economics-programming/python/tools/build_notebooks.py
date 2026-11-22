"""Jupyter Notebook（notebooks/）を、書き出す。

    uv run python -m tools.build_notebooks            # すべて
    uv run python -m tools.build_notebooks ch05       # 名前を指定（前方一致）

各ノートブックは、(1) 説明、(2) 数字を書き換えるセル（Parameters）、(3) 各章の関数を
呼んで、結果を表示するセル、(4) 図、(5) 「試してみよう」の順にそろえる。
セルの並びは、章ごとに tools/notebooks/chNN.py に書く。
`試してみよう` に書く数値は、実際に実行して確かめた値だけにする。
"""

import sys
from collections.abc import Callable
from pathlib import Path

from nbformat.notebooknode import NotebookNode

from tools.notebook_builder import write
from tools.notebooks import (
    ch01,
    ch02,
    ch03,
    ch04,
    ch05,
    ch06,
    ch07,
    ch08,
    ch09,
    ch10,
    ch11,
    ch12,
)

NOTEBOOKS_DIR = Path(__file__).resolve().parents[1] / "notebooks"
NOTEBOOKS: dict[str, Callable[[], list[NotebookNode]]] = {
    ch01.NAME: ch01.cells,
    ch02.NAME: ch02.cells,
    ch03.NAME: ch03.cells,
    ch04.NAME: ch04.cells,
    ch05.NAME: ch05.cells,
    ch06.NAME: ch06.cells,
    ch07.NAME: ch07.cells,
    ch08.NAME: ch08.cells,
    ch09.NAME: ch09.cells,
    ch10.NAME: ch10.cells,
    ch11.NAME: ch11.cells,
    ch12.NAME: ch12.cells,
}


def main() -> None:
    prefixes = sys.argv[1:]
    for name, build in sorted(NOTEBOOKS.items()):
        if prefixes and not any(name.startswith(p) for p in prefixes):
            continue
        path = NOTEBOOKS_DIR / f"{name}.ipynb"
        write(path, build())
        print(f"生成: {path.name}")


if __name__ == "__main__":
    main()
