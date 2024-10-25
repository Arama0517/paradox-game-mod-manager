from prompt_toolkit.shortcuts import (
    input_dialog,
    message_dialog,
    radiolist_dialog,
    yes_no_dialog,
)
from steam.enums import EResult
from steam.webauth import WebAuth

from src.dialog import PROMPT_TOOLKIT_DIALOG_TITLE
from src.settings import save_settings, settings
from src.steam_clients import client

__all__ = ['main']


def main():
    while True:
        match radiolist_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE,
            '请选择要执行的操作',
            '确认',
            '返回',
            [
                ('add', '添加账号'),
                ('remove', '移除账号'),
            ],
        ).run():
            case 'add':
                _add()
            case 'remove':
                _remove()
            case _:
                return


def _add():
    while True:
        user_name = input_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE, '请输入用户的名字', '确认', '返回'
        ).run()
        if not user_name:
            return
        if user_name in settings['users']:
            message_dialog(PROMPT_TOOLKIT_DIALOG_TITLE, '用户已存在', '继续').run()
            continue
        password = input_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE,
            '请输入用户的密码',
            '确认',
            '返回',
            password=True,
        ).run()
        if not password:
            return

        webauth = WebAuth()
        try:
            webauth.cli_login(user_name, password)
        except Exception as e:
            message_dialog(PROMPT_TOOLKIT_DIALOG_TITLE, f'登录失败\n{e}', '确认').run()
            continue

        settings['users'][user_name] = {
            'user_name': user_name,
            'password': password,
            'token': webauth.refresh_token,
        }
        save_settings()

        if not client.logged_on:
            if (
                client.login(user_name, access_token=webauth.refresh_token)
                != EResult.OK
            ):
                client.logout()
        message_dialog(PROMPT_TOOLKIT_DIALOG_TITLE, '添加成功', '确认').run()
        return


def _remove():
    options = []
    for user_name in settings['users'].keys():
        options += [(user_name, user_name)]
    if not options:
        message_dialog(PROMPT_TOOLKIT_DIALOG_TITLE, '你还没有添加任何一个用户!').run()
        return
    user_name = radiolist_dialog(
        PROMPT_TOOLKIT_DIALOG_TITLE, '请选择要移除的用户', '确认', '返回', options
    ).run()
    if not user_name:
        return

    if yes_no_dialog(
        PROMPT_TOOLKIT_DIALOG_TITLE, '真的要移除吗?', '确认', '取消'
    ).run():
        del settings['users'][user_name]
        save_settings()
        if client.username == user_name:
            client.logout()
    return
