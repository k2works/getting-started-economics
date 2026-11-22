"""記事の図を、`lib/` の関数から生成し、図が古くなっていないかを検出する。

使い方（`apps/<シリーズ名>/python/` で）:

    uv run python -m article_tools.render_figures          # 図を生成し、指紋を保存
    uv run python -m article_tools.render_figures --check  # 図が古くないか確かめる

図は `docs/article/<シリーズ名>/images/` に作る。PNG のピクセルは、
OS やライブラリの版で、わずかに変わるので比べない。代わりに、図に描いたデータ
（線の座標・棒の高さ・塗り・矢印・文字・軸の名前・タイトル）から「指紋」（ハッシュ）を作り、
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
from matplotlib.axes import Axes  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.patches import Polygon, Rectangle  # noqa: E402
from matplotlib.text import Annotation  # noqa: E402

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
# 絶対値がこれより小さい値は、小数の桁でなく、有効数字で丸める
_SMALL = 1e-3
_SIGNIFICANT = 4
_IMAGE_REFERENCE = re.compile(r"!\[[^\]]*\]\(images/([^)]+?)\.png\)")


def _round_small(value: float) -> float:
    return float(f"{value:.{_SIGNIFICANT}g}")


def _round_array(values: Any, log: Any = False) -> Any:
    """座標などの数値の並びを丸めて、JSON にできるリストにする。

    ふつうの値は、これまでどおり小数 `_DIGITS` 桁に丸める。対数目盛の軸の座標
    （`log` が真の列）で、絶対値が `_SMALL` 未満の値（0 と、無限大・NaN を除く）
    だけ、有効数字 `_SIGNIFICANT` 桁に丸める。`log` は、値の最後の次元に合わせて
    広げる（点の並びなら `(x 軸が対数か, y 軸が対数か)`、軸の範囲なら 1 つの真偽値）。

    なぜ、すべての値を有効数字にしないか。規則は 1 つで済むが、ふつうの値
    （例: 123.456789 は、小数 4 桁なら 123.4568、有効数字 4 桁なら 123.5）も
    丸め方が変わり、すべての図の指紋を作り直すことになる。

    なぜ、小さい値をすべてでなく、対数目盛の軸に限るか。線形目盛の小さい値は、
    0 になるはずの値の計算誤差（10⁻¹⁵ 程度。OS や BLAS の版で変わる）であることが
    多い。有効数字で丸めると、その誤差が指紋に入り、指紋が環境で揺れる。線形目盛
    では、10⁻⁵ と 10⁻⁷ の差は、図の上で見分けられないので、小数 4 桁で足りる。
    対数目盛では、10⁻⁵ と 10⁻⁷ は 2 目盛も離れて見えるのに、小数 4 桁ではどちらも
    0 に潰れる。そこで、対数目盛の小さい値だけ、有効数字で丸める。
    """
    array = np.asarray(values, dtype=float)
    rounded = np.round(array, _DIGITS)
    small = (
        np.asarray(log, dtype=bool)
        & np.isfinite(array)
        & (array != 0)
        & (np.abs(array) < _SMALL)
    )
    if small.any():
        rounded[small] = [_round_small(float(v)) for v in array[small]]
    return rounded.tolist()


def _round_number(value: float, log: bool) -> float:
    """1 つの数値を丸める。丸め方は `_round_array` と同じ。"""
    if log and np.isfinite(value) and value != 0 and abs(value) < _SMALL:
        return _round_small(value)
    return round(value, _DIGITS)


def _log_axes(ax: Axes) -> tuple[bool, bool]:
    """x 軸・y 軸が対数目盛か（点の並びを丸めるときの `log`）。"""
    return ax.get_xscale() == "log", ax.get_yscale() == "log"


def _texts(ax: Axes) -> list[dict[str, Any]]:
    return [
        {"text": t.get_text(), "xy": _round_array(t.get_position(), _log_axes(ax))}
        for t in ax.texts
        if not isinstance(t, Annotation)
    ]


def _annotations(ax: Axes) -> list[dict[str, Any]]:
    """矢印の向き（`xy` が矢の先、`xytext` が矢の根元）と、文字・矢の形。"""
    log = _log_axes(ax)
    annotations = []
    for a in ax.texts:
        if not isinstance(a, Annotation):
            continue
        props = a.arrowprops
        arrow = None if props is None else str(props.get("arrowstyle"))
        annotations.append(
            {
                "text": a.get_text(),
                "xy": _round_array(a.xy, log),
                "xytext": _round_array(a.xyann, log),
                "arrow": arrow,
            }
        )
    return annotations


def _collections(ax: Axes) -> list[dict[str, Any]]:
    """`fill_between` の塗り・散布図の点など（頂点と、点を置いた位置）。"""
    log = _log_axes(ax)
    return [
        {
            "paths": [_round_array(path.vertices, log) for path in c.get_paths()],
            "offsets": _round_array(c.get_offsets(), log),
        }
        for c in ax.collections
    ]


def _titles(ax: Axes) -> dict[str, str]:
    titles = {loc: ax.get_title(loc) for loc in ("left", "center", "right")}
    return {loc: title for loc, title in titles.items() if title}


def fingerprint(fig: Figure) -> str:
    """図に描いたデータから、指紋（ハッシュ）を作る。

    見るのは、線の座標と線種・棒の高さ・多角形・軸の名前と範囲・タイトル・
    図に書いた文字・矢印（向きを含む）・塗りや散布図の点（collections）。
    多角形・タイトル・文字・矢印・collections は、図にあるときだけ指紋の入力に
    足す。これらのない図の指紋は、足す前と同じ値のままにする。
    """
    axes = []
    for ax in fig.axes:
        log = x_log, y_log = _log_axes(ax)
        lines = []
        for line in ax.lines:
            xy = _round_array(line.get_xydata(), log)
            style = line.get_linestyle()
            lines.append({"label": line.get_label(), "style": style, "xy": xy})
        bars = [
            _round_number(float(p.get_height()), y_log)
            for p in ax.patches
            if isinstance(p, Rectangle)
        ]
        entry: dict[str, Any] = {
            "xlabel": ax.get_xlabel(),
            "ylabel": ax.get_ylabel(),
            "xlim": _round_array(ax.get_xlim(), x_log),
            "ylim": _round_array(ax.get_ylim(), y_log),
            "lines": lines,
            "bars": bars,
        }
        optional = {
            "polygons": [
                _round_array(p.get_xy(), log)
                for p in ax.patches
                if isinstance(p, Polygon)
            ],
            "titles": _titles(ax),
            "texts": _texts(ax),
            "annotations": _annotations(ax),
            "collections": _collections(ax),
        }
        # 図にない要素は足さない（これまでの図の指紋を、同じ値のままにする）
        entry |= {key: value for key, value in optional.items() if value}
        axes.append(entry)
    payload: Any = axes
    if fig.get_suptitle():  # 図全体のタイトルのない図は、これまでと同じ値のまま
        payload = {"axes": axes, "suptitle": fig.get_suptitle()}
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True)
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
