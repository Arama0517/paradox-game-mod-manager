from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup
from loguru import logger
from prompt_toolkit.shortcuts import (
    checkboxlist_dialog,
    input_dialog,
    message_dialog,
    yes_no_dialog,
)
from steam import webapi
from steam.client.cdn import CDNDepotManifest

from src import mods
from src.cmd import clear
from src.dialog import PROMPT_TOOLKIT_DIALOG_TITLE
from src.path import MODS_DIR_PATH
from src.settings import save_settings, settings
from src.steam_clients import cdn_client
from src.validator import SteamIDValidator


# 没有找到怎么获取依赖的做法暂时只能这样了
def get_item_dependencies(item_id: str) -> list[str]:
    response = requests.get(
        f'https://steamcommunity.com/sharedfiles/filedetails/?id={item_id}'
    )
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    required_items_container = soup.find('div', id='RequiredItems')
    if required_items_container:
        dependencies = []
        for item in required_items_container.find_all('a', href=True):
            url = item['href']
            dependencies += [parse_qs(urlparse(url).query)['id'][0]]  # 解析URL的id参数
        return dependencies
    else:
        return []


def main():
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

        need_install_items_info = [item_info]

        dependencies = get_item_dependencies(item_id)
        if dependencies:
            dependencies_item_info = webapi.post(
                'ISteamRemoteStorage',
                'GetPublishedFileDetails',
                params={
                    'itemcount': len(dependencies),
                    'publishedfileids': dependencies,
                },
            )['response']['publishedfiledetails']
            options = []
            for item in dependencies_item_info:
                if item['publishedfileid'] in settings['mods']:
                    continue
                options += [(item, item['title'])]
            if options:
                need_install_items_info += (
                    checkboxlist_dialog(
                        PROMPT_TOOLKIT_DIALOG_TITLE,
                        '检测到此模组拥有依赖项, 是否安装\n不选择和选择不安装的效果一致',  # noqa: E501
                        '确认',
                        '不安装',
                        options,
                        [option[0] for option in options],
                    ).run()
                    or []
                )

        mod_install_durations = 0

        manifests_with_item_info: list[tuple[dict, CDNDepotManifest]] = []
        for item_info in need_install_items_info:
            logger.info(f'正在获取清单: {item_info["title"]}')
            manifests_with_item_info += [
                (
                    item_info,
                    cdn_client.get_manifest_for_workshop_item(int(item_id)),
                )
            ]
            logger.info('获取成功')

        for item_info, manifest in manifests_with_item_info:
            logger.info(f'开始安装: {item_info["title"]}')
            mod_install_duration = mods.download(
                manifest, MODS_DIR_PATH / item_id
            ).total_seconds()
            settings['mods'][item_id] = item_info
            save_settings()
            mod_install_durations += mod_install_duration
            logger.info(f'安装成功, 共计用时: {mod_install_duration}')

        message_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE,
            f'下载完成, 共计用时: {mod_install_durations:.2f}秒',
            '继续',
        ).run()


__all__ = ['main']
