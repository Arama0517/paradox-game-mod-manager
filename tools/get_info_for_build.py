import json
from pathlib import Path

import tomli

with (Path().cwd() / 'pyproject.toml').open('rb') as f:
    print(json.dumps(tomli.load(f)))
