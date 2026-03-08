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


def get_login_token():
    token, dict_ = JWT.encrypt({})
    dict_['token'] = token
    return dict_

def authenticate(email, password):
    if email == Global.ADMIN_EMAIL and md5(password) == Global.ADMIN_PASSWORD:
        return get_login_token()
    raise AuthErrors.FAIL_AUTH

def require_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            request = analyse.get_request(*args)
            token = request.META.get('HTTP_TOKEN')
            if token is None:
                raise AuthErrors.REQUIRE_LOGIN
            JWT.decrypt(token)
        except Exception as err:
            raise AuthErrors.REQUIRE_LOGIN(details=err)
        return func(*args, **kwargs)
    return wrapper

def require_account(func):
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
            raise AuthErrors.REQUIRE_ACCOUNT(details=err)
        return func(*args, **kwargs)
    return wrapper
