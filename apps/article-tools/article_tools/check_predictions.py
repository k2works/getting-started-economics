"""記事の「予想の答え合わせ」のスクリプトを実行し、記事の出力と照合する。

各章の「予想する」には答えを書かず、「プログラミング」の節の小節「予想の答え合わせ」で、
プログラムを動かして答えを確かめる。その小節の python のコードブロックと、
直後の text のコードブロック（出力）を取り出し、実行して、出力が一致するかを調べる。
数値は、小数に丸めた最後の桁のずれを許す（`check_realdata.compare_outputs`）。

使い方（`apps/<シリーズ名>/python/` で）:

    uv run python -m article_tools.check_predictions
"""

import re
import sys
from dataclasses import dataclass

from article_tools.check_articles import APP_DIR, DOCS_DIR
from article_tools.check_realdata import compare_outputs, run_script

_HEADING = "### 予想の答え合わせ"
# 見出しから、次の見出し（## か ###）までの範囲
_SECTION = re.compile(r"^### 予想の答え合わせ\n(.*?)(?=^#{2,3} |\Z)", re.S | re.M)
_BLOCKS = re.compile(r"```python\n(.*?)```\n.*?```text\n(.*?)```", re.S)


@dataclass(frozen=True)
class Prediction:
    script: str
    expected: str


def extract_predictions(markdown: str) -> list[Prediction]:
    """「予想の答え合わせ」の小節ごとに、スクリプトと、記事に載せた出力を取り出す。"""
    found = []
    for section in _SECTION.finditer(markdown):
        block = _BLOCKS.search(section.group(1))
        if block:
            found.append(Prediction(block.group(1), block.group(2)))
    return found


def check_predictions() -> list[str]:
    """記事の予想の答え合わせを実行し、記事の出力と一致するかを調べる。"""
    problems = []
    for path in sorted(DOCS_DIR.glob("[0-9][0-9]-*.md")) + sorted(
        DOCS_DIR.glob("appendix-*.md")
    ):
        text = path.read_text(encoding="utf-8")
        if _HEADING in text and not extract_predictions(text):
            problems.append(
                f"{path.name}: 予想の答え合わせに、コードと出力のブロックがない"
            )
        for item in extract_predictions(text):
            try:
                actual = run_script(item.script, APP_DIR)
            except RuntimeError as error:
                problems.append(f"{path.name}: 実行に失敗: {error}")
                continue
            problems.extend(
                f"{path.name}: {problem}"
                for problem in compare_outputs(item.expected, actual)
            )
    return problems


def main() -> int:
    problems = check_predictions()
    print(f"{'NG' if problems else 'OK'}  予想の答え合わせの実行と出力の照合")
    for problem in problems:
        print(f"    {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
