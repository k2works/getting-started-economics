"""記事の図を、`lib/` の関数から生成し、図が古くなっていないかを検出する。

使い方（`apps/<シリーズ名>/python/` で）:

    uv run python -m article_tools.render_figures          # 図を生成し、指紋を保存
    uv run python -m article_tools.render_figures --check  # 図が古くないか確かめる

図は `docs/article/<シリーズ名>/images/` に作る。PNG のピクセルは、
OS やライブラリの版で、わずかに変わるので比べない。代わりに、図に描いたデータ
（線の座標・棒の高さ・軸の名前）から「指紋」（ハッシュ）を作り、
`tools/figure_fingerprints.json` に保存した値と比べる。モデルの係数や、
`lib/` の関数を変えて、図のデータが変わると、指紋が変わって、検査が失敗する。
"""

import hashlib
import importlib
import json
import os
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

# 対象のシリーズ（apps/<名前>/python/）。実行する場所か、環境変数で決める
APP_DIR = Path(os.environ.get("ARTICLE_APP_DIR", Path.cwd())).resolve()
# シリーズ固有のデータ（図の登録・抜粋・指紋など）は、シリーズの tools/ に置く
TOOLS_DIR = APP_DIR / "tools"
# apps/<シリーズ名>/python/ の「シリーズ名」が、記事のディレクトリ名
SERIES = APP_DIR.parent.name
ARTICLE_DIR = APP_DIR.parents[2] / "docs" / "article" / SERIES
IMAGES_DIR = ARTICLE_DIR / "images"
FINGERPRINTS_FILE = TOOLS_DIR / "figure_fingerprints.json"


# 図の数値を丸める桁数（OS や数値計算の版による、ごく小さな誤差を無視する）
_DIGITS = 4
_IMAGE_REFERENCE = re.compile(r"!\[[^\]]*\]\(images/([^)]+?)\.png\)")


def fingerprint(fig: Figure) -> str:
    """図に描いたデータ（座標・線種・棒の高さ・軸の名前と範囲）から、指紋（ハッシュ）を作る。"""
    axes = []
    for ax in fig.axes:
        lines = []
        for line in ax.lines:
            points: Any = line.get_xydata()
            xy = np.round(points, _DIGITS).tolist()
            style = line.get_linestyle()
            lines.append({"label": line.get_label(), "style": style, "xy": xy})
        bars = [
            round(float(p.get_height()), _DIGITS)
            for p in ax.patches
            if isinstance(p, Rectangle)
        ]
        entry: dict[str, Any] = {
            "xlabel": ax.get_xlabel(),
            "ylabel": ax.get_ylabel(),
            "xlim": np.round(ax.get_xlim(), _DIGITS).tolist(),
            "ylim": np.round(ax.get_ylim(), _DIGITS).tolist(),
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


_REDO = "uv run python -m article_tools.render_figures で再生成する"


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


def load_figures() -> dict[str, Callable[[], Figure]]:
    """シリーズの tools/figure_registry.py に登録された、図の作り方（名前 -> 関数）。"""
    if str(APP_DIR) not in sys.path:
        sys.path.insert(0, str(APP_DIR))
    figures: dict[str, Callable[[], Figure]] = importlib.import_module(
        "tools.figure_registry"
    ).FIGURES
    return figures


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
    for name, make in load_figures().items():
        fig = make()
        fig.savefig(IMAGES_DIR / f"{name}.png", dpi=100)
        fingerprints[name] = fingerprint(fig)
        print(f"生成: images/{name}.png")
    text = json.dumps(fingerprints, ensure_ascii=False, indent=2, sort_keys=True)
    FINGERPRINTS_FILE.write_text(text + "\n", encoding="utf-8")


def check() -> int:
    """図が古くなっていないかを確かめる。ずれがあれば、1 を返す。"""
    current = {name: fingerprint(make()) for name, make in load_figures().items()}
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
