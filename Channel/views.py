from django.views import View
from smartdjango import analyse
from smartdjango.analyse import Request

from Channel.channels.dispatcher import ChannelDispatcher
from Channel.mail_senders import MailSenderManager
from Channel.params import ChannelParams, MailSenderParams
from utils import auth


class ChannelView(View):
    def get(self, request):
        """
        GET /api/channel/
        """
        return ChannelDispatcher.active_channels()


class SendView(View):
    @analyse.json(ChannelParams.message, ChannelParams.deliveries)
    @auth.require_account
    def post(self, request: Request):
        """
        POST /api/channel/send
        """
        return ChannelDispatcher.send(
            message=request.json.message,
            deliveries=request.json.deliveries,
            account=request.data.account,
        )


class MailSenderListView(View):
    @auth.require_login
    def get(self, request):
        """
        GET /api/channel/mail
        """
        return MailSenderManager.list()

    @auth.require_login
    @analyse.json(
        MailSenderParams.sender_id,
        MailSenderParams.email,
        MailSenderParams.password,
        MailSenderParams.smtp_server,
        MailSenderParams.smtp_port,
        MailSenderParams.enabled.copy().null().default(True),
        MailSenderParams.weight.copy().null().default(1),
    )
    def post(self, request):
        """
        POST /api/channel/mail
        """
        return MailSenderManager.create(request.json())


class MailSenderItemView(View):
    @auth.require_login
    def get(self, request, sender_id):
        """
        GET /api/channel/mail/:sender_id
        """
        return MailSenderManager.get(sender_id)

    @auth.require_login
    @analyse.json(
        MailSenderParams.email.copy().null().default(None),
        MailSenderParams.password.copy().null().default(None),
        MailSenderParams.smtp_server.copy().null().default(None),
        MailSenderParams.smtp_port.copy().null().default(None),
        MailSenderParams.enabled.copy().null().default(None),
        MailSenderParams.weight.copy().null().default(None),
    )
    def put(self, request, sender_id):
        """
        PUT /api/channel/mail/:sender_id
        """
        payload = {}
        for key in ['email', 'password', 'smtp_server', 'smtp_port', 'enabled', 'weight']:
            value = getattr(request.json, key)
            if value is not None:
                payload[key] = value
        return MailSenderManager.update(sender_id, payload)

    @auth.require_login
    def delete(self, request, sender_id):
        """
        DELETE /api/channel/mail/:sender_id
        """
        return MailSenderManager.delete(sender_id)
