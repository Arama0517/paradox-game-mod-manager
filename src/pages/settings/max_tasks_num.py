from prompt_toolkit.shortcuts import input_dialog

from src.settings import save_settings, settings
from src.utils import PROMPT_TOOLKIT_DIALOG_TITLE
from src.validator import IntValidator


def main():
    max_tasks_num = input_dialog(
        PROMPT_TOOLKIT_DIALOG_TITLE,
        '请输入要设置的最大任务数\n不建议设置的过高, 可能会导致占用的资源较大',
        '确认',
        '返回',
        validator=IntValidator(),
        default=str(settings['max_tasks_num']),
    ).run()
    if not max_tasks_num:
        return
    settings['max_tasks_num'] = int(max_tasks_num)
    save_settings()


__all__ = ['main']
