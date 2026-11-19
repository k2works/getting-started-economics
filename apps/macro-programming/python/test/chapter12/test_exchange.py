"""第 12 章: 貨幣の中立性・為替レートのテスト。

実質為替レート q = e × P* ÷ P。例: e = 100、P* = 2、P = 4 なら q = 50。
"""

import numpy as np
import pandas as pd
import pytest

from lib.chapter11.money import load_money_panel
from lib.chapter12.exchange import (
    load_exchange,
    log_change,
    money_neutrality_regression,
    real_exchange_rate,
    regime_statistics,
)


def test_実質為替レートは名目レートに外国の物価を掛けて自国の物価で割る() -> None:
    assert real_exchange_rate(100, 2, 4) == pytest.approx(50)


def test_系列でも計算できる() -> None:
    e = pd.Series([100.0, 200.0])
    q = real_exchange_rate(e, pd.Series([2.0, 2.0]), pd.Series([4.0, 8.0]))
    assert q.tolist() == pytest.approx([50, 50])


@pytest.mark.parametrize("args", [(0, 2, 4), (100, 0, 4), (100, 2, 0)])
def test_為替レートと物価は正でなければならない(
    args: tuple[float, float, float],
) -> None:
    with pytest.raises(ValueError, match="正"):
        real_exchange_rate(*args)


def test_自国と外国の物価が同じ率で上がれば実質レートは名目レートに比例する() -> None:
    e = pd.Series([100.0, 110.0, 121.0])
    p = pd.Series([1.0, 1.1, 1.21])
    pf = pd.Series([1.0, 1.1, 1.21])
    q = real_exchange_rate(e, pf, p)
    assert (q / e).tolist() == pytest.approx([1, 1, 1])


def test_対数の変化率はパーセント() -> None:
    changes = log_change(pd.Series([100.0, 110.0, 99.0]))
    assert changes.tolist() == pytest.approx([100 * np.log(1.1), 100 * np.log(0.9)])


def test_同梱のデータは1960年から2019年までの240四半期() -> None:
    df = load_exchange()
    assert len(df) == 240
    assert str(df.index[0]) == "1960Q1"
    assert str(df.index[-1]) == "2019Q4"
    assert list(df.columns) == ["nominal_rate", "price_domestic", "price_foreign"]


def test_相場制度ごとの統計は固定と変動の2行() -> None:
    stats = regime_statistics(load_exchange(), "1973Q1")
    assert list(stats.index) == ["fixed", "floating"]
    assert list(stats.columns) == [
        "nominal_volatility",
        "real_volatility",
        "correlation",
    ]


def test_変動相場では名目レートが大きく動き実質レートも同じように動く() -> None:
    stats = regime_statistics(load_exchange(), "1973Q1")
    nominal = stats["nominal_volatility"]
    assert float(nominal["floating"]) > 10 * float(nominal["fixed"])
    assert float(stats["correlation"]["floating"]) > 0.95


def test_固定相場では名目レートの動きと実質レートの動きは弱い関係() -> None:
    stats = regime_statistics(load_exchange(), "1973Q1")
    assert float(stats["correlation"]["fixed"]) < 0.5


def test_相場制度ごとの統計の値() -> None:
    stats = regime_statistics(load_exchange(), "1973Q1")
    assert stats["nominal_volatility"].tolist() == pytest.approx(
        [0.126, 3.012], abs=0.001
    )
    assert stats["real_volatility"].tolist() == pytest.approx([0.327, 3.030], abs=0.001)
    assert stats["correlation"].tolist() == pytest.approx([0.24, 0.993], abs=0.005)


@pytest.mark.parametrize(
    "break_period", ["1960Q1", "1960Q3", "2030Q1", "2019Q4", "2019Q3"]
)
def test_切り替えの時点はデータの範囲の内側でなければならない(
    break_period: str,
) -> None:
    with pytest.raises(ValueError, match="切り替え"):
        regime_statistics(load_exchange(), break_period)


def test_貨幣の伸び率は実質成長率を説明しない() -> None:
    result = money_neutrality_regression(load_money_panel())
    assert result.coefficients["money_growth"] == pytest.approx(0.002, abs=0.01)
    assert abs(result.t_values()["money_growth"]) < 2


def test_貨幣の中立性の回帰は実質成長率を貨幣の伸び率に回帰する() -> None:
    result = money_neutrality_regression(load_money_panel())
    assert list(result.coefficients.index) == ["const", "money_growth"]
    assert result.coefficients["const"] == pytest.approx(2.44, abs=0.01)


def test_前後にちょうど3四半期あれば計算できる() -> None:
    stats = regime_statistics(load_exchange(), "1960Q4")
    assert list(stats.index) == ["fixed", "floating"]
    stats = regime_statistics(load_exchange(), "2019Q2")
    assert list(stats.index) == ["fixed", "floating"]
