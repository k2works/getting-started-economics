"""第 11 章: インフレとマネーストックのテスト。

貨幣数量説（MV = PY）を成長率で書くと、物価上昇率 = 貨幣の伸び率 − 実質成長率 + 流通速度の伸び率。
例: 貨幣が年 5%、実質成長率 1% で、流通速度が一定なら、物価上昇率は 4%。
"""

from pathlib import Path

import pandas as pd
import pytest

from lib.chapter11.money import (
    country_averages,
    hyperinflation_episodes,
    implied_velocity_growth,
    load_money_panel,
    long_run_relation,
    money_inflation_regression,
    quantity_theory_inflation,
    to_annual_average,
)


def exact_panel() -> pd.DataFrame:
    """物価上昇率 = 貨幣の伸び率 − 2.5 を、ちょうど満たす 3 か国 × 3 年の表。"""
    rows = []
    for country, level in (("A", 4.0), ("B", 8.0), ("C", 6.0)):
        for year, wiggle in ((2000, -1.0), (2001, 0.0), (2002, 1.5)):
            money = level + wiggle
            rows.append((country, year, money, 2.5, money - 2.5))
    df = pd.DataFrame(
        rows, columns=["country", "year", "money_growth", "real_growth", "inflation"]
    )
    return df.set_index(["country", "year"])


def test_貨幣が5パーセント_実質成長が1パーセントなら物価上昇率は4パーセント() -> None:
    assert quantity_theory_inflation(5, 1) == pytest.approx(4)


def test_流通速度が上がると物価上昇率も上がる() -> None:
    assert quantity_theory_inflation(5, 1, velocity_growth=0.5) == pytest.approx(4.5)


def test_実質成長率が高いと物価上昇率は低くなる() -> None:
    assert quantity_theory_inflation(5, 3) < quantity_theory_inflation(5, 1)


def test_観測した物価上昇率から流通速度の伸び率を求める() -> None:
    assert implied_velocity_growth(5, 1, 4.5) == pytest.approx(0.5)


def test_流通速度の伸び率を求めて数量説に戻すと元の物価上昇率になる() -> None:
    velocity = implied_velocity_growth(7.0, 2.0, 6.1)
    assert quantity_theory_inflation(7.0, 2.0, velocity) == pytest.approx(6.1)


def test_四半期の系列を年平均にする() -> None:
    index = pd.period_range("2000Q1", periods=8, freq="Q")
    series = pd.Series([1.0, 2, 3, 4, 5, 6, 7, 8], index=index)
    annual = to_annual_average(series)
    assert list(annual.index) == [2000, 2001]
    assert annual.tolist() == pytest.approx([2.5, 6.5])


def test_四半期でない系列は年平均にできない() -> None:
    with pytest.raises(ValueError, match="四半期"):
        to_annual_average(pd.Series([1.0, 2.0, 3.0]))


def test_CSVを読むと国と年が行の名前になる(tmp_path: Path) -> None:
    path = tmp_path / "money.csv"
    path.write_text(
        "country,year,money_growth,real_growth,inflation\nA,2000,5.0,1.0,4.0\n",
        encoding="utf-8",
    )
    df = load_money_panel(path)
    assert list(df.index.names) == ["country", "year"]
    assert df.loc[("A", 2000), "inflation"] == 4.0


def test_同梱のパネルは20か国の30年() -> None:
    df = load_money_panel()
    assert len(df) == 600
    assert df.index.get_level_values("country").nunique() == 20


def test_ちょうどの関係を満たす表では傾き1を復元できる() -> None:
    result = money_inflation_regression(exact_panel())
    assert result.coefficients["money_growth"] == pytest.approx(1)
    assert result.coefficients["const"] == pytest.approx(-2.5)
    assert result.r_squared == pytest.approx(1)


def test_同梱のパネルでは貨幣の伸び率の係数がほぼ1() -> None:
    result = money_inflation_regression(load_money_panel())
    assert result.coefficients["money_growth"] == pytest.approx(1.029, abs=0.001)
    assert result.r_squared == pytest.approx(0.985, abs=0.001)
    assert result.n_obs == 600


def test_ハイパーインフレを除いても傾きは1に近いが当てはまりは下がる() -> None:
    result = money_inflation_regression(load_money_panel(), max_inflation=100)
    assert result.coefficients["money_growth"] == pytest.approx(1.005, abs=0.001)
    assert result.r_squared == pytest.approx(0.629, abs=0.001)
    assert result.n_obs == 593


def test_ハイパーインフレの国と年を取り出す() -> None:
    episodes = hyperinflation_episodes(load_money_panel(), threshold=100)
    assert len(episodes) == 7
    assert set(episodes.index.get_level_values("country")) == {"E19", "E20"}
    years = episodes.index.get_level_values("year")
    assert sorted(years[episodes.index.get_level_values("country") == "E19"]) == [
        1992,
        1993,
        1994,
        1995,
    ]


def test_しきい値が高ければハイパーインフレは見つからない() -> None:
    assert len(hyperinflation_episodes(load_money_panel(), threshold=1000)) == 0


def test_国ごとの平均() -> None:
    averages = country_averages(exact_panel())
    assert averages.loc["A", "money_growth"] == pytest.approx(4.0 + 0.5 / 3)
    assert list(averages.index) == ["A", "B", "C"]


def test_長期の関係では平均の物価上昇率が貨幣の伸び率から実質成長率を引いた値に比例する() -> (
    None
):
    result = long_run_relation(exact_panel())
    assert result.coefficients["money_minus_real_growth"] == pytest.approx(1)


def test_同梱のパネルの長期の関係の傾きは1に近い() -> None:
    result = long_run_relation(load_money_panel())
    assert result.coefficients["money_minus_real_growth"] == pytest.approx(
        1.011, abs=0.002
    )
    assert result.r_squared == pytest.approx(0.999, abs=0.001)
    assert result.n_obs == 20


def test_しきい値ちょうどの物価上昇率は除かず_ハイパーインフレにも数えない() -> None:
    panel = exact_panel()
    top = float(panel["inflation"].max())
    assert money_inflation_regression(panel, max_inflation=top).n_obs == len(panel)
    assert len(hyperinflation_episodes(panel, threshold=top)) == 0
