from datetime import timedelta

PROMPT_TOOLKIT_DIALOG_TITLE = '钢铁雄心4模组管理器'


def format_duration(delta: timedelta) -> str:
    # 计算小时、分钟和秒
    total_seconds = int(delta.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    parts = []
    if hours > 0:
        parts.append(f'{hours}小时')
    if minutes > 0:
        parts.append(f'{minutes}分钟')
    if seconds > 0 or not parts:  # 如果没有小时和分钟，确保秒数显示
        parts.append(f'{seconds}秒')

    return ' '.join(parts)


__all__ = ['PROMPT_TOOLKIT_DIALOG_TITLE', 'format_duration']
