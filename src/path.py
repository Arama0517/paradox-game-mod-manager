import json
import winreg
from pathlib import Path

CURRENT_DIR_PATH = Path.cwd()

# 配置文件
SETTINGS_FILE_PATH = CURRENT_DIR_PATH / 'pgmm-settings.json'
LAUNCHER_SETTINGS_FILE_PATH = CURRENT_DIR_PATH / 'launcher-settings.json'

with winreg.OpenKey(
    winreg.HKEY_CURRENT_USER,
    r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders',
) as reg_key:
    documents_path = winreg.QueryValueEx(reg_key, 'Personal')[0]

with LAUNCHER_SETTINGS_FILE_PATH.open('r', encoding='utf-8') as f:
    _settings = json.load(f)

DATA_DIR_PATH = Path(
    _settings['gameDataPath'].replace('%USER_DOCUMENTS%', documents_path)
)
MOD_BOOT_FILES_PATH = DATA_DIR_PATH / 'mod'
MODS_DIR_PATH = CURRENT_DIR_PATH / 'mods'


__all__ = [
    'CURRENT_DIR_PATH',
    'DATA_DIR_PATH',
    'MODS_DIR_PATH',
    'MOD_BOOT_FILES_PATH',
    'SETTINGS_FILE_PATH',
    'LAUNCHER_SETTINGS_FILE_PATH',
]
