from prompt_toolkit.shortcuts import input_dialog

from src.dialog import PROMPT_TOOLKIT_DIALOG_TITLE
from src.settings import save_settings, settings
from src.validator import IntValidator


def main():
    _download_max_threads = input_dialog(
        PROMPT_TOOLKIT_DIALOG_TITLE,
        '请输入要设置的线程数\n不建议设置的过高, 可能会导致占用内存过大',
        '确认',
        '返回',
        validator=IntValidator(),
        default=settings['download_max_threads'],
    ).run()
    if not _download_max_threads:
        return
    settings['download_max_threads'] = _download_max_threads
    save_settings()


__all__ = ['main']
