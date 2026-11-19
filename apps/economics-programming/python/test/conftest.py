"""テスト全体の設定。画面を開かずに図を描くため、matplotlib のバックエンドを Agg にする。"""

import matplotlib

matplotlib.use("Agg")
