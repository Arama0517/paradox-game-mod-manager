from pathlib import Path

CURRENT_DIR_PATH = Path.cwd()
DATA_DIR_PATH = CURRENT_DIR_PATH / 'game_data'

MODS_DIR_PATH = CURRENT_DIR_PATH / 'mods'
MOD_BOOT_FILES_PATH = DATA_DIR_PATH / 'mod'

# 启动器配置文件
LAUNCHER_SETTINGS_FILE_PATH = CURRENT_DIR_PATH / 'launcher-settings.json'

__all__ = [
    'CURRENT_DIR_PATH',
    'DATA_DIR_PATH',
    'MODS_DIR_PATH',
    'MOD_BOOT_FILES_PATH',
    'LAUNCHER_SETTINGS_FILE_PATH',
]
