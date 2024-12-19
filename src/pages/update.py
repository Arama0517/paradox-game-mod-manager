from prompt_toolkit.shortcuts import message_dialog
from steam.protobufs.steammessages_publishedfile_pb2 import (
    PublishedFileDetails,
)

from src.cdn import (
    install_workshop_items,
)
from src.logger import logger
from src.settings import settings
from src.steam_clients import client
from src.utils import PROMPT_TOOLKIT_DIALOG_TITLE, format_duration


async def main():
    items_id = list(map(int, settings['mods'].keys()))
    if len(items_id) == 0:
        await message_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE, '你还没有安装任何模组', '返回'
        ).run_async()
        return
    items_info: list[PublishedFileDetails] = (
        await client.send_um_and_wait(
            'PublishedFile.GetDetails#1',
            {
                'publishedfileids': items_id,
                'language': 7,  # 简体中文
            },
        )
    ).body.publishedfiledetails

    need_update_items_info = []
    for item_info in items_info:
        if (
            item_info.time_updated
            != settings['mods'][str(item_info.publishedfileid)]['time_updated']
        ):
            logger.info(f'{item_info.title} 需要更新')
            need_update_items_info.append(item_info)
        else:
            logger.info(f'{item_info.title} 已经是最新版本')
    if not need_update_items_info:
        await message_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE,
            '没有需要更新的模组',
            '返回',
        ).run_async()
        return

    mod_update_durations = await install_workshop_items(need_update_items_info)
    await message_dialog(
        PROMPT_TOOLKIT_DIALOG_TITLE,
        f'安装完成, 共计用时: {format_duration(mod_update_durations)}',
        '继续',
    ).run_async()


__all__ = ['main']
