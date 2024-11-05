from pathlib import Path

import tomli
from lib_not_dr.nuitka import nuitka_config_type, raw_config_type


def main(raw_config: raw_config_type) -> nuitka_config_type:
    config: nuitka_config_type = raw_config['cli']  # type: ignore
    with (Path().cwd() / 'pyproject.toml').open('rb') as f:
        project = tomli.load(f)['project']
    config['product-version'] = project['version']
    config['file-version'] = project['version']
    config['output-filename'] = f'{project["name"]}.exe'
    config['file-description'] = project['description']
    config['product-name'] = project['name']
    return config
