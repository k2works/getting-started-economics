"""図の登録（tools/figure_registry.py）のテスト。"""

import re

from tools.figure_registry import FIGURES


def test_記事の図の名前は画像ファイル名と対応している() -> None:
    assert FIGURES
    assert all(re.fullmatch(r"ch\d{2}-[a-z0-9-]+", name) for name in FIGURES)
