from prompt_toolkit.document import Document
from prompt_toolkit.validation import ValidationError, Validator


class IntValidator(Validator):
    def validate(self, document: Document) -> None:
        if not document.text:
            raise ValidationError(message='不能为空')
        if not document.text.isdigit() and int(document.text) <= 0:
            raise ValidationError(message='请输入一个有效的数字')


__all__ = ['IntValidator']
