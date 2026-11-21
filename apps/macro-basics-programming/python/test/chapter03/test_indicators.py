"""第 3 章: 景気動向指数（DI・CI）と、雇用の指標のテスト。"""

import math
from pathlib import Path

import pandas as pd
import pytest

from lib.chapter03.indicators import (
    composite_index,
    diffusion_index,
    job_openings_ratio,
    load_indicators,
    unemployment_rate,
)

DATA = Path(__file__).resolve().parents[2] / "data" / "ch03_indicators.csv"

# 3 つの系列の 4 か月。a は ↑↓↑、b は →↑↑、c は ↓↑↑ と動く
SERIES = pd.DataFrame(
    {
        "a": [100, 110, 105, 120],
        "b": [50, 50, 55, 60],
        "c": [200, 190, 195, 210],
    },
    index=["m0", "m1", "m2", "m3"],
)


def test_DIは上昇した系列の割合で変わらない系列は半分と数える() -> None:
    di = diffusion_index(SERIES)
    assert math.isnan(di["m0"])
    # m1: a が上昇（1）、b が変わらない（0.5）、c が低下（0）→ 1.5 ÷ 3
    assert di["m1"] == pytest.approx(50)
    assert di["m2"] == pytest.approx(200 / 3)
    assert di["m3"] == pytest.approx(100)


def test_すべて上昇なら100すべて低下なら0() -> None:
    up = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
    down = pd.DataFrame({"x": [2, 1], "y": [4, 3]})
    assert diffusion_index(up).iloc[1] == 100
    assert diffusion_index(down).iloc[1] == 0


def test_DIが50を超えれば上向き() -> None:
    di = diffusion_index(SERIES).dropna()
    assert (di > 50).tolist() == [False, True, True]


def test_欠損のある月のDIは計算しない() -> None:
    missing = SERIES.copy()
    missing.loc["m2", "a"] = float("nan")
    di = diffusion_index(missing)
    assert math.isnan(di["m2"]) and math.isnan(di["m3"])
    assert di["m1"] == pytest.approx(50)


def test_CIは系列の変化率の平均を積み上げた値() -> None:
    series = pd.DataFrame(
        {"x": [100, 110, 121], "y": [200, 200, 220]}, index=["t0", "t1", "t2"]
    )
    # 変化率の平均: t1 は (10% + 0%) ÷ 2 = 5%、t2 は (10% + 10%) ÷ 2 = 10%
    assert composite_index(series, base="t0").tolist() == pytest.approx(
        [100, 105, 115.5]
    )


def test_CIは基準の時点が100になる() -> None:
    series = pd.DataFrame(
        {"x": [100, 110, 121], "y": [200, 200, 220]}, index=["t0", "t1", "t2"]
    )
    ci = composite_index(series, base="t1")
    assert ci.tolist() == pytest.approx([100 / 1.05, 100, 110])


def test_CIの基準がなければエラー() -> None:
    with pytest.raises(ValueError, match="基準"):
        composite_index(SERIES, base="m9")


def test_有効求人倍率は有効求人数を有効求職者数で割った値() -> None:
    assert job_openings_ratio(openings=1500, applicants=1000) == pytest.approx(1.5)
    assert job_openings_ratio(openings=900, applicants=1200) == pytest.approx(0.75)
    assert job_openings_ratio(openings=0, applicants=1000) == 0


def test_有効求人倍率は求職者が0以下か求人が負ならエラー() -> None:
    with pytest.raises(ValueError, match="求職者数"):
        job_openings_ratio(openings=100, applicants=0)
    with pytest.raises(ValueError, match="求職者数"):
        job_openings_ratio(openings=100, applicants=-1)
    with pytest.raises(ValueError, match="求人数"):
        job_openings_ratio(openings=-1, applicants=100)


def test_完全失業率は完全失業者を労働力人口で割った値() -> None:
    # 労働力人口 = 6500 + 200 = 6700、200 ÷ 6700 × 100
    assert unemployment_rate(employed=6500, unemployed=200) == pytest.approx(2.9850746)


def test_失業者がいなければ0で全員が失業者なら100() -> None:
    assert unemployment_rate(employed=6500, unemployed=0) == 0
    assert unemployment_rate(employed=0, unemployed=200) == 100


def test_完全失業率は人数が負か労働力人口が0ならエラー() -> None:
    with pytest.raises(ValueError, match="負"):
        unemployment_rate(employed=-1, unemployed=200)
    with pytest.raises(ValueError, match="負"):
        unemployment_rate(employed=6500, unemployed=-1)
    with pytest.raises(ValueError, match="労働力人口が 0"):
        unemployment_rate(employed=0, unemployed=0)


def test_CSVの指標を月を行にして読み込む() -> None:
    table = load_indicators(DATA)
    assert table.shape == (12, 4)
    assert table.index.name == "month"
    assert table.index[0] == "2025-01"
    assert list(table.columns) == [
        "production",
        "retail_sales",
        "job_openings_ratio",
        "income",
    ]
    assert table.loc["2025-01", "production"] == 100


def test_読み込んだ指標は毎月のDIが0から100の間() -> None:
    di = diffusion_index(load_indicators(DATA)).dropna()
    assert len(di) == 11
    assert ((di >= 0) & (di <= 100)).all()


def test_欠損のあるCSVはエラー(tmp_path: Path) -> None:
    path = tmp_path / "broken.csv"
    path.write_text("month,x\n2025-01,1\n2025-02,\n", encoding="utf-8")
    with pytest.raises(ValueError, match="欠損"):
        load_indicators(path)
