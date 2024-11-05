import winreg
from pathlib import Path

CURRENT_DIR_PATH = Path.cwd()

# 启动器配置文件
LAUNCHER_SETTINGS_FILE_PATH = CURRENT_DIR_PATH / 'launcher-settings.json'


DATA_DIR_PATH = None
MOD_BOOT_FILES_PATH = None
MODS_DIR_PATH = CURRENT_DIR_PATH / 'mods'


def initialize_data_dir(settings: dict):
    global DATA_DIR_PATH, MOD_BOOT_FILES_PATH
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders',
    ) as reg_key:
        documents_path = winreg.QueryValueEx(reg_key, 'Personal')[0]

    DATA_DIR_PATH = Path(
        settings['gameDataPath'].replace('%USER_DOCUMENTS%', documents_path)
    )
    MOD_BOOT_FILES_PATH = DATA_DIR_PATH / 'mod'


__all__ = [
    'CURRENT_DIR_PATH',
    'DATA_DIR_PATH',
    'MODS_DIR_PATH',
    'MOD_BOOT_FILES_PATH',
    'LAUNCHER_SETTINGS_FILE_PATH',
    'initialize_data_dir',
]
