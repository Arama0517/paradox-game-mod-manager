import atexit
import os
import sys
import traceback
from pathlib import Path

import requests
from loguru import logger
from prompt_toolkit.shortcuts import input_dialog, message_dialog, radiolist_dialog
from steam import webapi
from steam.webauth import WebAuth, WebAuthException

from src.cmd import clear
from src.dialog import PROMPT_TOOLKIT_DIALOG_TITLE
from src.path import CURRENT_DIR_PATH, DATA_DIR_PATH, MOD_BOOT_FILES_PATH, MODS_DIR_PATH
from src.settings import save_settings, settings
from src.validator import CertificatePathValidator

DEFAULT_USERS = {
    'thb112259': 'steamok7416',
    'agt8729': 'Apk66433',
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
                case None:
                    sys.exit(1)
                case 'retry':
                    continue
                case 'disable_ssl':
                    settings['ssl'] = False
                case 'set_local_certificate':
                    certificate_path = input_dialog(
                        PROMPT_TOOLKIT_DIALOG_TITLE,
                        '请输入证书路径',
                        validator=CertificatePathValidator(),
                    ).run()
                    settings['ssl'] = certificate_path


def main():
    def except_hook(exc_type, exc_value, exc_traceback):
        error_message_file_path = CURRENT_DIR_PATH / 'error.txt'
        with error_message_file_path.open('w', encoding='utf-8') as f:
            f.write(
                ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            )
        message_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE,
            f'发生了一个错误\n请前往<https://github.com/Arama0517/hoi4-mods-manager/issues/>提出issue\n错误信息路径: {error_message_file_path}',  # noqa: E501
            '退出',
        ).run()

    sys.excepthook = except_hook

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
        for user_name, password in DEFAULT_USERS.items():
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

    if 'download_max_threads' not in settings:
        settings['download_max_threads'] = min(32, max(1, (os.cpu_count() or 1) // 2))

    if 'chunk_size' not in settings:
        settings['max_chunk_size'] = 1024 * 1024

    settings['gameDataPath'] = str(DATA_DIR_PATH)  # 数据目录

    save_settings()

    MODS_DIR_PATH.mkdir(parents=True, exist_ok=True)
    MOD_BOOT_FILES_PATH.mkdir(parents=True, exist_ok=True)

    from src import pages
    from src.steam_clients import client

    def exit_hook():
        if client is not None and client.logged_on:
            logger.info('登出')
            client.logout()

    atexit.register(exit_hook)

    while True:
        clear()

        text = '请选择一个选项'
        options = [
            ('start', '启动客户端'),
        ]
        if not client.logged_on:
            text += '\n没有可用的账号, 无法使用模组相关功能'
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
            case _:
                break


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
