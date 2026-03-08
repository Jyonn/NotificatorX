import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

from smartdjango import Code, Error

from Account.models import Account
from NotificatorX.global_settings import Global, MailAccount
from Channel.channels.base import BaseChannel
from Channel.channels.formats import MessageFormats
from utils.email_template import EmailTemplate
from utils.i18n import get_brand_name, get_product_name, resolve_locale, translate


@Error.register
class MailErrors:
    REQUEST = Error('Mail Request', code=Code.InternalServerError)
    NO_ACTIVE_SENDER = Error('No active mail sender', code=Code.InternalServerError)


class Mail(BaseChannel):
    key = 'mail'
    active = True
    supported_formats = {
        MessageFormats.TEXT,
        MessageFormats.HTML,
        MessageFormats.MARKDOWN,
    }
    mail_accounts = Global.mail_accounts
    _rotation_index = 0
    # sender = Global.SENDER_EMAIL
    # token = Global.SENDER_PASSWORD
    # smtp = Global.SMTP_SERVER
    # port = Global.SMTP_PORT

    @classmethod
    def build_html(cls, format_: str, subject: str, content, options: dict, locale: str):
        recipient_name = options.get('recipient_name') or options.get('appellation')
        action_url = options.get('action_url')
        action_text = options.get('action_text')
        footer_note = options.get('footer_note')
        sender_name = get_brand_name(
            locale,
            brand_en=Global.BRAND_NAME_EN,
            brand_zh=Global.BRAND_NAME_ZH,
        )

        if format_ == MessageFormats.HTML:
            return str(content)

        content_html = EmailTemplate.text_to_html(content)
        return EmailTemplate(
            subject=subject,
            content_html=content_html,
            recipient_name=recipient_name,
            action_url=action_url,
            action_text=action_text,
            footer_note=footer_note,
            sender_name=sender_name,
            locale=locale,
            brand_name=get_brand_name(
                locale,
                brand_en=Global.BRAND_NAME_EN,
                brand_zh=Global.BRAND_NAME_ZH,
            ),
            product_name=get_product_name(
                locale,
                product_en=Global.PRODUCT_NAME_EN,
                product_zh=Global.PRODUCT_NAME_ZH,
            ),
        ).export()

    @classmethod
    def weighted_accounts(cls):
        cls.mail_accounts = Global.load_mail_accounts()
        weighted = []
        for account in cls.mail_accounts:
            weighted.extend([account] * account.weight)
        return weighted

    @classmethod
    def get_send_order(cls):
        pool = cls.weighted_accounts()
        if len(pool) == 0:
            raise MailErrors.NO_ACTIVE_SENDER

        start = cls._rotation_index % len(pool)
        cls._rotation_index = (cls._rotation_index + 1) % len(pool)
        rotated = pool[start:] + pool[:start]

        ordered = []
        seen = set()
        for item in rotated:
            if item.sender_id in seen:
                continue
            seen.add(item.sender_id)
            ordered.append(item)
        return ordered

    @classmethod
    def handler(cls, target: str, message: dict, options: dict, account: Account, format_: str):
        locale = resolve_locale(options=options, message=message, default=Global.DEFAULT_NOTIFY_LOCALE)
        subject = message.get('title') or translate(locale, 'mail.default_subject')
        content = message.get('body')
        recipient_name = options.get('recipient_name') or options.get('appellation')
        html = cls.build_html(format_, subject, content, options, locale)
        from_name = get_brand_name(
            locale,
            brand_en=Global.BRAND_NAME_EN,
            brand_zh=Global.BRAND_NAME_ZH,
        )

        last_err = None
        for mail_account in cls.get_send_order():  # type: MailAccount
            msg = MIMEText(html, 'html', 'utf-8')
            msg['From'] = formataddr((from_name, mail_account.mail))
            msg['To'] = formataddr((recipient_name or target, target))
            msg['Subject'] = subject

            try:
                server = smtplib.SMTP_SSL(mail_account.server, mail_account.port)
                server.login(mail_account.mail, mail_account.password)
                server.sendmail(mail_account.mail, [target, ], msg.as_string())
                server.quit()
                return
            except Exception as err:
                last_err = err
                continue

        raise MailErrors.REQUEST(details=last_err)
