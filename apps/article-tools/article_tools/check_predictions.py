"""記事の「予想の答え合わせ」のスクリプトを実行し、記事の出力と照合する。

各章の「予想する」には答えを書かず、「プログラミング」の節の小節「予想の答え合わせ」で、
プログラムを動かして答えを確かめる。その小節の python のコードブロックと、
直後の text のコードブロック（出力）を取り出し、実行して、出力が一致するかを調べる。
数値は、**記事に表示した桁で、実際の値を、丸めたものと一致する**ことを求める
（`compare_prediction_outputs`。桁が 2 つずれた値は、通さない。プラットフォーム差の、
相対 1e-9 だけを許す）。

使い方（`apps/<シリーズ名>/python/` で）:

    uv run python -m article_tools.check_predictions
"""

import re
import sys
from dataclasses import dataclass

from article_tools.check_articles import APP_DIR, DOCS_DIR
from article_tools.check_realdata import run_script

_HEADING = "### 予想の答え合わせ"
# 見出しから、次の見出し（## か ###）までの範囲
_SECTION = re.compile(r"^### 予想の答え合わせ\n(.*?)(?=^#{2,3} |\Z)", re.S | re.M)
_BLOCKS = re.compile(r"```python\n(.*?)```\n.*?```text\n(.*?)```", re.S)
# 数値: 整数部・小数部・指数部（表示した桁数を、小数部から読み取る）
_NUMBER = re.compile(r"-?\d+(?:\.(\d+))?(?:e([-+]?\d+))?")
# プラットフォーム（OS・ライブラリ）の差で、最後の桁が揺れる分
_PLATFORM_REL_TOL = 1e-9


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


def _display_unit(token_fraction: str | None, token_exponent: str | None) -> float:
    """表示した最後の桁の大きさ（0.167 なら 0.001、5.208e-05 なら 1e-08）。"""
    decimals = len(token_fraction) if token_fraction else 0
    exponent = int(token_exponent) if token_exponent else 0
    return 10.0 ** (exponent - decimals)


def compare_prediction_outputs(expected: str, actual: str) -> list[str]:
    """記事の出力と、実際の出力を、行ごとに比べる。

    数字以外の文字は、一致を求める。数値は、記事に表示した桁で、実際の値を丸めたものと
    一致する（実際の値との差が、表示した最後の桁の半分以内）ことを求める。
    プラットフォーム差として、実際の値の相対 1e-9 だけを、さらに許す。
    """
    want, got = expected.splitlines(), actual.splitlines()
    problems = []
    if len(want) != len(got):
        problems.append(f"行数が違う: 記事 {len(want)} 行、実行結果 {len(got)} 行")
    for number, (a, b) in enumerate(zip(want, got, strict=False), start=1):
        if _NUMBER.sub("#", a) != _NUMBER.sub("#", b):
            problems.append(
                f"{number}行目の文字が違う: 記事 {a[:60]} / 実行結果 {b[:60]}"
            )
            continue
        for shown, real in zip(_NUMBER.finditer(a), _NUMBER.finditer(b), strict=True):
            x, y = float(shown.group()), float(real.group())
            half_unit = _display_unit(shown.group(1), shown.group(2)) / 2
            if abs(x - y) > half_unit + _PLATFORM_REL_TOL * abs(y):
                problems.append(
                    f"{number}行目の数値が違う: "
                    f"記事 {shown.group()} / 実行結果 {real.group()}"
                )
    return problems


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
                for problem in compare_prediction_outputs(item.expected, actual)
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
