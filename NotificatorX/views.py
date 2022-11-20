from SmartDjango import Analyse, P, E
from django import views

from utils.auth import Auth


class AuthView(views.View):
    @staticmethod
    @Analyse.r(b=[P('email', '邮箱'), P('password', '密码')])
    def post(r):
        """
        账号认证
        POST /api/auth
        """
        return Auth.login(**r.d.dict())


class ErrorView(views.View):
    @staticmethod
    def get(_):
        """
        GET /api/error
        """
        return E.all()
