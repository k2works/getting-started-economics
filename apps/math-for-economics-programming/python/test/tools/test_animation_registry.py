"""アニメーションの登録（tools/animation_registry）と、書き出し（tools/render_animations）のテスト。"""

import glob
from pathlib import Path

import pytest
from matplotlib.animation import FuncAnimation

from lib.animations.common import linear_values, make_animation
from tools import render_animations
from tools.animation_registry import ANIMATIONS


def test_アニメーションの名前は章の番号で始まる() -> None:
    for name in ANIMATIONS:
        assert name[:2] == "ch"
        assert name[2:4].isdigit()
        assert name[4] == "-"


@pytest.mark.parametrize("name", sorted(ANIMATIONS))
def test_登録したアニメーションのGIFがある(name: str) -> None:
    path = render_animations.IMAGES_DIR / f"{name}.gif"
    assert path.exists(), f"{name}: `python -m tools.render_animations` で生成する"
    assert path.read_bytes()[:6] == b"GIF89a"


@pytest.mark.parametrize("name", sorted(ANIMATIONS))
def test_登録したアニメーションは記事から参照される(name: str) -> None:
    chapter = name[2:4]
    articles = glob.glob(str(render_animations.IMAGES_DIR.parent / f"{chapter}-*.md"))
    assert articles, f"{name}: 第 {chapter} 章の記事がない"
    text = Path(articles[0]).read_text(encoding="utf-8")
    assert f"images/{name}.gif" in text


def test_記事のGIFは登録されている() -> None:
    referenced = {
        Path(p).stem for p in glob.glob(str(render_animations.IMAGES_DIR / "*.gif"))
    }
    assert referenced == set(ANIMATIONS)


def test_書き出しはGIFを作る(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def sample() -> FuncAnimation:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        (line,) = ax.plot([], [])

        def update(i: int) -> None:
            line.set_data([0, 1], [0, i])

        plt.close(fig)
        return make_animation(fig, update, 3)

    monkeypatch.setattr(render_animations, "ANIMATIONS", {"ch99-sample": sample})
    written = render_animations.render(tmp_path / "out")
    assert [p.name for p in written] == ["ch99-sample.gif"]
    assert written[0].read_bytes()[:6] == b"GIF89a"
    assert render_animations.render(tmp_path / "out2", ["ch98"]) == []


def test_等間隔の値は両端を含む() -> None:
    assert linear_values(0, 10, 5) == [0, 2.5, 5, 7.5, 10]
    assert linear_values(4, 1, 4) == [4, 3, 2, 1]


def test_フレーム数は2以上() -> None:
    with pytest.raises(ValueError, match="フレーム数"):
        linear_values(0, 1, 1)
