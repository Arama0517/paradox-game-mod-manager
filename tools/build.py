import subprocess
import sys
from pathlib import Path

import tomli

with (Path.cwd() / 'pyproject.toml').open('rb') as f:
    project = tomli.load(f)['project']

config = {
    'main': 'src/main.py',
    'output-dir': 'build',
    'output-filename': f'{project["name"]}.exe',
    # 编译选项
    'clang': True,
    'msvc': 'latest',
    'standalone': True,
    'onefile': True,
    # 文件信息
    'company-name': 'Arama',
    'copyright': 'Copyright ©Arama. All rights reserved.',
    'product-version': project['version'],
    'file-version': project['version'],
    'file-description': project['description'],
    'product-name': project['name'],
    # 依赖
    'include-package': ['steam'],
    'assume-yes-for-download': True,
}

args = []
for k, v in config.items():
    if isinstance(v, bool):
        if v:
            args.append(f'--{k}')
    elif isinstance(v, str):
        args.append(f'--{k}={v}')
    elif isinstance(v, list):
        args.append(f'--{k}={",".join(v)}')

subprocess.check_call(['nuitka'] + args + sys.argv[1:], shell=True)
