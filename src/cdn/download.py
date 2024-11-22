from datetime import datetime, timedelta
from pathlib import Path

from gevent.pool import Pool
from gevent.queue import Queue
from rich.console import RenderableType
from rich.progress import (
    BarColumn,
    Progress,
    ProgressColumn,
    SpinnerColumn,
    Task,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.text import Text
from steam.client.cdn import CDNDepotFile, CDNDepotManifest
from steam.protobufs.steammessages_publishedfile_pb2 import (
    CPublishedFile_GetDetails_Response,
)

from src.cdn.manifests import get_manifests_for_workshop_item
from src.path import MODS_DIR_PATH
from src.settings import save_settings, settings


class DownloadSpeedColumn(ProgressColumn):
    def __init__(self):
        super().__init__()
        self.last_update_time = datetime.now()
        self.last_completed = 0.0

        self.message = self.get_message(0)

    @classmethod
    def get_message(cls, speed: int | float) -> Text:
        units = ['B', 'KiB', 'MiB', 'GiB', 'TiB']
        unit_index = 0
        size = speed
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        text = Text(f'{size:.2f} {units[unit_index]}/s')
        mebibyte = 1024 * 1024  # MiB
        if speed >= 5 * mebibyte:
            text.style = 'green'
        elif speed >= 2 * mebibyte:
            text.style = 'yellow'
        else:
            text.style = 'red'
        return text

    def render(self, task: Task) -> RenderableType:
        current_time = datetime.now()
        time_diff = (current_time - self.last_update_time).total_seconds()
        if time_diff < 1:
            return self.message
        byte_diff = task.completed - self.last_completed
        self.last_update_time = current_time
        self.last_completed = task.completed
        self.message = self.get_message(byte_diff / time_diff)
        return self.message


def worker(
    queue: Queue,
    download_dir_path: Path,
    progress: Progress,
    task_id: TaskID,
    pool: Pool,
):
    while not queue.empty():
        cdn_file: CDNDepotFile = queue.get()
        with open(download_dir_path / cdn_file.filename, 'wb') as f:
            while True:
                data = cdn_file.read(settings['max_chunk_size'])
                if not data:
                    break
                f.write(data)
                progress.advance(task_id, len(data))


def download_manifest(
    manifest: CDNDepotManifest,
    download_dir_path: Path,
) -> timedelta:
    files_size = 0
    pool = Pool(settings['max_tasks_num'])

    queue: Queue = Queue()
    for cdn_file in manifest.iter_files():
        if cdn_file.is_directory:
            (download_dir_path / cdn_file.filename).mkdir(parents=True, exist_ok=True)
            continue
        queue.put(cdn_file)
        files_size += cdn_file.size

    start_time: datetime = datetime.now()

    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}', style='bold dim'),
        BarColumn(),
        TaskProgressColumn(),
        DownloadSpeedColumn(),
        TimeRemainingColumn(),
    ) as progress:
        task_id: TaskID = progress.add_task(
            f'正在下载: {manifest.name} ', total=files_size
        )

        for _ in range(min(settings['max_tasks_num'], queue.qsize())):
            pool.spawn(worker, queue, download_dir_path, progress, task_id, pool)
        pool.join()
        progress.update(task_id, description=f'下载成功: {manifest.name}')
    return datetime.now() - start_time


def install_workshop_items(
    items_id: list[CPublishedFile_GetDetails_Response],
) -> timedelta:
    durations = timedelta()

    manifests = get_manifests_for_workshop_item(items_id)
    for manifest in manifests:
        item_id = str(manifest.item_info.publishedfileid)

        durations += download_manifest(manifest, MODS_DIR_PATH / item_id)
        settings['mods'][item_id] = {
            'title': manifest.item_info.title,
            'time_updated': manifest.item_info.time_updated,
        }

        save_settings()
    return durations


__all__ = ['download_manifest', 'install_workshop_items']