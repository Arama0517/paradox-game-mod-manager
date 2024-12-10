import re
import subprocess
from pathlib import Path
from re import Pattern

import aiofiles

from src.path import CURRENT_DIR_PATH, MOD_BOOT_FILES_PATH, MODS_DIR_PATH


def get_pattern(field: str) -> Pattern[str]:
    return re.compile(rf'(?:^|[^a-zA-Z_]){field}\s*=\s*"([^"]+)"')


async def main():
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

    for mod_path in MODS_DIR_PATH.iterdir():
        mod_boot_file_path = MOD_BOOT_FILES_PATH / f'ugc_{mod_path.name}.mod'

        mod_descriptor_file_path: None | Path = None
        for f in mod_path.iterdir():
            if f.suffix == '.mod':
                mod_descriptor_file_path = f
                break

        # 没有找到描述文件, 可能不是模组
        if mod_descriptor_file_path is None:
            continue

        mod_picture_file_path: None | Path = None
        for f in mod_path.iterdir():
            if f.stem == 'thumbnail' or f.suffix in ['.png', '.jpg', '.jpeg']:
                mod_picture_file_path = f
                break

        async with aiofiles.open(mod_descriptor_file_path, 'r', encoding='utf-8') as f:
            data = await f.read()

        async with aiofiles.open(mod_boot_file_path, 'w', encoding='utf-8') as f:
            # 有些模组会在描述文件里自带path, 这里覆盖一下
            result = get_pattern('path').sub(f'path="{mod_path.as_posix()}"', data)
            if result == data:
                # 没有自带的情况
                result = result + f'\npath="{mod_path.as_posix()}"'

            if mod_picture_file_path is not None and not get_pattern('picture').search(
                data
            ):
                result = result + f'\npicture="{mod_picture_file_path.name}"'
            await f.write(result)

    subprocess.check_call(CURRENT_DIR_PATH / 'dowser.exe')


__all__ = ['main']
