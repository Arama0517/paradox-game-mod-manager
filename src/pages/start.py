import re
import subprocess
from pathlib import Path

from loguru import logger

from src.path import CURRENT_DIR_PATH, MOD_BOOT_FILES_PATH, MODS_DIR_PATH

_PATH_REGEX = r'(?:^|[^a-zA-Z_])path\s*=\s*"([^"]+)"'


def main():
    for file in MOD_BOOT_FILES_PATH.iterdir():
        if file.suffix != '.mod':
            continue
        with file.open('r', encoding='utf-8') as f:
            data = f.read()
        result = re.search(_PATH_REGEX, data, flags=0)

        # 没有找到path字段
        if not result:
            logger.info(f'删除无效定位文件: {file}')
            file.unlink()
            continue

        mod_path = Path(result.group(1))
        # mod源目录不存在
        if not mod_path.exists():
            logger.info(f'删除无效定位文件: {file}')
            file.unlink()
            continue

    # 生成mod定位文件
    for mod in MODS_DIR_PATH.iterdir():
        mod_boot_file_path = MOD_BOOT_FILES_PATH / f'{mod.name}.mod'

        mod_decsriptor_file_path = Path('$')
        for f in mod.iterdir():
            if f.suffix == '.mod':
                mod_decsriptor_file_path = f
                break

        # 没有找到描述文件, 可能不是mod
        if not mod_decsriptor_file_path.exists():
            continue

        if not mod_boot_file_path.exists():
            with mod_boot_file_path.open('w', encoding='utf-8') as f:
                data = mod_decsriptor_file_path.read_text(encoding='utf-8')
                result = re.compile(_PATH_REGEX).sub(f'path="{mod.as_posix()}"', data)
                # 有些模组会在描述文件里自带path, 这里覆盖一下
                if result != data:
                    f.write(result)
                else:
                    # 没有自带的情况
                    f.write(data)
                    f.write(f'\npath="{mod.as_posix()}"')

    subprocess.check_call(CURRENT_DIR_PATH / 'dowser.exe')


__all__ = ['main']
