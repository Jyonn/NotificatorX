from django.views import View
from smartdjango import analyse
from smartdjango.analyse import Request

from Channel.channels.dispatcher import ChannelDispatcher
from Channel.channels.formats import MessageFormats
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


class BarkView(View):
    @analyse.json(
        ChannelParams.uri,
        ChannelParams.content,
        ChannelParams.title,
        ChannelParams.sound,
        ChannelParams.url,
        ChannelParams.icon,
        ChannelParams.group,
    )
    @auth.require_account
    def post(self, request):
        """
        POST /api/channel/bark
        """
        options = {
            'title': request.json.title,
            'sound': request.json.sound,
            'url': request.json.url,
            'icon': request.json.icon,
            'group': request.json.group,
        }
        options = {k: v for k, v in options.items() if v is not None}
        return ChannelDispatcher.send(
            message={
                'format': MessageFormats.TEXT,
                'title': request.json.title,
                'body': request.json.content,
            },
            deliveries=[{
                'channel': 'bark',
                'target': request.json.uri,
                'options': options,
            }],
            account=request.data.account,
        )


class SMSView(View):
    @analyse.json(ChannelParams.phone, ChannelParams.content)
    @auth.require_account
    def post(self, request):
        """
        POST /api/channel/sms
        """
        return ChannelDispatcher.send(
            message={
                'format': MessageFormats.TEXT,
                'body': request.json.content,
            },
            deliveries=[{
                'channel': 'sms',
                'target': request.json.phone,
                'options': {},
            }],
            account=request.data.account,
        )


class MailView(View):
    @analyse.json(
        ChannelParams.mail,
        ChannelParams.content,
        ChannelParams.appellation,
        ChannelParams.recipient_name,
        ChannelParams.action_url,
        ChannelParams.action_text,
        ChannelParams.footer_note,
        ChannelParams.locale,
        ChannelParams.subject,
    )
    @auth.require_account
    def post(self, request):
        """
        POST /api/channel/mail
        """
        options = {}
        if request.json.appellation is not None:
            options['appellation'] = request.json.appellation
        if request.json.recipient_name is not None:
            options['recipient_name'] = request.json.recipient_name
        if request.json.action_url is not None:
            options['action_url'] = request.json.action_url
        if request.json.action_text is not None:
            options['action_text'] = request.json.action_text
        if request.json.footer_note is not None:
            options['footer_note'] = request.json.footer_note
        if request.json.locale is not None:
            options['locale'] = request.json.locale

        return ChannelDispatcher.send(
            message={
                'format': MessageFormats.TEXT,
                'title': request.json.subject,
                'body': request.json.content,
            },
            deliveries=[{
                'channel': 'mail',
                'target': request.json.mail,
                'options': options,
            }],
            account=request.data.account,
        )


class WebhookView(View):
    @analyse.json(
        ChannelParams.webhook_url,
        ChannelParams.method,
        ChannelParams.headers,
        ChannelParams.query,
        ChannelParams.body,
    )
    @auth.require_account
    def post(self, request):
        """
        POST /api/channel/webhook
        """
        format_ = (
            MessageFormats.JSON
            if isinstance(request.json.body, (dict, list))
            else MessageFormats.TEXT
        )

        options = {
            'method': request.json.method,
            'headers': request.json.headers,
            'query': request.json.query,
        }
        if request.json.body is not None:
            options['body'] = request.json.body
        options = {k: v for k, v in options.items() if v is not None}

        return ChannelDispatcher.send(
            message={
                'format': format_,
                'body': request.json.body if request.json.body is not None else '',
            },
            deliveries=[{
                'channel': 'webhook',
                'target': request.json.url,
                'options': options,
            }],
            account=request.data.account,
        )


class MailSenderListView(View):
    @auth.require_login
    def get(self, request):
        """
        GET /api/channel/mail-senders
        """
        return MailSenderManager.list()

    @auth.require_login
    @analyse.json(
        MailSenderParams.sender_id,
        MailSenderParams.email,
        MailSenderParams.password,
        MailSenderParams.smtp_server,
        MailSenderParams.smtp_port,
        MailSenderParams.enabled_create,
        MailSenderParams.weight_create,
    )
    def post(self, request):
        """
        POST /api/channel/mail-senders
        """
        return MailSenderManager.create(request.json())


class MailSenderItemView(View):
    @auth.require_login
    def get(self, request, sender_id):
        """
        GET /api/channel/mail-senders/:sender_id
        """
        return MailSenderManager.get(sender_id)

    @auth.require_login
    @analyse.json(
        MailSenderParams.email_optional,
        MailSenderParams.password_optional,
        MailSenderParams.smtp_server_optional,
        MailSenderParams.smtp_port_optional,
        MailSenderParams.enabled_optional,
        MailSenderParams.weight_optional,
    )
    def put(self, request, sender_id):
        """
        PUT /api/channel/mail-senders/:sender_id
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
        DELETE /api/channel/mail-senders/:sender_id
        """
        return MailSenderManager.delete(sender_id)
