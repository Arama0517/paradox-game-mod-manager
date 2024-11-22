from gevent.pool import Pool
from gevent.queue import Queue
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

from src.settings import settings
from src.steam_clients import cdn_client


class CDNWorkshopDepotManifest(CDNDepotManifest):
    item_info: PublishedFileDetails = None


def worker(
    queue: Queue,
    manifests: list[CDNWorkshopDepotManifest],
    progress: Progress,
):
    while not queue.empty():
        item_info: PublishedFileDetails = queue.get()

        # 获取清单请求吗
        task_id = progress.add_task(f'正在获取清单请求码: {item_info.title}', total=3)
        app_id = depot_id = item_info.consumer_appid
        manifest_gid = item_info.hcontent_file
        manifest_request_code = cdn_client.get_manifest_request_code(
            app_id,
            depot_id,
            manifest_gid,
        )

        # 获取清单内容
        progress.update(
            task_id,
            completed=1,
            description=f'正在获取清单内容: {item_info.title}',
        )
        resp = cdn_client.cdn_cmd(
            'depot',
            f'{depot_id}/manifest/{manifest_gid}/5/{manifest_request_code}',
            app_id,
            depot_id,
        )
        manifest = CDNWorkshopDepotManifest(
            cdn_client,
            app_id,
            resp.content,
        )

        # 解码清单
        progress.update(
            task_id,
            completed=2,
            description=f'正在解码清单内的文件名: {item_info.title}',
        )
        manifest.decrypt_filenames(cdn_client.get_depot_key(app_id, depot_id))
        cdn_client.manifests[(app_id, depot_id, manifest_gid)] = manifest

        # 添加信息
        manifest.name = item_info.title
        manifest.item_info = item_info
        progress.update(
            task_id,
            completed=3,
            description=f'获取清单完成: {item_info.title}',
        )

        # 添加进去
        manifests.append(manifest)


def get_manifests_for_workshop_item(
    items_info: list[PublishedFileDetails],
) -> list[CDNWorkshopDepotManifest]:
    manifests = []
    queue: Queue = Queue()
    pool: Pool = Pool(settings['max_tasks_num'])

    for item in items_info:
        queue.put(item)

    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}', style='bold dim'),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    ) as progress:
        for _ in range(min(settings['max_tasks_num'], queue.qsize())):
            pool.spawn(worker, queue, manifests, progress)
        pool.join()
    return manifests


__all__ = ['get_manifests_for_workshop_item', 'CDNWorkshopDepotManifest']
