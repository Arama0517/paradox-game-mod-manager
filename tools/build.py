import re
import sys
from pathlib import Path

import tomli
from PyInstaller.__main__ import run


def get_nested_value(data, keys):
    for key in keys:
        data = data[key]
    return data


def replace_placeholders(template, data):
    if not isinstance(template, str):
        return str(template)

    def replacer(match):
        placeholder = match.group(1)
        keys = placeholder.split('.')
        try:
            return str(get_nested_value(data, keys))
        except KeyError:
            return match.group(0)

    return re.sub(r'\{([^}]+)}', replacer, template)


with (Path.cwd() / 'pyproject.toml').open('rb') as f:
    data = tomli.load(f)

args = ['src/main.py'] + sys.argv[1:]
for key, value in data['tool']['pyinstaller'].items():
    if value is True:
        args.append(replace_placeholders(f'--{key}', data))
    elif isinstance(value, list):
        for v in value:
            args.append(replace_placeholders(f'--{key}={v}', data))
    else:
        args.append(replace_placeholders(f'--{key}={value}', data))

print(args)
run(args)
