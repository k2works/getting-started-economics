"""アニメーション（GIF）を、記事の画像のディレクトリに書き出す。

uv run python -m tools.render_animations
"""

from pathlib import Path

from tools.animation_registry import ANIMATIONS

IMAGES_DIR = (
    Path(__file__).resolve().parents[4]
    / "docs"
    / "article"
    / "econometrics-programming"
    / "images"
)
FPS = 10
DPI = 70


def render(directory: Path = IMAGES_DIR) -> list[Path]:
    """登録したアニメーションを、すべて GIF にして、書き出したファイルの一覧を返す。"""
    directory.mkdir(parents=True, exist_ok=True)
    written = []
    for name, build in sorted(ANIMATIONS.items()):
        path = directory / f"{name}.gif"
        build().save(path, writer="pillow", fps=FPS, dpi=DPI)
        written.append(path)
    return written


def main() -> None:
    for path in render():
        print(f"生成: {path.name}（{path.stat().st_size // 1024} KB）")


if __name__ == "__main__":
    main()
