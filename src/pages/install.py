from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup
from prompt_toolkit.shortcuts import (
    checkboxlist_dialog,
    input_dialog,
    message_dialog,
    yes_no_dialog,
)
from steam import webapi

from src import cdn
from src.cmd import clear
from src.dialog import PROMPT_TOOLKIT_DIALOG_TITLE
from src.path import MODS_DIR_PATH
from src.settings import save_settings, settings
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

        need_install_items_id = [item_id]

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
            for item_info in dependencies_item_info:
                if item_info['publishedfileid'] in settings['mods']:
                    continue
                options += [(item_info['publishedfileid'], item_info['title'])]
            if options:
                need_install_items_id += (
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

        manifests = cdn.get_manifests_for_workshop_item(need_install_items_id)

        for item_id, result in manifests.items():
            mod_install_duration = (
                cdn.download_manifest(result['manifest'], MODS_DIR_PATH / item_id)
            ).total_seconds()
            settings['mods'][item_id] = result['item_info']
            save_settings()
            mod_install_durations += mod_install_duration

        message_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE,
            f'安装完成, 共计用时: {mod_install_durations:.2f}秒',
            '继续',
        ).run()


__all__ = ['main']
