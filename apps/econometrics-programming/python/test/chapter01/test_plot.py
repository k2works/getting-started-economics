"""第 1 章: 確率分布の図のテスト。"""

from typing import Any

import pytest

from lib.chapter01.plot import plot_densities


def ys(line: Any) -> list[float]:
    data: Any = line.get_ydata()
    return [float(v) for v in data]


def xs(line: Any) -> list[float]:
    data: Any = line.get_xdata()
    return [float(v) for v in data]


def test_正規分布とt分布の線が順に描かれる() -> None:
    ax = plot_densities().axes[0]
    assert [line.get_label() for line in ax.lines] == [
        "Normal",
        "t(2)",
        "t(5)",
        "t(30)",
    ]


def test_中心の高さは理論値と一致する() -> None:
    ax = plot_densities().axes[0]
    middle = len(xs(ax.lines[0])) // 2
    assert xs(ax.lines[0])[middle] == pytest.approx(0)
    assert ys(ax.lines[0])[middle] == pytest.approx(0.398942, abs=1e-6)
    assert ys(ax.lines[1])[middle] == pytest.approx(0.353553, abs=1e-6)


def test_横軸は負の4から4まで() -> None:
    ax = plot_densities().axes[0]
    grid = xs(ax.lines[0])
    assert grid[0] == pytest.approx(-4)
    assert grid[-1] == pytest.approx(4)
    assert len(grid) == 201


def test_自由度が小さいほど裾が厚い() -> None:
    ax = plot_densities().axes[0]
    tail = [ys(line)[-1] for line in ax.lines]
    assert tail[1] > tail[2] > tail[3] > tail[0]


def test_自由度を指定できる() -> None:
    ax = plot_densities(degrees_of_freedom=(3,)).axes[0]
    assert [line.get_label() for line in ax.lines] == ["Normal", "t(3)"]


def test_軸の名前() -> None:
    ax = plot_densities().axes[0]
    assert ax.get_xlabel() == "Value"
    assert ax.get_ylabel() == "Density"
