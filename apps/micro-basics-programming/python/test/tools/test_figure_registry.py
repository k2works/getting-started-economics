"""図の登録（tools/figure_registry.py）のテスト。"""

import re
from importlib import import_module
from pathlib import Path

from tools.figure_registry import FIGURES

FIGURE_DIR = Path(__file__).resolve().parents[2] / "tools" / "figures"


def test_記事の図の名前は画像ファイル名と対応している() -> None:
    assert FIGURES
    assert all(re.fullmatch(r"ch\d{2}-[a-z0-9-]+", name) for name in FIGURES)


def test_章ごとの登録は自分の章の名前だけを持ち重複なく合成される() -> None:
    total = 0
    for path in sorted(FIGURE_DIR.glob("ch[0-9][0-9].py")):
        module = import_module(f"tools.figures.{path.stem}")
        assert all(name.startswith(f"{path.stem}-") for name in module.FIGURES)
        total += len(module.FIGURES)
    assert total == len(FIGURES)
