""" Jyonn Liu 180111

系统配置类
"""
from django.db import models
from smartdjango import Error

from Config.validators import ConfigValidator, ConfigErrors


class Config(models.Model):
    vldt = ConfigValidator

    key = models.CharField(
        max_length=vldt.MAX_KEY_LENGTH,
        unique=True,
        validators=[vldt.key],
    )

    value = models.CharField(
        max_length=vldt.MAX_VALUE_LENGTH,
        validators=[vldt.value],
    )

    @classmethod
    def get_config_by_key(cls, key) -> 'Config':
        try:
            return cls.objects.get(key=key)
        except cls.DoesNotExist as err:
            raise ConfigErrors.NOT_FOUND(details=err)

    @classmethod
    def get_value_by_key(cls, key, default=None):
        try:
            return cls.get_config_by_key(key).value
        except Exception:
            return default

    @classmethod
    def update_value(cls, key, value):
        try:
            config = cls.get_config_by_key(key)
            config.value = value
            config.save()
        except Error as e:
            if e == ConfigErrors.NOT_FOUND:
                try:
                    config = cls(
                        key=key,
                        value=value,
                    )
                    config.save()
                except Exception as err:
                    raise ConfigErrors.CREATE(details=err)
            else:
                raise e
        except Exception as err:
            raise ConfigErrors.CREATE(details=err)


class ConfigInstance:
    ADMIN_EMAIL = 'ADMIN_EMAIL'
    ADMIN_PASSWORD = 'ADMIN_PASSWORD'

    JWT_ENCODE_ALGO = 'JWT_ENCODE_ALGO'
    PROJECT_SECRET_KEY = 'PROJECT_SECRET_KEY'

    SENDER_EMAIL = 'SENDER_EMAIL'
    SENDER_EMAIL_PWD = 'SENDER_EMAIL_PASSWORD'
    SMTP_SERVER = 'SMTP_SERVER'
    SMTP_PORT = 'SMTP_PORT'

    MAIL_SENDERS = 'MAIL_SENDERS'
    MAIL_SENDER = 'MAIL_SENDER'
    NOTIFY_DEFAULT_LOCALE = 'NOTIFY_DEFAULT_LOCALE'
    NOTIFY_BRAND_NAME_EN = 'NOTIFY_BRAND_NAME_EN'
    NOTIFY_BRAND_NAME_ZH = 'NOTIFY_BRAND_NAME_ZH'
    NOTIFY_PRODUCT_NAME_EN = 'NOTIFY_PRODUCT_NAME_EN'
    NOTIFY_PRODUCT_NAME_ZH = 'NOTIFY_PRODUCT_NAME_ZH'

    SENDERS = 'SENDERS'

    YUNPIAN_APPKEY = 'YUNPIAN_APPKEY'


CI = ConfigInstance
