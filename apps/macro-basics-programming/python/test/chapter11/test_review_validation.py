"""全体レビュー（2026-11-21）の指摘: 浮動小数点のほぼ同じ値と、負の雑音を弾く。"""

import pytest

from lib.chapter11.okun import okun_coefficients, synthetic_unemployment_change


def test_浮動小数点のほぼ同じ成長率でもエラー() -> None:
    with pytest.raises(ValueError, match="すべて同じ"):
        okun_coefficients([0.1 + 0.2, 0.3, 0.3], [1.0, 2.0, 3.0])
    with pytest.raises(ValueError, match="すべて同じ"):
        okun_coefficients([0.1, 0.1, 0.1], [1.0, 2.0, 3.0])


def test_雑音が負なら日本語のエラー() -> None:
    with pytest.raises(ValueError, match="雑音"):
        synthetic_unemployment_change([1.0, 2.0], -0.4, 1.2, -0.1, 0)
