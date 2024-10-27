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
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.text import Text
from steam.client.cdn import CDNDepotFile, CDNDepotManifest

from src.settings import settings


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


async def write(
    cdn_file: CDNDepotFile, download_dir_path: Path, progress: Progress, task_id: TaskID
):
    file_path: Path = download_dir_path / cdn_file.filename
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


async def download_worker(
    queue: asyncio.Queue[CDNDepotFile],
    download_dir_path: Path,
    progress: Progress,
    task_id: TaskID,
):
    while not queue.empty():
        cdn_file = await queue.get()
        await write(cdn_file, download_dir_path, progress, task_id)
        queue.task_done()


async def download_async(
    manifest: CDNDepotManifest, download_dir_path: Path
) -> timedelta:
    files_size = 0
    queue = asyncio.Queue()
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
        task_id = progress.add_task(
            f'[bold dim]正在下载: {manifest.name} ', total=files_size
        )
        tasks = [
            download_worker(queue, download_dir_path, progress, task_id)
            for _ in range(min(settings['download_max_threads'], queue.qsize()))
        ]
        await asyncio.gather(*tasks)
        progress.update(task_id, description='[bold dim]下载成功')
    return datetime.now() - start_time


def download_manifest(manifest: CDNDepotManifest, download_dir_path: Path) -> timedelta:
    return asyncio.run(download_async(manifest, download_dir_path))


__all__ = ['download_manifest']
