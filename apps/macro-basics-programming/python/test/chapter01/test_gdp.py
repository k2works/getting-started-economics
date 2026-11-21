"""第 1 章: GDP と付加価値のテスト。"""

import pytest

from lib.chapter01.gdp import (
    GrowthAccounting,
    gdp_from_stages,
    gni,
    growth_accounting,
    is_in_gdp,
    ndp,
    stock_path,
    value_added,
)

# 小麦 → 小麦粉 → パン の 3 段階。生産額と、前の段階から買った中間投入（万円）
OUTPUT = [300, 700, 1000]
INTERMEDIATE = [0, 300, 700]


def test_付加価値は生産額から中間投入を引いた値() -> None:
    assert value_added(OUTPUT, INTERMEDIATE) == [300, 400, 300]


def test_付加価値の合計は最終財の価値に等しい() -> None:
    assert gdp_from_stages(OUTPUT, INTERMEDIATE) == 1000
    assert gdp_from_stages(OUTPUT, INTERMEDIATE) == OUTPUT[-1]


def test_段階の数が違えばエラー() -> None:
    with pytest.raises(ValueError, match="同じ長さ"):
        value_added([300, 700], [0, 300, 700])


def test_中間投入が生産額より大きいとエラー() -> None:
    with pytest.raises(ValueError, match="中間投入"):
        value_added([300, 700], [0, 800])


def test_中間投入が生産額に等しければ付加価値は0で有効() -> None:
    assert value_added([100, 100], [0, 100]) == [100, 0]


def test_GNIは国内のGDPに海外からの受取を足し海外への支払を引く() -> None:
    assert gni(1000, income_from_abroad=30, income_to_abroad=20) == 1010


def test_NDPはGDPから固定資本減耗を引く() -> None:
    assert ndp(1000, depreciation=150) == 850


def test_帰属計算で含めるものと含めないもの() -> None:
    for item in ("政府サービス", "持ち家の家賃", "農家の自家消費"):
        assert is_in_gdp(item)
    for item in ("キャピタルゲイン", "中古品の売買", "家事労働"):
        assert not is_in_gdp(item)


def test_知らない項目はエラー() -> None:
    with pytest.raises(ValueError, match="知らない項目"):
        is_in_gdp("宝くじの当せん金")


def test_ストックはフローを足し上げた経路() -> None:
    assert stock_path(100, [10, -5, 20]) == [100, 110, 105, 125]


def test_フローがなければストックは動かない() -> None:
    assert stock_path(100, []) == [100]


def test_成長会計の技術進歩率は残差() -> None:
    result = growth_accounting(
        growth=6.0,
        labor_growth=7.0,
        labor_share=0.4,
        capital_growth=4.0,
        capital_share=0.6,
    )
    assert result.labor == pytest.approx(2.8)
    assert result.capital == pytest.approx(2.4)
    assert result.technology == pytest.approx(0.8)


def test_成長率は3つの寄与の和() -> None:
    result = growth_accounting(5.0, 2.0, 0.7, 3.0, 0.3)
    assert isinstance(result, GrowthAccounting)
    total = result.labor + result.capital + result.technology
    assert total == pytest.approx(result.growth)


def test_分配率の合計が1でなければエラー() -> None:
    with pytest.raises(ValueError, match="合計が 1"):
        growth_accounting(6.0, 7.0, 0.4, 4.0, 0.5)


def test_要素の増加がなければ成長はすべて技術進歩() -> None:
    result = growth_accounting(3.0, 0.0, 0.5, 0.0, 0.5)
    assert result.technology == pytest.approx(3.0)
