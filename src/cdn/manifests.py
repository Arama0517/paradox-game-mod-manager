from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from steam import webapi
from steam.client.cdn import CDNDepotManifest

from src.steam_clients import cdn_client


def get_manifests_for_workshop_item(
    items_id: list[str],
) -> dict[str, dict[str, CDNDepotManifest | dict]]:
    manifests = {}
    items_info = webapi.post(
        'ISteamRemoteStorage',
        'GetPublishedFileDetails',
        params={
            'itemcount': len(items_id),
            'publishedfileids': items_id,
        },
    )['response']['publishedfiledetails']

    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    ) as progress:
        task_id = progress.add_task('[bold dim]正在获取清单中...', total=len(items_id))
        for item_info in items_info:
            progress.update(
                task_id,
                description=f'[bold dim]正在获取清单: {item_info["title"]}',
            )
            item_id = item_info['publishedfileid']
            manifest = cdn_client.get_manifest_for_workshop_item(int(item_id))
            manifest.name = item_info['title']
            manifests[item_id] = {
                'item_info': item_info,
                'manifest': manifest,
            }
            progress.advance(task_id, 1)
        progress.update(task_id, description='[bold dim]清单获取完成')
    return manifests


__all__ = ['get_manifests_for_workshop_item']
