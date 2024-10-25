from loguru import logger
from steam.client import SteamClient
from steam.client.cdn import CDNClient
from steam.enums import EResult
from steam.webauth import WebAuth

from src.settings import save_settings, settings

client = SteamClient()
for user_name, user_info in settings['users'].items():
    logger.info(f'尝试登录: {user_name}')
    while True:
        client.logout()

        result: EResult = client.login(
            user_name, access_token=settings['users'][user_name]['token']
        )
        match result:
            case EResult.OK:
                logger.info('登录成功')
            case EResult.AccessDenied:
                try:
                    logger.warning('持久登录失败, 尝试重新获取token')
                    webauth = WebAuth()
                    webauth.cli_login(user_name, user_info['password'])
                    settings['users'][user_name]['token'] = webauth.refresh_token
                    save_settings()
                    continue
                except Exception as e:
                    logger.error(f'登录失败, 错误: {e}')
            case _:
                logger.error(f'登录失败, 错误: {result.name}, 错误代码: {result.value}')
        break
    if client.logged_on:
        break


cdn_client = CDNClient(client)

__all__ = ['client', 'cdn_client']
