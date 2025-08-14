from django.views import View
from smartdjango import analyse, Validator

from Channel.channels.bark import Bark
from Channel.channels.mail import Mail
from Channel.channels.sms import SMS
from utils.auth import Auth


class ChannelView(View):
    list = [Bark, Mail, SMS]

    def get(self, request):
        """
        GET /api/channel/
        """
        return list(map(lambda c: c.__name__, filter(lambda c: c.active, ChannelView.list)))


class BarkView(View):
    @analyse.json(
        'uri',
        'content',
        Validator('title').null().default(None),
        Validator('sound').null().default(None),
        Validator('url').null().default(None),
        Validator('icon').null().default(None),
        Validator('group').null().default(None)
    )
    @Auth.require_account()
    def post(self, request):
        """
        POST /api/channel/bark
        """
        return Bark.run(request.json, request.data.account)


class SMSView(View):
    @analyse.json('phone', 'content')
    @Auth.require_account()
    def post(self, request):
        """
        POST /api/channel/sms
        """
        return SMS.run(request.json, request.data.account)


class MailView(View):
    @analyse.json(
        'mail',
        'content',
        Validator('appellation').null().default(None),
        Validator('subject').default('中央通知').null()
    )
    @Auth.require_account()
    def post(self, request):
        """
        POST /api/channel/mail
        """
        return Mail.run(request.json, request.data.account)
