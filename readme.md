# NotificatorX

Your personal notification system.

## What is it?

NotificatorX is a notification system that allows you to send notifications to your users. For now, it supports sms, email, bark, and webhook notifications.

## How to use it?

### Install Personal Notification System
 
#### Requirements

- django > 5
- smartdjango > 4.3.0
- mysql database with configuration file `mysql.local.conf`

#### Admin Settings

The following settings are required to be configured in `Config_config` table:

- `ADMIN_EMAIL`: The email address of the administrator.
- `ADMIN_PASSWORD`: The password of the administrator account.

#### Email Settings

The following settings are required to be configured in `Config_config` table:

- `MAIL_SENDERS`: JSON array of sender ids, for example `["primary","backup"]`
- `MAIL_SENDER_<ID>_EMAIL`: sender email
- `MAIL_SENDER_<ID>_PASSWORD`: sender password
- `MAIL_SENDER_<ID>_SMTP_SERVER`: smtp server
- `MAIL_SENDER_<ID>_SMTP_PORT`: smtp port
- `MAIL_SENDER_<ID>_ENABLED`: optional, `true/false`, default `true`
- `MAIL_SENDER_<ID>_WEIGHT`: optional positive integer, default `1`
- `NOTIFY_DEFAULT_LOCALE`: optional, default `en-US`, supports `en-US`, `zh-CN`
- `NOTIFY_BRAND_NAME_EN`: optional, default `Meadow Inbox`
- `NOTIFY_BRAND_NAME_ZH`: optional, default `原野信箱`
- `NOTIFY_PRODUCT_NAME_EN`: optional, default `Notificator`
- `NOTIFY_PRODUCT_NAME_ZH`: optional, default `Notificator`

Example (`ID = PRIMARY`):

- `MAIL_SENDER_PRIMARY_EMAIL = noreply@example.com`
- `MAIL_SENDER_PRIMARY_PASSWORD = app_password`
- `MAIL_SENDER_PRIMARY_SMTP_SERVER = smtp.example.com`
- `MAIL_SENDER_PRIMARY_SMTP_PORT = 465`
- `MAIL_SENDER_PRIMARY_ENABLED = true`
- `MAIL_SENDER_PRIMARY_WEIGHT = 3`

Startup validation is enabled for mail sender configuration. Invalid or incomplete sender config will fail at service startup.

Mail sender admin APIs (require admin `Token` header):

- `GET /api/channel/mail-senders`: list senders
- `POST /api/channel/mail-senders`: create sender
- `GET /api/channel/mail-senders/<sender_id>`: get sender
- `PUT /api/channel/mail-senders/<sender_id>`: update sender
- `DELETE /api/channel/mail-senders/<sender_id>`: delete sender

Create payload example:

```json
{
  "sender_id": "PRIMARY",
  "email": "noreply@example.com",
  "password": "app_password",
  "smtp_server": "smtp.example.com",
  "smtp_port": 465,
  "enabled": true,
  "weight": 3
}
```

#### SMS Settings

The following settings are required to be configured in `Config_config` table:

- `YUNPIAN_APPKEY`: yunpian appkey, you should apply for it from [yunpian](https://www.yunpian.com/)

### Install Notification Client

#### Requirements

`pip install notificator`

#### Usage

```python
from notificator import Notificator

notificator = Notificator(
    username='your username',  # should be applied via `POST /api/account/` 
    token='your token', 
    token_type=Notificator.TokenType.RAW
)

# mail notification
notificator.mail(
    subject='subject',
    content='content',
    recipient_name='recipient name',
    mail='email address',
    action_url='https://example.com',
    action_text='View Details',
    footer_note='Need help? reply to this email.',
)

# sms notification
notificator.sms(
    content='content',
    phone='phone number',
)

# bark notification
notificator.bark(
    uri='bark uri',
    content='content',
    title='title',
    sound='sound',
    icon='icon',
    group='group',
    url='url',
)

# webhook notification
notificator.webhook(
    url='https://example.com/notify',
    method='POST',
    headers={'Authorization': 'Bearer xxx'},
    query={'source': 'notificator'},
    body={'message': 'content'},
)
```

### Unified Channel API (Recommended)

`POST /api/channel/send`

```json
{
  "message": {
    "format": "text",
    "title": "optional",
    "locale": "optional, en-US/zh-CN",
    "body": "required"
  },
  "deliveries": [
    {
      "channel": "sms",
      "target": "+8613800000000",
      "options": {}
    },
    {
      "channel": "mail",
      "target": "user@example.com",
      "options": {
        "locale": "zh-CN",
        "recipient_name": "Tom",
        "action_url": "https://example.com/jobs/123",
        "action_text": "View Details"
      }
    },
    {
      "channel": "webhook",
      "target": "https://example.com/hook",
      "options": {
        "method": "POST",
        "headers": {
          "Authorization": "Bearer xxx"
        }
      }
    }
  ]
}
```

Format support:

- `sms`: `text`
- `mail`: `text`, `html`, `markdown`
- `bark`: `text`, `markdown`
- `webhook`: `text`, `json`

If a channel does not support the selected format (for example, `sms` + `json`), the request is rejected.

Mail options (recommended):

- `locale`: language for mail rendering (`en-US` default, `zh-CN` optional)
- `recipient_name`: receiver display name in greeting line
- `action_url`: CTA button link
- `action_text`: CTA button text (default: `View Details`)
- `footer_note`: extra footer text

SMS locale behavior:

- `options.locale` / `message.locale` also applies to sms default template
- `en-US`: `[Notificator] {name}: {message}`
- `zh-CN`: `【Notificator】{name}：{message}`

Locale precedence:

- `deliveries[].options.locale`
- `message.locale`
- `NOTIFY_DEFAULT_LOCALE` (defaults to `en-US`)

Brand defaults:

- English: `Meadow Inbox`
- Chinese: `原野信箱`

Legacy compatibility:

- `appellation` is still accepted and mapped to `recipient_name`
