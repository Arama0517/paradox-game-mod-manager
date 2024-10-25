from pathlib import Path

import requests
from prompt_toolkit.document import Document
from prompt_toolkit.validation import ValidationError, Validator
from steam import webapi
from steam.enums import EResult


class SteamIDValidator(Validator):
    def validate(self, document: Document) -> None:
        if not document.text:
            raise ValidationError(message='不能为空')
        if not document.text.isdigit():
            raise ValidationError(message='请输入一个有效的创意工坊ID')
        item_info = webapi.post(
            'ISteamRemoteStorage',
            'GetPublishedFileDetails',
            params={
                'itemcount': 1,
                'publishedfileids': [document.text],
            },
        )['response']['publishedfiledetails'][0]
        if EResult(item_info['result']) != EResult.OK:
            raise ValidationError(message='请输入一个有效的创意工坊ID')
        if item_info['consumer_app_id'] != 394360:
            raise ValidationError(message='暂不支持其他游戏的模组')


class CertificatePathValidator(Validator):
    def validate(self, document: Document) -> None:
        if not document.text:
            raise ValidationError(message='不可为空')
        path = Path(document.text)
        if not path.exists():
            raise ValidationError(message='请输入一个真实存在的路径')
        if path.is_dir():
            raise ValidationError(message='请输入一个有效的证书')
        try:
            session = requests.Session()
            session.verify = path
            webapi.get('ISteamWebAPIUtil', 'GetServerInfo', session=session)
        except Exception as e:
            raise ValidationError(message=str(e))


class IntValidator(Validator):
    def validate(self, document: Document) -> None:
        if not document.text:
            raise ValidationError(message='不能为空')
        if not document.text.isdigit() and int(document.text) <= 0:
            raise ValidationError(message='请输入一个有效的数字')


__all__ = [
    'SteamIDValidator',
    'CertificatePathValidator',
    'IntValidator',
]
