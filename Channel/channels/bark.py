from urllib.parse import quote

from smartdjango import Error, Code

from Account.models import Account
from Channel.channels.base import BaseChannel
from Channel.channels.formats import MessageFormats
from utils.grabber import Grabber

quote_safe = lambda x: quote(x, safe='')


@Error.register
class BarkErrors:
    REQUEST = Error('Bark Request', code=Code.InternalServerError)


class Bark(BaseChannel):
    key = 'bark'
    worker = Grabber()
    active = True
    supported_formats = {MessageFormats.TEXT, MessageFormats.MARKDOWN}

    @classmethod
    def handler(cls, target: str, message: dict, options: dict, account: Account, format_: str):
        uri = target
        if not uri.endswith('/'):
            uri += '/'

        title = message.get('title') or options.get('title') or ''
        title = '【{}】{}'.format(account.nick, title)
        content = str(message.get('body'))
        path = '%s%s/%s' % (uri, quote_safe(title), quote_safe(content))

        query = dict()
        params = ['sound', 'url', 'icon', 'group']
        for param in params:
            value = options.get(param)
            if value:
                query[param] = value

        try:
            cls.worker.get(path, query=query)
        except Exception as err:
            raise BarkErrors.REQUEST(details=err)
