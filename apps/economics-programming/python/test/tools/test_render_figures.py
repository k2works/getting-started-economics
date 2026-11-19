"""図の生成ツール（tools/render_figures.py）のテスト。"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Polygon

from tools.render_figures import (
    FIGURES,
    find_problems,
    fingerprint,
    referenced_images,
)


def make_line_figure(y: float = 2.0, label: str = "A") -> Figure:
    fig, ax = plt.subplots()
    ax.plot([0.0, 1.0], [1.0, y], label=label)
    ax.set_xlabel("X")
    plt.close(fig)
    return fig


def make_bar_figure(height: float = 3.0) -> Figure:
    fig, ax = plt.subplots()
    ax.bar([0, 1], [height, 1.0])
    plt.close(fig)
    return fig


def test_同じ図の指紋は同じ() -> None:
    assert fingerprint(make_line_figure()) == fingerprint(make_line_figure())


def test_線の座標が変わると指紋も変わる() -> None:
    assert fingerprint(make_line_figure(y=2.0)) != fingerprint(make_line_figure(y=2.5))


def test_線の名前が変わると指紋も変わる() -> None:
    assert fingerprint(make_line_figure(label="A")) != fingerprint(
        make_line_figure(label="B")
    )


def test_棒の高さが変わると指紋も変わる() -> None:
    assert fingerprint(make_bar_figure(3.0)) != fingerprint(make_bar_figure(3.5))


def test_ごく小さな数値の誤差では指紋は変わらない() -> None:
    assert fingerprint(make_line_figure(y=2.0)) == fingerprint(
        make_line_figure(y=2.0 + 1e-9)
    )


def test_指紋は16進数の文字列() -> None:
    value = fingerprint(make_line_figure())
    assert len(value) == 64
    assert set(value) <= set("0123456789abcdef")


def test_記事の図の名前は画像ファイル名と対応している() -> None:
    assert "ch07-market" in FIGURES
    assert all(name.startswith("ch") for name in FIGURES)


def test_Markdownから画像のファイル名を取り出す() -> None:
    text = (
        "![市場](images/ch07-market.png)\n"
        "本文 ![成長率](images/ch12-growth.png) 本文\n"
        "![外部](https://example.com/a.png)\n"
    )
    assert referenced_images(text) == {"ch07-market", "ch12-growth"}


def test_問題がなければ何も報告しない() -> None:
    names = {"a", "b"}
    assert (
        find_problems(
            current={"a": "1", "b": "2"},
            stored={"a": "1", "b": "2"},
            on_disk=names,
            referenced=names,
        )
        == []
    )


def test_指紋が保存した値と違えば画像が古いと報告する() -> None:
    names = {"a"}
    problems = find_problems(
        current={"a": "NEW"}, stored={"a": "OLD"}, on_disk=names, referenced=names
    )
    assert len(problems) == 1
    assert "a" in problems[0]
    assert "再生成" in problems[0]


def test_保存した指紋がなければ報告する() -> None:
    names = {"a"}
    problems = find_problems(
        current={"a": "1"}, stored={}, on_disk=names, referenced=names
    )
    assert len(problems) == 1


def test_画像ファイルがなければ報告する() -> None:
    problems = find_problems(
        current={"a": "1"}, stored={"a": "1"}, on_disk=set(), referenced={"a"}
    )
    assert any("ファイルがない" in p for p in problems)


def test_登録されていない画像ファイルは孤立として報告する() -> None:
    problems = find_problems(
        current={"a": "1"},
        stored={"a": "1"},
        on_disk={"a", "orphan"},
        referenced={"a"},
    )
    assert any("orphan" in p and "孤立" in p for p in problems)


def test_記事から参照されていない図は報告する() -> None:
    problems = find_problems(
        current={"a": "1", "b": "2"},
        stored={"a": "1", "b": "2"},
        on_disk={"a", "b"},
        referenced={"a"},
    )
    assert any("b" in p and "参照されていない" in p for p in problems)


def test_記事が登録されていない図を参照していたら報告する() -> None:
    problems = find_problems(
        current={"a": "1"},
        stored={"a": "1"},
        on_disk={"a"},
        referenced={"a", "ghost"},
    )
    assert any("ghost" in p and "登録されていない" in p for p in problems)


def test_塗りつぶした多角形の頂点が変わると指紋も変わる() -> None:
    def make(x: float) -> Figure:
        fig, ax = plt.subplots()
        ax.add_patch(Polygon([(0, 0), (1, 0), (x, 1)]))
        plt.close(fig)
        return fig

    assert fingerprint(make(0.5)) == fingerprint(make(0.5))
    assert fingerprint(make(0.5)) != fingerprint(make(0.7))
