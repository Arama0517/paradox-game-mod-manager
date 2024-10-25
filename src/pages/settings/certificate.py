from pathlib import Path

import requests
from prompt_toolkit.document import Document
from prompt_toolkit.shortcuts import input_dialog, radiolist_dialog
from prompt_toolkit.validation import ValidationError, Validator
from steam import webapi

from src.dialog import PROMPT_TOOLKIT_DIALOG_TITLE
from src.settings import save_settings, settings

__all__ = ['main', 'CertificatePathValidator']


class CertificatePathValidator(Validator):
    def validate(self, document: Document) -> None:
        if not document.text:
            raise ValidationError(message='不可为空')
        path = Path(document.text)
        if not path.exists():
            raise ValidationError(message='请输入一个真实存在的路径')
        if path.is_dir():
            raise ValidationError(message='请输入一个有效的证书')
        try:
            session = requests.Session()
            session.verify = path
            webapi.get('ISteamWebAPIUtil', 'GetServerInfo', session=session)
        except Exception as e:
            raise ValidationError(message=str(e))


def main():
    default: str
    match settings['ssl']:
        case True:
            default = 'enable'
        case False:
            default = 'disable'
        case _:
            default = 'enable_with_local_certificate'
    ssl = radiolist_dialog(
        PROMPT_TOOLKIT_DIALOG_TITLE,
        '请选择一个选项',
        '确认',
        '返回',
        [
            ('enable', '启用证书验证'),
            ('enable_with_local_certificate', '启用证书验证并设置本地证书路径'),
            ('disable', '禁用证书验证'),
        ],
        default,
    ).run()
    match ssl:
        case None:
            return
        case 'enable':
            settings['ssl'] = True
        case 'enable_with_local_certificate':
            certificate_path = input_dialog(
                PROMPT_TOOLKIT_DIALOG_TITLE,
                '请输入证书路径',
                validator=CertificatePathValidator(),
                default=default if default == ssl else '',  # 只在需要时提供默认值
            ).run()
            settings['ssl'] = certificate_path
        case 'disable':
            settings['ssl'] = False

    save_settings()
