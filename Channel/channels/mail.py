import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Optional

from SmartDjango import E, Hc

from Account.models import Account
from NotificatorX.global_settings import Global
from Channel.channels.base import BaseChannel
from utils.email_template import EmailTemplate


@E.register(id_processor=E.idp_cls_prefix())
class MailError:
    REQUEST = E('Mail Request', hc=Hc.InternalServerError)


class Mail(BaseChannel):
    class Body:
        mail: str
        subject: Optional[str] = '中央通知'
        appellation: Optional[str] = None
        content: str

    sender = Global.SENDER_EMAIL
    token = Global.SENDER_PASSWORD
    smtp = Global.SMTP_SERVER
    port = Global.SMTP_PORT

    @staticmethod
    def appellation_formatter(appellation):
        default = '你好：'
        if appellation is None or appellation == default:
            return default
        return '你好，{}：'.format(appellation)

    @classmethod
    def handler(cls, body: Body, account: Account):
        email = EmailTemplate(
            body.subject,
            cls.appellation_formatter(body.appellation),
            body.content,
        )

        msg = MIMEText(email.export(), 'html', 'utf-8')
        msg['From'] = formataddr(("中央通知服务", cls.sender))
        msg['To'] = formataddr((body.appellation, body.mail))
        msg['Subject'] = '【{}】通知'.format(account.nick)

        try:
            server = smtplib.SMTP_SSL(cls.smtp, cls.port)
            server.login(cls.sender, cls.token)
            server.sendmail(cls.sender, [body.mail, ], msg.as_string())
            server.quit()
        except Exception as err:
            raise MailError.REQUEST(debug_message=err)
