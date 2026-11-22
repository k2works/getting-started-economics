// 連載のノートブックを JupyterLab で起動する。
//
// 使い方: node ops/scripts/notebook.js <連載のディレクトリ名>
//
// 通常はトークン認証つきで起動する。Codespaces（環境変数 CODESPACES=true）では、
// ポートの転送が GitHub のログインで守られるので、トークンを無効にする。
// そのため、Codespaces のポート 8888 を Public にしてはいけない。
import { spawn } from 'node:child_process';

const series = process.argv[2];
if (!series) {
  console.error('使い方: node ops/scripts/notebook.js <連載のディレクトリ名>');
  process.exit(2);
}

const args = [
  'run', '--directory', `apps/${series}/python`, '--with', 'jupyterlab',
  'jupyter', 'lab', '--notebook-dir', 'notebooks', '--no-browser',
  '--ServerApp.port=8888',
];

if (process.env.CODESPACES === 'true') {
  args.push(
    '--ServerApp.ip=127.0.0.1',
    '--ServerApp.allow_remote_access=True',
    '--IdentityProvider.token=',
    '--ServerApp.password=',
  );
}

const child = spawn('uv', args, { stdio: 'inherit', shell: process.platform === 'win32' });
child.on('exit', (code) => process.exit(code ?? 0));
