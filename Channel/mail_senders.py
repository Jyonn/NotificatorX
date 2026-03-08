import json
import re

from django.db import transaction
from smartdjango import Error, Code, OK

from Config.models import Config, CI


@Error.register
class MailSenderErrors:
    INVALID_SENDER_ID = Error('Invalid sender_id', code=Code.BadRequest)
    SENDER_EXISTS = Error('Sender already exists', code=Code.BadRequest)
    SENDER_NOT_FOUND = Error('Sender not found', code=Code.NotFound)
    EMAIL_REQUIRED = Error('Email is required', code=Code.BadRequest)
    PASSWORD_REQUIRED = Error('Password is required', code=Code.BadRequest)
    SMTP_SERVER_REQUIRED = Error('SMTP server is required', code=Code.BadRequest)
    SMTP_PORT_REQUIRED = Error('SMTP port is required', code=Code.BadRequest)
    INVALID_ENABLED = Error('enabled must be boolean', code=Code.BadRequest)
    INVALID_WEIGHT = Error('weight must be a positive integer', code=Code.BadRequest)
    INVALID_SMTP_PORT = Error('smtp_port must be a positive integer', code=Code.BadRequest)
    INVALID_MAIL_SENDERS = Error('Invalid MAIL_SENDERS config', code=Code.InternalServerError)


class MailSenderManager:
    id_regex = re.compile(r'^[A-Za-z0-9_]{1,32}$')

    @classmethod
    def _normalize_sender_id(cls, sender_id):
        sender_id = str(sender_id or '').strip().upper()
        if not cls.id_regex.match(sender_id):
            raise MailSenderErrors.INVALID_SENDER_ID
        return sender_id

    @classmethod
    def _sender_key(cls, sender_id, suffix):
        return f'{CI.MAIL_SENDER}_{sender_id}_{suffix}'

    @classmethod
    def _parse_sender_ids(cls):
        raw = Config.get_value_by_key(CI.MAIL_SENDERS)
        if raw is None:
            return []
        try:
            data = json.loads(raw)
        except Exception as err:
            raise MailSenderErrors.INVALID_MAIL_SENDERS(details=err)
        if not isinstance(data, list):
            raise MailSenderErrors.INVALID_MAIL_SENDERS
        return [cls._normalize_sender_id(i) for i in data]

    @classmethod
    def _save_sender_ids(cls, sender_ids):
        Config.update_value(CI.MAIL_SENDERS, json.dumps(sender_ids))

    @classmethod
    def _refresh_runtime_mail_accounts(cls):
        from NotificatorX.global_settings import Global
        try:
            Global.load_mail_accounts()
        except Exception as err:
            raise MailSenderErrors.INVALID_MAIL_SENDERS(details=err)

    @classmethod
    def _extract_sender(cls, sender_id):
        email = Config.get_value_by_key(cls._sender_key(sender_id, 'EMAIL'))
        password = Config.get_value_by_key(cls._sender_key(sender_id, 'PASSWORD'))
        smtp_server = Config.get_value_by_key(cls._sender_key(sender_id, 'SMTP_SERVER'))
        smtp_port = Config.get_value_by_key(cls._sender_key(sender_id, 'SMTP_PORT'))
        enabled_raw = Config.get_value_by_key(cls._sender_key(sender_id, 'ENABLED'), 'true')
        weight_raw = Config.get_value_by_key(cls._sender_key(sender_id, 'WEIGHT'), '1')

        if enabled_raw in ('true', 'True', '1', 1, True):
            enabled = True
        elif enabled_raw in ('false', 'False', '0', 0, False):
            enabled = False
        else:
            enabled = True

        try:
            weight = int(weight_raw)
            if weight <= 0:
                weight = 1
        except Exception:
            weight = 1

        try:
            smtp_port_int = int(smtp_port) if smtp_port is not None else None
        except Exception:
            smtp_port_int = None

        return {
            'sender_id': sender_id,
            'email': email,
            'smtp_server': smtp_server,
            'smtp_port': smtp_port_int,
            'enabled': enabled,
            'weight': weight,
            'has_password': bool(password),
        }

    @classmethod
    def list(cls):
        sender_ids = cls._parse_sender_ids()
        return [cls._extract_sender(sender_id) for sender_id in sender_ids]

    @classmethod
    def get(cls, sender_id):
        sender_id = cls._normalize_sender_id(sender_id)
        sender_ids = cls._parse_sender_ids()
        if sender_id not in sender_ids:
            raise MailSenderErrors.SENDER_NOT_FOUND
        return cls._extract_sender(sender_id)

    @classmethod
    def create(cls, payload):
        sender_id = cls._normalize_sender_id(payload.get('sender_id'))
        email = str(payload.get('email') or '').strip()
        password = str(payload.get('password') or '').strip()
        smtp_server = str(payload.get('smtp_server') or '').strip()
        smtp_port = int(payload.get('smtp_port'))
        enabled = payload.get('enabled', True)
        weight = int(payload.get('weight', 1))

        with transaction.atomic():
            sender_ids = cls._parse_sender_ids()
            if sender_id in sender_ids:
                raise MailSenderErrors.SENDER_EXISTS

            Config.update_value(cls._sender_key(sender_id, 'EMAIL'), email)
            Config.update_value(cls._sender_key(sender_id, 'PASSWORD'), password)
            Config.update_value(cls._sender_key(sender_id, 'SMTP_SERVER'), smtp_server)
            Config.update_value(cls._sender_key(sender_id, 'SMTP_PORT'), str(smtp_port))
            Config.update_value(cls._sender_key(sender_id, 'ENABLED'), 'true' if enabled else 'false')
            Config.update_value(cls._sender_key(sender_id, 'WEIGHT'), str(weight))

            sender_ids.append(sender_id)
            cls._save_sender_ids(sender_ids)
            cls._refresh_runtime_mail_accounts()

        return cls._extract_sender(sender_id)

    @classmethod
    def update(cls, sender_id, payload):
        sender_id = cls._normalize_sender_id(sender_id)

        with transaction.atomic():
            sender_ids = cls._parse_sender_ids()
            if sender_id not in sender_ids:
                raise MailSenderErrors.SENDER_NOT_FOUND

            if 'email' in payload:
                email = str(payload.get('email')).strip()
                Config.update_value(cls._sender_key(sender_id, 'EMAIL'), email)

            if 'password' in payload:
                password = str(payload.get('password')).strip()
                Config.update_value(cls._sender_key(sender_id, 'PASSWORD'), password)

            if 'smtp_server' in payload:
                smtp_server = str(payload.get('smtp_server')).strip()
                Config.update_value(cls._sender_key(sender_id, 'SMTP_SERVER'), smtp_server)

            if 'smtp_port' in payload:
                smtp_port = int(payload.get('smtp_port'))
                Config.update_value(cls._sender_key(sender_id, 'SMTP_PORT'), str(smtp_port))

            if 'enabled' in payload:
                enabled = payload.get('enabled')
                Config.update_value(cls._sender_key(sender_id, 'ENABLED'), 'true' if enabled else 'false')

            if 'weight' in payload:
                weight = int(payload.get('weight'))
                Config.update_value(cls._sender_key(sender_id, 'WEIGHT'), str(weight))

            cls._refresh_runtime_mail_accounts()

        return cls._extract_sender(sender_id)

    @classmethod
    def delete(cls, sender_id):
        sender_id = cls._normalize_sender_id(sender_id)
        with transaction.atomic():
            sender_ids = cls._parse_sender_ids()
            if sender_id not in sender_ids:
                raise MailSenderErrors.SENDER_NOT_FOUND

            for suffix in ['EMAIL', 'PASSWORD', 'SMTP_SERVER', 'SMTP_PORT', 'ENABLED', 'WEIGHT']:
                Config.objects.filter(key=cls._sender_key(sender_id, suffix)).delete()

            sender_ids = [i for i in sender_ids if i != sender_id]
            cls._save_sender_ids(sender_ids)
            cls._refresh_runtime_mail_accounts()

        return OK
