from prompt_toolkit.shortcuts import radiolist_dialog

from src.dialog import PROMPT_TOOLKIT_DIALOG_TITLE
from src.pages.settings import certificate, download_max_threads, max_chunk_size, users

__all__ = ['main']


def main():
    options = [
        ('users', 'steam账号'),
        ('download_max_threads', '下载时使用线程的最大数量'),
        ('max_chunk_size', '下载时切片的大小'),
        ('certificate', '证书验证'),
    ]
    while True:
        match radiolist_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE, '请选择要配置的选项', '确认', '返回', options
        ).run():
            case 'users':
                users.main()
            case 'download_max_threads':
                download_max_threads.main()
            case 'max_chunk_size':
                max_chunk_size.main()
            case 'certificate':
                certificate.main()
            case _:
                return
