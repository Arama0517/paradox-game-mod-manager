from time import sleep

from loguru import logger
from prompt_toolkit.shortcuts import message_dialog
from steam import webapi

from src import mods
from src.dialog import PROMPT_TOOLKIT_DIALOG_TITLE
from src.path import MOD_BOOT_FILES_PATH
from src.settings import save_settings, settings


def main():
    items_id = list(settings['mods'].keys())
    if len(items_id) == 0:
        message_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE, '你还没有安装任何模组', '返回'
        ).run()
        return
    items_info = webapi.post(
        'ISteamRemoteStorage',
        'GetPublishedFileDetails',
        params={
            'itemcount': len(items_id),
            'publishedfileids': items_id,
        },
    )['response']['publishedfiledetails']

    mod_update_durations = 0
    changed = False
    for item_info in items_info:
        item_id = item_info['publishedfileid']
        if item_info['time_updated'] != settings['mods'][item_id]['time_updated']:
            logger.info(f'{item_info["title"]} 需要更新')
            # 需要更新模组
            mod_update_duration = mods.download(int(item_id)).total_seconds()
            settings['mods'][item_id] = item_info
            (MOD_BOOT_FILES_PATH / f'{item_id}.mod').unlink(missing_ok=True)
            save_settings()
            mod_update_durations += mod_update_duration
            logger.info(f'更新成功, 共计用时: {mod_update_duration:.2f}秒')
            changed = True
        else:
            logger.info(f'{item_info["title"]} 已经是最新版本')
    sleep(1)
    message_dialog(
        PROMPT_TOOLKIT_DIALOG_TITLE,
        f'更新完成, 共计用时: {mod_update_durations:.2f}秒'
        if changed
        else '没有需要更新的模组',
        '返回',
    ).run()


__all__ = ['main']
