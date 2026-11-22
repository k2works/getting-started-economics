"""図の生成ツール（tools/render_figures.py）のテスト。"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Polygon

from article_tools.render_figures import (
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


def make_styled_figure(linestyle: str = "-", xlim: float = 1.0) -> Figure:
    fig, ax = plt.subplots()
    ax.plot([0.0, 1.0], [1.0, 2.0], linestyle=linestyle, label="A")
    ax.set_xlim(0, xlim)
    plt.close(fig)
    return fig


def test_線種が変わると指紋も変わる() -> None:
    assert fingerprint(make_styled_figure("-")) != fingerprint(make_styled_figure("--"))


def test_軸の範囲が変わると指紋も変わる() -> None:
    assert fingerprint(make_styled_figure(xlim=1.0)) != fingerprint(
        make_styled_figure(xlim=2.0)
    )


# 矢印・文字・塗り・タイトルのない図の指紋は、要素を足す前と同じ値のままにする。
# 値を変えると、すべての連載の指紋を作り直すことになる
def test_矢印も塗りもタイトルもない図の指紋はこれまでと同じ() -> None:
    assert fingerprint(make_line_figure()) == (
        "d2663207b0586a3bcffa8ae2f921f14803cfbe084948f5f3602d911069ac2ee3"
    )
    assert fingerprint(make_bar_figure()) == (
        "f1865175569e5fe275d384714bc92f776dcbb14070445a7109e93c36edcac5b6"
    )


def make_arrow_figure(xy: tuple[float, float], xytext: tuple[float, float]) -> Figure:
    fig, ax = plt.subplots()
    ax.plot([0.0, 1.0], [0.0, 1.0])
    ax.annotate("", xy=xy, xytext=xytext, arrowprops={"arrowstyle": "->"})
    plt.close(fig)
    return fig


def test_矢印の向きが変わると指紋も変わる() -> None:
    forward = make_arrow_figure(xy=(1.0, 1.0), xytext=(0.0, 0.0))
    backward = make_arrow_figure(xy=(0.0, 0.0), xytext=(1.0, 1.0))
    assert fingerprint(forward) == fingerprint(
        make_arrow_figure(xy=(1.0, 1.0), xytext=(0.0, 0.0))
    )
    assert fingerprint(forward) != fingerprint(backward)


def test_矢印の文字が変わると指紋も変わる() -> None:
    def make(text: str) -> Figure:
        fig, ax = plt.subplots()
        ax.annotate(text, xy=(1.0, 1.0), xytext=(0.0, 0.0))
        plt.close(fig)
        return fig

    assert fingerprint(make("均衡")) != fingerprint(make("最適"))


def test_図に書いた文字が変わると指紋も変わる() -> None:
    def make(text: str, x: float = 0.5) -> Figure:
        fig, ax = plt.subplots()
        ax.text(x, 0.5, text)
        plt.close(fig)
        return fig

    assert fingerprint(make("A")) != fingerprint(make("B"))
    assert fingerprint(make("A", x=0.5)) != fingerprint(make("A", x=0.7))


def make_filled_figure(top: float = 1.0) -> Figure:
    fig, ax = plt.subplots()
    ax.fill_between([0.0, 1.0, 2.0], [0.0, 0.0, 0.0], [top, top, top])
    ax.set_xlim(0, 2)  # 軸の範囲を固定し、塗りの違いだけを見る
    ax.set_ylim(0, 2)
    plt.close(fig)
    return fig


def test_塗りつぶした領域が変わると指紋も変わる() -> None:
    assert fingerprint(make_filled_figure(1.0)) == fingerprint(make_filled_figure(1.0))
    assert fingerprint(make_filled_figure(1.0)) != fingerprint(make_filled_figure(1.5))


def test_散布図の点が変わると指紋も変わる() -> None:
    def make(y: float) -> Figure:
        fig, ax = plt.subplots()
        ax.scatter([0.0, 1.0], [0.0, y])
        ax.set_xlim(0, 3)  # 軸の範囲を固定し、点の違いだけを見る
        ax.set_ylim(0, 3)
        plt.close(fig)
        return fig

    assert fingerprint(make(1.0)) != fingerprint(make(2.0))


def test_タイトルが変わると指紋も変わる() -> None:
    def make(title: str) -> Figure:
        fig = make_line_figure()
        fig.axes[0].set_title(title)
        return fig

    assert fingerprint(make("需要")) != fingerprint(make("供給"))


def test_図全体のタイトルが変わると指紋も変わる() -> None:
    def make(title: str) -> Figure:
        fig = make_line_figure()
        fig.suptitle(title)
        return fig

    assert fingerprint(make("第 1 章")) != fingerprint(make("第 2 章"))


def make_log_figure(smallest: float) -> Figure:
    fig, ax = plt.subplots()
    ax.loglog([1e-1, 1e-2, 1e-3], [1e-3, 1e-5, smallest])
    ax.set_xlim(1e-4, 1)  # 軸の範囲を固定し、線の座標の違いだけを見る
    ax.set_ylim(1e-9, 1)
    plt.close(fig)
    return fig


def test_対数目盛の小さな値の違いを区別する() -> None:
    assert fingerprint(make_log_figure(1e-5)) != fingerprint(make_log_figure(1e-7))


def test_小さな値も有効数字の5桁目以降の違いでは指紋は変わらない() -> None:
    assert fingerprint(make_log_figure(1.2345e-7)) == fingerprint(
        make_log_figure(1.2345e-7 * (1 + 1e-9))
    )


def test_線形目盛では0になるはずの値の計算誤差で指紋は変わらない() -> None:
    def make(noise: float) -> Figure:
        fig, ax = plt.subplots()
        ax.plot([0.0, 1.0, 2.0], [1.0, noise, 1.0])
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 2)
        plt.close(fig)
        return fig

    assert fingerprint(make(0.0)) == fingerprint(make(5.7e-15))
    assert fingerprint(make(4.4e-15)) == fingerprint(make(6.7e-15))


def test_対数目盛の小さな棒の高さの違いを区別する() -> None:
    def make(height: float) -> Figure:
        fig = make_bar_figure(height)
        fig.axes[0].set_yscale("log")
        fig.axes[0].set_ylim(1e-9, 10)
        return fig

    assert fingerprint(make(1e-5)) != fingerprint(make(1e-7))
