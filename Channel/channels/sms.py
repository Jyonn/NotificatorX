from smartdjango import Error, Code

from Account.models import Account
from NotificatorX.global_settings import Global
from Channel.channels.base import BaseChannel
from Channel.channels.formats import MessageFormats
from utils.grabber import Grabber
from utils.i18n import resolve_locale, translate


@Error.register
class SMSErrors:
    REQUEST = Error('SMS Request', code=Code.InternalServerError)


class SMS(BaseChannel):
    key = 'sms'
    worker = Grabber(
        data_type='form',
        headers={
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        },
    )
    active = False
    supported_formats = {MessageFormats.TEXT}
    apikey = Global.YUNPIAN_APPKEY
    appurl = "https://sms.yunpian.com/v2/sms/single_send.json"
    template = '[Notificator] {name}: {message}'

    @classmethod
    def handler(cls, target: str, message: dict, options: dict, account: Account, format_: str):
        phone = target
        if not phone.startswith('+'):
            phone = '+86' + phone

        locale = resolve_locale(options=options, message=message, default=Global.DEFAULT_NOTIFY_LOCALE)
        template = options.get('template') or translate(locale, 'sms.default_template')
        content = str(message.get('body'))

        if '#message#' in str(template) or '#name#' in str(template):
            text = str(template).replace('#message#', content).replace('#name#', account.nick)
        else:
            try:
                text = str(template).format(name=account.nick, message=content)
            except Exception:
                text = str(template)

        try:
            cls.worker.post(cls.appurl, data=dict(
                apikey=cls.apikey,
                text=text,
                mobile=phone,
            ))
        except Exception as err:
            raise SMSErrors.REQUEST(details=err)
