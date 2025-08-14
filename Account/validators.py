import re

from smartdjango import Error, Code


@Error.register
class AccountErrors:
    NOT_FOUND = Error('账号不存在', code=Code.NotFound)
    PASSWORD_ERROR = Error('密码错误', code=Code.Forbidden)
    ALREADY_EXIST = Error('账号已存在', code=Code.Forbidden)
    INVALID_NAME = Error('名称不合法', code=Code.Forbidden)


class AccountValidator:
    MAX_NAME_LENGTH = 10
    MAX_NICK_LENGTH = 10
    MAX_TOKEN_LENGTH = 32

    @classmethod
    def name(cls, name):
        """验证账户名合法"""
        valid_chars = '^[A-Za-z0-9_]{4,20}$'
        if re.match(valid_chars, name) is None:
            raise AccountErrors.INVALID_NAME
