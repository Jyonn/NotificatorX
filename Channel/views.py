from SmartDjango import Analyse
from django import views
from smartify import P

from Channel.channels.bark import Bark
from Channel.channels.mail import Mail
from Channel.channels.sms import SMS
from utils.auth import Auth


class ChannelView(views.View):
    list = [Bark, Mail, SMS]

    @staticmethod
    def get(_):
        """
        GET /api/channel/
        """
        return list(map(lambda c: c.__name__, filter(lambda c: c.active, ChannelView.list)))


class BarkView(views.View):
    @staticmethod
    @Analyse.r(b=[
        'uri', 'content',
        P('title').null(), P('sound').null(), P('url').null(), P('icon').null(), P('group').null()
    ])
    @Auth.require_account()
    def post(r):
        """
        POST /api/channel/bark
        """
        return Bark.run(r.d, r.d.account)


class SMSView(views.View):
    @staticmethod
    @Analyse.r(b=['phone', 'content'])
    @Auth.require_account()
    def post(r):
        """
        POST /api/channel/sms
        """
        return SMS.run(r.d, r.d.account)


class MailView(views.View):
    @staticmethod
    @Analyse.r(b=['mail', 'content', P('appellation').null(), P('subject').default('中央通知')])
    @Auth.require_account()
    def post(r):
        """
        POST /api/channel/mail
        """
        return Mail.run(r.d, r.d.account)
