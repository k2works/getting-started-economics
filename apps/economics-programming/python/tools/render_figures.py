"""記事の図を、`lib/` の関数から生成し、図が古くなっていないかを検出する。

使い方（`apps/economics-programming/python/` で）:

    uv run python -m tools.render_figures           # 図を生成して、指紋を保存する
    uv run python -m tools.render_figures --check   # 図が古くなっていないか確かめる

図は `docs/article/economics-programming/images/` に作る。PNG のピクセルは、
OS やライブラリの版で、わずかに変わるので比べない。代わりに、図に描いたデータ
（線の座標・棒の高さ・軸の名前）から「指紋」（ハッシュ）を作り、
`tools/figure_fingerprints.json` に保存した値と比べる。モデルの係数や、
`lib/` の関数を変えて、図のデータが変わると、指紋が変わって、検査が失敗する。
"""

import hashlib
import json
import random
import re
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import numpy as np  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.patches import Polygon, Rectangle  # noqa: E402

from lib.chapter01.plot import plot_demand_curve  # noqa: E402
from lib.chapter02.plot import plot_elasticity_regions  # noqa: E402
from lib.chapter03.plot import plot_schedules  # noqa: E402
from lib.chapter03.schedule import demand_schedule, supply_schedule  # noqa: E402
from lib.chapter04.plot import plot_cost_curves  # noqa: E402
from lib.chapter05.adjustment import walras_path  # noqa: E402
from lib.chapter05.plot import plot_price_paths  # noqa: E402
from lib.chapter06.bisection import make_excess_demand  # noqa: E402
from lib.chapter06.plot import plot_bisection  # noqa: E402
from lib.chapter07.plot import draw_market, draw_tax_wedge  # noqa: E402
from lib.chapter08.simulation import plot_histogram, sample_means  # noqa: E402
from lib.chapter09.plot import plot_keynesian_cross  # noqa: E402
from lib.chapter10.plot import (  # noqa: E402
    plot_profit_maximization,
    plot_utility_maximization,
)
from lib.chapter11.economy import load_economy  # noqa: E402
from lib.chapter12.charts import plot_gdp_chart, plot_growth_chart  # noqa: E402
from lib.chapter13.islm import IsLmModel, plot_islm  # noqa: E402
from lib.chapter14.plot import plot_adas, plot_phillips_curve  # noqa: E402
from lib.chapter15.plot import (  # noqa: E402
    plot_cournot,
    plot_externality,
    plot_monopoly,
)

APP_DIR = Path(__file__).resolve().parents[1]
ARTICLE_DIR = APP_DIR.parents[2] / "docs" / "article" / "economics-programming"
IMAGES_DIR = ARTICLE_DIR / "images"
FINGERPRINTS_FILE = Path(__file__).resolve().parent / "figure_fingerprints.json"

# 記事に載せる図。名前が、画像のファイル名（名前.png）になる
FIGURES: dict[str, Callable[[], Figure]] = {
    "ch01-demand": lambda: plot_demand_curve(100, 2),
    "ch02-elasticity": lambda: plot_elasticity_regions(100, 2),
    "ch03-schedules": lambda: plot_schedules(
        demand_schedule([0, 10, 20, 30], 100, 2),
        supply_schedule([0, 10, 20, 30], 0, 3),
    ),
    "ch05-price-paths": lambda: plot_price_paths(
        {
            f"step {step}": walras_path(lambda p: 100 - 2 * p, lambda p: 3 * p, 0, step)
            for step in (0.1, 0.3)
        },
        equilibrium_price=20,
    ),
    "ch06-bisection": lambda: plot_bisection(
        make_excess_demand(100, 2, 0, 3), 0, 100, steps=6
    ),
    "ch10-utility": lambda: plot_utility_maximization(2, 4, 40),
    "ch10-profit": lambda: plot_profit_maximization(15),
    "ch14-adas": lambda: plot_adas(IsLmModel(), 1250, after=IsLmModel(government=120)),
    "ch14-phillips": lambda: plot_phillips_curve(4, 2, 0.5, new_expected_inflation=3),
    "ch15-cournot": lambda: plot_cournot(100, 2, 10),
    "ch15-externality": lambda: plot_externality(100, 2, 0, 3, 5),
    "ch04-cost-curves": lambda: plot_cost_curves(),
    "ch07-market": lambda: draw_market(100, 2, 0, 3),
    "ch07-tax-wedge": lambda: draw_tax_wedge(100, 2, 0, 3, 5),
    "ch08-sample-means": lambda: plot_histogram(
        sample_means(30, 1000, random.Random(0)), bins=20
    ),
    "ch09-keynesian-cross": lambda: plot_keynesian_cross(
        20, 0.8, 30, new_investment=40
    ),
    "ch12-gdp": lambda: plot_gdp_chart(load_economy()),
    "ch12-growth": lambda: plot_growth_chart(load_economy()),
    "ch13-islm-fiscal": lambda: plot_islm(IsLmModel(), after=IsLmModel(government=120)),
    "ch13-islm-monetary": lambda: plot_islm(
        IsLmModel(), after=IsLmModel(money_supply=575)
    ),
    "ch15-monopoly": lambda: plot_monopoly(100, 2, 10),
}

# 図の数値を丸める桁数（OS や数値計算の版による、ごく小さな誤差を無視する）
_DIGITS = 4
_IMAGE_REFERENCE = re.compile(r"!\[[^\]]*\]\(images/([^)]+?)\.png\)")


def fingerprint(fig: Figure) -> str:
    """図に描いたデータ（座標・棒の高さ・軸の名前）から、指紋（ハッシュ）を作る。"""
    axes = []
    for ax in fig.axes:
        lines = []
        for line in ax.lines:
            points: Any = line.get_xydata()
            xy = np.round(points, _DIGITS).tolist()
            lines.append({"label": line.get_label(), "xy": xy})
        bars = [
            round(float(p.get_height()), _DIGITS)
            for p in ax.patches
            if isinstance(p, Rectangle)
        ]
        entry: dict[str, Any] = {
            "xlabel": ax.get_xlabel(),
            "ylabel": ax.get_ylabel(),
            "lines": lines,
            "bars": bars,
        }
        polygons = [
            np.round(p.get_xy(), _DIGITS).tolist()
            for p in ax.patches
            if isinstance(p, Polygon)
        ]
        if polygons:  # 多角形のない図の指紋は、これまでと同じ値のままにする
            entry["polygons"] = polygons
        axes.append(entry)
    text = json.dumps(axes, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def referenced_images(markdown: str) -> set[str]:
    """Markdown から、`images/名前.png` の形で参照している図の名前を取り出す。"""
    return set(_IMAGE_REFERENCE.findall(markdown))


_REDO = "uv run python -m tools.render_figures で再生成する"


def _fingerprint_problem(name: str, value: str, stored: dict[str, str]) -> list[str]:
    """図の指紋が、保存した値と合っているかを調べる。"""
    if name not in stored:
        return [f"{name}: 保存した指紋がない。{_REDO}"]
    if stored[name] != value:
        return [f"{name}: 図のデータが変わって、画像が古い。{_REDO}"]
    return []


def find_problems(
    current: dict[str, str],
    stored: dict[str, str],
    on_disk: set[str],
    referenced: set[str],
) -> list[str]:
    """図の指紋・ファイル・記事からの参照のずれを、すべて返す。"""
    problems = []
    for name, value in sorted(current.items()):
        problems += _fingerprint_problem(name, value, stored)
        if name not in on_disk:
            problems.append(f"{name}: 画像ファイルがない。{_REDO}")
        if name not in referenced:
            problems.append(f"{name}: 記事から参照されていない図")
    for name in sorted(on_disk - set(current)):
        problems.append(f"{name}: 登録されていない画像ファイル（孤立）。削除する")
    for name in sorted(referenced - set(current)):
        problems.append(f"{name}: 記事が参照している図が、FIGURES に登録されていない")
    return problems


def _load_stored() -> dict[str, str]:
    if not FINGERPRINTS_FILE.exists():
        return {}
    data: dict[str, str] = json.loads(FINGERPRINTS_FILE.read_text(encoding="utf-8"))
    return data


def _referenced_in_articles() -> set[str]:
    names: set[str] = set()
    for path in ARTICLE_DIR.glob("*.md"):
        names |= referenced_images(path.read_text(encoding="utf-8"))
    return names


def render() -> None:
    """図を生成して、PNG と指紋を保存する。"""
    IMAGES_DIR.mkdir(exist_ok=True)
    fingerprints = {}
    for name, make in FIGURES.items():
        fig = make()
        fig.savefig(IMAGES_DIR / f"{name}.png", dpi=100)
        fingerprints[name] = fingerprint(fig)
        print(f"生成: images/{name}.png")
    text = json.dumps(fingerprints, ensure_ascii=False, indent=2, sort_keys=True)
    FINGERPRINTS_FILE.write_text(text + "\n", encoding="utf-8")


def check() -> int:
    """図が古くなっていないかを確かめる。ずれがあれば、1 を返す。"""
    current = {name: fingerprint(make()) for name, make in FIGURES.items()}
    on_disk = {p.stem for p in IMAGES_DIR.glob("*.png")}
    problems = find_problems(
        current, _load_stored(), on_disk, _referenced_in_articles()
    )
    print(f"{'NG' if problems else 'OK'}  図の検査（{len(current)} 点）")
    for problem in problems:
        print(f"    {problem}")
    return 1 if problems else 0


def main(argv: list[str]) -> int:
    if "--check" in argv:
        return check()
    render()
    return check()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
