import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterator

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

from src.path import MODS_DIR_PATH
from src.settings import settings
from src.steam_clients import cdn_client

__all__ = ['download']


def _format_size(size: int | float):
    units = ['B', 'KiB', 'MiB', 'GiB', 'TiB']
    size = size
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    return f'{size:.2f} {units[unit_index]}'


async def _write_mod_files(
    cdn_files: Iterator[CDNDepotFile],
    download_path: Path,
    progress: Progress,
    task_id: TaskID,
):
    loop = asyncio.get_event_loop()
    for cdn_file in cdn_files:
        file_path: Path = download_path / cdn_file.filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(file_path, 'wb') as f:
            while True:
                data: bytes = await loop.run_in_executor(
                    None, cdn_file.read, settings['max_chunk_size']
                )
                if not data:
                    break
                await f.write(data)
                progress.advance(task_id, len(data))
                del data
        del cdn_file


def _sort_cdn_depot_files(
    manifest: CDNDepotManifest,
) -> tuple[Iterator[Iterator[CDNDepotFile]], int]:
    files = [target for target in manifest.iter_files() if not target.is_directory]

    max_chunks = min(len(files), settings['download_max_threads'])
    chunks = [[] for _ in range(max_chunks)]
    chunk_sizes = [0] * max_chunks

    min_chunk_index = 0

    for file in sorted(files, key=lambda f: f.size, reverse=True):
        chunks[min_chunk_index].append(file)
        chunk_sizes[min_chunk_index] += file.size

        min_size = chunk_sizes[min_chunk_index]
        for i in range(max_chunks):
            if chunk_sizes[i] < min_size:
                min_chunk_index = i
                min_size = chunk_sizes[i]

    return (iter(chunk) for chunk in chunks), sum(chunk_sizes)


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
    manifest = cdn_client.get_manifest_for_workshop_item(int(item_id))
    if isinstance(manifest, Exception):
        raise manifest

    start_time = datetime.now()
    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        BarColumn(),
        TaskProgressColumn(),
        DownloadSpeedColumn(),
        TimeRemainingColumn(),
    ) as progress:
        chunks, files_size = _sort_cdn_depot_files(manifest)
        task_id = progress.add_task('[bold dim]正在下载模组中...', total=files_size)

        tasks = [
            _write_mod_files(chunk, MODS_DIR_PATH / item_id, progress, task_id) for chunk in chunks
        ]
        await asyncio.gather(*tasks)
    return datetime.now() - start_time


def download(item_id: str) -> timedelta:
    return asyncio.run(_download(item_id))
