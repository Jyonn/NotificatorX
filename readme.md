# NotificatorX

Your personal notification system.

## What is it?

NotificatorX is a notification system that allows you to send notifications to your users. For now, it supports sms, email, and bark notifications.

## How to use it?

### Install Personal Notification System
 
#### Requirements

- django == 3.1.12
- SmartDjango == 3.5.1
- mysql database with configuration file `mysql.local.conf`

#### Admin Settings

The following settings are required to be configured in `Config_config` table:

- `ADMIN_EMAIL`: The email address of the administrator.
- `ADMIN_PASSWORD`: The password of the administrator account.

#### Email Settings

The following settings are required to be configured in `Config_config` table:

- `SMTP_SERVER`: smtp server
- `SMTP_PORT`: smtp port
- `SENDER_EMAIL`: sender email
- `SENDER_EMAIL_PASSWORD`: sender password

#### SMS Settings

The following settings are required to be configured in `Config_config` table:

- `YUNPIAN_APPKEY`: yunpian appkey, you should apply for it from [yunpian](https://www.yunpian.com/)

### Install Notification Client

#### Requirements

`pip install notificator`

#### Usage

```python
from CentralNotificationSDK import Notificator

notificator = Notificator(
    username='your username',  # should be applied via `POST /api/account/` 
    token='your token', 
    token_type=Notificator.TokenType.RAW
)

# mail notification
notificator.mail(
    subject='subject',
    content='content',
    appellation='appellation',
    mail='email address',
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
```

