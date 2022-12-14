import json

from SmartDjango import NetPacker

from Config.models import Config, CI


class MailAccount:
    def __init__(self, mail):
        self.mail = mail
        self.password = Config.get_value_by_key(f'{CI.SENDER_EMAIL_PWD}_{mail}')
        self.port = Config.get_value_by_key(f'{CI.SMTP_PORT}_{mail}')
        self.server = Config.get_value_by_key(f'{CI.SMTP_SERVER}_{mail}')


class Global:
    ADMIN_EMAIL = Config.get_value_by_key(CI.ADMIN_EMAIL)
    ADMIN_PASSWORD = Config.get_value_by_key(CI.ADMIN_PASSWORD)

    SECRET_KEY = Config.get_value_by_key(CI.PROJECT_SECRET_KEY)
    JWT_ENCODE_ALGO = Config.get_value_by_key(CI.JWT_ENCODE_ALGO)

    SENDER_EMAIL = Config.get_value_by_key(CI.SENDER_EMAIL)
    SENDER_PASSWORD = Config.get_value_by_key(CI.SENDER_EMAIL_PWD)
    SMTP_PORT = Config.get_value_by_key(CI.SMTP_PORT)
    SMTP_SERVER = Config.get_value_by_key(CI.SMTP_SERVER)

    YUNPIAN_APPKEY = Config.get_value_by_key(CI.YUNPIAN_APPKEY)

    SENDERS = json.loads(Config.get_value_by_key(CI.SENDERS))
    mail_accounts = [MailAccount(mail) for mail in SENDERS]


# NetPacker.set_mode(debug=False)

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
