import json

from Config.models import Config, CI
from utils.i18n import normalize_locale


class MailAccount:
    def __init__(self, sender_id, mail, password, port, server, enabled=True, weight=1):
        self.sender_id = sender_id
        self.mail = mail
        self.password = password
        self.port = int(port)
        self.server = server
        self.enabled = enabled
        self.weight = int(weight)


def _to_bool(value, default=True):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    raw = str(value).strip().lower()
    if raw in ('1', 'true', 'yes', 'y', 'on'):
        return True
    if raw in ('0', 'false', 'no', 'n', 'off'):
        return False
    raise ValueError(f'invalid bool value: {value}')


def _to_positive_int(value, default=1):
    if value is None:
        return default
    number = int(value)
    if number <= 0:
        raise ValueError(f'invalid positive integer value: {value}')
    return number


def _sender_key(sender_id, suffix):
    normalized = str(sender_id).strip().upper()
    return f'{CI.MAIL_SENDER}_{normalized}_{suffix}'


def _is_proj_init_mode():
    try:
        from django.conf import settings
        return bool(getattr(settings, 'PROJ_INIT', False))
    except Exception:
        return False


def _load_mail_accounts():
    raw = Config.get_value_by_key(CI.MAIL_SENDERS)
    if raw is None:
        if _is_proj_init_mode():
            return []
        raise RuntimeError(f'Missing required mail config key: {CI.MAIL_SENDERS}')

    try:
        sender_ids = json.loads(raw)
    except Exception as err:
        if _is_proj_init_mode():
            return []
        raise RuntimeError(f'Invalid {CI.MAIL_SENDERS} config: {err}')

    if not isinstance(sender_ids, list) or len(sender_ids) == 0:
        if _is_proj_init_mode():
            return []
        raise RuntimeError(f'{CI.MAIL_SENDERS} must be a non-empty JSON array')

    errors = []
    accounts = []
    for sender_id in sender_ids:
        sender_id = str(sender_id).strip()
        if not sender_id:
            errors.append('sender id cannot be empty')
            continue

        email_key = _sender_key(sender_id, 'EMAIL')
        password_key = _sender_key(sender_id, 'PASSWORD')
        server_key = _sender_key(sender_id, 'SMTP_SERVER')
        port_key = _sender_key(sender_id, 'SMTP_PORT')
        enabled_key = _sender_key(sender_id, 'ENABLED')
        weight_key = _sender_key(sender_id, 'WEIGHT')

        email = Config.get_value_by_key(email_key)
        password = Config.get_value_by_key(password_key)
        server = Config.get_value_by_key(server_key)
        port = Config.get_value_by_key(port_key)
        enabled_raw = Config.get_value_by_key(enabled_key, 'true')
        weight_raw = Config.get_value_by_key(weight_key, '1')

        missing = []
        if not email:
            missing.append(email_key)
        if not password:
            missing.append(password_key)
        if not server:
            missing.append(server_key)
        if not port:
            missing.append(port_key)
        if missing:
            errors.append(f'[{sender_id}] missing keys: {", ".join(missing)}')
            continue

        try:
            enabled = _to_bool(enabled_raw, default=True)
        except Exception as err:
            errors.append(f'[{sender_id}] invalid {enabled_key}: {err}')
            continue

        try:
            weight = _to_positive_int(weight_raw, default=1)
        except Exception as err:
            errors.append(f'[{sender_id}] invalid {weight_key}: {err}')
            continue

        try:
            account = MailAccount(
                sender_id=sender_id,
                mail=email,
                password=password,
                port=port,
                server=server,
                enabled=enabled,
                weight=weight,
            )
        except Exception as err:
            errors.append(f'[{sender_id}] invalid sender config: {err}')
            continue

        if account.enabled:
            accounts.append(account)

    if errors:
        if _is_proj_init_mode():
            return []
        raise RuntimeError('Invalid mail sender config: ' + '; '.join(errors))

    if len(accounts) == 0:
        if _is_proj_init_mode():
            return []
        raise RuntimeError('No enabled mail sender found in MAIL_SENDERS config')

    return accounts


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

    DEFAULT_NOTIFY_LOCALE = normalize_locale(Config.get_value_by_key(CI.NOTIFY_DEFAULT_LOCALE, 'en-US'))
    BRAND_NAME_EN = Config.get_value_by_key(CI.NOTIFY_BRAND_NAME_EN, 'Meadow Inbox')
    BRAND_NAME_ZH = Config.get_value_by_key(CI.NOTIFY_BRAND_NAME_ZH, '原野信箱')
    PRODUCT_NAME_EN = Config.get_value_by_key(CI.NOTIFY_PRODUCT_NAME_EN, 'Notificator')
    PRODUCT_NAME_ZH = Config.get_value_by_key(CI.NOTIFY_PRODUCT_NAME_ZH, 'Notificator')

    mail_accounts = _load_mail_accounts()

    @classmethod
    def load_mail_accounts(cls):
        cls.mail_accounts = _load_mail_accounts()
        return cls.mail_accounts


import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
