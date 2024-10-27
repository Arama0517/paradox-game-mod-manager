from prompt_toolkit.shortcuts import input_dialog

from src.dialog import PROMPT_TOOLKIT_DIALOG_TITLE
from src.settings import save_settings, settings
from src.validator import IntValidator

_TEXT = """请输入要设置的大小, 单位为字节
不建议设置的过小, 会导致写入速度过慢
"""


def main():
    _max_chunk_size = input_dialog(
        PROMPT_TOOLKIT_DIALOG_TITLE,
        _TEXT,
        '确认',
        '返回',
        validator=IntValidator(),
        default=str(settings['max_chunk_size']),
    ).run()
    if not _max_chunk_size and _max_chunk_size == settings['max_chunk_size']:
        return
    settings['max_chunk_size'] = _max_chunk_size
    save_settings()


__all__ = ['main']
