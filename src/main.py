from gevent.monkey import patch_all

# 这里的thread不能改成True会导致用户输入的时候心跳被阻塞
patch_all(thread=False)

from src.monkey import patch_all

patch_all()

import json
import os
import sys
import traceback
from pathlib import Path
from typing import Callable
from warnings import filterwarnings

from prompt_toolkit.shortcuts import input_dialog, message_dialog, radiolist_dialog
from steam.webauth import WebAuth, WebAuthException

from src.path import (
    CURRENT_DIR_PATH,
    LAUNCHER_SETTINGS_FILE_PATH,
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
    import requests
    from steam import webapi

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


def init():
    filterwarnings('ignore', category=UserWarning)

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
        with LAUNCHER_SETTINGS_FILE_PATH.open('r', encoding='utf-8') as f:
            launcher_settings = json.load(f)
        for username, password in (
            DEFAULT_USERS.get(launcher_settings['gameId']) or {}
        ).items():
            webauth = WebAuth()
            try:
                webauth.login(username, password)
            except WebAuthException:
                continue
            if not webauth.logged_on:
                continue
            settings['users'][username] = {
                'username': username,
                'password': password,
                'token': webauth.refresh_token,
            }

    if 'mods' not in settings:
        settings['mods'] = {}

    if 'max_tasks_num' not in settings:
        settings['max_tasks_num'] = min(32, max(1, (os.cpu_count() or 1)))

    if 'chunk_size' not in settings:
        settings['max_chunk_size'] = 1024 * 1024

    save_settings()

    MODS_DIR_PATH.mkdir(parents=True, exist_ok=True)
    MOD_BOOT_FILES_PATH.mkdir(parents=True, exist_ok=True)

    from src.steam_clients import send_login

    send_login()


def main():
    from src import pages
    from src.steam_clients import client, send_login

    while True:
        text = '请选择一个选项'
        options = [
            (pages.start, '启动游戏客户端'),
        ]
        if not client.logged_on:
            text += '\n没有可用的账号, 无法使用模组相关功能'
            options += [(send_login, '重试登录')]
        else:
            options += [
                (pages.install, '安装模组'),
                (pages.uninstall, '卸载模组'),
                (pages.update, '更新模组'),
            ]
        options += [(pages.settings, '设置')]

        func: Callable[[], None] | None = radiolist_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE, text, '确定', '退出', options
        ).run()
        if not func:
            break
        func()


ERROR_TRACEBACK_FILE_PATH = CURRENT_DIR_PATH / 'error_traceback.txt'
ERROR_ISSUE_URL = 'https://github.com/Arama0517/hoi4-mods-manager/issues/new/choose'
ERROR_TEXT = f"""发生了一个错误
请打开链接: <{ERROR_ISSUE_URL}>
选择反馈Bug后填写你遇到的问题, 复现的过程和错误跟踪文件中的内容
错误跟踪文件路径: {ERROR_TRACEBACK_FILE_PATH}"""


if __name__ == '__main__':
    try:
        init()
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        with ERROR_TRACEBACK_FILE_PATH.open('w', encoding='utf-8') as f:
            traceback.print_exception(e, file=f)
        message_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE,
            ERROR_TEXT,
            '退出',
        ).run()
