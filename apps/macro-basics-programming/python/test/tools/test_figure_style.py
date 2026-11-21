"""全体レビュー（2026-11-21）の指摘: 全図に共通する、凡例と線種の規則。

章ごとのテストが、線種・凡例を確かめていなかったので、登録された全 28 図に、規則を課す。
"""

import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from tools.figure_registry import FIGURES


def _axes(name: str) -> list[Axes]:
    return FIGURES[name]().axes


def _labelled_lines(ax: Axes) -> list[Line2D]:
    return [x for x in ax.lines if not str(x.get_label()).startswith("_")]


def _shifted_curves(ax: Axes) -> list[Line2D]:
    """動かしたあとの曲線（マーカーのない線。均衡の点と、第 6 章の累積の系列は除く）。"""
    return [
        x
        for x in _labelled_lines(ax)
        if "after" in str(x.get_label()).lower()
        and "round" not in str(x.get_label()).lower()
        and x.get_marker() in (None, "None", "")
    ]


@pytest.mark.parametrize("name", sorted(FIGURES))
def test_名前のある線は凡例に載る(name: str) -> None:
    for ax in _axes(name):
        labelled = _labelled_lines(ax)
        if not labelled:
            continue
        legend = ax.get_legend()
        assert legend is not None, f"{name}: 凡例がない"
        shown = {t.get_text() for t in legend.get_texts()}
        assert {x.get_label() for x in labelled} <= shown


@pytest.mark.parametrize("name", sorted(FIGURES))
def test_動かしたあとの曲線は点線で描く(name: str) -> None:
    for ax in _axes(name):
        for item in _shifted_curves(ax):
            # 破線（動かした曲線）か点線（為替調整後の IS。第 14 章）。実線は元の曲線だけ
            assert item.get_linestyle() in ("--", ":"), f"{name}: {item.get_label()}"


def test_動かしたあとの曲線のある図が存在する() -> None:
    """規則が、空振りにならないことの確認（対象が 1 本もなければ、上の検査は無意味）。"""
    count = sum(
        1 for name in FIGURES for ax in _axes(name) for item in _shifted_curves(ax)
    )
    assert count >= 8
