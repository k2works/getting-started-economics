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


def test_種を固定した雑音の値() -> None:
    # 傾き −0.4、切片 1.2 の直線（0.8、0.4、0.0）に、種 0・標準偏差 0.1 の雑音が乗る
    values = synthetic_unemployment_change([1.0, 2.0, 3.0], -0.4, 1.2, 0.1, 0)
    assert values == pytest.approx(
        [0.8125730221093392, 0.3867895136708697, 0.06404226504432799], abs=1e-12
    )
