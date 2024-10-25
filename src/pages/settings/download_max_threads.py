from prompt_toolkit.document import Document
from prompt_toolkit.shortcuts import input_dialog
from prompt_toolkit.validation import ValidationError, Validator

from src.dialog import PROMPT_TOOLKIT_DIALOG_TITLE
from src.settings import save_settings, settings

__all__ = ['main']


class _DownloadThreadsValidator(Validator):
    def validate(self, document: Document) -> None:
        if not document.text:
            raise ValidationError(message='不能为空')
        if not document.text.isdigit() and int(document.text) <= 0:
            raise ValidationError(message='请输入一个有效的数字')


def main():
    _download_max_threads = input_dialog(
        PROMPT_TOOLKIT_DIALOG_TITLE,
        '请输入要设置的线程数\n不建议设置的过高, 可能会导致占用内存过大',
        '确认',
        '返回',
        validator=_DownloadThreadsValidator(),
        default=settings['download_max_threads'],
    ).run()
    if not _download_max_threads:
        return
    settings['download_max_threads'] = _download_max_threads
    save_settings()
