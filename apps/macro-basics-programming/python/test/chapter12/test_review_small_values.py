"""全体レビュー（2026-11-21）の指摘: 0 より大きく 1 未満の有効な値。"""

import pytest

from lib.chapter12.consumption import lifecycle_consumption
from lib.chapter12.investment import accelerator_investment, tobins_q


def test_生涯の年数が1未満の正でも有効() -> None:
    assert lifecycle_consumption(10, 0.25, 0.5) == pytest.approx(5)


def test_資本係数0は許される() -> None:
    assert accelerator_investment(0, 10) == 0


def test_再取得価格が1未満の正でもqを求められる() -> None:
    assert tobins_q(1, 0.5) == pytest.approx(2)
