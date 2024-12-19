from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from steam.client.cdn import CDNDepotManifest
from steam.protobufs.steammessages_publishedfile_pb2 import (
    PublishedFileDetails,
)

from src.steam_clients import cdn_client


class CDNWorkshopDepotManifest(CDNDepotManifest):
    item_info: PublishedFileDetails = None


async def get_manifests_for_workshop_item(
    items_info: list[PublishedFileDetails],
) -> list[CDNWorkshopDepotManifest]:
    manifests = []

    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}', style='bold dim'),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    ) as progress:
        task_id = progress.add_task(
            description='正在获取清单...', total=len(items_info)
        )
        for item_info in items_info:
            progress.update(task_id, description=f'正在获取清单: {item_info.title}')
            manifest: CDNWorkshopDepotManifest = (
                await cdn_client.get_manifest_for_workshop_item(
                    item_info.publishedfileid
                )
            )

            manifest.item_info = item_info
            manifests.append(manifest)
            progress.advance(task_id)
        progress.update(task_id, description='获取清单成功')

    return manifests


__all__ = ['get_manifests_for_workshop_item', 'CDNWorkshopDepotManifest']
