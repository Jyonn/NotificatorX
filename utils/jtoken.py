"""171203 Adel Liu

第一次使用jwt身份认证技术
"""
import datetime

import jwt
from SmartDjango import E

from NotificatorX.global_settings import Global


@E.register()
class JWTError:
    JWT_EXPIRED = E("认证过期")
    ERROR_JWT_FORMAT = E("错误的认证格式")
    JWT_PARAM_INCOMPLETE = E("认证参数不完整")


class JWT:
    @staticmethod
    def encrypt(dict_, replace=True, expire_second=7 * 60 * 60 * 24):
        """
        jwt签名加密
        :param replace: 如果dict_中存在ctime或expire是否替换
        :param dict_: 被加密的字典数据
        :param expire_second: 过期时间
        """
        if replace or 'ctime' not in dict_.keys():
            dict_['ctime'] = datetime.datetime.now().timestamp()
        if replace or 'expire' not in dict_.keys():
            dict_['expire'] = expire_second
        encode_str = jwt.encode(dict_, Global.SECRET_KEY, algorithm=Global.JWT_ENCODE_ALGO)
        if isinstance(encode_str, bytes):
            encode_str = encode_str.decode()
        return encode_str, dict_

    @staticmethod
    def decrypt(str_: str):
        """
        jwt签名解密
        :param str_: 被加密的字符串
        """
        try:
            dict_ = jwt.decode(str_, Global.SECRET_KEY, Global.JWT_ENCODE_ALGO)
        except jwt.DecodeError as err:
            raise JWTError.ERROR_JWT_FORMAT(debug_message=err)
        if 'expire' not in dict_.keys() \
                or 'ctime' not in dict_.keys() \
                or not isinstance(dict_['ctime'], float) \
                or not isinstance(dict_['expire'], int):
            raise JWTError.JWT_PARAM_INCOMPLETE
        if datetime.datetime.now().timestamp() > dict_['ctime'] + dict_['expire']:
            raise JWTError.JWT_EXPIRED
        return dict_
