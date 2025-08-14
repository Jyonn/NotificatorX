from typing import Optional
from urllib.parse import quote

from smartdjango import Error, Code

from Account.models import Account
from Channel.channels.base import BaseChannel
from utils.grabber import Grabber

quote_safe = lambda x: quote(x, safe='')


@Error.register
class BarkErrors:
    REQUEST = Error('Bark Request', code=Code.InternalServerError)


class Bark(BaseChannel):
    class Body:
        uri: str
        content: str
        title: Optional[str] = None
        sound: Optional[str] = None
        icon: Optional[str] = None
        group: Optional[str] = None
        url: Optional[str] = None

    worker = Grabber()
    active = True

    @classmethod
    def handler(cls, body: Body, account: Account):
        if not body.uri.endswith('/'):
            body.uri += '/'

        if not body.title:
            body.title = ''
        body.title = '【{}】{}'.format(account.nick, body.title)
        path = '%s%s/%s' % (body.uri, quote_safe(body.title), quote_safe(body.content))

        query = dict()
        params = ['sound', 'url', 'icon', 'group']
        for param in params:
            value = getattr(body, param)
            if value:
                query[param] = value

        try:
            cls.worker.get(path, query=query)
        except Exception as err:
            raise BarkErrors.REQUEST(debug_message=err)
