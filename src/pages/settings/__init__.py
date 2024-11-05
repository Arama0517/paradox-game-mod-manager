from prompt_toolkit.shortcuts import radiolist_dialog

from src.pages.settings import certificate, max_chunk_size, max_threads, users
from src.utils import PROMPT_TOOLKIT_DIALOG_TITLE

__all__ = ['main']


def main():
    options = [
        ('users', 'steam账号'),
        ('max_threads', '一些异步操作时多线程的数量'),
        ('max_chunk_size', '下载时切片的大小'),
        ('certificate', '证书验证'),
    ]
    while True:
        match radiolist_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE, '请选择要配置的选项', '确认', '返回', options
        ).run():
            case 'users':
                users.main()
            case 'max_threads':
                max_threads.main()
            case 'max_chunk_size':
                max_chunk_size.main()
            case 'certificate':
                certificate.main()
            case _:
                return
