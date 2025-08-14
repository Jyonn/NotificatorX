from functools import wraps

from smartdjango import analyse, Error, Code

from Account.models import Account
from NotificatorX.global_settings import Global
from utils.hash import md5
from utils.jtoken import JWT


@Error.register
class AuthErrors:
    REQUIRE_LOGIN = Error("需要登录", code=Code.Unauthorized)
    FAIL_AUTH = Error("登录失败", code=Code.Unauthorized)

    REQUIRE_ACCOUNT = Error("需要口令", code=Code.Unauthorized)
    FAIL_ACCOUNT = Error("口令错误", code=Code.BadRequest)


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
        raise AuthErrors.FAIL_AUTH

    @classmethod
    def require_login(cls):
        def decorator(func):
            @wraps(func)
            def wrapper(r, *args, **kwargs):
                try:
                    jwt_str = r.META.get('HTTP_TOKEN')
                    if jwt_str is None:
                        raise AuthErrors.REQUIRE_LOGIN
                    JWT.decrypt(jwt_str)
                except Exception as err:
                    raise AuthErrors.REQUIRE_LOGIN(debug_message=err)
                return func(r, *args, **kwargs)
            return wrapper
        return decorator

    @classmethod
    def require_account(cls):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                request = analyse.get_request(*args)
                try:
                    auth = request.META.get('HTTP_AUTH')
                    if auth is None:
                        raise AuthErrors.REQUIRE_ACCOUNT
                    auth = auth.split('$', 1)
                    if len(auth) != 2:
                        raise AuthErrors.FAIL_ACCOUNT
                    request.data.account = Account.auth(*auth)
                except Exception as err:
                    raise AuthErrors.REQUIRE_ACCOUNT(debug_message=err)
                return func(*args, **kwargs)
            return wrapper
        return decorator
