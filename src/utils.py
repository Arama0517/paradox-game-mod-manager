PROMPT_TOOLKIT_DIALOG_TITLE = '钢铁雄心4模组管理器'


def format_duration(seconds: float) -> str:
    hours = round(seconds // 3600)
    minutes = round((seconds % 3600) // 60)
    seconds = round(seconds % 60)

    parts = []
    if hours > 0:
        parts.append(f'{hours}小时')
    if minutes > 0:
        parts.append(f'{minutes}分钟')
    if seconds > 0 or not parts:
        parts.append(f'{seconds}秒')

    return ' '.join(parts)


__all__ = ['PROMPT_TOOLKIT_DIALOG_TITLE', 'format_duration']
