"""実データのスクリプトの検査（tools/check_realdata.py）のテスト。"""

from pathlib import Path

from article_tools.check_realdata import (
    compare_outputs,
    extract_realdata_scripts,
    run_script,
)

ARTICLE = """\
## 実際のデータ

次のスクリプトを `practice/chapter06/wage1.py` として保存し、実行します。

```python
print("a", 1.5)
```

```text
a 1.5
```

別の説明です。

次のスクリプトを、`practice/chapter10/wagepan.py` として保存し、実行します。

```python
print("b")
```

```text
b
```
"""


def test_記事から実データのスクリプトと出力を取り出す() -> None:
    scripts = extract_realdata_scripts(ARTICLE)
    assert [s.name for s in scripts] == ["chapter06/wage1", "chapter10/wagepan"]
    assert scripts[0].script == 'print("a", 1.5)\n'
    assert scripts[0].expected == "a 1.5\n"


def test_スクリプトの案内がなければ空() -> None:
    assert extract_realdata_scripts("本文だけ\n```python\nx = 1\n```\n") == []


def test_同じ出力なら不一致はない() -> None:
    assert compare_outputs("a 1.5\nb -2\n", "a 1.5\nb -2\n") == []


def test_数値は許容誤差の範囲なら一致とみなす() -> None:
    assert compare_outputs("x 965.31 3.159e-45\n", "x 965.32 3.1591e-45\n") == []


def test_数値が許容誤差を超えてずれれば不一致() -> None:
    problems = compare_outputs("x 965.31\n", "x 1278.0\n")
    assert len(problems) == 1
    assert "1行目" in problems[0]


def test_文字が違えば不一致() -> None:
    assert len(compare_outputs("a 1\n", "b 1\n")) == 1


def test_行数が違えば不一致() -> None:
    assert len(compare_outputs("a 1\nb 2\n", "a 1\n")) == 1


def test_スクリプトを実行して出力を得る(tmp_path: Path) -> None:
    assert run_script("print(1 + 1)\n", tmp_path) == "2\n"
