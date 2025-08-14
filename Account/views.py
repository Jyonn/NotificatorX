from django import views
from smartdjango import analyse, Validator, OK

from Account.models import Account
from Account.params import AccountParams
from utils.auth import Auth


class AccountView(views.View):
    @Auth.require_login()
    def get(self, request):
        """
        获取账号列表
        GET /api/account
        """
        return Account.get_all()

    @Auth.require_login()
    @analyse.json(AccountParams.name, AccountParams.nick)
    def post(self, request):
        """
        创建账号
        POST /api/account
        """
        account = Account.create(**request.json())
        return account.d()

    @Auth.require_login()
    @analyse.argument(AccountParams.id_getter)
    @analyse.json(
        AccountParams.nick.null().default(None),
        Validator('token').null().default(None).process(bool)
    )
    def put(self, request):
        """
        修改账号信息
        PUT /api/account/:id
        """
        account = request.argument.account
        if request.json.token:
            account.renew_token()
        if request.json.nick:
            account.update(request.json.nick)
        return account.d()

    @Auth.require_login()
    @analyse.argument(AccountParams.id_getter)
    def delete(self, request):
        """
        删除账号
        DELETE /api/account/:id
        """
        request.argument.account.delete()
        return OK
