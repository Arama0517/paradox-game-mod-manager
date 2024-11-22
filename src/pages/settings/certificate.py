from prompt_toolkit.shortcuts import input_dialog, radiolist_dialog

from src.settings import save_settings, settings
from src.utils import PROMPT_TOOLKIT_DIALOG_TITLE
from src.validator import CertificatePathValidator


def main():
    ssl = radiolist_dialog(
        PROMPT_TOOLKIT_DIALOG_TITLE,
        '请选择一个选项',
        '确认',
        '返回',
        [
            (True, '启用证书验证'),
            ('path', '启用证书验证并设置本地证书路径'),
            (False, '禁用证书验证'),
        ],
        settings['ssl'] if isinstance(settings['ssl'], bool) else 'path',
    ).run()
    if isinstance(ssl, bool):
        settings['ssl'] = ssl
    elif ssl == 'path':
        certificate_path = input_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE,
            '请输入证书路径',
            validator=CertificatePathValidator(),
            default=settings['ssl'] if ssl == 'path' else '',
        ).run()
        settings['ssl'] = certificate_path
    else:
        return

    save_settings()


__all__ = ['main']
