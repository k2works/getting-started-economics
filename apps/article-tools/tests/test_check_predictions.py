"""「予想の答え合わせ」の検査（article_tools/check_predictions.py）のテスト。"""

import pytest

from article_tools.check_predictions import (
    compare_prediction_outputs,
    extract_predictions,
)

ARTICLE = """\
## 5.2 予想する

問い。

## 5.3 プログラミング

### 予想の答え合わせ

予想した答えを、プログラムで確かめます。

```python
print("a", 1.5)
```

```text
a 1.5
```

説明です。

### 実行結果

```python
print("別のブロック")
```

```text
別のブロック
```
"""


def test_予想の答え合わせのスクリプトと出力を取り出す() -> None:
    found = extract_predictions(ARTICLE)
    assert len(found) == 1
    assert found[0].script == 'print("a", 1.5)\n'
    assert found[0].expected == "a 1.5\n"


def test_予想の答え合わせの外のブロックは対象にしない() -> None:
    text = "### 実行結果\n\n```python\nprint(1)\n```\n\n```text\n1\n```\n"
    assert extract_predictions(text) == []


def test_次の見出しを越えてブロックを探さない() -> None:
    text = (
        "### 予想の答え合わせ\n\n導入だけで、ブロックがない。\n\n"
        "### 実行結果\n\n```python\nprint(1)\n```\n\n```text\n1\n```\n"
    )
    assert extract_predictions(text) == []


def test_節ごとに別々に取り出す() -> None:
    text = ARTICLE + ARTICLE.replace("a 1.5", "b 2").replace('"a", 1.5', '"b", 2')
    found = extract_predictions(text)
    assert [item.expected for item in found] == ["a 1.5\n", "b 2\n"]


@pytest.mark.parametrize(
    ("expected", "actual"),
    [
        ("0.167", "0.16700000000000001"),  # 実際の値を、表示の桁に丸めたもの
        ("0.167", "0.1668"),  # 丸めると 0.167
        ("100.0", "100.04"),
        ("1.998046875", "1.998046875"),
        ("5.208e-05", "5.2084e-05"),  # 指数表記の桁
        (
            "1.2676506002282153",
            "1.2676506002282257",
        ),  # プラットフォーム差（相対 1e-9 以内）
        ("10049", "10049"),
        ("a 1.5 b 2", "a 1.5 b 2.0"),
    ],
)
def test_表示した桁で丸めた値と一致すれば通る(expected: str, actual: str) -> None:
    assert compare_prediction_outputs(expected, actual) == []


@pytest.mark.parametrize(
    ("expected", "actual"),
    [
        (
            "5.208e-05",
            "5.208e-07",
        ),  # 桁が 2 つずれた小さい値（旧: 絶対許容 2e-4 で通っていた）
        ("2.999268", "2.999468"),
        ("10049", "10058"),  # 整数の、相対 1e-3 以内のずれ（旧: 通っていた）
        ("1.105166667", "1.10535"),
        ("0.167", "0.169"),  # 表示の桁の、丸めと違う
        ("100.0", "100.1"),
    ],
)
def test_桁がずれた値は通さない(expected: str, actual: str) -> None:
    problems = compare_prediction_outputs(expected, actual)
    assert len(problems) == 1
    assert "数値が違う" in problems[0]


def test_数字以外の文字の違いと行数の違いを見つける() -> None:
    assert "文字が違う" in compare_prediction_outputs("a 1.0", "b 1.0")[0]
    assert "行数が違う" in compare_prediction_outputs("1.0\n2.0", "1.0")[0]
