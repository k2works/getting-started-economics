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
    # 「Open in JupyterLab」は、GitHub のページが JupyterLab を iframe で埋め込む。
    # Jupyter の既定（frame-ancestors 'self'）だと、埋め込みがブロックされる。
    c.ServerApp.tornado_settings = {  # noqa: F821
        "headers": {
            "Content-Security-Policy": (
                "frame-ancestors 'self' https://*.github.dev https://*.github.com "
                "https://github.com https://*.githubpreview.dev"
            )
        }
    }
