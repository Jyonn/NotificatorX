from django import views
from smartdjango import analyse, OK

from Account.models import Account
from Account.params import AccountParams
from utils import auth


class AccountView(views.View):
    @auth.require_login
    def get(self, request):
        """
        获取账号列表
        GET /api/account
        """
        return Account.get_all()

    @auth.require_login
    @analyse.json(AccountParams.name, AccountParams.nick)
    def post(self, request):
        """
        创建账号
        POST /api/account
        """
        account = Account.create(**request.json())
        return account.d()

    @auth.require_login
    @analyse.argument(AccountParams.id_getter)
    @analyse.json(
        AccountParams.name.copy().null().default(None),
        AccountParams.nick.copy().null().default(None),
        AccountParams.renew,
    )
    def put(self, request):
        """
        修改账号信息
        PUT /api/account/:id
        """
        account = request.argument.account
        account.update(
            name=request.json.name,
            nick=request.json.nick,
        )
        if request.json.renew:
            account.renew_token()
        return account.d()

    @auth.require_login
    @analyse.argument(AccountParams.id_getter)
    def delete(self, request):
        """
        删除账号
        DELETE /api/account/:id
        """
        request.argument.account.delete()
        return OK
