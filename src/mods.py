import asyncio
from datetime import datetime, timedelta
from pathlib import Path

import aiofiles
from rich.console import RenderableType
from rich.progress import (
    BarColumn,
    Progress,
    ProgressColumn,
    SpinnerColumn,
    Task,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.text import Text
from steam.client.cdn import CDNDepotFile, CDNDepotManifest

from .path import MODS_DIR_PATH
from .settings import settings
from .steam_clients import cdn_client

__all__ = ['download']


def _format_size(size: int | float):
    units = ['B', 'KiB', 'MiB', 'GiB', 'TiB']
    size = size
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    return f'{size:.2f} {units[unit_index]}'


class DownloadSpeedColumn(ProgressColumn):
    def __init__(self):
        super().__init__()
        self.last_update_time = datetime.now()
        self.last_completed = 0.0

        self.message = self.get_message(0)

    @classmethod
    def get_message(cls, speed: int | float) -> Text:
        text = f'{_format_size(speed)}/s'
        mebibyte = 1024 * 1024  # MiB
        if speed >= 5 * mebibyte:
            return Text(text, style='green')
        elif speed >= 2 * mebibyte:
            return Text(text, style='yellow')
        else:
            return Text(text, style='red')

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


async def _download(item_id: str) -> timedelta:
    manifest: CDNDepotManifest | Exception = cdn_client.get_manifest_for_workshop_item(
        int(item_id)
    )
    if isinstance(manifest, Exception):
        raise manifest

    files_size = 0
    queue: asyncio.Queue[CDNDepotFile] = asyncio.Queue()
    for cdn_file in manifest.iter_files():
        cdn_file: CDNDepotFile
        if cdn_file.is_directory:
            continue
        await queue.put(cdn_file)
        files_size += cdn_file.size

    start_time = datetime.now()
    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        BarColumn(),
        TaskProgressColumn(),
        DownloadSpeedColumn(),
        TimeRemainingColumn(),
    ) as progress:
        task_id = progress.add_task('[bold dim]正在下载模组中...', total=files_size)

        async def download_worker():
            while not queue.empty():
                cdn_file = await queue.get()
                file_path: Path = MODS_DIR_PATH / item_id / cdn_file.filename
                file_path.parent.mkdir(parents=True, exist_ok=True)

                async with aiofiles.open(file_path, 'wb') as f:
                    loop = asyncio.get_event_loop()
                    while True:
                        data: bytes = await loop.run_in_executor(
                            None, cdn_file.read, settings['max_chunk_size']
                        )
                        if not data:
                            break
                        await f.write(data)
                        progress.advance(task_id, len(data))
                queue.task_done()

        tasks = [download_worker() for _ in range(settings['download_max_threads'])]

        await asyncio.gather(*tasks)
    return datetime.now() - start_time


def download(item_id: str) -> timedelta:
    return asyncio.run(_download(item_id))
