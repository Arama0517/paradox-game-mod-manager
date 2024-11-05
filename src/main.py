import os
import sys
import traceback
from pathlib import Path

import requests
from prompt_toolkit.shortcuts import input_dialog, message_dialog, radiolist_dialog
from steam import webapi
from steam.webauth import WebAuth, WebAuthException

from src.cmd import clear
from src.path import (
    CURRENT_DIR_PATH,
    MOD_BOOT_FILES_PATH,
    MODS_DIR_PATH,
)
from src.settings import save_settings, settings
from src.utils import PROMPT_TOOLKIT_DIALOG_TITLE
from src.validator import CertificatePathValidator

DEFAULT_USERS = {
    'hoi4': {
        'thb112259': 'steamok7416',
        'agt8729': 'Apk66433',
    },
    'victoria3': {'steamok1090250': 'steamok45678919'},
}


def init_ssl():
    while True:
        try:
            webapi.get('ISteamWebAPIUtil', 'GetServerInfo')
            break
        except requests.exceptions.SSLError:
            ssl = radiolist_dialog(
                PROMPT_TOOLKIT_DIALOG_TITLE,
                'SSL错误\n请选择一个选项',
                '确认',
                '退出',
                [
                    ('retry', '重试'),
                    ('disable_ssl', '关闭证书认证'),
                    ('set_local_certificate', '设置本地证书路径'),
                ],
            ).run()
            match ssl:
                case 'retry':
                    continue
                case 'disable_ssl':
                    settings['ssl'] = False
                case 'set_local_certificate':
                    certificate_path = input_dialog(
                        PROMPT_TOOLKIT_DIALOG_TITLE,
                        '请输入证书路径',
                        '确认',
                        '退出',
                        validator=CertificatePathValidator(),
                    ).run()
                    if not certificate_path:
                        sys.exit(1)
                    settings['ssl'] = certificate_path
                case _:
                    sys.exit(1)


def main():
    clear()

    # 初始化配置文件
    if (
        'ssl' not in settings
        or type(settings['ssl']) is not bool
        and not Path(settings['ssl']).exists()
    ):
        settings['ssl'] = True

    init_ssl()

    if 'users' not in settings:
        settings['users'] = {}
        for user_name, password in (
            DEFAULT_USERS.get(settings['gameId']) or {}
        ).items():
            webauth = WebAuth()
            try:
                webauth.login(user_name, password)
            except WebAuthException:
                continue
            if not webauth.logged_on:
                continue
            settings['users'][user_name] = {
                'user_name': user_name,
                'password': password,
                'token': webauth.refresh_token,
            }

    if 'mods' not in settings:
        settings['mods'] = {}

    if 'max_threads' not in settings:
        settings['max_threads'] = min(32, max(1, (os.cpu_count() or 1) // 2))

    if 'chunk_size' not in settings:
        settings['max_chunk_size'] = 1024 * 1024

    save_settings()

    MODS_DIR_PATH.mkdir(parents=True, exist_ok=True)
    MOD_BOOT_FILES_PATH.mkdir(parents=True, exist_ok=True)

    from src import pages
    from src.steam_clients import client, login

    login()

    while True:
        clear()

        text = '请选择一个选项'
        options = [
            ('start', '启动游戏客户端'),
        ]
        if not client.logged_on:
            text += '\n没有可用的账号, 无法使用模组相关功能'
            options += [('relogin', '重试登录')]
        else:
            options += [
                ('install', '安装模组'),
                ('uninstall', '卸载模组'),
                ('update', '更新模组'),
            ]
        options += [('settings', '设置')]

        match radiolist_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE, text, '确定', '退出', options
        ).run():
            case 'start':
                pages.start()
                break
            case 'install':
                pages.install()
            case 'uninstall':
                pages.uninstall()
            case 'update':
                pages.update()
            case 'settings':
                pages.settings()
            case 'relogin':
                login()
            case _:
                break


ERROR_TRACEBACK_FILE_PATH = CURRENT_DIR_PATH / 'error_traceback.txt'
ERROR_ISSUE_URL = 'https://github.com/Arama0517/hoi4-mods-manager/issues/new/choose'
ERROR_TEXT = f"""发生了一个错误
请打开链接: <{ERROR_ISSUE_URL}>
选择反馈Bug后填写你遇到的问题, 复现的过程和错误跟踪文件中的内容
错误跟踪文件路径: {ERROR_TRACEBACK_FILE_PATH}"""


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        error_traceback_file_path = CURRENT_DIR_PATH / 'error_traceback.txt'
        with error_traceback_file_path.open('w', encoding='utf-8') as f:
            traceback.print_exception(e, file=f)
        message_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE,
            ERROR_TEXT,
            '退出',
        ).run()
    finally:
        from src.steam_clients import client

        client.logout()
