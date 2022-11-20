import abc

from SmartDjango import E
from pydantic import BaseModel


@E.register(id_processor=E.idp_cls_prefix())
class ChannelError:
    INACTIVE = E("Channel Inactive")


class BaseChannel(abc.ABC):
    active = True

    @classmethod
    def handler(cls, body: BaseModel, user):
        raise NotImplementedError

    @classmethod
    def run(cls, body: BaseModel, user):
        if not cls.active:
            raise ChannelError.INACTIVE
        return cls.handler(body, user)
