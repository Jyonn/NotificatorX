from SmartDjango import Analyse
from django import views
from oba import Obj
from smartify import P

from Account.models import AccountP, Account
from utils.auth import Auth


class AccountView(views.View):
    @staticmethod
    @Auth.require_login()
    def get(_):
        """
        获取账号列表
        GET /api/account
        """
        return Account.get_all()

    @staticmethod
    @Auth.require_login()
    @Analyse.r(b=[AccountP.name, AccountP.nick])
    def post(r):
        """
        创建账号
        POST /api/account
        """
        account = Account.create(**Obj.raw(r.d))
        return account.d()

    @staticmethod
    @Auth.require_login()
    @Analyse.r(a=[AccountP.account], b=[AccountP.nick.null(), P('token').null().process(bool)])
    def put(r):
        """
        修改账号信息
        PUT /api/account/:id
        """
        account = r.d.account
        if r.d.token:
            account.renew_token()
        if r.d.nick:
            account.update(r.d.nick)
        return account.d()

    @staticmethod
    @Auth.require_login()
    @Analyse.r(a=[AccountP.account])
    def delete(r):
        """
        删除账号
        DELETE /api/account/:id
        """
        r.d.account.delete()
