"""第 12 章: 投資の理論のテスト。"""

import pytest

from lib.chapter12.investment import (
    accelerator_investment,
    accelerator_path,
    desired_capital,
    should_invest,
    stock_adjustment_investment,
    tobins_q,
)


def test_加速度原理の投資は資本係数と所得の増加分の積() -> None:
    assert accelerator_investment(2, 50) == pytest.approx(100)


def test_所得の増加が止まると投資は0になる() -> None:
    assert accelerator_investment(2, 0) == 0


def test_所得が減ると投資は負になる() -> None:
    assert accelerator_investment(2, -10) == pytest.approx(-20)


def test_資本係数が0なら投資は0() -> None:
    assert accelerator_investment(0, 50) == 0


def test_資本係数が負ならエラー() -> None:
    with pytest.raises(ValueError, match="資本係数"):
        accelerator_investment(-1, 50)


def test_所得の増加率が下がると投資は所得より先に減る() -> None:
    incomes = [100, 120, 140, 150, 155, 155]
    assert accelerator_path(2, incomes) == pytest.approx([40, 40, 20, 10, 0])


def test_所得が1期分しかなければ投資の系列は空() -> None:
    assert accelerator_path(2, [100]) == []


def test_最適な資本ストックは資本係数と所得の積() -> None:
    assert desired_capital(2, 100) == pytest.approx(200)


def test_資本ストック調整原理は最適な資本との差の一部だけ投資する() -> None:
    assert stock_adjustment_investment(0.5, 200, 120) == pytest.approx(40)


def test_加速子が1なら差を一度に埋める() -> None:
    assert stock_adjustment_investment(1, 200, 120) == pytest.approx(80)


def test_資本が最適より多ければ投資は負() -> None:
    assert stock_adjustment_investment(0.5, 100, 120) == pytest.approx(-10)


@pytest.mark.parametrize("adjust", [0, -0.5, 1.2])
def test_加速子が範囲外ならエラー(adjust: float) -> None:
    with pytest.raises(ValueError, match="加速子"):
        stock_adjustment_investment(adjust, 200, 120)


def test_トービンのqは市場価値を再取得価格で割る() -> None:
    assert tobins_q(120, 100) == pytest.approx(1.2)


def test_再取得価格が0以下ならエラー() -> None:
    with pytest.raises(ValueError, match="再取得価格"):
        tobins_q(120, 0)


def test_qが1より大きければ投資する() -> None:
    assert should_invest(1.2) is True
    assert should_invest(0.8) is False


def test_qがちょうど1なら投資しない() -> None:
    assert should_invest(1.0) is False
