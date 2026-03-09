import re

from django.db import models
from django.utils.crypto import get_random_string
from smartdjango.models import Model

from Account.validators import AccountErrors, AccountValidator


class Account(Model):
    vldt = AccountValidator

    id = models.AutoField(primary_key=True)

    name = models.CharField(
        max_length=vldt.MAX_NAME_LENGTH,
        unique=True,
        null=False,
        validators=[vldt.name]
    )

    nick = models.CharField(
        max_length=vldt.MAX_NICK_LENGTH,
        null=False,
    )

    token = models.CharField(
        max_length=vldt.MAX_TOKEN_LENGTH,
        null=False,
    )

    @classmethod
    def auth(cls, name, token):

        account = cls.get(name)
        if account.token != token:
            raise AccountErrors.PASSWORD_ERROR

        return account

    @classmethod
    def get(cls, name):
        try:
            return cls.objects.get(name=name)
        except cls.DoesNotExist as err:
            raise AccountErrors.NOT_FOUND(debug_message=err)

    @classmethod
    def get_by_id(cls, id):
        try:
            return cls.objects.get(id=id)
        except cls.DoesNotExist as err:
            raise AccountErrors.NOT_FOUND(debug_message=err)

    @classmethod
    def create(cls, name, nick):
        if cls.objects.filter(name=name).exists():
            raise AccountErrors.ALREADY_EXIST
        return cls.objects.create(
            name=name,
            nick=nick,
            token=get_random_string(length=32),
        )

    @classmethod
    def get_all(cls):
        return cls.objects.all().map(cls.d)

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
