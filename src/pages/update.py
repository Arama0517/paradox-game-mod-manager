from loguru import logger
from prompt_toolkit.shortcuts import message_dialog
from steam import webapi
from steam.client.cdn import CDNDepotManifest

from src import mods
from src.dialog import PROMPT_TOOLKIT_DIALOG_TITLE
from src.path import MODS_DIR_PATH
from src.settings import save_settings, settings
from src.steam_clients import cdn_client


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

    manifests_with_item_info: list[tuple[dict, CDNDepotManifest]] = []
    for item_info in items_info:
        item_id: int = int(item_info['publishedfileid'])
        if item_info['time_updated'] != settings['mods'][item_id]['time_updated']:
            logger.info(f'{item_info["title"]} 需要更新, 正在获取清单')
            try:
                manifests_with_item_info += [
                    item_info,
                    cdn_client.get_manifest_for_workshop_item(item_id),
                ]
                logger.info('获取成功')
            except Exception as e:
                logger.error(f'获取失败, 错误: {e}')
                continue
        else:
            logger.info(f'{item_info["title"]} 已经是最新版本')
    if not manifests_with_item_info:
        message_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE,
            '没有需要更新的模组',
            '返回',
        ).run()
        return

    mod_update_durations = 0
    for item_info, manifest in manifests_with_item_info:
        logger.info(f'开始更新: {item_info["title"]}')
        mod_update_duration = mods.download(
            manifest, MODS_DIR_PATH / item_info['publishedfileid']
        ).total_seconds()
        settings['mods'][item_info['publishedfileid']] = item_info
        save_settings()
        mod_update_durations += mod_update_duration
        logger.info(f'更新成功, 共计用时: {mod_update_duration:.2f}秒')

    message_dialog(
        PROMPT_TOOLKIT_DIALOG_TITLE,
        f'更新完成, 共计用时: {mod_update_durations:.2f}秒',
        '返回',
    ).run()


__all__ = ['main']
