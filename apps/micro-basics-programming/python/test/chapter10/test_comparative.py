"""第 10 章: 絶対優位・比較優位・生産可能性フロンティアのテスト。"""

import pytest

from lib.chapter10.comparative import (
    Country,
    absolute_advantage,
    comparative_advantage,
    mutually_beneficial_terms,
    opportunity_cost_of_agriculture,
    opportunity_cost_of_industry,
    ppf_endpoints,
    trade_gain_per_unit,
)

# 1 単位を作るのに必要な労働者の数（人）。大国は、どちらも少ない人数で作れる
LARGE = Country("Large", labor_industry=4, labor_agriculture=8)
SMALL = Country("Small", labor_industry=20, labor_agriculture=10)


def test_工業の機会費用は農業の何単位をあきらめるか() -> None:
    assert opportunity_cost_of_industry(LARGE) == 0.5
    assert opportunity_cost_of_industry(SMALL) == 2.0


def test_農業の機会費用は工業の何単位をあきらめるか() -> None:
    assert opportunity_cost_of_agriculture(LARGE) == 2.0
    assert opportunity_cost_of_agriculture(SMALL) == 0.5


def test_2つの機会費用は逆数() -> None:
    for country in (LARGE, SMALL):
        product = opportunity_cost_of_industry(
            country
        ) * opportunity_cost_of_agriculture(country)
        assert product == pytest.approx(1)


def test_大国は両方の財で絶対優位() -> None:
    assert absolute_advantage(LARGE, SMALL, "industry") == "Large"
    assert absolute_advantage(LARGE, SMALL, "agriculture") == "Large"


def test_絶対優位は必要な労働が少ない国() -> None:
    assert absolute_advantage(SMALL, LARGE, "industry") == "Large"


def test_比較優位は機会費用が低い国() -> None:
    assert comparative_advantage(LARGE, SMALL, "industry") == "Large"
    assert comparative_advantage(LARGE, SMALL, "agriculture") == "Small"


def test_全部の財で比較優位のある国はない() -> None:
    winners = {
        comparative_advantage(LARGE, SMALL, "industry"),
        comparative_advantage(LARGE, SMALL, "agriculture"),
    }
    assert winners == {"Large", "Small"}


def test_機会費用が同じなら比較優位はない() -> None:
    twin = Country("Twin", 8, 16)
    assert comparative_advantage(LARGE, twin, "industry") is None
    assert comparative_advantage(LARGE, twin, "agriculture") is None


def test_必要な労働が同じなら絶対優位はない() -> None:
    same = Country("Same", 4, 8)
    assert absolute_advantage(LARGE, same, "industry") is None


def test_知らない財ならエラー() -> None:
    with pytest.raises(ValueError, match="財"):
        absolute_advantage(LARGE, SMALL, "service")
    with pytest.raises(ValueError, match="財"):
        comparative_advantage(LARGE, SMALL, "service")


def test_必要な労働は正でなければエラー() -> None:
    with pytest.raises(ValueError, match="労働"):
        Country("Bad", 0, 8)
    with pytest.raises(ValueError, match="労働"):
        Country("Bad", 4, -1)


def test_必要な労働が1未満の正の値でも国を作れる() -> None:
    country = Country("Fast", 0.5, 0.25)
    assert opportunity_cost_of_industry(country) == 2.0


def test_生産可能性フロンティアの両端() -> None:
    assert ppf_endpoints(LARGE, 80) == ((20, 0), (0, 10))
    assert ppf_endpoints(SMALL, 40) == ((2, 0), (0, 4))


def test_生産可能性フロンティアの傾きの大きさは機会費用() -> None:
    (industry, _), (_, agriculture) = ppf_endpoints(LARGE, 80)
    assert agriculture / industry == opportunity_cost_of_industry(LARGE)


def test_労働量は正でなければエラー() -> None:
    with pytest.raises(ValueError, match="労働量"):
        ppf_endpoints(LARGE, 0)


def test_貿易の条件は2国の機会費用の間() -> None:
    assert mutually_beneficial_terms(LARGE, SMALL) == (0.5, 2.0)
    assert mutually_beneficial_terms(SMALL, LARGE) == (0.5, 2.0)


def test_交換比率が範囲の内側なら両国が得をする() -> None:
    # 工業 1 単位と農業 1 単位を交換する（交換比率 1）
    assert trade_gain_per_unit(opportunity_cost_of_industry(LARGE), 1) == 0.5
    assert trade_gain_per_unit(opportunity_cost_of_agriculture(SMALL), 1 / 1) == 0.5


def test_交換比率が範囲の外なら一方が損をする() -> None:
    assert trade_gain_per_unit(opportunity_cost_of_industry(LARGE), 0.4) < 0
    assert trade_gain_per_unit(opportunity_cost_of_agriculture(SMALL), 0.4) < 0


def test_特化して貿易すると世界全体の価値が増える() -> None:
    # 交換比率 1（工業 1 = 農業 1）で、世界の生産の価値を比べる。大国 80 人、小国 40 人
    def value(industry: float, agriculture: float) -> float:
        return industry + agriculture

    before = value(80 / 2 / 4 + 40 / 2 / 20, 80 / 2 / 8 + 40 / 2 / 10)
    large_industry = ppf_endpoints(LARGE, 80)[0][0]
    small_agriculture = ppf_endpoints(SMALL, 40)[1][1]
    after = value(large_industry, small_agriculture)
    assert before == 18
    assert after == 24
    assert after > before
