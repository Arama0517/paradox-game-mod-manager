import shutil

from prompt_toolkit.shortcuts import checkboxlist_dialog, message_dialog
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)

from src.path import MOD_BOOT_FILES_PATH, MODS_DIR_PATH
from src.settings import save_settings, settings
from src.utils import PROMPT_TOOLKIT_DIALOG_TITLE


def main():
    options: list[tuple[str, str]] = []
    for item_id, item_info in settings['mods'].items():
        options.append((item_id, item_info['title']))
    if not options:
        message_dialog(
            PROMPT_TOOLKIT_DIALOG_TITLE, '你还没有安装任何模组', '返回'
        ).run()
        return

    items_id = checkboxlist_dialog(
        PROMPT_TOOLKIT_DIALOG_TITLE, '请选择要卸载的模组', '卸载', '取消', options
    ).run()
    if not items_id:
        return

    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}', style='bold dim'),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    ) as progress:
        task_id = progress.add_task(
            '正在删除模组...',
            total=len(items_id),
        )
        for item_id in items_id:
            progress.update(
                task_id,
                description=f'正在删除模组: {settings["mods"][item_id]["title"]}',
            )
            shutil.rmtree(MODS_DIR_PATH / item_id)
            progress.advance(task_id, 1)
            (MOD_BOOT_FILES_PATH / f'{item_id}.mod').unlink(missing_ok=True)
            del settings['mods'][item_id]
            save_settings()
        progress.update(task_id, description='删除成功')
    message_dialog(PROMPT_TOOLKIT_DIALOG_TITLE, '卸载完成', '返回').run()


__all__ = ['main']
