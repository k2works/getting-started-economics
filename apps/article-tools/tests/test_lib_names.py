"""章をまたぐ公開名の重複検査（article_tools/lib_names.py）のテスト。"""

from pathlib import Path

from article_tools.lib_names import duplicated_names, public_names


def test_モジュールの公開名を取り出す(tmp_path: Path) -> None:
    source = (
        "A = 1\n_B = 2\nD: int = 3\n\ndef f():\n    pass\n\n"
        "class C:\n    pass\n\ndef _g():\n    pass\n"
    )
    module = tmp_path / "m.py"
    module.write_text(source, encoding="utf-8")
    assert public_names(module) == ["A", "D", "f", "C"]


def test_章をまたいで重複した名前を見つける(tmp_path: Path) -> None:
    for chapter, body in (
        ("chapter01", "def f():\n    pass\n"),
        ("chapter02", "def f():\n    pass\n\ndef g():\n    pass\n"),
    ):
        directory = tmp_path / chapter
        directory.mkdir()
        (directory / "__init__.py").write_text("def f():\n    pass\n", encoding="utf-8")
        (directory / "m.py").write_text(body, encoding="utf-8")
    assert duplicated_names(tmp_path) == {"f": ["chapter01/m.py", "chapter02/m.py"]}


def test_重複がなければ空(tmp_path: Path) -> None:
    directory = tmp_path / "chapter01"
    directory.mkdir()
    (directory / "m.py").write_text("def f():\n    pass\n", encoding="utf-8")
    assert duplicated_names(tmp_path) == {}
