# Jupyter Server のシステム設定（/etc/jupyter/jupyter_server_config.py に置かれる）。
#
# Codespaces（環境変数 CODESPACES=true）では、「Open in JupyterLab」で起動するサーバーを
# トークンなしにする。ポートの転送が GitHub のログインで守られるため。
# そのため、Codespaces のポート 8888 を Public にしてはいけない。
import os

if os.environ.get("CODESPACES") == "true":
    c.IdentityProvider.token = ""  # noqa: F821
    c.ServerApp.password = ""  # noqa: F821
    c.ServerApp.allow_remote_access = True  # noqa: F821
