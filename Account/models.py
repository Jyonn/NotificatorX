import re

from SmartDjango import models, E, Hc
from django.utils.crypto import get_random_string
from smartify import P


@E.register(id_processor=E.idp_cls_prefix())
class AccountError:
    NOT_FOUND = E('账号不存在', hc=Hc.NotFound)
    PASSWORD_ERROR = E('密码错误', hc=Hc.Forbidden)
    ALREADY_EXIST = E('账号已存在', hc=Hc.Forbidden)
    INVALID_NAME = E('名称不合法', hc=Hc.Forbidden)


class Account(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(
        max_length=10,
        unique=True,
        null=False,
    )

    nick = models.CharField(
        max_length=10,
        null=False,
    )

    token = models.CharField(
        max_length=32,
        null=False,
    )

    @classmethod
    def auth(cls, name, token):
        cls.validator(locals())

        account = cls.get(name)
        if account.token != token:
            raise AccountError.PASSWORD_ERROR

        return account

    @classmethod
    def get(cls, name):
        try:
            return cls.objects.get(name=name)
        except cls.DoesNotExist as err:
            raise AccountError.NOT_FOUND(debug_message=err)

    @classmethod
    def get_by_id(cls, id):
        try:
            return cls.objects.get(id=id)
        except cls.DoesNotExist as err:
            raise AccountError.NOT_FOUND(debug_message=err)

    @staticmethod
    def _valid_name(name):
        """验证账户名合法"""
        valid_chars = '^[A-Za-z0-9_]{4,20}$'
        if re.match(valid_chars, name) is None:
            raise AccountError.INVALID_NAME

    @classmethod
    def create(cls, name, nick):
        if cls.objects.filter(name=name).exists():
            raise AccountError.ALREADY_EXIST
        return cls.objects.create(
            name=name,
            nick=nick,
            token=get_random_string(length=32),
        )

    @classmethod
    def get_all(cls):
        return cls.objects.all().dict(cls.d)

    def renew_token(self):
        self.token = get_random_string(length=32)
        self.save()
        return self

    def d(self):
        return self.dictify('id', 'name', 'token', 'nick')

    def update(self, nick):
        self.nick = nick
        self.save()
        return self


class AccountP:
    name, token, nick = Account.P('name', 'token', 'nick')
    account = P('id', yield_name='account').process(Account.get_by_id)
