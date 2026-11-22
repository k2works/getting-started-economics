"""実装の変異確認: 演算子・定数などを 1 か所ずつ書き換え、テストが落ちるかを見る。

生き残った変異は、テストが、その書き換えを見分けられない箇所
（テストの穴か、等価な変異）。本物のリポジトリは書き換えない。
`lib`・`test` などを一時ディレクトリに複製して、その中で変異させる。

    cd apps/<連載>/python
    uv run python -m article_tools.mutate lib/chapter05/cost.py [...]

既定では、対象と同じ章のテスト（`test/chapterNN`）だけを流す。
`--tests` で、ディレクトリを指定し、`--all-tests` で、全テストを流す。
生き残りがあっても、終了コードは 0（情報提供のため）。
"""

import argparse
import ast
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

# 複製する、連載のディレクトリ・ファイル（無いものは飛ばす）。
# data・notebooks は、それを読むテストのため
COPIED = ("lib", "test", "tools", "data", "notebooks", "pyproject.toml", "conftest.py")
# 複製に古い .pyc が混ざると、変異前のコードが動く
# （同じ長さの書き換えが、同じ秒に続くと起きる）
IGNORED = shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache")

_ARITH: dict[type[ast.operator], type[ast.operator]] = {
    ast.Add: ast.Sub,
    ast.Sub: ast.Add,
    ast.Mult: ast.Div,
    ast.Div: ast.Mult,
    ast.Pow: ast.Mult,
    ast.FloorDiv: ast.Div,
    ast.Mod: ast.FloorDiv,
}
_COMPARE: dict[type[ast.cmpop], type[ast.cmpop]] = {
    ast.Lt: ast.LtE,
    ast.LtE: ast.Lt,
    ast.Gt: ast.GtE,
    ast.GtE: ast.Gt,
    ast.Eq: ast.NotEq,
    ast.NotEq: ast.Eq,
    ast.Is: ast.IsNot,
    ast.IsNot: ast.Is,
    ast.In: ast.NotIn,
    ast.NotIn: ast.In,
}
_BOOL: dict[type[ast.boolop], type[ast.boolop]] = {ast.And: ast.Or, ast.Or: ast.And}
_MAXMIN = {"max": "min", "min": "max"}

# 生き残ったときに、等価な変異（テストの穴ではない）を疑う手がかり
HINTS = {
    "compare": "等号の有無（< と <=）は、連続な量で境界の値ちょうどに"
    "当たらないと、等価になりやすい。境界の値のテストを足すか、"
    "等価なら理由を記録する",
    "const": "許容誤差・反復の上限・刻み幅・表示の桁などの定数は、"
    "少し変えても結果が変わらず、等価になりやすい",
    "maxmin": "候補が 1 つに決まる場面（要素が 1 つ・default だけ）では、"
    "max と min は等価",
    "arith": "0・1 との演算（x * 1 と x / 1、x + 0 と x - 0）や、"
    "2 ** 2 と 2 * 2 は等価",
    "abs": "引数が常に非負なら、abs の除去は等価",
    "neg": "0 の符号の反転や、2 乗される値の符号の反転は等価",
    "bool": "両辺が常に同じ真偽になる場面では、and と or は等価",
    "not": "not の除去が等価になることは少ない。テストの穴を疑う",
    "true_false": "既定の引数の真偽値なら、テストがその引数を渡していない可能性がある",
    "return": "戻り値を使わない関数（検証して例外を投げるだけ）では、"
    "return None は等価",
}

_Key = tuple[str, int, int, int, int]


@dataclass(frozen=True)
class Mutant:
    """1 か所だけ書き換えた変異。source は、書き換えた後のソース全体。"""

    kind: str
    line: int
    description: str
    source: str


@dataclass(frozen=True)
class Survivor:
    file: str
    mutant: Mutant


@dataclass
class Report:
    total: int
    survivors: list[Survivor] = field(default_factory=list)
    timeouts: int = 0
    seconds: float = 0.0
    workdir: Path | None = None


class MutationError(Exception):
    """変異確認を始められない（対象・テストのディレクトリが無い、変異の前からテストが落ちる）。"""


# ---- 変異の生成（純粋関数） ----


def _key(node: ast.AST) -> _Key:
    """ノードの型と、始まり・終わりの位置。入れ子の演算の内側と外側を、終わりの位置で見分ける。"""
    return (
        type(node).__name__,
        getattr(node, "lineno", -1),
        getattr(node, "col_offset", -1),
        getattr(node, "end_lineno", -1),
        getattr(node, "end_col_offset", -1),
    )


def _excluded(tree: ast.Module) -> set[int]:
    """変異させない部分木（docstring・型注釈・__all__）に含まれるノードの id。"""
    roots = [
        root
        for node in ast.walk(tree)
        for root in (*_annotations(node), *_all_values(node), *_docstring(node))
        if root is not None
    ]
    return {id(n) for root in roots for n in ast.walk(root)}


def _annotations(node: ast.AST) -> list[ast.AST | None]:
    if isinstance(node, ast.arg):
        return [node.annotation]
    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
        return [node.returns]
    if isinstance(node, ast.AnnAssign):
        return [node.annotation]
    if isinstance(node, ast.TypeAlias):
        return [node]
    return []


def _all_values(node: ast.AST) -> list[ast.AST | None]:
    """`__all__ = [...]` の右辺（名前の文字列の並び）。"""
    targets: list[ast.expr]
    value: ast.expr | None
    if isinstance(node, ast.Assign):
        targets, value = node.targets, node.value
    elif isinstance(node, ast.AnnAssign | ast.AugAssign):
        targets, value = [node.target], node.value
    else:
        return []
    named = any(isinstance(t, ast.Name) and t.id == "__all__" for t in targets)
    return [value] if named else []


def _docstring(node: ast.AST) -> list[ast.AST | None]:
    scopes = ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef
    if not isinstance(node, scopes) or not node.body:
        return []
    first = node.body[0]
    if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
        return [first] if isinstance(first.value.value, str) else []
    return []


def _new_constant(value: object) -> object | None:
    """定数の変異後の値。値が変わらない（無限大の 1.5 倍など）なら None。"""
    new: object
    if isinstance(value, bool):
        new = not value
    elif isinstance(value, int):
        new = 1 if value == 0 else value + 1
    elif isinstance(value, float):
        new = 1.0 if value == 0 else value * 1.5
    else:
        return None
    return None if new == value or new != new else new


# 書き換える関数。新しく解析し直した木の、同じ位置のノードを受け取る
_Edit = Callable[[ast.AST], ast.AST]


def _sites(tree: ast.Module) -> list[tuple[str, ast.AST, _Edit]]:
    skip = _excluded(tree)
    sites: list[tuple[str, ast.AST, _Edit]] = []
    for node in ast.walk(tree):
        if id(node) in skip:
            continue
        for kind, edit in _edits(node):
            sites.append((kind, node, edit))
    sites.sort(key=lambda s: (_key(s[1])[1], _key(s[1])[2], _key(s[1])[3:]))
    return sites


def _edits(node: ast.AST) -> list[tuple[str, _Edit]]:  # noqa: C901 （種類の一覧）
    if isinstance(node, ast.BinOp) and type(node.op) in _ARITH:
        swapped = _ARITH[type(node.op)]
        return [("arith", lambda n: _set(n, "op", swapped()))]
    if isinstance(node, ast.Compare):
        return [
            ("compare", _swap_compare(i, _COMPARE[type(op)]))
            for i, op in enumerate(node.ops)
            if type(op) in _COMPARE
        ]
    if isinstance(node, ast.BoolOp):
        other = _BOOL[type(node.op)]
        return [("bool", lambda n: _set(n, "op", other()))]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return [("not", lambda n: _operand(n))]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return [("neg", lambda n: _operand(n))]
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        name = node.func.id
        if name == "abs" and len(node.args) == 1 and not node.keywords:
            return [("abs", lambda n: _first_arg(n))]
        if name in _MAXMIN:
            return [("maxmin", lambda n: _rename_call(n, _MAXMIN[name]))]
    if isinstance(node, ast.Constant):
        new = _new_constant(node.value)
        if new is not None:
            kind = "true_false" if isinstance(node.value, bool) else "const"
            return [(kind, lambda n: _set(n, "value", new))]
    if isinstance(node, ast.Return) and node.value is not None:
        value = node.value
        if not (isinstance(value, ast.Constant) and value.value is None):
            return [("return", lambda n: _set(n, "value", ast.Constant(None)))]
    return []


def _set(node: ast.AST, name: str, value: object) -> ast.AST:
    setattr(node, name, value)
    return node


def _swap_compare(index: int, swapped: type[ast.cmpop]) -> _Edit:
    def edit(node: ast.AST) -> ast.AST:
        assert isinstance(node, ast.Compare)
        node.ops[index] = swapped()
        return node

    return edit


def _operand(node: ast.AST) -> ast.AST:
    assert isinstance(node, ast.UnaryOp)
    return node.operand


def _first_arg(node: ast.AST) -> ast.AST:
    assert isinstance(node, ast.Call)
    return node.args[0]


def _rename_call(node: ast.AST, name: str) -> ast.AST:
    assert isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    node.func.id = name
    return node


class _Replace(ast.NodeTransformer):
    """位置（始まりと終わり）と型が一致するノードを 1 つだけ書き換える。"""

    def __init__(self, key: _Key, edit: _Edit) -> None:
        self.key = key
        self.edit = edit
        self.replaced: ast.AST | None = None

    def visit(self, node: ast.AST) -> ast.AST:
        if self.replaced is None and _key(node) == self.key:
            self.replaced = self.edit(node)
            return self.replaced
        result: ast.AST = super().visit(node)
        return result


def _one_line(text: str) -> str:
    return " ".join(text.split())


def generate_mutants(source: str) -> list[Mutant]:
    """ソースから、1 か所ずつ書き換えた変異を、位置の順に作る。"""
    tree = ast.parse(source)
    mutants = []
    for kind, node, edit in _sites(tree):
        before = ast.get_source_segment(source, node) or ast.unparse(node)
        replacer = _Replace(_key(node), edit)
        mutated = ast.fix_missing_locations(replacer.visit(ast.parse(source)))
        if replacer.replaced is None:
            continue
        after = ast.unparse(replacer.replaced)
        mutants.append(
            Mutant(
                kind=kind,
                line=_key(node)[1],
                description=f"{_one_line(before)} → {_one_line(after)}",
                source=ast.unparse(mutated),
            )
        )
    return mutants


# ---- 実行（複製の中で） ----

_CHAPTER = re.compile(r"^lib/(chapter\d+)/[^/]+\.py$")


def default_test_dir(target: str) -> str:
    """対象（lib/chapterNN/x.py）と同じ章のテストのディレクトリ。"""
    match = _CHAPTER.match(target)
    if match is None:
        raise MutationError(
            f"{target}: 章のディレクトリにないので、--tests でテストを指定してください"
        )
    return f"test/{match.group(1)}"


def _copy_app(app_dir: Path) -> Path:
    workdir = Path(tempfile.mkdtemp(prefix="mutate-"))
    for name in COPIED:
        src = app_dir / name
        if src.is_dir():
            shutil.copytree(src, workdir / name, ignore=IGNORED)
        elif src.is_file():
            shutil.copy2(src, workdir / name)
    return workdir


def _passes(workdir: Path, test_dir: str, timeout: float) -> bool:
    """テストが全部通れば True。時間切れは、変異を倒した（False）とみなす。"""
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    command = [sys.executable, "-m", "pytest", test_dir, "-q", "-x"]
    command += ["-p", "no:cacheprovider"]
    result = subprocess.run(
        command,
        cwd=workdir,
        env=env,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    return result.returncode == 0


def _relative(app_dir: Path, target: str) -> str:
    path = Path(target)
    if path.is_absolute():
        try:
            path = path.resolve().relative_to(app_dir.resolve())
        except ValueError as error:
            raise MutationError(f"{target}: 連載のディレクトリの外です") from error
    rel = path.as_posix()
    if not (app_dir / rel).is_file():
        raise MutationError(f"{target}: ファイルがありません")
    return rel


def run(
    app_dir: Path,
    targets: Sequence[str],
    *,
    tests: str | None = None,
    all_tests: bool = False,
    timeout: float = 60,
    keep: bool = False,
    progress: Callable[[str], None] | None = None,
) -> Report:
    """対象のファイルの変異を、複製の中で 1 つずつテストし、生き残りを報告する。"""
    started = time.monotonic()
    files = [_relative(app_dir, t) for t in targets]
    plan = [(f, "test" if all_tests else tests or default_test_dir(f)) for f in files]
    for _, test_dir in plan:
        if not (app_dir / test_dir).is_dir():
            raise MutationError(f"{test_dir}: テストのディレクトリがありません")

    workdir = _copy_app(app_dir)
    report = Report(total=0, workdir=workdir)
    try:
        for test_dir in dict.fromkeys(t for _, t in plan):
            if not _safe_passes(workdir, test_dir, timeout):
                raise MutationError(f"{test_dir}: 変異の前から、テストが通りません")
        for rel, test_dir in plan:
            _mutate_file(workdir, rel, test_dir, timeout, report, progress)
    finally:
        if not keep:
            shutil.rmtree(workdir, ignore_errors=True)
        report.seconds = time.monotonic() - started
    return report


def _safe_passes(workdir: Path, test_dir: str, timeout: float) -> bool:
    try:
        return _passes(workdir, test_dir, timeout)
    except subprocess.TimeoutExpired:
        return False


def _mutate_file(
    workdir: Path,
    rel: str,
    test_dir: str,
    timeout: float,
    report: Report,
    progress: Callable[[str], None] | None,
) -> None:
    path = workdir / rel
    original = path.read_bytes()
    mutants = generate_mutants(original.decode("utf-8").replace("\r\n", "\n"))
    for index, mutant in enumerate(mutants, start=1):
        path.write_text(mutant.source, encoding="utf-8")
        try:
            survived = _passes(workdir, test_dir, timeout)
        except subprocess.TimeoutExpired:
            survived = False
            report.timeouts += 1
        finally:
            path.write_bytes(original)
        report.total += 1
        if survived:
            report.survivors.append(Survivor(rel, mutant))
        if progress is not None:
            mark = "生き残り" if survived else "倒した"
            progress(f"[{index}/{len(mutants)}] {rel}:{mutant.line} {mark}")


# ---- 報告と CLI ----


def format_report(report: Report) -> str:
    killed = report.total - len(report.survivors)
    lines = [
        f"変異: {report.total}（倒した: {killed}、うち時間切れ: {report.timeouts}）"
        f"  生き残り: {len(report.survivors)}  所要: {report.seconds:.1f} 秒"
    ]
    if report.survivors:
        lines.append("生き残り:")
        lines += [
            f"  {s.file}:{s.mutant.line} {s.mutant.kind} {s.mutant.description}"
            for s in report.survivors
        ]
        kinds = dict.fromkeys(s.mutant.kind for s in report.survivors)
        lines.append("ヒント（等価な変異の可能性）:")
        lines += [f"  - {kind}: {HINTS[kind]}" for kind in kinds if kind in HINTS]
    if report.workdir is not None and report.workdir.exists():
        lines.append(f"複製: {report.workdir}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m article_tools.mutate", description=__doc__.splitlines()[0]
    )
    parser.add_argument("files", nargs="+", help="変異させる lib のファイル")
    parser.add_argument("--tests", help="流すテストのディレクトリ（既定: 同じ章）")
    parser.add_argument("--all-tests", action="store_true", help="全テストを流す")
    parser.add_argument(
        "--timeout", type=float, default=60, help="1 回のテストの上限（秒）"
    )
    parser.add_argument("--keep", action="store_true", help="複製を残す")
    args = parser.parse_args(argv)
    app_dir = Path(os.environ.get("ARTICLE_APP_DIR", Path.cwd())).resolve()
    try:
        report = run(
            app_dir,
            args.files,
            tests=args.tests,
            all_tests=args.all_tests,
            timeout=args.timeout,
            keep=args.keep,
            progress=lambda line: print(line, file=sys.stderr, flush=True),
        )
    except MutationError as error:
        print(f"エラー: {error}", file=sys.stderr)
        return 2
    print(format_report(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
