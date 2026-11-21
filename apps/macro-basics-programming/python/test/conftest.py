"""テスト全体の設定。

Matplotlib のバックエンドを、画面を使わない Agg に固定する。固定しないと、環境によって
Tk が選ばれ、図のテストが、まれに `TclError`（tk.tcl が見つからない）で落ちる。
"""

import matplotlib

matplotlib.use("Agg")
