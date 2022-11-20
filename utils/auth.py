from functools import wraps

from SmartDjango import E

from Account.models import Account
from NotificatorX.global_settings import Global
from utils.hash import md5
from utils.jtoken import JWT


@E.register()
class AuthError:
    REQUIRE_LOGIN = E("需要登录")
    FAIL_AUTH = E("登录失败")

    REQUIRE_ACCOUNT = E("需要口令")
    FAIL_ACCOUNT = E("口令错误")


class Auth:
    @staticmethod
    def get_login_token():
        token, dict_ = JWT.encrypt({})
        dict_['token'] = token
        return dict_

    @classmethod
    def login(cls, email, password):
        if email == Global.ADMIN_EMAIL and md5(password) == Global.ADMIN_PASSWORD:
            return cls.get_login_token()
        raise AuthError.FAIL_AUTH

    @classmethod
    def require_login(cls):
        def decorator(func):
            @wraps(func)
            def wrapper(r, *args, **kwargs):
                try:
                    jwt_str = r.META.get('HTTP_TOKEN')
                    if jwt_str is None:
                        raise AuthError.REQUIRE_LOGIN
                    JWT.decrypt(jwt_str)
                except Exception as err:
                    raise AuthError.REQUIRE_LOGIN(debug_message=err)
                return func(r, *args, **kwargs)
            return wrapper
        return decorator

    @classmethod
    def require_account(cls):
        def decorator(func):
            @wraps(func)
            def wrapper(r, *args, **kwargs):
                try:
                    auth = r.META.get('HTTP_AUTH')
                    if auth is None:
                        raise AuthError.REQUIRE_ACCOUNT
                    auth = auth.split('$', 1)
                    if len(auth) != 2:
                        raise AuthError.FAIL_ACCOUNT
                    r.d.account = Account.auth(*auth)
                except Exception as err:
                    raise AuthError.REQUIRE_ACCOUNT(debug_message=err)
                return func(r, *args, **kwargs)
            return wrapper
        return decorator
