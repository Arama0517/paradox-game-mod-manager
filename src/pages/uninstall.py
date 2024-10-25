import shutil

from prompt_toolkit.shortcuts import checkboxlist_dialog, message_dialog

from src.dialog import PROMPT_TOOLKIT_DIALOG_TITLE
from src.path import MOD_BOOT_FILES_PATH, MODS_DIR_PATH
from src.settings import save_settings, settings


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

    for item_id in items_id:
        shutil.rmtree(MODS_DIR_PATH / item_id)
        del settings['mods'][item_id]
        (MOD_BOOT_FILES_PATH / f'{item_id}.mod').unlink(missing_ok=True)

    save_settings()
    message_dialog(PROMPT_TOOLKIT_DIALOG_TITLE, '卸载完成', '返回').run()


__all__ = ['main']
