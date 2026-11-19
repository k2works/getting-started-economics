"""第 7 章: 一物一価と購買力平価のテスト。

例: 同じ商品が、日本で 450 円、米国で 5.5 ドル。為替レートが 1 ドル 150 円なら、
円で 450 ÷ 150 = 3 ドル。PPP レート = 450 ÷ 5.5 ≈ 81.8 円 / ドル。
相対価格水準 = 3 ÷ 5.5 ≈ 0.545（日本のほうが、米国より、安い）。
"""

import numpy as np
import pytest

from lib.chapter07.ppp import (
    income_adjusted_gaps,
    load_prices,
    penn_effect_regression,
    ppp_rate,
    price_in_dollars,
    relative_price_level,
    relative_price_levels,
)


def test_円の価格をドルに直す() -> None:
    assert price_in_dollars(450, 150) == pytest.approx(3)


def test_PPPレートは自国の価格を米国の価格で割った値() -> None:
    assert ppp_rate(450, 5.5) == pytest.approx(450 / 5.5)


def test_相対価格水準は米国の価格を1としたドル建ての価格() -> None:
    assert relative_price_level(450, 150, 5.5) == pytest.approx(3 / 5.5)


def test_相対価格水準はPPPレートを為替レートで割った値() -> None:
    level = relative_price_level(450, 150, 5.5)
    assert level == pytest.approx(ppp_rate(450, 5.5) / 150)


def test_一物一価が成り立てばPPPレートは為替レートと等しい() -> None:
    # 825 円 ÷ 150 = 5.5 ドル
    assert relative_price_level(825, 150, 5.5) == pytest.approx(1)
    assert ppp_rate(825, 5.5) == pytest.approx(150)


@pytest.mark.parametrize(
    ("local", "rate", "us"), [(0, 150, 5.5), (450, 0, 5.5), (450, 150, 0), (-1, 1, 1)]
)
def test_価格と為替レートは正でなければならない(
    local: float, rate: float, us: float
) -> None:
    with pytest.raises(ValueError, match="正"):
        relative_price_level(local, rate, us)


def test_ドル換算の価格も為替レートは正でなければならない() -> None:
    with pytest.raises(ValueError, match="正"):
        price_in_dollars(450, 0)


def test_同梱のデータは基準の国を含む20か国() -> None:
    df = load_prices()
    assert len(df) == 20
    assert df.index[0] == "BASE"
    assert list(df.columns) == ["local_price", "exchange_rate", "income"]


def test_基準の国の相対価格水準は1() -> None:
    levels = relative_price_levels(load_prices())
    assert levels["BASE"] == pytest.approx(1)


def test_相対価格水準を国ごとに求める() -> None:
    df = load_prices()
    levels = relative_price_levels(df)
    assert levels["D01"] == pytest.approx(
        relative_price_level(
            float(df["local_price"]["D01"]),
            float(df["exchange_rate"]["D01"]),
            float(df["local_price"]["BASE"]),
        )
    )


def test_基準の国がなければ受け付けない() -> None:
    df = load_prices().drop(index="BASE")
    with pytest.raises(ValueError, match="基準"):
        relative_price_levels(df)


def test_豊かな国ほど物価が高いペン効果() -> None:
    result = penn_effect_regression(load_prices())
    assert list(result.coefficients.index) == ["const", "ln_income"]
    assert result.coefficients["ln_income"] == pytest.approx(0.233, abs=0.001)
    assert result.t_values()["ln_income"] > 5


def test_所得で説明した後の差の合計は0() -> None:
    gaps = income_adjusted_gaps(load_prices())
    assert gaps.sum() == pytest.approx(0, abs=1e-9)
    assert len(gaps) == 20


def test_所得で説明した後の差は対数の相対価格水準と回帰直線の差() -> None:
    df = load_prices()
    result = penn_effect_regression(df)
    gaps = income_adjusted_gaps(df)
    levels = relative_price_levels(df)
    fitted = result.coefficients["const"] + result.coefficients["ln_income"] * np.log(
        df["income"]
    )
    assert gaps.to_numpy() == pytest.approx((np.log(levels) - fitted).to_numpy())


@pytest.mark.parametrize(("local", "us"), [(0, 5.5), (450, 0)])
def test_PPPレートの計算でも価格は正でなければならない(local: float, us: float) -> None:
    with pytest.raises(ValueError, match="正"):
        ppp_rate(local, us)
