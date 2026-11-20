"""「予想の答え合わせ」の検査（article_tools/check_predictions.py）のテスト。"""

from article_tools.check_predictions import extract_predictions

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
