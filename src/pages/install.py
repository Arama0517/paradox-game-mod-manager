import shutil

from prompt_toolkit.shortcuts import input_dialog, message_dialog, yes_no_dialog
from steam import webapi

from src import mods
from src.cmd import clear
from src.dialog import PROMPT_TOOLKIT_DIALOG_TITLE
from src.path import MODS_DIR_PATH
from src.settings import save_settings, settings
from src.validator import SteamIDValidator


def main() -> None:
    while True:
        clear()
        item_id = input_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE,
            '请输入要安装的Mod的创意工坊ID',
            '安装',
            '返回',
            validator=SteamIDValidator(),
        ).run()
        if item_id is None:
            break
        if item_id in settings['mods']:
            message_dialog(
                PROMPT_TOOLKIT_DIALOG_TITLE, '该Mod已经安装过了', '继续'
            ).run()
            continue

        item_info = webapi.post(
            'ISteamRemoteStorage',
            'GetPublishedFileDetails',
            params={
                'itemcount': 1,
                'publishedfileids': [item_id],
            },
        )['response']['publishedfiledetails'][0]
        if not yes_no_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE,
            f'是否安装名为 {item_info["title"]} 的Mod?',
            yes_text='安装',
            no_text='取消',
        ).run():
            continue

        try:
            mod_install_duration = mods.download(int(item_id)).total_seconds()

            settings['mods'][item_id] = item_info
            save_settings()

            message_dialog(
                PROMPT_TOOLKIT_DIALOG_TITLE,
                f'下载完成, 共计用时: {mod_install_duration:.2f}秒',
                '继续',
            ).run()
        except Exception as e:
            message_dialog(
                PROMPT_TOOLKIT_DIALOG_TITLE, f'下载失败, 请稍后再试\n错误: {e}', '继续'
            ).run()
            shutil.rmtree(MODS_DIR_PATH / item_id, ignore_errors=True)
            continue


__all__ = ['main']
