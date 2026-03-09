import json
import re

from smartdjango import Error, Code

from Account.models import Account
from NotificatorX.global_settings import Global
from Channel.channels.base import BaseChannel
from Channel.channels.formats import MessageFormats


@Error.register
class SMSErrors:
    REQUEST = Error('SMS Request', code=Code.InternalServerError)
    VERIFICATION_ONLY = Error('SMS only supports verification messages', code=Code.BadRequest)
    INVALID_CN_PHONE = Error('Only China mainland (+86) mobile numbers are supported', code=Code.BadRequest)
    INVALID_BODY = Error('Verification body must contain {code, time}', code=Code.BadRequest)
    INVALID_TEMPLATE_PARAM = Error('template_param must be an object', code=Code.BadRequest)
    INVALID_CONFIG = Error('Aliyun SMS config is incomplete', code=Code.InternalServerError)
    SDK_MISSING = Error('Aliyun SMS SDK is not installed', code=Code.InternalServerError)


class SMS(BaseChannel):
    key = 'sms'
    active = True
    supported_formats = {MessageFormats.VERIFICATION}
    cn_mobile_regex = re.compile(r'^1[3-9]\d{9}$')

    @classmethod
    def normalize_cn_phone(cls, target: str):
        raw = str(target or '').strip()
        if raw.startswith('+'):
            if not raw.startswith('+86'):
                raise SMSErrors.INVALID_CN_PHONE
            raw = raw[3:]
        elif raw.startswith('86') and len(raw) == 13:
            raw = raw[2:]

        if cls.cn_mobile_regex.match(raw) is None:
            raise SMSErrors.INVALID_CN_PHONE
        return raw

    @classmethod
    def create_client(cls):
        try:
            from alibabacloud_credentials.client import Client as CredentialClient
            from alibabacloud_dypnsapi20170525.client import Client as Dypnsapi20170525Client
            from alibabacloud_tea_openapi import models as open_api_models
        except Exception as err:
            raise SMSErrors.SDK_MISSING(details=err)

        endpoint = Global.ALI_SMS_ENDPOINT or 'dypnsapi.aliyuncs.com'
        access_key_id = Global.ALI_SMS_ACCESS_KEY_ID
        access_key_secret = Global.ALI_SMS_ACCESS_KEY_SECRET

        if access_key_id and access_key_secret:
            config = open_api_models.Config(
                access_key_id=access_key_id,
                access_key_secret=access_key_secret,
            )
        else:
            credential = CredentialClient()
            config = open_api_models.Config(credential=credential)

        config.endpoint = endpoint
        return Dypnsapi20170525Client(config)

    @classmethod
    def handler(cls, target: str, message: dict, options: dict, account: Account, format_: str):
        if format_ != MessageFormats.VERIFICATION:
            raise SMSErrors.VERIFICATION_ONLY

        body = message.get('body')
        if not isinstance(body, dict):
            raise SMSErrors.INVALID_BODY

        code = body.get('code')
        time_min = body.get('time')
        if not isinstance(code, str) or not isinstance(time_min, int) or time_min <= 0:
            raise SMSErrors.INVALID_BODY

        sign_name = Global.ALI_SMS_SIGN_NAME
        template_code = Global.ALI_SMS_TEMPLATE_CODE
        if not sign_name or not template_code:
            raise SMSErrors.INVALID_CONFIG

        phone_number = cls.normalize_cn_phone(target)
        template_param = options.get('template_param') or {}
        if not isinstance(template_param, dict):
            raise SMSErrors.INVALID_TEMPLATE_PARAM
        template_param = dict(template_param)
        template_param['code'] = code
        template_param['time'] = str(time_min)
        template_param['min'] = str(time_min)

        try:
            from alibabacloud_dypnsapi20170525 import models as dypnsapi_20170525_models
            from alibabacloud_tea_util import models as util_models

            client = cls.create_client()
            request = dypnsapi_20170525_models.SendSmsVerifyCodeRequest(
                sign_name=sign_name,
                template_code=template_code,
                phone_number=phone_number,
                template_param=json.dumps(template_param, ensure_ascii=False),
            )
            runtime = util_models.RuntimeOptions()
            client.send_sms_verify_code_with_options(request, runtime)
        except Exception as err:
            raise SMSErrors.REQUEST(details=err)
