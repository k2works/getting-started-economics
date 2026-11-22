"""章をまたぐ import の向きのテスト。

`lib/chapterNN` と `test/chapterNN` は、前の章（`chapterMM`、MM <= NN）だけを import する。
後の章への import や循環が入ると、`import *` で解答を実行する検査（その章以前だけを読む）が、
解答だけを壊すので、先にここで見つける。
"""

import ast
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parents[2]
PREFIX = "lib.chapter"


def _chapter_of(name: str) -> int | None:
    """`lib.chapter05.derivative` のような名前から、章の番号（5）を取り出す。"""
    if not name.startswith(PREFIX):
        return None
    return int(name.removeprefix(PREFIX).split(".")[0])


def _imported_chapters(path: Path) -> set[int]:
    chapters: set[int] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        names = []
        if isinstance(node, ast.ImportFrom) and node.module:
            names = [node.module]
        elif isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        for name in names:
            chapter = _chapter_of(name)
            if chapter is not None:
                chapters.add(chapter)
    return chapters


def _own_chapter(path: Path) -> int:
    chapter_dir = next(p for p in path.parents if p.name.startswith("chapter"))
    return int(chapter_dir.name.removeprefix("chapter"))


FILES = sorted(
    [*APP.glob("lib/chapter*/*.py"), *APP.glob("test/chapter*/*.py")],
    key=lambda p: p.as_posix(),
)


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.relative_to(APP).as_posix())
def test_章は前の章だけをimportする(path: Path) -> None:
    own = _own_chapter(path)
    later = {c for c in _imported_chapters(path) if c > own}
    assert not later, f"第 {own} 章が、後の章 {sorted(later)} を import している"


def test_判定が空振りしない() -> None:
    """依存を数える仕組みが、実際の import を見つけられること（第 5 章は、第 2 章を使う）。"""
    derivative = APP / "lib" / "chapter05" / "derivative.py"
    assert 2 in _imported_chapters(derivative)
    assert _chapter_of("numpy") is None
    assert _chapter_of("lib.chapter05.derivative") == 5
