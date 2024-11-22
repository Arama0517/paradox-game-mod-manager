from pathlib import Path

import requests
from prompt_toolkit.document import Document
from prompt_toolkit.validation import ValidationError, Validator
from steam import webapi
from steam.core.msg import MsgProto
from steam.enums import EResult


class SteamIDValidator(Validator):
    def validate(self, document: Document) -> None:
        if not document.text:
            raise ValidationError(message='不能为空')
        if not document.text.isdigit():
            raise ValidationError(message='请输入一个有效的创意工坊ID')

        from src.steam_clients import anonymous_client

        resp: MsgProto = anonymous_client.send_um_and_wait(
            'PublishedFile.GetDetails#1', {'publishedfileids': [int(document.text)]}
        )
        if (
            resp.header.eresult != EResult.OK
            or resp.body.publishedfiledetails[0].result != EResult.OK
        ):
            raise ValidationError(message='请输入一个有效的创意工坊ID')


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


__all__ = ['SteamIDValidator', 'IntValidator', 'CertificatePathValidator']
