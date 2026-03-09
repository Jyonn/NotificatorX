from smartdjango import Params, Validator

from Account.models import Account


class AccountParams(metaclass=Params):
    model_class = Account

    name: Validator
    nick: Validator
    renew = Validator('renew').null().default(False).to(bool)

    id_getter = Validator('id', final_name='account').to(Account.get_by_id)
