from collections.abc import Callable

from prompt_toolkit.shortcuts import radiolist_dialog

from src.pages.settings import certificate, max_chunk_size, max_tasks_num, users
from src.utils import PROMPT_TOOLKIT_DIALOG_TITLE

__all__ = ['main']


def main():
    while True:
        func: Callable[[], None] = radiolist_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE,
            '请选择要配置的选项',
            '确认',
            '返回',
            [
                (users.main, 'steam账号'),
                (max_tasks_num.main, '异步操作时最大的任务数'),
                (max_chunk_size.main, '下载时切片的大小'),
                (certificate.main, '证书验证'),
            ],
        ).run()
        if not func:
            break
        func()
