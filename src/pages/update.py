from prompt_toolkit.shortcuts import message_dialog
from steam import webapi
from steam.enums import EResult
from steam.exceptions import SteamError

from src.cdn import (
    install_workshop_items,
)
from src.logger import logger
from src.settings import settings
from src.utils import PROMPT_TOOLKIT_DIALOG_TITLE, format_duration


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

    need_update_items_id = []
    for item_info in items_info:
        item_id = item_info['publishedfileid']
        if item_info['time_updated'] != settings['mods'][item_id]['time_updated']:
            logger.info(f'{item_info["title"]} 需要更新')
            try:
                need_update_items_id += [item_id]
            except Exception as e:
                logger.error(f'获取失败, 错误: {e}')
                continue
        else:
            logger.info(f'{item_info["title"]} 已经是最新版本')
    if not need_update_items_id:
        message_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE,
            '没有需要更新的模组',
            '返回',
        ).run()
        return

    try:
        mod_update_durations = install_workshop_items(need_update_items_id)
        message_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE,
            f'安装完成, 共计用时: {format_duration(mod_update_durations)}',
            '继续',
        ).run()
    except SteamError as e:
        if e.eresult != EResult.NotLoggedOn:
            raise e
        message_dialog(PROMPT_TOOLKIT_DIALOG_TITLE, '没有可用的账号', '返回').run()


__all__ = ['main']
