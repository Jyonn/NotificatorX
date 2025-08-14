from smartdjango import Params, Validator

from Account.models import Account


class AccountParams(metaclass=Params):
    model_class = Account

    name: Validator
    nick: Validator
    token: Validator

    id_getter = Validator('id', final_name='account').to(Account.get_by_id)
