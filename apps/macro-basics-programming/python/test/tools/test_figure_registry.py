"""図の登録（tools/figure_registry.py）のテスト。"""

import re

from tools.figure_registry import FIGURES


def test_記事の図の名前は画像ファイル名と対応している() -> None:
    assert FIGURES
    assert all(re.fullmatch(r"ch\d{2}-[a-z0-9-]+", name) for name in FIGURES)


def test_章ごとの登録は自分の章の名前だけを持ち重複なく合成される() -> None:
    from tools.figures import (
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
        ch13,
        ch14,
    )  # fmt: skip

    chapters = [
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
        ch13,
        ch14,
    ]  # noqa: E501
    total = 0
    for number, module in enumerate(chapters, start=1):
        assert all(name.startswith(f"ch{number:02d}-") for name in module.FIGURES)
        total += len(module.FIGURES)
    assert total == len(FIGURES)
