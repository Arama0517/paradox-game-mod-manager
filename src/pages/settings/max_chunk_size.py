from prompt_toolkit.shortcuts import input_dialog

from src.settings import save_settings, settings
from src.utils import PROMPT_TOOLKIT_DIALOG_TITLE
from src.validator import IntValidator


def main():
    max_chunk_size = input_dialog(
        PROMPT_TOOLKIT_DIALOG_TITLE,
        '请输入要设置的大小, 单位为字节',
        '确认',
        '返回',
        validator=IntValidator(),
        default=str(settings['max_chunk_size']),
    ).run()
    if not max_chunk_size:
        return
    settings['max_chunk_size'] = int(max_chunk_size)
    save_settings()


__all__ = ['main']
