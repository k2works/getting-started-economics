"""第 11 章: フィリップス曲線のテスト。"""

import pytest

from lib.chapter11.phillips import (
    accelerating_inflation_path,
    implied_natural_rate,
    short_run_inflation,
)

# π = π^e − β(u − u_n)、u_n = 5、π^e = 2、β = 0.5
NATURAL = 5
EXPECTED = 2
BETA = 0.5


def test_自然失業率ではインフレ率は期待インフレ率に等しい() -> None:
    assert short_run_inflation(NATURAL, NATURAL, EXPECTED, BETA) == pytest.approx(2)


def test_失業率が自然失業率より低いとインフレ率は期待より高い() -> None:
    assert short_run_inflation(4, NATURAL, EXPECTED, BETA) == pytest.approx(2.5)


def test_失業率が自然失業率より高いとインフレ率は期待より低い() -> None:
    assert short_run_inflation(6, NATURAL, EXPECTED, BETA) == pytest.approx(1.5)


def test_短期のフィリップス曲線は右下がり() -> None:
    rates = [short_run_inflation(u, NATURAL, EXPECTED, BETA) for u in (3, 4, 5, 6)]
    assert rates == sorted(rates, reverse=True)


def test_期待インフレ率が上がると曲線は上へ動く() -> None:
    low = short_run_inflation(4, NATURAL, 2, BETA)
    high = short_run_inflation(4, NATURAL, 4, BETA)
    assert high - low == pytest.approx(2)


def test_感応度が0以下ならエラー() -> None:
    with pytest.raises(ValueError, match="感応度"):
        short_run_inflation(4, NATURAL, EXPECTED, 0)


def test_観測から自然失業率を逆算する() -> None:
    assert implied_natural_rate(4, 3, 2, 0.5) == pytest.approx(6)


def test_逆算した自然失業率で観測のインフレ率が再現される() -> None:
    natural = implied_natural_rate(4, 3, 2, 0.5)
    assert short_run_inflation(4, natural, 2, 0.5) == pytest.approx(3)


def test_逆算でも感応度が0以下ならエラー() -> None:
    with pytest.raises(ValueError, match="感応度"):
        implied_natural_rate(4, 3, 2, 0)


def test_失業率を自然失業率より低く保つとインフレ率は加速する() -> None:
    path = accelerating_inflation_path(4, NATURAL, EXPECTED, BETA, 3)
    assert path == pytest.approx([2.0, 2.5, 3.0, 3.5])


def test_自然失業率に保てばインフレ率は変わらない() -> None:
    path = accelerating_inflation_path(NATURAL, NATURAL, EXPECTED, BETA, 3)
    assert path == pytest.approx([2, 2, 2, 2])


def test_失業率を自然失業率より高く保つとデフレが加速する() -> None:
    path = accelerating_inflation_path(6, NATURAL, EXPECTED, BETA, 2)
    assert path == pytest.approx([2.0, 1.5, 1.0])


def test_期間が負ならエラー() -> None:
    with pytest.raises(ValueError, match="期間"):
        accelerating_inflation_path(4, NATURAL, EXPECTED, BETA, -1)


def test_加速の経路でも感応度が0以下ならエラー() -> None:
    with pytest.raises(ValueError, match="感応度"):
        accelerating_inflation_path(4, NATURAL, EXPECTED, 0, 3)


def test_期間が0なら経路は初期のインフレ率だけ() -> None:
    path = accelerating_inflation_path(4, 5, 2.0, 0.5, periods=0)
    assert path == [2.0]
