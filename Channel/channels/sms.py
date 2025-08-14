from smartdjango import Error, Code

from Account.models import Account
from NotificatorX.global_settings import Global
from Channel.channels.base import BaseChannel
from utils.grabber import Grabber


@Error.register
class SMSErrors:
    REQUEST = Error('SMS Request', code=Code.InternalServerError)


class SMS(BaseChannel):
    class Body:
        phone: str
        content: str

    worker = Grabber(
        data_type='form',
        headers={
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        },
    )
    active = True
    apikey = Global.YUNPIAN_APPKEY
    appurl = "https://sms.yunpian.com/v2/sms/single_send.json"
    template = '【MasterWhole】命令#name#的运行结果已出：#message#'

    @classmethod
    def handler(cls, body: Body, account: Account):
        if not body.phone.startswith('+'):
            body.phone = '+86' + body.phone

        try:
            cls.worker.post(cls.appurl, data=dict(
                apikey=cls.apikey,
                text=cls.template.replace('#message#', body.content).replace('#name#', account.nick),
                mobile=body.phone,
            ))
        except Exception as err:
            raise SMSErrors.REQUEST(debug_message=err)
