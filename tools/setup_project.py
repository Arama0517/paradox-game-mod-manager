import json
from pathlib import Path

LAUNCHER_SETTINGS_FILE_PATH = Path.cwd() / 'launcher-settings.json'
DATA = {
    'gameId': 'hoi4',
    'gameDataPath': '%USER_DOCUMENTS%/Paradox Interactive/Hearts of Iron IV',
}

if not LAUNCHER_SETTINGS_FILE_PATH.exists():
    with LAUNCHER_SETTINGS_FILE_PATH.open('w', encoding='utf-8') as f:
        json.dump(DATA, f, indent=4)
