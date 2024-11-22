import json
from typing import TypedDict

from src.path import SETTINGS_FILE_PATH


class Mod(TypedDict):
    title: str
    time_updated: int


class User(TypedDict):
    password: str
    token: str
    user_name: str


class Settings(TypedDict):
    max_chunk_size: int
    max_tasks_num: int
    mods: dict[str, Mod]
    ssl: str | bool
    users: dict[str, User]


if not SETTINGS_FILE_PATH.exists():
    with SETTINGS_FILE_PATH.open('w', encoding='utf-8') as _f:
        json.dump({}, _f)


with SETTINGS_FILE_PATH.open('r', encoding='utf-8') as _f:
    settings: Settings = json.load(_f)


def save_settings():
    with SETTINGS_FILE_PATH.open('w', encoding='utf-8') as _f:
        json.dump(settings, _f, indent=4, ensure_ascii=False, sort_keys=True)


__all__ = ['settings', 'save_settings']
