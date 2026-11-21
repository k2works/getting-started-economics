"""章をまたいで、公開する名前が重複しないことのテスト。

練習問題の解答は、その章以前のすべての章を `import *` して実行する（tools/check_articles）。
名前が重複すると、あとの章の定義が、前の章の定義を、黙って上書きする。章を足すたびに壊れるのを防ぐ。
"""

import ast
from collections import defaultdict
from pathlib import Path

LIB = Path(__file__).resolve().parents[2] / "lib"


def public_names(path: Path) -> list[str]:
    """モジュールのトップレベルで定義された、公開する名前（`_` で始まらないもの）。"""
    names = []
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.FunctionDef | ast.ClassDef):
            names.append(node.name)
        elif isinstance(node, ast.Assign):
            names.extend(t.id for t in node.targets if isinstance(t, ast.Name))
    return [name for name in names if not name.startswith("_")]


def test_モジュールの公開名を取り出す(tmp_path: Path) -> None:
    source = "A = 1\n_B = 2\n\ndef f():\n    pass\n\nclass C:\n    pass\n\ndef _g():\n    pass\n"
    module = tmp_path / "m.py"
    module.write_text(source, encoding="utf-8")
    assert public_names(module) == ["A", "f", "C"]


def test_章をまたいで公開名が重複しない() -> None:
    owners: dict[str, list[str]] = defaultdict(list)
    for path in sorted(LIB.glob("chapter*/*.py")):
        if path.name == "__init__.py":
            continue
        for name in public_names(path):
            owners[name].append(f"{path.parent.name}/{path.name}")
    duplicated = {name: where for name, where in owners.items() if len(where) > 1}
    assert duplicated == {}
