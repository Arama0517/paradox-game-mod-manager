import asyncio
import os
import traceback
from typing import Awaitable, Callable
from warnings import filterwarnings

from nest_asyncio import apply
from prompt_toolkit.shortcuts import message_dialog, radiolist_dialog
from steam.webauth import WebAuth, WebAuthException

from src import pages
from src.path import (
    CURRENT_DIR_PATH,
    MOD_BOOT_FILES_PATH,
    MODS_DIR_PATH,
)
from src.settings import launcher_settings, save_settings, settings
from src.steam_clients import client, send_login
from src.utils import PROMPT_TOOLKIT_DIALOG_TITLE

apply()

DEFAULT_USERS = {
    'hoi4': {
        'thb112259': 'steamok7416',
        'agt8729': 'Apk66433',
    },
    'victoria3': {'steamok1090250': 'steamok45678919'},
    'stellaris': {'wbtq1084073': 'steamok010101'},
}


async def init():
    filterwarnings('ignore', category=UserWarning)

    # 初始化配置文件
    if 'users' not in settings:
        settings['users'] = {}
        for username, password in (
            DEFAULT_USERS.get(launcher_settings['gameId']) or {}
        ).items():
            async with WebAuth() as webauth:
                try:
                    await webauth.login(username, password)
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

    await send_login()


async def main():
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

        func: Callable[[], Awaitable[None]] | None = await radiolist_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE, text, '确定', '退出', options
        ).run_async()
        if not func:
            break
        await func()


ERROR_TRACEBACK_FILE_PATH = CURRENT_DIR_PATH / 'error_traceback.txt'
ERROR_ISSUE_URL = 'https://github.com/Arama0517/hoi4-mods-manager/issues/new/choose'
ERROR_TEXT = f"""发生了一个错误
请打开链接: <{ERROR_ISSUE_URL}>
选择反馈Bug后填写你遇到的问题, 复现的过程和错误跟踪文件中的内容
错误跟踪文件路径: {ERROR_TRACEBACK_FILE_PATH}"""


if __name__ == '__main__':
    try:
        asyncio.run(init())
        asyncio.run(main())
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
