from typing import Optional

from prompt_toolkit.shortcuts import (
    checkboxlist_dialog,
    input_dialog,
    message_dialog,
)
from steam.enums import EResult
from steam.exceptions import SteamError
from steam.protobufs.steammessages_publishedfile_pb2 import (
    PublishedFileDetails,
)

from src.cdn import install_workshop_items
from src.settings import settings
from src.steam_clients import client
from src.utils import PROMPT_TOOLKIT_DIALOG_TITLE, format_duration


async def get_item_children(
    item_info: PublishedFileDetails,
    result: Optional[list[PublishedFileDetails]] = None,
) -> list[PublishedFileDetails]:
    if result is None:
        result = []

    if EResult(item_info.result) != EResult.OK:
        return []

    # 防止result多出来个合集装不了
    if item_info not in result and item_info.can_subscribe:
        result.append(item_info)

    if item_info.num_children != 0:
        children_info = (
            await client.send_um_and_wait(
                'PublishedFile.GetDetails#1',
                {
                    'publishedfileids': [
                        child.publishedfileid for child in item_info.children
                    ],
                    'includechildren': True,
                    'includetags': False,
                    'includeadditionalpreviews': False,
                    'includekvtags': False,
                    'includevotes': False,
                    'short_description': True,
                    'includeforsaledata': False,
                    'includemetadata': False,
                    'language': 7,
                },
            )
        ).body.publishedfiledetails
        for child in children_info:
            if child in result:
                continue
            await get_item_children(child, result)
    return result


async def main():
    while True:
        item_id = await input_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE,
            '请输入创意工坊ID(可安装一键安装合集)',
            '安装',
            '返回',
        ).run_async()
        if item_id is None:
            break
        try:
            item_id = int(item_id)
        except ValueError:
            await message_dialog(
                PROMPT_TOOLKIT_DIALOG_TITLE, '请输入一个有效的创意工坊ID', '继续'
            ).run_async()
            continue
        item_info: PublishedFileDetails = (
            await client.send_um_and_wait(
                'PublishedFile.GetDetails#1',
                {
                    'publishedfileids': [item_id],
                    'includechildren': True,
                },
            )
        ).body.publishedfiledetails[0]
        if item_info.result != EResult.OK:
            await message_dialog(
                PROMPT_TOOLKIT_DIALOG_TITLE, '请输入一个有效的创意工坊ID', '继续'
            ).run_async()
            continue

        items_info = sorted(
            await get_item_children(item_info), key=lambda item: item.title
        )
        if len(items_info) <= 0:
            await message_dialog(
                PROMPT_TOOLKIT_DIALOG_TITLE, '请输入一个有效的创意工坊ID', '继续'
            ).run_async()
            continue

        options = []
        for item_info in items_info:
            if str(item_info.publishedfileid) in settings['mods']:
                continue
            options += [(item_info, item_info.title)]

        if not options:
            await message_dialog(
                PROMPT_TOOLKIT_DIALOG_TITLE, '此物品和此物品的所有依赖已被安装', '继续'
            ).run_async()
            continue

        need_install_items_info = (
            await checkboxlist_dialog(
                PROMPT_TOOLKIT_DIALOG_TITLE,
                '请选择要安装的物品(如果有依赖会包含依赖项)',  # noqa: E501
                '确认',
                '取消',
                options,
                [option[0] for option in options],
            ).run_async()
            or []
        )
        if not need_install_items_info:
            await message_dialog(
                PROMPT_TOOLKIT_DIALOG_TITLE, '没有需要安装的物品', '继续'
            ).run_async()
            continue

        try:
            mod_install_durations = await install_workshop_items(
                need_install_items_info
            )
            await message_dialog(
                PROMPT_TOOLKIT_DIALOG_TITLE,
                f'安装完成, 共计用时: {format_duration(mod_install_durations)}',
                '继续',
            ).run_async()
        except SteamError as e:
            if e.eresult != EResult.NotLoggedOn:
                raise e
            await message_dialog(
                PROMPT_TOOLKIT_DIALOG_TITLE, '没有可用的账号', '返回'
            ).run_async()


__all__ = ['main']
