class NotifyLocales:
    EN_US = 'en-US'
    ZH_CN = 'zh-CN'
    DEFAULT = EN_US
    ALL = (EN_US, ZH_CN)
    ALIASES = {
        'en': EN_US,
        'en-us': EN_US,
        'zh': ZH_CN,
        'zh-cn': ZH_CN,
        'zh-hans': ZH_CN,
        'cn': ZH_CN,
    }

    @classmethod
    def all(cls):
        return list(cls.ALL)


def parse_locale(value):
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    key = raw.replace('_', '-').lower()
    return NotifyLocales.ALIASES.get(key)


def normalize_locale(value, default=NotifyLocales.DEFAULT):
    parsed = parse_locale(value)
    if parsed:
        return parsed
    return parse_locale(default) or NotifyLocales.DEFAULT


def resolve_locale(options=None, message=None, default=NotifyLocales.DEFAULT):
    options = options or {}
    message = message or {}

    for candidate in (
        options.get('locale'),
        options.get('lang'),
        message.get('locale'),
    ):
        parsed = parse_locale(candidate)
        if parsed:
            return parsed
    return normalize_locale(default)


def get_brand_name(locale, brand_en='Meadow Inbox', brand_zh='原野信箱'):
    if normalize_locale(locale) == NotifyLocales.ZH_CN:
        return brand_zh
    return brand_en


def get_product_name(locale, product_en='Notificator', product_zh='Notificator'):
    if normalize_locale(locale) == NotifyLocales.ZH_CN:
        return product_zh
    return product_en


def translate(locale, key, **kwargs):
    catalog = {
        'mail.default_subject': {
            NotifyLocales.EN_US: 'Notification',
            NotifyLocales.ZH_CN: '通知',
        },
        'mail.greeting': {
            NotifyLocales.EN_US: 'Hi {recipient_name},',
            NotifyLocales.ZH_CN: '{recipient_name}，你好：',
        },
        'mail.action.view_details': {
            NotifyLocales.EN_US: 'View Details',
            NotifyLocales.ZH_CN: '查看详情',
        },
        'mail.footer.sent_by': {
            NotifyLocales.EN_US: 'Sent by {sender_name}',
            NotifyLocales.ZH_CN: '此邮件由 {sender_name} 发送',
        },
        'sms.default_template': {
            NotifyLocales.EN_US: '[Notificator] {name}: {message}',
            NotifyLocales.ZH_CN: '【Notificator】{name}：{message}',
        },
    }
    lang = normalize_locale(locale)
    text = catalog.get(key, {}).get(lang) or catalog.get(key, {}).get(NotifyLocales.EN_US) or key
    if kwargs:
        return text.format(**kwargs)
    return text
