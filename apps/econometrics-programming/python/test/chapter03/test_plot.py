"""第 3 章: 多重共線性の図のテスト。"""

from typing import Any

from lib.chapter03.plot import plot_collinearity_distributions


def line_x(ax: Any) -> list[float]:
    values: Any = ax.lines[0].get_xdata()
    return [float(v) for v in values]


def test_2つの分布のヒストグラムと真の値の線() -> None:
    low = [0.9, 1.0, 1.1, 1.0]
    high = [0.2, 1.0, 1.8, 1.0]
    ax = plot_collinearity_distributions(low, high).axes[0]
    assert len(ax.patches) == 2 * 20
    assert [line.get_label() for line in ax.lines] == ["True value"]
    legend = ax.get_legend()
    assert legend is not None
    assert [t.get_text() for t in legend.get_texts()] == [
        "Correlation low",
        "Correlation high",
        "True value",
    ]


def test_ヒストグラムの度数の合計は観測数() -> None:
    low = [0.9, 1.0, 1.1, 1.0]
    high = [0.2, 1.0, 1.8]
    ax = plot_collinearity_distributions(low, high).axes[0]
    bars: list[Any] = list(ax.patches)
    heights = [p.get_height() for p in bars]
    assert sum(heights[:20]) == len(low)
    assert sum(heights[20:]) == len(high)


def test_真の値の線は既定で1の位置() -> None:
    ax = plot_collinearity_distributions([1.0, 1.1], [0.5, 1.5]).axes[0]
    assert line_x(ax) == [1.0, 1.0]
    ax = plot_collinearity_distributions([1.0, 1.1], [0.5, 1.5], 2.0).axes[0]
    assert line_x(ax) == [2.0, 2.0]


def test_軸の名前() -> None:
    ax = plot_collinearity_distributions([1.0, 1.1], [0.5, 1.5]).axes[0]
    assert ax.get_xlabel() == "Estimated coefficient of x1"
    assert ax.get_ylabel() == "Frequency"
