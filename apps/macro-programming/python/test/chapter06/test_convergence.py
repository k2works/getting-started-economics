"""第 6 章: 所得収斂のテスト。

収斂の式: (1 ÷ T)·ln(y_T ÷ y_0) = a + β·ln y_0。β < 0 なら、初期の所得が低い国ほど速く成長する。
全員が同じ速さ λ で、共通の定常状態 c に近づくなら、β = −(1 − e^(−λT)) ÷ T が成り立つ。
"""

import numpy as np
import pandas as pd
import pytest

from lib.chapter02.growth import load_panel
from lib.chapter06.convergence import (
    beta_by_start_year,
    beta_convergence,
    club_convergence,
    half_life_years,
    implied_speed,
    income_growth,
)

SPEED = 0.02
STEADY = 3.0  # 共通の定常状態の対数所得


def exact_panel(start: int = 2000, end: int = 2020) -> pd.DataFrame:
    """全国が、同じ速さ λ = 0.02 で、共通の定常状態に近づく、ちょうどの関係を満たす表。"""
    initial = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 2.5])
    years = end - start
    final = STEADY + (initial - STEADY) * np.exp(-SPEED * years)
    rows = []
    for i, (a, b) in enumerate(zip(initial, final, strict=True)):
        for year, value in ((start, a), (end, b)):
            rows.append((f"C{i}", year, np.exp(value), 1.0, 1.0))
    df = pd.DataFrame(rows, columns=["country", "year", "y", "k", "h"])
    return df.set_index(["country", "year"])


def test_10年で2倍になる国の成長率は年6_93パーセント() -> None:
    rows = [("A", 2000, 1.0, 1.0, 1.0), ("A", 2010, 2.0, 1.0, 1.0)]
    panel = pd.DataFrame(rows, columns=["country", "year", "y", "k", "h"])
    panel = panel.set_index(["country", "year"])
    growth = income_growth(panel, 2000, 2010)
    assert growth["A"] == pytest.approx(100 * np.log(2) / 10)


def test_期間の始まりは終わりより前でなければならない() -> None:
    with pytest.raises(ValueError, match="期間"):
        income_growth(exact_panel(), 2020, 2000)


def test_パネルにない年は受け付けない() -> None:
    with pytest.raises(ValueError, match="年"):
        income_growth(exact_panel(), 1990, 2020)


def test_ちょうどの関係を満たす表では傾きを復元できる() -> None:
    result = beta_convergence(exact_panel(), 2000, 2020)
    expected = -(1 - np.exp(-SPEED * 20)) / 20  # 成長率を小数で見たときの β
    assert result.coefficients["ln_y0"] / 100 == pytest.approx(expected)
    assert result.r_squared == pytest.approx(1)


def test_傾きから収束の速さを求める() -> None:
    result = beta_convergence(exact_panel(), 2000, 2020)
    assert implied_speed(result.coefficients["ln_y0"], 20) == pytest.approx(SPEED)


def test_収束の速さ0_02の半減期は約34_7年() -> None:
    assert half_life_years(0.02) == pytest.approx(34.66, abs=0.01)


def test_収束の速さは正でなければならない() -> None:
    with pytest.raises(ValueError, match="収束の速さ"):
        half_life_years(0)


def test_傾きが大きすぎて収束の速さが決まらないときは受け付けない() -> None:
    # 1 + β·T ≤ 0 になる傾き（成長率の小数 β = −0.1、T = 20）
    with pytest.raises(ValueError, match="傾き"):
        implied_speed(-10, 20)


def test_同梱のパネルでは貧しい国ほど速く成長する() -> None:
    result = beta_convergence(load_panel(), 1990, 2019)
    assert result.coefficients["ln_y0"] < 0
    assert result.t_values()["ln_y0"] < -3


def test_同梱のパネルの絶対的収斂の傾きと速さ() -> None:
    result = beta_convergence(load_panel(), 1990, 2019)
    assert result.coefficients["ln_y0"] == pytest.approx(-0.485, abs=0.001)
    speed = implied_speed(result.coefficients["ln_y0"], 29)
    assert speed == pytest.approx(0.0052, abs=0.0001)


def test_初期の人的資本を加えた条件付き収斂() -> None:
    absolute = beta_convergence(load_panel(), 1990, 2019)
    conditional = beta_convergence(load_panel(), 1990, 2019, controls=["h"])
    assert list(conditional.coefficients.index) == ["const", "ln_y0", "ln_h0"]
    assert conditional.r_squared >= absolute.r_squared


def test_条件に使える変数はkとhだけ() -> None:
    with pytest.raises(ValueError, match="条件"):
        beta_convergence(load_panel(), 1990, 2019, controls=["gdp"])


def test_クラブ収斂は初期の所得が高い半分と低い半分に分けて推定する() -> None:
    clubs = club_convergence(load_panel(), 1990, 2019)
    assert set(clubs) == {"rich", "poor"}
    assert clubs["rich"].n_obs == 12
    assert clubs["poor"].n_obs == 12


def test_期間をずらした傾きは一つずつ直接求めた傾きと一致する() -> None:
    panel = load_panel()
    series = beta_by_start_year(panel, window=10)
    assert series.index.min() == 1990
    assert series.index.max() == 2009
    direct = beta_convergence(panel, 1995, 2005).coefficients["ln_y0"]
    assert series[1995] == pytest.approx(direct)


def test_期間の幅は1年以上でなければならない() -> None:
    with pytest.raises(ValueError, match="幅"):
        beta_by_start_year(load_panel(), window=0)


def test_期間が0年でも受け付けない() -> None:
    with pytest.raises(ValueError, match="期間"):
        income_growth(exact_panel(), 2000, 2000)


def test_1と傾きと期間の積がちょうど0になる傾きは受け付けない() -> None:
    # 1 + (−5 ÷ 100) × 20 = 0
    with pytest.raises(ValueError, match="傾き"):
        implied_speed(-5, 20)


def test_クラブ収斂の低い半分は初期の所得の低い12か国() -> None:
    panel = load_panel()
    first = panel.xs(1990, level="year")["y"].sort_values()
    poorest = set(first.index[:12])
    countries = panel.index.get_level_values("country")
    direct = beta_convergence(panel[countries.isin(poorest)], 1990, 2019)
    clubs = club_convergence(panel, 1990, 2019)
    assert clubs["poor"].coefficients["ln_y0"] == pytest.approx(
        direct.coefficients["ln_y0"]
    )
    assert clubs["poor"].coefficients["ln_y0"] != pytest.approx(
        clubs["rich"].coefficients["ln_y0"]
    )
