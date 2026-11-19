"""記事とサンプル実装のずれを検出する。

次の 3 つを調べる。ずれがあれば、内容を表示して、終了コード 1 で終わる。

1. 記事の完成形のコード例が、`lib/` と `test/` のソースに含まれているか
   （説明用の抜粋は `tools/article_code_excerpts.json` に、そのまま登録する）
2. 各章の「実行結果」の件数が、その章のテストの件数と一致しているか
3. 各章の練習問題の「解答」に書いたコードが、実際に実行できるか

使い方（`apps/<シリーズ名>/python/` で）:

    uv run python -m tools.check_articles
"""

import json
import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
# apps/<シリーズ名>/python/ の「シリーズ名」が、記事のディレクトリ名
SERIES = APP_DIR.parent.name
DOCS_DIR = APP_DIR.parents[2] / "docs" / "article" / SERIES
EXCERPTS_FILE = Path(__file__).resolve().parent / "article_code_excerpts.json"

# 完成形として照合する、トップレベルの定義の書き出し
_DEFINITION_START = r"(?:def |class |@|[A-Z_]+[: =]|# )"
_BLOCK_PATTERN = re.compile(r"```python\n(.*?)```", re.S)
_COUNT_PATTERN = re.compile(
    r"uv run pytest test/chapter(\d{2})\n```\n\n```text\n(\d+) passed\n```"
)

# 解答のコードを実行するときに、章ごとに前もって用意する定義（章の番号 -> コード）
PRELUDES_FILE = Path(__file__).resolve().parent / "answer_preludes.json"


def load_preludes() -> dict[str, str]:
    """章ごとの、解答の前に置く定義を読み込む。ファイルがなければ、空。"""
    if not PRELUDES_FILE.exists():
        return {}
    data: dict[str, str] = json.loads(PRELUDES_FILE.read_text(encoding="utf-8"))
    return data


def extract_python_blocks(markdown: str) -> list[str]:
    """記事から Python のコードブロックを、字下げを除いて取り出す。"""
    blocks = (m.group(1) for m in _BLOCK_PATTERN.finditer(markdown))
    return [textwrap.dedent(b).strip("\n") for b in blocks]


def top_level_definitions(block: str) -> list[str]:
    """コードブロックを、関数・クラス・定数などの単位に分けて、定義だけを返す。"""
    parts = re.split(rf"\n\n\n(?={_DEFINITION_START})", block)
    return [p.strip("\n") for p in parts if re.match(_DEFINITION_START, p.strip("\n"))]


def strip_answers(markdown: str) -> str:
    """練習問題の解答（折りたたみ）の節を取り除く。"""
    start = markdown.find('??? note "解答')
    if start == -1:
        return markdown
    end = markdown.find("\n## ", start)
    return markdown[:start] + (markdown[end:] if end != -1 else "")


def find_mismatches(markdown: str, source: str, allowed: list[str]) -> list[str]:
    """ソースに含まれず、許可した抜粋でもない、記事の定義を返す。"""
    body = strip_answers(markdown)
    definitions = [
        d for block in extract_python_blocks(body) for d in top_level_definitions(block)
    ]
    return [d for d in definitions if d not in source and d not in allowed]


def read_reported_counts(markdown: str) -> list[tuple[int, int]]:
    """「実行結果」に書かれた（章, テスト件数）を、出てくる順にすべて読み取る。

    同じ章の実行結果が、複数の箇所にあっても、すべてを返す。
    """
    return [
        (int(m.group(1)), int(m.group(2))) for m in _COUNT_PATTERN.finditer(markdown)
    ]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def _article_files() -> list[Path]:
    chapters = sorted(DOCS_DIR.glob("[01][0-9]-*.md"))
    return chapters + sorted(DOCS_DIR.glob("appendix-*.md"))


def _source_text() -> str:
    files = [*APP_DIR.glob("lib/**/*.py"), *APP_DIR.glob("test/**/*.py")]
    return "\n".join(_read(f) for f in sorted(files))


def _load_excerpts() -> dict[str, list[str]]:
    if not EXCERPTS_FILE.exists():
        return {}
    data: dict[str, list[str]] = json.loads(EXCERPTS_FILE.read_text(encoding="utf-8"))
    return data


def check_code_blocks() -> list[str]:
    """記事の完成形のコード例が、実装・テストのソースと一致するかを調べる。"""
    source = _source_text()
    excerpts = _load_excerpts()
    problems = []
    for path in _article_files():
        allowed = excerpts.get(path.name, [])
        for text in find_mismatches(_read(path), source, allowed):
            first = text.split("\n")[0]
            problems.append(f"{path.name}: ソースにないコード: {first}")
    return problems


def _actual_counts() -> dict[int, int]:
    """章ごとのテスト件数を、pytest の収集結果（テストの ID）から数える。

    pytest の起動は 1 回だけにする（起動のたびに、ライブラリの読み込みで時間がかかる）。
    """
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q",
         "-p", "no:cacheprovider", "test"],
        cwd=APP_DIR, capture_output=True, text=True, encoding="utf-8", check=False,
    )  # fmt: skip
    counts: dict[int, int] = {}
    for line in result.stdout.splitlines():
        match = re.match(r"test[/\\]chapter(\d{2})[/\\]", line)
        if match:
            chapter = int(match.group(1))
            counts[chapter] = counts.get(chapter, 0) + 1
    return counts


def check_counts() -> list[str]:
    """記事の「実行結果」の件数が、実際のテスト件数と一致するかを調べる。"""
    actual_counts = _actual_counts()
    problems = []
    for path in _article_files():
        for chapter, reported in read_reported_counts(_read(path)):
            actual = actual_counts.get(chapter, 0)
            if actual != reported:
                problems.append(
                    f"{path.name}: 実行結果は {reported} 件だが、実際は {actual} 件"
                )
    return problems


def _answer_module(chapter: int, markdown: str) -> str | None:
    """解答のコードを、1 つのテストモジュールにまとめる。解答がなければ None。"""
    start = markdown.find('??? note "解答')
    if start == -1:
        return None
    end = markdown.find("\n## ", start)
    section = markdown[start : end if end != -1 else len(markdown)]
    blocks = extract_python_blocks(section)
    imports = "\n".join(
        f"from lib.{f.parent.name}.{f.stem} import *"
        for f in sorted(APP_DIR.glob("lib/chapter*/*.py"))
        if f.stem != "__init__"
    )
    header = (
        "import math, random, statistics, dataclasses\n"
        "import numpy as np\nimport pandas as pd\nimport pytest\n"
        "import matplotlib\nmatplotlib.use('Agg')\n"
        "import matplotlib.pyplot as plt\n"
        "from matplotlib.figure import Figure\n"
        "from collections.abc import Mapping\n"
    )
    return (
        header
        + imports
        + "\n"
        + load_preludes().get(str(chapter), "")
        + "\n\n".join(blocks)
    )


def _run_answers(modules: dict[int, str]) -> str | None:
    """全章の解答のモジュールを、1 回の pytest で実行する。失敗したときは出力を返す。"""
    with tempfile.TemporaryDirectory() as tmp:
        for chapter, module in modules.items():
            file = Path(tmp) / f"test_answers_{chapter:02d}.py"
            file.write_text(module, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
             "--continue-on-collection-errors",
             "--rootdir", str(APP_DIR), "-c", str(APP_DIR / "pyproject.toml"), tmp],
            cwd=APP_DIR, capture_output=True, text=True, encoding="utf-8",
            errors="replace", check=False,
        )  # fmt: skip
    # 5 は「テストがない」。関数やコード片だけの解答は、エラーなく読み込めればよい
    return None if result.returncode in (0, 5) else result.stdout


def _failed_chapters(output: str) -> list[int]:
    """pytest の出力の、FAILED・ERROR の行から、失敗した章を取り出す。"""
    marks = ("FAILED", "ERROR")
    lines = [row for row in output.splitlines() if row.startswith(marks)]
    found = re.findall(r"test_answers_(\d{2})\.py", "\n".join(lines))
    return sorted({int(chapter) for chapter in found})


def check_answers() -> list[str]:
    """各章の解答のコードが、実際に実行できるかを調べる。"""
    modules: dict[int, str] = {}
    for path in _article_files():
        match = re.match(r"(\d{2})-", path.name)
        module = _answer_module(int(match.group(1)), _read(path)) if match else None
        if match and module:
            modules[int(match.group(1))] = module
    output = _run_answers(modules) if modules else None
    if output is None:
        return []
    problems = [
        f"第 {chapter} 章の解答のコードが実行できない"
        for chapter in _failed_chapters(output)
    ]
    return problems + ["\n".join(output.strip().split("\n")[-25:])]


def main() -> int:
    checks = [
        ("記事のコード例と実装の照合", check_code_blocks),
        ("実行結果の件数の照合", check_counts),
        ("解答のコードの実行", check_answers),
    ]
    failed = 0
    for title, check in checks:
        problems = check()
        print(f"{'NG' if problems else 'OK'}  {title}")
        for problem in problems:
            print(f"    {problem}")
        failed += bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
