import json

from .path import LAUNCHER_SETTINGS_FILE_PATH

__all__ = ['settings', 'save_settings']


with LAUNCHER_SETTINGS_FILE_PATH.open('r', encoding='utf-8') as f:
    settings = json.load(f)


def save_settings():
    with LAUNCHER_SETTINGS_FILE_PATH.open('w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)
