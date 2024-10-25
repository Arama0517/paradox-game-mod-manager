from prompt_toolkit.shortcuts import input_dialog, radiolist_dialog

from src.dialog import PROMPT_TOOLKIT_DIALOG_TITLE
from src.settings import save_settings, settings
from src.validator import CertificatePathValidator


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


__all__ = ['main']
