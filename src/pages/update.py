from prompt_toolkit.shortcuts import message_dialog
from steam import webapi

from src import cdn
from src.dialog import PROMPT_TOOLKIT_DIALOG_TITLE
from src.logger import logger
from src.path import MODS_DIR_PATH
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

    need_update_items_id = []
    for item_info in items_info:
        item_id = item_info['publishedfileid']
        if item_info['time_updated'] != settings['mods'][item_id]['time_updated']:
            logger.info(f'{item_info["title"]} 需要更新')
            try:
                need_update_items_id += [item_id]
                logger.info('获取成功')
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

    mod_update_durations = 0

    manifests = cdn.get_manifests_for_workshop_item(need_update_items_id)
    for item_id, result in manifests.items():
        logger.info(f'开始更新: {result["item_info"]["title"]}')
        mod_update_duration = cdn.download_manifest(
            result['manifest'], MODS_DIR_PATH / item_id
        ).total_seconds()
        settings['mods'][item_id] = result['item_info']
        save_settings()
        mod_update_durations += mod_update_duration
        logger.info(f'更新成功, 共计用时: {mod_update_duration:.2f}秒')

    message_dialog(
        PROMPT_TOOLKIT_DIALOG_TITLE,
        f'更新完成, 共计用时: {mod_update_durations:.2f}秒',
        '返回',
    ).run()


__all__ = ['main']
