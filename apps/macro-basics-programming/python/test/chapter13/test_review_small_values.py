"""全体レビュー（2026-11-21）の指摘: 0 より大きく 1 未満の有効な値。"""

import pytest

from lib.chapter13.quantity import marshall_k


def test_流通速度が1未満の正でもマーシャルのkを求められる() -> None:
    assert marshall_k(0.5) == pytest.approx(2)
