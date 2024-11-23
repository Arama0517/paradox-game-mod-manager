import re
import subprocess
import sys
from pathlib import Path
from re import Pattern

from src.path import CURRENT_DIR_PATH, MOD_BOOT_FILES_PATH, MODS_DIR_PATH


def get_pattern(field: str) -> Pattern[str]:
    return re.compile(rf'(?:^|[^a-zA-Z_]){field}\s*=\s*"([^"]+)"')


def main():
    for file in MOD_BOOT_FILES_PATH.iterdir():
        file: Path
        if not file.is_file() or file.suffix != '.mod':
            continue
        with file.open('r', encoding='utf-8') as f:
            data = f.read()
        replaced_mod_dir_path_data = get_pattern('path').search(data)

        if not replaced_mod_dir_path_data:
            file.unlink()
            continue

        replaced_mod_dir_path_data = Path(replaced_mod_dir_path_data.group(1))
        if not replaced_mod_dir_path_data.exists():
            file.unlink()
            continue

    for mod in MODS_DIR_PATH.iterdir():
        mod_boot_file_path = MOD_BOOT_FILES_PATH / f'{mod.name}.mod'

        mod_descriptor_file_path = Path('$')
        for f in mod.iterdir():
            if f.suffix == '.mod':
                mod_descriptor_file_path = f
                break

        # 没有找到描述文件, 可能不是模组
        if not mod_descriptor_file_path.exists():
            continue

        if not mod_boot_file_path.exists():
            with mod_boot_file_path.open('w', encoding='utf-8') as f:
                data = mod_descriptor_file_path.read_text(encoding='utf-8')
                replaced_mod_dir_path_data = get_pattern('path').sub(
                    f'path="{mod.as_posix()}"', data
                )
                # 有些模组会在描述文件里自带path, 这里覆盖一下
                if replaced_mod_dir_path_data != data:
                    f.write(replaced_mod_dir_path_data)
                else:
                    # 没有自带的情况
                    f.write(data)
                    f.write(f'\npath="{mod.as_posix()}"')

    subprocess.check_call(CURRENT_DIR_PATH / 'dowser.exe')
    sys.exit(0)


__all__ = ['main']
