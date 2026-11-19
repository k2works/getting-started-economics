"""記事の「実際のデータで試す」のスクリプトを実行し、記事の出力と照合する。

第 6・10・13・16 章のスクリプトは、読者が `practice/` に保存して実行する。`practice/` は
Git の管理外なので、`lib/` の関数を変えても、壊れたことに気づけない。
そこで、記事のスクリプトを取り出して実行し、出力の数値が記事と一致するかを調べる。

実データの `wooldridge` が要るので、任意の依存グループ `realdata` を入れて実行する。

    uv run --group realdata python -m article_tools.check_realdata
"""

import math
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

# 対象のシリーズ（apps/<名前>/python/）。実行する場所か、環境変数で決める
APP_DIR = Path(os.environ.get("ARTICLE_APP_DIR", Path.cwd())).resolve()
# シリーズ固有のデータ（図の登録・抜粋・指紋など）は、シリーズの tools/ に置く
TOOLS_DIR = APP_DIR / "tools"
SERIES = APP_DIR.parent.name
DOCS_DIR = APP_DIR.parents[2] / "docs" / "article" / SERIES

# 「次のスクリプトを `practice/chapter06/wage1.py` として保存し」と、
# そのあとの 2 つのコードブロック（スクリプトと、その出力）
_SCRIPT = re.compile(
    r"次のスクリプトを[、]?\s*`practice/(chapter\d{2}/\w+)\.py` として保存.*?\n"
    r"```python\n(.*?)```\n.*?```text\n(.*?)```",
    re.S,
)
_NUMBER = re.compile(r"-?\d+(?:\.\d+)?(?:e[-+]?\d+)?")
# 小数 2〜4 桁に丸めた値の、最後の桁のずれ（プラットフォーム差）を許す
_REL_TOL = 1e-3
_ABS_TOL = 2e-4


@dataclass(frozen=True)
class RealdataScript:
    name: str
    script: str
    expected: str


def extract_realdata_scripts(markdown: str) -> list[RealdataScript]:
    """記事から、実データのスクリプトと、その出力（記事に載せた値）を取り出す。"""
    return [
        RealdataScript(m.group(1), m.group(2), m.group(3))
        for m in _SCRIPT.finditer(markdown)
    ]


def compare_outputs(expected: str, actual: str) -> list[str]:
    """出力を行ごとに比べる。数値は許容誤差の範囲で一致すればよい。"""
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
        for x, y in zip(_NUMBER.findall(a), _NUMBER.findall(b), strict=True):
            if not math.isclose(float(x), float(y), rel_tol=_REL_TOL, abs_tol=_ABS_TOL):
                problems.append(f"{number}行目の数値が違う: 記事 {x} / 実行結果 {y}")
    return problems


def run_script(script: str, app_dir: Path) -> str:
    """スクリプトを、アプリの根を import できる状態で実行して、標準出力を返す。"""
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "script.py"
        path.write_text(script, encoding="utf-8")
        env = {
            **os.environ,
            "PYTHONPATH": str(app_dir),
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8",
        }
        result = subprocess.run(
            [sys.executable, str(path)],
            cwd=app_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            check=False,
        )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip().splitlines()[-1])
    return result.stdout


def check_realdata() -> list[str]:
    """記事の実データのスクリプトを実行し、記事の出力と一致するかを調べる。"""
    problems = []
    found = 0
    for path in sorted(DOCS_DIR.glob("[0-9][0-9]-*.md")):
        text = path.read_text(encoding="utf-8")
        for item in extract_realdata_scripts(text):
            found += 1
            try:
                actual = run_script(item.script, APP_DIR)
            except RuntimeError as error:
                problems.append(f"{path.name} {item.name}: 実行に失敗: {error}")
                continue
            problems.extend(
                f"{path.name} {item.name}: {problem}"
                for problem in compare_outputs(item.expected, actual)
            )
    if found == 0:
        problems.append("実データのスクリプトが 1 本も見つからない")
    return problems


def main() -> int:
    problems = check_realdata()
    print(f"{'NG' if problems else 'OK'}  実データのスクリプトの実行と出力の照合")
    for problem in problems:
        print(f"    {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
