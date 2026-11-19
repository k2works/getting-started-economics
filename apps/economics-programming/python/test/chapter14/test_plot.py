"""第 14 章: AD-AS 分析とフィリップス曲線の図のテスト。"""

from typing import Any

import pytest
from matplotlib.lines import Line2D

from lib.chapter13.islm import IsLmModel
from lib.chapter14.indicators import phillips_inflation
from lib.chapter14.plot import plot_adas, plot_phillips_curve

PHILLIPS = {"natural_rate": 4, "expected_inflation": 2, "slope": 0.5}


def xy(line: Line2D) -> list[tuple[float, float]]:
    data: Any = line.get_xydata()
    return [(float(x), float(y)) for x, y in data]


def test_総需要曲線は物価が上がると所得が減る右下がり() -> None:
    ax = plot_adas(IsLmModel(), full_employment_income=1250).axes[0]
    ad = xy(ax.lines[0])
    assert all(x1 > x2 for (x1, _), (x2, _) in zip(ad, ad[1:], strict=False))
    assert all(p1 < p2 for (_, p1), (_, p2) in zip(ad, ad[1:], strict=False))


def test_AD_ASの図には総需要_古典派の総供給_均衡点がある() -> None:
    ax = plot_adas(IsLmModel(), full_employment_income=1250).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "AD",
        "AS (classical)",
        "Equilibrium",
    ]


def test_古典派の総供給は完全雇用所得で垂直() -> None:
    ax = plot_adas(IsLmModel(), full_employment_income=1250).axes[0]
    assert all(x == 1250 for x, _ in xy(ax.lines[1]))


def test_均衡点は物価1で所得1250() -> None:
    ax = plot_adas(IsLmModel(), full_employment_income=1250).axes[0]
    assert xy(ax.lines[2]) == [pytest.approx((1250, 1), abs=1e-6)]


def test_政府支出を増やすと総需要曲線が右にずれ物価だけが上がる() -> None:
    ax = plot_adas(
        IsLmModel(),
        full_employment_income=1250,
        after=IsLmModel(government=120),
    ).axes[0]
    assert [line.get_label() for line in ax.lines][-2:] == [
        "AD (after)",
        "Equilibrium (after)",
    ]
    ((income, price),) = xy(ax.lines[4])
    assert income == pytest.approx(1250, abs=1e-6)
    assert price > 1


def test_フィリップス曲線は失業率が上がると物価上昇率が下がる() -> None:
    ax = plot_phillips_curve(**PHILLIPS).axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Phillips curve",
        "Natural rate",
    ]
    points = xy(ax.lines[0])
    assert all(y == pytest.approx(phillips_inflation(x, **PHILLIPS)) for x, y in points)
    assert all(y1 > y2 for (_, y1), (_, y2) in zip(points, points[1:], strict=False))


def test_自然失業率の点は失業率4で期待物価上昇率2() -> None:
    ax = plot_phillips_curve(**PHILLIPS).axes[0]
    assert xy(ax.lines[1]) == [pytest.approx((4, 2))]


def test_期待物価上昇率が上がるとフィリップス曲線が上にずれる() -> None:
    ax = plot_phillips_curve(**PHILLIPS, new_expected_inflation=3).axes[0]
    labels = [line.get_label() for line in ax.lines]
    assert labels[-1] == "Phillips curve (after)"
    before, after = xy(ax.lines[0]), xy(ax.lines[2])
    assert all(
        a[1] - b[1] == pytest.approx(1) for a, b in zip(after, before, strict=True)
    )
