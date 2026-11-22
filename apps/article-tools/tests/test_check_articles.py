"""記事の検査ツール（tools/check_articles.py）のテスト。"""

import pytest

from article_tools.check_articles import (
    extract_python_blocks,
    find_mismatches,
    find_unfenced_code,
    read_reported_counts,
    source_definitions,
    strip_answers,
    top_level_definitions,
)

ARTICLE = """\
# 第 N 章

```python
def add(a: int, b: int) -> int:
    return a + b


def sub(a: int, b: int) -> int:
    return a - b
```

説明の文章。

- 手順
    ```python
    def indented() -> None:
        pass
    ```

```bash
uv run pytest test/chapter02
```

```text
10 passed
```

## N.6 練習問題

| 種類 | 問題 |
| :--- | :--- |
| 想起 | ... |

??? note "解答（先に自分で取り組んでから、開いてください）"

    ```python
    def answer() -> int:
        return 1
    ```

## N.7 振り返り

終わり。
"""


def test_記事からPythonのコードブロックを取り出す() -> None:
    blocks = extract_python_blocks(ARTICLE)
    assert len(blocks) == 3
    assert blocks[0].startswith("def add(a: int, b: int) -> int:")


def test_リストの中のコードブロックは字下げを取り除く() -> None:
    blocks = extract_python_blocks(ARTICLE)
    assert blocks[1] == "def indented() -> None:\n    pass"


def test_コードブロックを関数や定数の単位に分ける() -> None:
    block = extract_python_blocks(ARTICLE)[0]
    assert top_level_definitions(block) == [
        "def add(a: int, b: int) -> int:\n    return a + b",
        "def sub(a: int, b: int) -> int:\n    return a - b",
    ]


def test_定義でないコード片は分けた単位に含めない() -> None:
    block = "x = 1\nprint(x)"
    assert top_level_definitions(block) == []


def test_解答の節は検査の対象から外す() -> None:
    stripped = strip_answers(ARTICLE)
    assert "def answer()" not in stripped
    # 解答の次の節は残る
    assert "## N.7 振り返り" in stripped


def test_解答の節が最後にあるときも外せる() -> None:
    text = '本文\n\n??? note "解答（x）"\n\n    ```python\n    def answer() -> None:\n        pass\n    ```\n'
    assert "def answer" not in strip_answers(text)


def test_実装に含まれる定義は不一致にならない() -> None:
    source = "def add(a: int, b: int) -> int:\n    return a + b\n"
    assert find_mismatches(ARTICLE, source_definitions(source), allowed=[]) == [
        "def sub(a: int, b: int) -> int:\n    return a - b",
        "def indented() -> None:\n    pass",
    ]


def test_許可した抜粋は不一致にならない() -> None:
    source = "def add(a: int, b: int) -> int:\n    return a + b\n"
    allowed = [
        "def sub(a: int, b: int) -> int:\n    return a - b",
        "def indented() -> None:\n    pass",
    ]
    assert find_mismatches(ARTICLE, source_definitions(source), allowed=allowed) == []


def test_末尾の行を欠いた関数は不一致になる() -> None:
    """部分文字列の一致では、関数の `return` を消しても通ってしまう（全体レビューで実演）。"""
    source = "def add(a: int, b: int) -> int:\n    return a + b\n"
    cut = "```python\ndef add(a: int, b: int) -> int:\n```\n"
    assert find_mismatches(cut, source_definitions(source), allowed=[]) == [
        "def add(a: int, b: int) -> int:"
    ]


def test_ソースの定義は_デコレータと直前のコメントを含めて取り出す() -> None:
    source = (
        "import math\n\n"
        "# 許容誤差\n"
        "TOLERANCE = 1e-9\n\n\n"
        "@decorator\n"
        "def f() -> None:\n"
        "    pass\n\n\n"
        "class C:\n"
        "    value: int = 1\n"
    )
    found = source_definitions(source)
    assert "TOLERANCE = 1e-9" in found
    assert "# 許容誤差\nTOLERANCE = 1e-9" in found
    assert "@decorator\ndef f() -> None:\n    pass" in found
    assert "class C:\n    value: int = 1" in found
    assert not any(d.startswith("import") for d in found)


def test_一部の行だけの定数は不一致になる() -> None:
    source = "TABLE = {\n    1: 2,\n    3: 4,\n}\n"
    shown = "```python\nTABLE = {\n    1: 2,\n}\n```\n"
    assert find_mismatches(shown, source_definitions(source), allowed=[]) == [
        "TABLE = {\n    1: 2,\n}"
    ]


def test_フェンスの外のコード行を見つける() -> None:
    markdown = (
        "説明です。\n\n```python\nimport os\n```\n\n"
        "def test_x() -> None:\n    return None\n"
    )
    assert find_unfenced_code(markdown) == [
        "def test_x() -> None:",
        "    return None",
    ]


def test_フェンスの中のコードと文章は対象にしない() -> None:
    markdown = "文章 import の話。\n\n```python\ndef f():\n    return 1\n```\n"
    assert find_unfenced_code(markdown) == []


def test_字下げされたフェンスの中も対象にしない() -> None:
    markdown = "    ```python\n    def f():\n        return 1\n    ```\n"
    assert find_unfenced_code(markdown) == []


def test_実行結果の件数を読み取る() -> None:
    assert read_reported_counts(ARTICLE) == [(2, 10)]


def test_実行結果がなければ空() -> None:
    assert read_reported_counts("本文だけ") == []


@pytest.mark.parametrize("passed", ["5", "123"])
def test_件数は数字として読み取る(passed: str) -> None:
    text = (
        f"```bash\nuv run pytest test/chapter01\n```\n\n```text\n{passed} passed\n```\n"
    )
    assert read_reported_counts(text) == [(1, int(passed))]


TEMPLATE = "```bash\nuv run pytest test/chapter01\n```\n\n```text\n{} passed\n```\n"


def test_同じ章の実行結果が2か所あれば両方を読み取る() -> None:
    text = TEMPLATE.format(5) + "\n途中の文章\n\n" + TEMPLATE.format(6)
    assert read_reported_counts(text) == [(1, 5), (1, 6)]
