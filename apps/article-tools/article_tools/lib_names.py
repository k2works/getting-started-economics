"""章をまたいで、公開する名前が重複しないことの検査。

練習問題の解答は、その章以前のすべての章を `import *` して実行する（check_articles）。
名前が重複すると、あとの章の定義が、前の章の定義を、黙って上書きする。
連載ごとの `test/tools/test_lib_names.py` から、この関数を呼ぶ。
"""

import ast
from collections import defaultdict
from pathlib import Path


def public_names(path: Path) -> list[str]:
    """モジュールのトップレベルで定義された、公開する名前（`_` で始まらないもの）。"""
    names: list[str] = []
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.FunctionDef | ast.ClassDef):
            names.append(node.name)
        elif isinstance(node, ast.Assign):
            names.extend(t.id for t in node.targets if isinstance(t, ast.Name))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.append(node.target.id)
    return [name for name in names if not name.startswith("_")]


def duplicated_names(lib_dir: Path) -> dict[str, list[str]]:
    """`lib/chapterNN/*.py` の公開名のうち、複数のファイルで定義されているもの。"""
    owners: dict[str, list[str]] = defaultdict(list)
    for path in sorted(lib_dir.glob("chapter*/*.py")):
        if path.name == "__init__.py":
            continue
        for name in public_names(path):
            owners[name].append(f"{path.parent.name}/{path.name}")
    return {name: where for name, where in owners.items() if len(where) > 1}
