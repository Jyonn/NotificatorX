import json
from urllib import parse, request

from smartdjango import Error, Code

from Account.models import Account
from Channel.channels.base import BaseChannel
from Channel.channels.formats import MessageFormats


@Error.register
class WebhookErrors:
    INVALID_METHOD = Error("Invalid webhook method", code=Code.BadRequest)
    INVALID_HEADERS = Error("Invalid webhook headers", code=Code.BadRequest)
    INVALID_QUERY = Error("Invalid webhook query", code=Code.BadRequest)
    REQUEST = Error("Webhook Request", code=Code.InternalServerError)


class Webhook(BaseChannel):
    key = 'webhook'
    active = True
    supported_formats = {MessageFormats.TEXT, MessageFormats.JSON}
    allowed_methods = {"GET", "POST", "PUT", "PATCH", "DELETE"}

    @classmethod
    def handler(cls, target: str, message: dict, options: dict, account: Account, format_: str):
        raw_method = options.get('method') or "POST"
        if not isinstance(raw_method, str):
            raise WebhookErrors.INVALID_METHOD
        method = raw_method.upper()
        if method not in cls.allowed_methods:
            raise WebhookErrors.INVALID_METHOD

        headers = options.get('headers') or {}
        if not isinstance(headers, dict):
            raise WebhookErrors.INVALID_HEADERS

        query = options.get('query') or {}
        if not isinstance(query, dict):
            raise WebhookErrors.INVALID_QUERY

        url = target
        if query:
            connector = '&' if '?' in url else '?'
            url += connector + parse.urlencode(query, doseq=True)

        content_type = options.get('content_type') or (
            'application/json'
            if format_ == MessageFormats.JSON
            else 'text/plain; charset=utf-8'
        )
        request_headers = {'Content-Type': content_type}
        request_headers.update(headers)
        request_headers.setdefault('X-Notificator-Account', account.name)
        request_headers.setdefault('X-Notificator-Nick', account.nick)

        data = None
        if method != 'GET':
            payload = options.get('body')
            if payload is None:
                payload = {
                    'account': {
                        'name': account.name,
                        'nick': account.nick,
                    },
                    'message': message,
                    'target': target,
                } if format_ == MessageFormats.JSON else str(message.get('body'))

            if isinstance(payload, (dict, list)):
                data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
            elif isinstance(payload, str):
                data = payload.encode('utf-8')
            else:
                data = str(payload).encode('utf-8')

        req = request.Request(url, data=data, method=method)
        for header, value in request_headers.items():
            req.add_header(str(header), str(value))

        try:
            resp = request.urlopen(req, timeout=30)
            resp.close()
        except Exception as err:
            raise WebhookErrors.REQUEST(details=err)
