import json
import os
import re
import subprocess
from pathlib import Path

import tomli


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

params = {}
for key, value in data['tool']['nuitka'].items():
    result = value
    if isinstance(value, list):
        result = '\n'.join(value)
    elif isinstance(value, dict):
        result = '\n'.join(f'{k}={v}' for k, v in value.items())
    elif isinstance(value, bool):
        result = str(value).lower()

    params[key] = replace_placeholders(result, data)


env = os.environ.copy()
env['NUITKA_WORKFLOW_INPUTS'] = json.dumps(params)
subprocess.check_call(['nuitka', '--github-workflow-options'], env=env, shell=True)
