from prompt_toolkit.shortcuts import input_dialog, yes_no_dialog
from steam.client import SteamClient
from steam.client.cdn import CDNClient
from steam.enums import EResult
from steam.enums.proto import EAuthSessionGuardType
from steam.webauth import (
    SUPPORTED_AUTH_TYPES,
    LoginIncorrect,
    TwoFactorCodeRequired,
    WebAuth,
    WebAuthException,
)

from src.logger import logger
from src.settings import save_settings, settings
from src.utils import PROMPT_TOOLKIT_DIALOG_TITLE

client = SteamClient()


async def cli_login(
    self: WebAuth,
    user_name: str,
    password: str,
    code: str = '',
    email_required: bool = False,
) -> WebAuth | None:
    """代替自带的cli_login"""
    while True:
        try:
            res = await self.login(user_name, password, code, email_required)
        except LoginIncorrect:
            password = await input_dialog(
                PROMPT_TOOLKIT_DIALOG_TITLE,
                f'密码错误, 请输入 {user_name} 的密码',
                '确认',
                '跳过此账号',
            ).run_async()
            continue
        except TwoFactorCodeRequired:
            allowed = set(self.allowed_confirmations)
            if allowed.isdisjoint(SUPPORTED_AUTH_TYPES):
                logger.error('暂不支持此账户的验证类型')
                return None

            can_confirm_with_app = EAuthSessionGuardType.DeviceConfirmation in allowed

            twofactor_code = ''
            while twofactor_code.strip() == '':
                text = ''
                if EAuthSessionGuardType.DeviceCode in allowed:
                    text = f'请输入 {user_name} 的 Steam Guard 验证码'
                elif EAuthSessionGuardType.EmailCode in allowed:
                    text = f'请输入 {user_name} 的邮箱验证码'
                if can_confirm_with_app:
                    if text == '':
                        if not await yes_no_dialog(
                            PROMPT_TOOLKIT_DIALOG_TITLE,
                            f'请在 Steam Guard 点击确认后点击此窗口的确认 (用户: {user_name})',  # noqa: E501
                            '确认',
                            '跳过此账号',
                        ).run_async():
                            return None
                    else:
                        text += ' (或者在第三方应用里点击确认后点击此窗口的确认)'

                if text != '':
                    twofactor_code = await input_dialog(
                        PROMPT_TOOLKIT_DIALOG_TITLE, text + ':', '确认', '跳过此账号'
                    ).run_async()
                    if not twofactor_code:
                        return None

                if can_confirm_with_app:
                    try:
                        await self._pollLoginStatus()
                        break
                    except TwoFactorCodeRequired:
                        pass

                if twofactor_code.strip():
                    using_email_code = EAuthSessionGuardType.EmailCode in allowed
                    await self._update_login_token(
                        twofactor_code,
                        EAuthSessionGuardType.EmailCode
                        if using_email_code
                        else EAuthSessionGuardType.DeviceCode,
                    )
                    try:
                        await self._pollLoginStatus()
                        break
                    except TwoFactorCodeRequired:
                        if not await yes_no_dialog(
                            PROMPT_TOOLKIT_DIALOG_TITLE,
                            '验证码错误, 请重试',
                            '确认',
                            '跳过此账号',
                        ).run_async():
                            return None
                        twofactor_code = ''
                        continue
                else:
                    if not await yes_no_dialog(
                        PROMPT_TOOLKIT_DIALOG_TITLE,
                        '身份验证失败, 请重试',
                        '确认',
                        '跳过此账号',
                    ).run_async():
                        return None
            await self._finalizeLogin()
            return self

        if hasattr(res, '__call__'):
            while True:
                try:
                    twofactor_code = await input_dialog(
                        PROMPT_TOOLKIT_DIALOG_TITLE,
                        f'请输入 {user_name} 的 2FA 或 邮箱验证码',
                        '确认',
                        '跳过此账号',
                    ).run_async()
                    resp = res(twofactor_code)
                    return resp
                except WebAuthException:
                    pass
        else:
            return self


_running_login = False


async def send_login():
    global _running_login
    if client.logged_on or _running_login:
        return

    _running_login = True
    for username, user_info in settings['users'].items():
        logger.info(f'尝试登录: [bold green]{username}[/bold green]')
        while True:
            result = await client.login(
                username, access_token=settings['users'][username]['token']
            )

            match result:
                case EResult.OK:
                    logger.info('登录成功')
                case EResult.AccessDenied:
                    try:
                        logger.warning('持久登录失效, 尝试重新获取Token')
                        async with WebAuth() as webauth:
                            if not await cli_login(
                                webauth, username, user_info['password']
                            ):
                                break
                            if username != webauth.username:
                                del settings['users'][username]
                            user_info = {
                                'username': webauth.username,
                                'password': webauth.password,
                                'token': webauth.refresh_token,
                            }
                            settings['users'][webauth.username] = user_info
                            save_settings()
                            continue
                    except KeyboardInterrupt:
                        pass
                    except Exception as e:
                        logger.error(f'登录失败, 错误: [bold red]{e}[/bold red]')
                case EResult.TryAnotherCM, EResult.ServiceUnavailable:
                    logger.warning('CM服务器不可用尝试使用其他服务器...')
                    client.cm_servers.mark_bad(client.current_server_addr)
                    await client.disconnect()
                    continue
                case _:
                    logger.error(
                        f'登录失败, 错误: [bold red]{result.name}[/bold red], 错误代码: [bold dim]{result.value}[/bold dim]'  # noqa: E501
                    )
            break
        if client.logged_on:
            break
    _running_login = False


@client.on(client.EVENT_DISCONNECTED)
async def _handle_disconnect():
    await client.reconnect(30)


cdn_client = CDNClient(client)


__all__ = ['send_login', 'cli_login', 'client', 'cdn_client']
