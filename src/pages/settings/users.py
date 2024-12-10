from typing import Awaitable, Callable

from prompt_toolkit.shortcuts import (
    input_dialog,
    message_dialog,
    radiolist_dialog,
    yes_no_dialog,
)
from steam.enums import EResult
from steam.webauth import WebAuth

from src.settings import save_settings, settings
from src.steam_clients import cli_login, client, send_login
from src.utils import PROMPT_TOOLKIT_DIALOG_TITLE


async def main():
    while True:
        func: Callable[[], Awaitable[None]] = await radiolist_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE,
            '请选择要执行的操作',
            '确认',
            '返回',
            [
                (add, '添加账号'),
                (remove, '移除账号'),
            ],
        ).run_async()
        if not func:
            return
        await func()


async def add():
    while True:
        username = await input_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE, '请输入用户的名字', '确认', '返回'
        ).run_async()
        if not username:
            return
        if username in settings['users']:
            await message_dialog(
                PROMPT_TOOLKIT_DIALOG_TITLE, '用户已存在', '继续'
            ).run_async()
            continue
        password = await input_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE,
            '请输入用户的密码',
            '确认',
            '返回',
            password=True,
        ).run_async()
        if not password:
            return

        webauth = WebAuth()
        try:
            await cli_login(webauth, username, password)
        except Exception as e:
            await message_dialog(
                PROMPT_TOOLKIT_DIALOG_TITLE, f'登录失败\n{e}', '确认'
            ).run_async()
            continue

        settings['users'][username] = {
            'username': username,
            'password': password,
            'token': webauth.refresh_token,
        }
        save_settings()

        if (
            not client.logged_on
            and await client.login(username, access_token=webauth.refresh_token)
            != EResult.OK
        ):
            await client.logout()
        await message_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE, '添加成功', '确认'
        ).run_async()
        return


async def remove():
    options = []
    for username in settings['users'].keys():
        options += [(username, username)]
    if not options:
        message_dialog(PROMPT_TOOLKIT_DIALOG_TITLE, '你还没有添加任何一个用户!').run()
        return
    username = radiolist_dialog(
        PROMPT_TOOLKIT_DIALOG_TITLE, '请选择要移除的用户', '确认', '返回', options
    ).run()
    if not username:
        return

    if yes_no_dialog(
        PROMPT_TOOLKIT_DIALOG_TITLE, '真的要移除吗?', '确认', '取消'
    ).run():
        del settings['users'][username]
        save_settings()
        if client.username == username:
            client.logout()
            send_login()


__all__ = ['main']
