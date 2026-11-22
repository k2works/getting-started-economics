"""章をまたいで、公開する名前が重複しないことのテスト。

検査の本体は、共通ツール（article_tools/lib_names.py）にある。
"""

from pathlib import Path

from article_tools.lib_names import duplicated_names

LIB = Path(__file__).resolve().parents[2] / "lib"


def test_章をまたいで公開名が重複しない() -> None:
    assert duplicated_names(LIB) == {}
