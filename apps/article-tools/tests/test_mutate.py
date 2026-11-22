"""変異確認（article_tools/mutate.py）のテスト。"""

import shutil
from pathlib import Path

import pytest

from article_tools.mutate import (
    Mutant,
    MutationError,
    Report,
    Survivor,
    default_test_dir,
    format_report,
    generate_mutants,
    run,
)


def _sources(source: str, kind: str) -> list[str]:
    return [m.source for m in generate_mutants(source) if m.kind == kind]


def _normalized(code: str) -> str:
    """比べるために、ast.unparse の書式に揃える。"""
    import ast

    return ast.unparse(ast.parse(code))


# ---- generate_mutants: 変異の種類 ----


def test_算術の演算子を1か所ずつ入れ替える() -> None:
    mutants = _sources("y = a + b - c\n", "arith")
    assert sorted(mutants) == sorted(
        [_normalized("y = a - b - c"), _normalized("y = a + b + c")]
    )


def test_入れ子の演算の内側と外側を取り違えない() -> None:
    mutants = _sources("y = a * b / 2\n", "arith")
    assert sorted(mutants) == sorted(
        [_normalized("y = a / b / 2"), _normalized("y = a * b * 2")]
    )


def test_べき乗と切り捨て除算と剰余も変異させる() -> None:
    mutants = _sources("y = a ** 2 + b // c + d % e\n", "arith")
    assert _normalized("y = a * 2 + b // c + d % e") in mutants
    assert _normalized("y = a ** 2 + b / c + d % e") in mutants
    assert _normalized("y = a ** 2 + b // c + d // e") in mutants


def test_比較の境界を1つずつずらす() -> None:
    mutants = _sources("y = a < b\nz = a == b\n", "compare")
    assert _normalized("y = a <= b\nz = a == b") in mutants
    assert _normalized("y = a < b\nz = a != b") in mutants


def test_連鎖比較はすべての位置をそれぞれ変異させる() -> None:
    mutants = _sources("ok = 0 < x < 10\n", "compare")
    assert sorted(mutants) == sorted(
        [_normalized("ok = 0 <= x < 10"), _normalized("ok = 0 < x <= 10")]
    )


def test_andとorを入れ替えnotを除く() -> None:
    source = "y = a and b\nz = not c\n"
    assert _sources(source, "bool") == [_normalized("y = a or b\nz = not c")]
    assert _sources(source, "not") == [_normalized("y = a and b\nz = c")]


def test_単項マイナスを除く() -> None:
    assert _sources("y = -x\n", "neg") == [_normalized("y = x")]


def test_absを除きmaxとminを入れ替える() -> None:
    source = "y = abs(x)\nz = max(a, min(b, c))\n"
    assert _sources(source, "abs") == [_normalized("y = x\nz = max(a, min(b, c))")]
    assert sorted(_sources(source, "maxmin")) == sorted(
        [
            _normalized("y = abs(x)\nz = min(a, min(b, c))"),
            _normalized("y = abs(x)\nz = max(a, max(b, c))"),
        ]
    )


def test_定数は整数に1を足し浮動小数は1点5倍し0は1にする() -> None:
    mutants = _sources("a = 3\nb = 0.5\nc = 0\nd = 0.0\n", "const")
    assert _normalized("a = 4\nb = 0.5\nc = 0\nd = 0.0") in mutants
    assert _normalized("a = 3\nb = 0.75\nc = 0\nd = 0.0") in mutants
    assert _normalized("a = 3\nb = 0.5\nc = 1\nd = 0.0") in mutants
    assert _normalized("a = 3\nb = 0.5\nc = 0\nd = 1.0") in mutants


def test_値が変わらない定数の変異は作らない() -> None:
    # 1e999 は無限大。1.5 倍しても無限大のまま
    assert _sources("big = 1e999\n", "const") == []


def test_真偽値の定数を反転する() -> None:
    assert _sources("flag = True\n", "true_false") == [_normalized("flag = False")]


def test_戻り値をNoneにする() -> None:
    source = "def f(x):\n    return x + 1\n\ndef g():\n    return\n"
    assert _sources(source, "return") == [
        _normalized("def f(x):\n    return None\n\ndef g():\n    return")
    ]


def test_docstringと型注釈と__all__は変異させない() -> None:
    source = (
        '"""モジュールの説明 1 + 2。"""\n'
        '__all__ = ["f"] + ["g"]\n'
        "LIMIT: Literal[3] = 7\n"
        "def f(x: Literal[1]) -> Literal[2]:\n"
        '    """関数の説明。"""\n'
        "    return x\n"
    )
    mutants = generate_mutants(source)
    descriptions = [m.description for m in mutants]
    assert [m.kind for m in mutants] == ["const", "return"]
    assert descriptions[0] == "7 → 8"


def test_変異は種類と行と元の記述を持つ() -> None:
    source = "def f(q):\n    if q <= 0:\n        raise ValueError\n"
    (mutant,) = [m for m in generate_mutants(source) if m.kind == "compare"]
    assert mutant == Mutant(
        kind="compare",
        line=2,
        description="q <= 0 → q < 0",
        source=mutant.source,
    )


# ---- 既定のテストのディレクトリ ----


def test_既定のテストは対象と同じ章のディレクトリ() -> None:
    assert default_test_dir("lib/chapter05/cost.py") == "test/chapter05"


def test_章のないファイルは既定のテストを決められない() -> None:
    with pytest.raises(MutationError):
        default_test_dir("lib/util.py")


# ---- 報告の書式 ----


def test_報告は総数と生き残りの一覧と等価のヒントを示す() -> None:
    mutant = Mutant("compare", 2, "x > 0 → x >= 0", "")
    report = Report(total=5, survivors=[Survivor("lib/chapter01/s.py", mutant)])
    text = format_report(report)
    assert "変異: 5" in text
    assert "生き残り: 1" in text
    assert "lib/chapter01/s.py:2 compare x > 0 → x >= 0" in text
    assert "ヒント" in text


# ---- run: 合成プロジェクトでの実行 ----

SAMPLE = '''\
"""合成の対象。"""


def is_positive(x: float) -> bool:
    return x > 0
'''

WEAK_TEST = """\
from lib.chapter01.sample import is_positive


def test_is_positive() -> None:
    assert is_positive(5) is True
    assert is_positive(-5) is False
"""

STRONG_TEST = (
    WEAK_TEST
    + """

def test_境界() -> None:
    assert is_positive(0) is False
    assert is_positive(0.5) is True
"""
)


def _project(root: Path, test_source: str) -> Path:
    (root / "lib" / "chapter01").mkdir(parents=True)
    (root / "test" / "chapter01").mkdir(parents=True)
    (root / "lib" / "__init__.py").write_text("", encoding="utf-8")
    (root / "lib" / "chapter01" / "__init__.py").write_text("", encoding="utf-8")
    (root / "lib" / "chapter01" / "sample.py").write_text(SAMPLE, encoding="utf-8")
    (root / "test" / "__init__.py").write_text("", encoding="utf-8")
    (root / "test" / "chapter01" / "__init__.py").write_text("", encoding="utf-8")
    (root / "test" / "chapter01" / "test_sample.py").write_text(
        test_source, encoding="utf-8"
    )
    (root / "pyproject.toml").write_text(
        '[tool.pytest.ini_options]\npythonpath = ["."]\n', encoding="utf-8"
    )
    return root


def _snapshot(root: Path) -> dict[str, bytes]:
    return {
        str(p.relative_to(root)): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def test_弱いテストの変異は生き残りとして報告され本物は変わらず複製は消える(
    tmp_path: Path,
) -> None:
    app = _project(tmp_path / "app", WEAK_TEST)
    before = _snapshot(app)

    report = run(app, ["lib/chapter01/sample.py"], timeout=60)

    assert report.total == 3  # 比較・定数・戻り値
    assert sorted(s.mutant.kind for s in report.survivors) == ["compare", "const"]
    assert all(s.file == "lib/chapter01/sample.py" for s in report.survivors)
    assert _snapshot(app) == before
    assert report.workdir is not None and not report.workdir.exists()


def test_十分なテストなら全部が倒され_keepなら元に戻った複製が残る(
    tmp_path: Path,
) -> None:
    app = _project(tmp_path / "app", STRONG_TEST)

    report = run(app, ["lib/chapter01/sample.py"], timeout=60, keep=True)

    try:
        assert report.total == 3
        assert report.survivors == []
        assert report.workdir is not None
        copied = report.workdir / "lib" / "chapter01" / "sample.py"
        assert copied.read_text(encoding="utf-8") == SAMPLE
    finally:
        if report.workdir is not None:
            shutil.rmtree(report.workdir, ignore_errors=True)


def test_変異の前からテストが落ちるなら止める(tmp_path: Path) -> None:
    app = _project(tmp_path / "app", "def test_x() -> None:\n    assert False\n")
    with pytest.raises(MutationError):
        run(app, ["lib/chapter01/sample.py"], timeout=60)
