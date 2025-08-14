from django import views
from smartdjango import analyse, Validator, Error

from utils.auth import Auth


class AuthView(views.View):
    @analyse.json(
        Validator('email', '邮箱'),
            Validator('password', '密码')
    )
    def post(self, request):
        """
        账号认证
        POST /api/auth
        """
        return Auth.login(**request.json())


class ErrorView(views.View):
    def get(self, request):
        """
        GET /api/error
        """
        return Error.all()
