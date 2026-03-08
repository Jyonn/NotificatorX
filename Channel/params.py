import re

from smartdjango import Params, DictValidator, Validator, ListValidator

from Channel.channels.dispatcher import ChannelDispatcher
from Channel.channels.formats import MessageFormats
from utils.i18n import parse_locale

sender_id_regex = re.compile(r'^[A-Za-z0-9_]{1,32}$')


def non_empty_str(value):
    return isinstance(value, str) and value.strip() != ''


def positive_int(value):
    return isinstance(value, int) and value > 0


def optional_dict(value):
    return value is None or isinstance(value, dict)


def optional_supported_locale(value):
    return value is None or parse_locale(value) is not None


def message_validator(value):
    format_ = value['format']
    body = value['body']
    if format_ == MessageFormats.TEXT and isinstance(body, str):
        return True
    if format_ == MessageFormats.HTML and isinstance(body, str):
        return True
    if format_ == MessageFormats.MARKDOWN and isinstance(body, str):
        return True
    if format_ == MessageFormats.JSON and isinstance(body, (dict, list)):
        return True
    return False


class ChannelParams(metaclass=Params):
    uri = Validator('uri').to(str).bool(non_empty_str, message='Invalid uri')
    content = Validator('content').to(str)
    title = Validator('title').null().default(None)
    sound = Validator('sound').null().default(None)
    url = Validator('url').null().default(None)
    icon = Validator('icon').null().default(None)
    group = Validator('group').null().default(None)

    phone = Validator('phone').to(str).bool(non_empty_str, message='Invalid phone')
    mail = Validator('mail').to(str).bool(non_empty_str, message='Invalid mail')
    subject = Validator('subject').null().default(None)
    locale = Validator('locale').null().default(None).bool(optional_supported_locale, message='Invalid locale')
    appellation = Validator('appellation').null().default(None)
    recipient_name = Validator('recipient_name').null().default(None)
    action_url = Validator('action_url').null().default(None)
    action_text = Validator('action_text').null().default(None)
    footer_note = Validator('footer_note').null().default(None)

    webhook_url = Validator('url').to(str).bool(non_empty_str, message='Invalid webhook url')
    method = Validator('method').null().default('POST').to(str).bool(
        lambda v: v.upper() in ('GET', 'POST', 'PUT', 'PATCH', 'DELETE'),
        message='Invalid method'
    )
    headers = Validator('headers').null().default(None).bool(optional_dict, message='headers must be an object')
    query = Validator('query').null().default(None).bool(optional_dict, message='query must be an object')
    body = Validator('body').null().default(None)

    message = DictValidator('message').fields(
        Validator('format').to(str).bool(lambda v: v in MessageFormats.all(), message='Invalid message format.'),
        Validator('title').null().default('', as_final=True),
        Validator('body'),
        Validator('locale').null().default(None, as_final=True).bool(
            optional_supported_locale,
            message='Invalid locale',
        ),
    ).bool(message_validator, message='Invalid (format, body) pair format.')

    deliveries = ListValidator('deliveries').element(DictValidator().fields(
        Validator('channel').to(str).bool(
            lambda v: v in ChannelDispatcher.active_channels(),
            message='Invalid channel deliveries.'
        ),
        Validator('target').to(str).bool(non_empty_str, message='Invalid delivery target.'),
        Validator('options').null().to(dict).default({}, as_final=True),
    ))


class MailSenderParams(metaclass=Params):
    sender_id = Validator('sender_id').to(str).bool(
        lambda v: sender_id_regex.match(v.strip().upper()) is not None,
        message='Invalid sender_id'
    )
    email = Validator('email').to(str).bool(non_empty_str, message='Email is required')
    password = Validator('password').to(str).bool(non_empty_str, message='Password is required')
    smtp_server = Validator('smtp_server').to(str).bool(non_empty_str, message='SMTP server is required')
    smtp_port = Validator('smtp_port').to(int).bool(positive_int, message='smtp_port must be a positive integer')
    enabled = Validator('enabled').bool(lambda v: isinstance(v, bool), message='enabled must be boolean')
    weight = Validator('weight').to(int).bool(positive_int, message='weight must be a positive integer')
    enabled_create = enabled.copy().null().default(True)
    weight_create = weight.copy().null().default(1)

    email_optional = email.copy().null().default(None)
    password_optional = password.copy().null().default(None)
    smtp_server_optional = smtp_server.copy().null().default(None)
    smtp_port_optional = smtp_port.copy().null().default(None)
    enabled_optional = enabled.copy().null().default(None)
    weight_optional = weight.copy().null().default(None)
