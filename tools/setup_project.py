import json

from src.path import LAUNCHER_SETTINGS_FILE_PATH

DATA = {
    'gameId': 'hoi4',
    'gameDataPath': '%USER_DOCUMENTS%/Paradox Interactive/Hearts of Iron IV',
}

if not LAUNCHER_SETTINGS_FILE_PATH.exists():
    with LAUNCHER_SETTINGS_FILE_PATH.open('w', encoding='utf-8') as f:
        json.dump(DATA, f, indent=4, sort_keys=True)
